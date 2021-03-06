#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import unittest

from topicmodeller.topicmodeller import TopicModeller


class TopicModellerTests(unittest.TestCase):

    class MockTokenizer(object):

        @classmethod
        def tokenize(cls, text):
            return [word for word in text.split() if word != 'is']

    def test_initialize_classify_save_load_classify_is_ok(self):
        doc1 = u'I like orange, i really love orange orange is my favorite color, green sucks'
        doc2 = u'Green is cool, green is nice, green is swag, orange not so much'
        docs = [doc1, doc2]

        topic_modeller = TopicModeller()
        topic_modeller._tokenizer = self.MockTokenizer()
        topic_modeller._remove_optimizations = True  # pylint: disable=protected-access
        topic_modeller.initialize(docs, num_topics=2)

        # check number of topics is expected
        self.assertEquals(2, len(topic_modeller.get_topics()))

        # check most recurrent words are selected topics (green, orange)
        index_orange = -1
        index_green = -1
        for index, topic in zip(range(2), topic_modeller.get_topics()):
            (word, _) = topic[0]
            if word == u'orange':
                index_orange = index
            if word == u'green':
                index_green = index
        self.assertNotEquals(-1, index_orange)
        self.assertNotEquals(-1, index_green)

        # check classification is logical between doc1 and doc2 with two axes:
        # -same doc, different topic
        # -same topic, different docs
        (ok1, classification_after_init_doc1) = topic_modeller.classify(doc1)
        self.assertTrue(ok1)
        self.assertEquals(len(topic_modeller.get_topics()), len(classification_after_init_doc1))
        (ok2, classification_after_init_doc2) = topic_modeller.classify(doc2)
        self.assertTrue(ok2)
        self.assertTrue(classification_after_init_doc1[index_orange] > classification_after_init_doc1[index_green])
        self.assertTrue(classification_after_init_doc2[index_orange] < classification_after_init_doc2[index_green])
        self.assertTrue(classification_after_init_doc1[index_orange] > classification_after_init_doc2[index_orange])
        self.assertTrue(classification_after_init_doc1[index_green] < classification_after_init_doc2[index_green])

        # check save then load model gives exact same classification for a document
        directory = os.path.dirname(os.path.abspath(__file__))
        topic_modeller.save(directory)

        deserialized_topic_modeller = TopicModeller()
        deserialized_topic_modeller._tokenizer = self.MockTokenizer()
        deserialized_topic_modeller.load(directory)

        (ok1_reload, classification_after_load_doc1) = deserialized_topic_modeller.classify(doc1)
        self.assertTrue(ok1_reload)
        self.assertEquals(len(topic_modeller.get_topics()), len(classification_after_load_doc1))
        for after_init, after_load in zip(classification_after_init_doc1, classification_after_load_doc1):
            self.assertAlmostEqual(after_init, after_load, places=4)

    def test_topic_field(self):
        nb_docs = 5
        nb_words_by_doc = 150
        dict_size = 150
        nb_topics = 2
        words = ["word" + str(i) for i in range(dict_size)]
        topic_modeller = self._build_topic_model(nb_docs, nb_topics, nb_words_by_doc, words)
        self.assertEquals(nb_topics, len(topic_modeller.get_topics()))
        for topic in topic_modeller.get_topics():
            # we keep topic_modeller._nb_words_by_topic most significant words for each topics
            self.assertEquals(topic_modeller._nb_words_by_topic, len(topic))
            for word, weight in topic:
                self.assertTrue(word in words)
                self.assertTrue(weight > 0)

    def test_get_model_id(self):
        nb_docs = 3
        nb_words_by_doc = 20
        dict_size = 50
        nb_topics = 2
        words = ["word" + str(i) for i in range(dict_size)]
        topic_modeller = self._build_topic_model(nb_docs, nb_topics, nb_words_by_doc, words)
        topic_modeller_same = self._build_topic_model(nb_docs, nb_topics, nb_words_by_doc, words)
        topic_modeller_diff = self._build_topic_model(nb_docs, nb_topics, nb_words_by_doc + 1, words)

        model_id = topic_modeller.get_model_id()
        model_id_same = topic_modeller_same.get_model_id()
        self.assertEquals(model_id, model_id_same)
        self.assertNotEquals(model_id, topic_modeller_diff)

        directory = os.path.dirname(os.path.abspath(__file__))
        topic_modeller.save(directory)
        deserialized_topic_modeller = TopicModeller()
        deserialized_topic_modeller._tokenizer = self.MockTokenizer()
        deserialized_topic_modeller.load(directory)
        model_id_after_load = deserialized_topic_modeller.get_model_id()
        self.assertEquals(model_id, model_id_after_load)

    def _build_topic_model(self, nb_docs, nb_topics, nb_words_by_doc, words):
        docs = []
        random.seed(0)
        for _ in range(nb_docs):
            doc = ""
            for _ in range(nb_words_by_doc):
                doc += " " + random.choice(words)
            docs.append(doc)
        topic_modeller = TopicModeller()
        topic_modeller._tokenizer = self.MockTokenizer()
        topic_modeller._remove_optimizations = True  # pylint: disable=protected-access
        topic_modeller.initialize(docs, num_topics=nb_topics)
        return topic_modeller


if __name__ == '__main__':
    unittest.main()
