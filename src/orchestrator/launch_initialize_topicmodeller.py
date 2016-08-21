#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from common.JsonDocLoader import JsonDocLoader
from topicmodeller.topicmodeller import TopicModeller
from orchestrator.initialize_topicmodeller import initialize_topicmodeller_and_db, initialize_db


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                    filename='initialize_model.log')


class RepeatableHtmlDocuments(object):

    def __init__(self, folder):
        self.doc_loader = JsonDocLoader(folder)

    def __iter__(self):
        for scraper_document in self.doc_loader:
            yield scraper_document.html_content


def run_init_tm_and_db(documents_folder, tm_data_folder, num_topics):
    html_documents = RepeatableHtmlDocuments(documents_folder)

    initialize_topicmodeller_and_db(TopicModeller.make_with_html_tokenizer(), html_documents, tm_data_folder, num_topics)


def run_init_db(tm_data_folder):
    topic_modeller = TopicModeller.make_with_html_tokenizer()
    topic_modeller.load(tm_data_folder)
    initialize_db(topic_modeller)


run_init_tm_and_db('/home/mohamed/Development/Data/gator/Scraping_11-01-2016',
                   '/home/mohamed/Development/Data/gator/TM_LAST', 512)

# run_init_db('/home/mohamed/Development/Data/gator/TM')
