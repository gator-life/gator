# coding=utf-8

import unittest
import jsonpickle
import vcr
from scraper.scraper import scrap
from common.scraperstructs import Document
import os

class ScraperIntegrationTests(unittest.TestCase):

    # to record:
        # set disconnected=False (to set 2sec delay between requests)
        # delete test_run_scraper.yaml
        # set record_mode='once'
    def test_scrap(self):
        nb_doc = 12  # <20 to keep test under 2sec, 20 minus 8 filtered
        curr_doc = 0

        directory = os.path.dirname(os.path.abspath(__file__))
        with vcr.use_cassette(directory + '/vcr_cassettes/test_run_scraper.yaml', record_mode='none'):
            for json_doc in scrap(disconnected=True):
                doc = jsonpickle.decode(json_doc)
                self.assertIsInstance(doc, Document)  # deserialization is ok
                self.assertIsNotNone(doc.html_content)  # we don't return unavailable pages
                self.assertIsInstance(doc.html_content, unicode)  # 'str' sucks, must use unicode (python 3 str versions)
                self.assertNotIn('.gif', doc.link_element.url)  # check extension filter
                self.assertNotIn('youtu', doc.link_element.url)  # check regex filter

                curr_doc += 1
                if curr_doc == nb_doc:
                    break
            else:
                self.fail('error: not enough docs extracted from cassette, should be ' + str(nb_doc) + ', was ' + curr_doc)

if __name__ == '__main__':
    unittest.main()




