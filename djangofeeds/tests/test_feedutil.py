import unittest2 as unittest
from datetime import datetime
import feedparser

from djangofeeds import feedutil
from djangofeeds.feedutil import date_to_datetime, find_post_content
from djangofeeds.tests.test_importers import get_data_file

NOT_ENCODEABLE = ('\xd0\x9e\xd1\x82\xd0\xb2\xd0\xb5\xd1\x82\xd1\x8b '
                  '\xd0\xbd\xd0\xb0 \xd0\xb2\xd0\xb0\xd1\x88\xd0\xb8 '
                  '\xd0\xb2\xd0\xbe\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd1'
                  '\x8b \xd0\xbf\xd1\x80\xd0\xbe Mac')


class test_date_to_datetime(unittest.TestCase):

    def test_no_date(self):
        x = date_to_datetime("date_test")
        date = x(None, {})
        now = datetime.now()
        self.assertTupleEqual((date.year, date.month, date.day),
                              (now.year, now.month, now.day))

    def test_wrong_type(self):
        x = date_to_datetime("date_test")
        date = x(None, {"date_test": object()})
        now = datetime.now()
        self.assertTupleEqual((date.year, date.month, date.day),
                              (now.year, now.month, now.day))


class test_find_post_content(unittest.TestCase):

    def test_returns_empty_string_on_UnicodeDecodeError(self):

        def raise_UnicodeDecodeError(*args, **kwargs):
            return "quickbrown".encode("zlib").encode("utf-8")

        prev = feedutil.truncate_html_words
        feedutil.truncate_html_words = raise_UnicodeDecodeError
        try:
            self.assertEqual(find_post_content(None, {
                                "description": "foobarbaz"}), "")
        finally:
            feedutil.truncate_html_words = prev


class test_generate_guid(unittest.TestCase):

    def test_handles_not_encodable_text(self):
        entry = dict(title=NOT_ENCODEABLE, link="http://foo.com")
        guid = feedutil.generate_guid(entry)
        self.assertTrue(guid)

    def test_is_unique(self):
        entry1 = dict(title="First", link="http://foo1.com")
        feedutil.generate_guid(entry1)
        entry2 = dict(title="Second", link="http://foo1.com")
        feedutil.generate_guid(entry2)
        self.assertNotEqual(entry1, entry2)

    def test_utf8_url(self):
        """Try to reproduce a utf8 encoding error."""
        utf8_entry = dict(title="UTF-8",
            link="premi\xc3\xa8re_")
        feedutil.get_entry_guid(None, utf8_entry)


    def test_search_alternate_links(self):
        feed_str = get_data_file("bbc_homepage.html")
        feed = feedparser.parse(feed_str)
        links = feedutil.search_alternate_links(feed)
        self.assertListEqual(links, [
            "http://newsrss.bbc.co.uk/rss/newsonline_world_edition/"
            "front_page/rss.xml"])

        feed_str = get_data_file("newsweek_homepage.html")
        feed = feedparser.parse(feed_str)
        links = feedutil.search_alternate_links(feed)
        self.assertListEqual(links, [
            "http://feeds.newsweek.com/newsweek/TopNews"])

class test_alternate_links(unittest.TestCase):

    def test_search_alternate_links_double_function(self):
        feed_str = get_data_file("smp.no.html")
        feed = feedparser.parse(feed_str)
        links = feedutil.search_alternate_links(feed)
        self.assertListEqual(links,
            ['http://www.smp.no/?service=rss',
            'http://www.smp.no/?service=rss&t=0',
            'http://www.smp.no/nyheter/?service=rss',
            'http://www.smp.no/kultur/?service=rss']
        )
        links = feedutil.search_links_url(feed_str, 'http://www.smp.no/')
        self.assertListEqual(links,
            ['http://www.smp.no/?service=rss',
            'http://www.smp.no/?service=rss&t=0',
            'http://www.smp.no/nyheter/?service=rss',
            'http://www.smp.no/kultur/?service=rss']
        )
