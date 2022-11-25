import os
import unittest
import config


# get_response
# get_links
# parse_page
# save_page
# parse_plain_text

# crawler
    # init
    # progress
    # crawl
    # index
    # filter
    # index frequency
    # get_word_frequency
    # get_frequency_json
    # save_frequency_json
    # save_frequency_csv


class TestCrawlerInit(unittest.TestCase):
    def test_init_name(self):
        num = Crawler.num_crawlers
        crawler = Crawler()
        self.assertEqual(str(crawler), f'crawler_{num}')
        

class TestCrawlerFrequency(unittest.TestCase):
    def test_index_freq(self):
        crawler = Crawler(record_frequency=True)
        data = "test test test test fun food food web web web web crawler"
        crawler.index_frequency(data)
        self.assertEqual(crawler.frequency_map['test'], 4)
        self.assertEqual(crawler.frequency_map['fun'], 1)
        self.assertEqual(crawler.frequency_map['food'], 2)
        self.assertEqual(crawler.frequency_map['web'], 4)

    def test_filter(self):
        crawler = Crawler()
        crawler.visited.add("example.com")
        self.assertEqual(crawler.filter("example.com"), False)

    def test_sanitized(self):
        crawler = Crawler()
        data = "he#$ll)(o"
        self.assertEqual(crawler.sanitize_word(data), 'hello')

    # TODO: test fequency json
    # TODO: crawl unit tests/ integration tests
        

    

    

if __name__ == '__main__':
    config.init()
    from crawler import Crawler

    unittest.main()