import re
import os
import socket
import ssl
import logging
import urlparse
import cchardet
import requests

from .reddit import reddit_link_elements_generator
from .scraperstructs import Document


def _is_valid_link(link_element, invalid_paths_regex, invalid_extensions):
    url = link_element.url
    path = urlparse.urlparse(url).path
    extension = os.path.splitext(path)[1]  # splitext split in two : path and extension
    if extension in invalid_extensions:
        return False
    invalid_path_found = invalid_paths_regex.search(url)
    if invalid_path_found:
        return False
    return True


class _HtmlExtractor(object):

    def __init__(self):
        self._requests = requests  # field instead of static call for mocking 'requests' lib in some tests

    def try_get_html(self, url):
        try:
            data = self._requests.get(url, timeout=2)

            header_encoding = data.encoding
            if not header_encoding:
                logging.debug('filtered: no header encoding, url:%s', url)
                return None
            # cchardet way faster than data.apparent_encoding
            # https://github.com/kennethreitz/requests/issues/2359
            guessed_encoding = cchardet.detect(data.content)['encoding'].lower()
            if guessed_encoding is None or header_encoding.lower() != guessed_encoding:
                logging.debug(
                    'filtered: guessed encoding %s different from header encoding %s, url:%s',
                    guessed_encoding, header_encoding, url)
                return None
            data.content.decode(guessed_encoding)  # check we can get unicode object from raw data (could raise exception)
            if not self._is_size_reasonable(data.text):
                logging.debug('filtered: size too big, url:%s', url)
                return None
            return data.text
        except (
                ssl.SSLError,
                socket.timeout,
                UnicodeDecodeError,
                requests.exceptions.RequestException
        ) as expected_exception:
            logging.warning('managed exception, url: ' + url)
            logging.exception(expected_exception)
            return None
        #  to not crash the whole process...
        except Exception as unexpected_exception:  # pylint: disable=broad-except
            logging.error('unexpected exception, url: ' + url)
            logging.exception(unexpected_exception)
            return None

    @classmethod
    def _is_size_reasonable(cls, text):
        return len(text) < 1000000


def _get_invalid_regex():
    invalid_path_video = ['youtu', 'vimeo', 'vid.me', 'tube', 'gfycat', 'vine', 'motion', 'twitch', 'stream', 'video']
    invalid_path_image = ['img', 'flickr', 'flic.kr', 'instagram', 'image', 'imgreview', 'screencloud', 'prnt']
    invalid_path_sound = ['itune', 'soundcloud', 'gifsound', 'spotify']
    invalid_path_social_network = ['twitter', 'facebook']
    invalid_path_aggregator = ['reddit', 'redd.it', 'tumblr', 'voat']
    invalid_path_store = ['ebay', 'amazon']
    invalid_path_dating = ['okcupid']
    invalid_paths = invalid_path_video + invalid_path_image + invalid_path_sound + invalid_path_social_network + \
        invalid_path_aggregator + invalid_path_store + invalid_path_dating
    invalid_paths_regex = re.compile('(' + '|'.join(invalid_paths) + ')')
    return invalid_paths_regex


def _scrap(disconnected):
    invalid_paths_regex = _get_invalid_regex()
    invalid_extensions = ['.jpg', '.gif', '.png', '.webm']
    links_elts = reddit_link_elements_generator(disconnected)
    filtered_links = (link for link in links_elts if _is_valid_link(link, invalid_paths_regex, invalid_extensions))
    docs = _get_doc_generator(filtered_links)
    return docs


def _get_doc_generator(link_elts):
    html_extractor = _HtmlExtractor()
    links_and_htmls = ((link, html_extractor.try_get_html(link.url)) for link in link_elts)
    documents = (Document(link, html) for link, html in links_and_htmls if html is not None)
    return documents


class Scraper(object):

    def __init__(self, disconnected=False):
        self.disconnected = disconnected

    def scrap(self):
        """
        :return: generator of scraperstructs.Document
        """
        return _scrap(self.disconnected)
