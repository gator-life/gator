#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from orchestrator.scrap_and_learn import scrap_and_learn
from common.datehelper import utcnow
import scraper.scraperstructs as scrap
from server.dal import Dal, NULL_FEATURE_SET, REF_FEATURE_SET
import server.frontendstructs as struct


class MockScraper(object):

    @staticmethod
    def scrap():
        def scrap_doc(index):
            str_index = str(index)
            return scrap.Document(
                scrap.LinkElement(
                    "url" + str_index, None, scrap.OriginInfo("title" + str_index, None, None, None, None), None),
                'html')

        # chunk_size(3) + 1
        # the last document is an other instance of a duplicated url, should be ignored by the url unicity checker
        return [scrap_doc(3), scrap_doc(4), scrap_doc(5), scrap_doc(6), scrap_doc(3)]


class MockSaver(object):

    def __init__(self):
        self.saved_docs = []

    def save(self, doc):
        self.saved_docs.append(doc)


class MockTopicModeller(object):
    feature_vector = [1.0]

    @staticmethod
    def classify(doc_content):
        if doc_content == 'html':
            return MockTopicModeller.feature_vector
        else:
            raise ValueError(doc_content)


class ScrapAndLearnTests(unittest.TestCase):

    def setUp(self):
        self.dal = Dal()
        self.dummy_feat_vec = struct.FeatureVector.make_from_scratch([], NULL_FEATURE_SET)

    def test_scrap_and_learn(self):
        # I)setup database and mocks
        # I.1) user
        user1 = struct.User.make_from_scratch("test_scrap_and_learn_user1", ["interests1"])
        self.dal.save_user(user1, "password1")
        self._save_dummy_profile_for_user(user1)
        user2 = struct.User.make_from_scratch("test_scrap_and_learn_user2", ["interests2"])
        self.dal.save_user(user2, "password2")
        self._save_dummy_profile_for_user(user2)
        # I.2) doc
        doc1 = struct.Document.make_from_scratch("url1", 'hash1', 'title1', "sum1", self.dummy_feat_vec)
        doc2 = struct.Document.make_from_scratch("url2", 'hash2', 'title2', "sum2", self.dummy_feat_vec)
        self.dal.save_documents([doc1, doc2])
        # I.3) userDoc
        user1_user_docs = [
            struct.UserDocument.make_from_scratch(doc1, grade=0.0),  # this one should be removed
            struct.UserDocument.make_from_scratch(doc2, grade=1.0)]
        self.dal.save_users_docs([(user1, user1_user_docs)])
        # II) Orchestrate
        mock_saver = MockSaver()
        scrap_and_learn(MockScraper(), mock_saver, MockTopicModeller(), docs_chunk_size=2,
                        user_docs_max_size=5, seen_urls_cache_start_date=utcnow(),
                        skip_user_func=lambda u: 'test_scrap_and_learn' not in u.email)

        # III) check database and mocks
        result_users_docs = self.dal.get_users_docs([user1, user2])
        result_user1_docs = result_users_docs[0]
        result_user2_docs = result_users_docs[1]
        self.assertEquals(5, len(result_user1_docs))  # 5 because of user_docs_max_size=5
        self.assertEquals(4, len(result_user2_docs))
        for user_doc in result_user1_docs:
            if user_doc.document.title == 'title1':  # doc1 should have been deleted because grade=0.0
                self.fail()
        self.assertEquals(4, len(mock_saver.saved_docs))  # MockScraper generate 4 docs
        for doc in mock_saver.saved_docs:
            # currently, model versioning is not managed, all is set to ref
            self.assertEquals(REF_FEATURE_SET, doc.feature_vector.feature_set_id)
            self.assertEquals(MockTopicModeller.feature_vector, doc.feature_vector.vector)

    def _save_dummy_profile_for_user(self, user):
        feature_vector = struct.FeatureVector.make_from_scratch([1.0], "featureSetId-test_scrap_learn")
        model_data = struct.UserProfileModelData.make_empty(1)
        self.dal.save_user_computed_profile(user, struct.UserComputedProfile.make_from_scratch(feature_vector, model_data))

if __name__ == '__main__':
    unittest.main()
