#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topicmodeller.topicmodeller import initialize_model

import logging


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,
                    filename='tm_initialize_model.log')

initialize_model(documents_folder='/home/mohamed/Development/Data/TopicModelling/recorded_html_01_08',
                 tm_data_folder='/home/mohamed/Development/Data/TopicModelling/data')
