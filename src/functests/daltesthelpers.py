# -*- coding: utf-8 -*-

import userdocmatch.frontendstructs as struct
from userdocmatch.dal import Dal
from server.dalaccount import DalAccount, Account


def create_user_dummy(email, password_hash, interests):
    dal_account = DalAccount()
    account = Account(email, password_hash)
    dal_account.create(account)
    user_id = account.account_id
    dal = Dal()
    ref_feature_set_id = dal.feature_set.get_ref_feature_set_id()
    dummy_doc1 = struct.Document(
        url='https://www.google.com', url_hash='hash_create_user_dummy_1_' + user_id, title='google.com',
        summary='we will buy you',
        feature_vector=struct.FeatureVector([1, 1, 1, 1], ref_feature_set_id))
    dummy_doc2 = struct.Document(
        url='gator.life', url_hash='hash_create_user_dummy_2_' + user_id, title='gator.life', summary='YGNI',
        feature_vector=struct.FeatureVector([1, 1, 1, 1], ref_feature_set_id))
    dal.doc.save_documents([dummy_doc1, dummy_doc2])

    new_user = struct.User.make_from_scratch(user_id=user_id, interests=interests)
    dal.user.save_user(new_user)
    user_doc1 = struct.UserDocument(document=dummy_doc1, grade=1.0)
    user_doc2 = struct.UserDocument(document=dummy_doc2, grade=0.5)
    dal.user_doc.save_user_docs(new_user, [user_doc1, user_doc2])

    return new_user


def init_features_dummy(feature_set_id):
    dal = Dal()
    model_id = 'init_features_dummy_model_id'
    dal.topic_model.save(struct.TopicModelDescription.make_from_scratch(model_id, [
        [('sport', 1)],
        [('trading', 1)],
        [('bmw', 1)],
        [('C++', 1)]
    ]))
    dal.feature_set.save_feature_set(
        struct.FeatureSet(
            feature_set_id, feature_names=['sport', 'trading', 'bmw', 'c++'], model_id=model_id))


NEW_USER_ID = "new_user_id"
