# the tested module
from item import *

# test helpers
import test_helper
from lib.mock import Mock
import pickle
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest
import config

sample_item = {
	'author': u'pizzaburger',
	'categories': {u'user/-/label/03-comics---imagery': u'03-comics---imagery',
	               u'user/-/state/com.google/fresh': u'fresh',
	               u'user/-/state/com.google/reading-list': u'reading-list'},
	'content': u'<div><br><p>Thx Penntastic</p>\n<p><img src="http://failblog.files.wordpress.com/2008/06/assembly-fail.jpg" alt="fail owned pwned pictures"></p>\n<img alt="" border="0" src="http://feeds.wordpress.com/1.0/categories/failblog.wordpress.com/1234/"> <img alt="" border="0" src="http://feeds.wordpress.com/1.0/tags/failblog.wordpress.com/1234/"> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/gocomments/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/comments/failblog.wordpress.com/1234/"></a> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/godelicious/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/delicious/failblog.wordpress.com/1234/"></a> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/gostumble/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/stumble/failblog.wordpress.com/1234/"></a> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/godigg/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/digg/failblog.wordpress.com/1234/"></a> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/goreddit/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/reddit/failblog.wordpress.com/1234/"></a> <img alt="" border="0" src="http://stats.wordpress.com/b.gif?host=failblog.org&amp;blog=2441444&amp;post=1234&amp;subd=failblog&amp;ref=&amp;feed=1"></div><img src="http://feeds.feedburner.com/~r/failblog/~4/318806514" height="1" width="1">',
	'crawled': 1214307453013L,
	'google_id': u'tag:google.com,2005:reader/item/dcb79527f18794d0',
	'link': u'http://feeds.feedburner.com/~r/failblog/~3/318806514/',
	'original_id': u'http://failblog.wordpress.com/?p=1234',
	'published': 1214269209.0,
	'sources': {u'feed/http://feeds.feedburner.com/failblog': u'tag:google.com,2005:reader/feed/http://feeds.feedburner.com/failblog'},
	'summary': u'',
	'title': u'Assembly Fail',
	'updated': 1214269209.0}

def item_with_title(title):
	item = sample_item.copy()
	item['title'] = title
	return item

class ItemTest(unittest.TestCase):

	def setUp(self):
		self.output_folder = test_helper.init_output_folder()

		# initialise the DB mock
		app_globals.DATABASE = self.mock_db = Mock()

	def tearDown(self):
		rm_rf(self.output_folder)
		self.mock_db.clear()
	
	# ------------------------------------------------------------------

	def test_basename(self):
		item = Item(sample_item, 'feed-name')
		assert item.basename == '20080624110009 Assembly Fail .||tag%3Agoogle.com%2C2005%3Areader%2Fitem%2Fdcb79527f18794d0||'
	
	def test_read(self):
		item = Item(sample_item, 'feed-name')
		
	def test_remove_open_and_close_html_tags(self):
		item = Item(item_with_title('<openTag attr="dsdjas">some title</openTag>'), 'feed-name')
		self.assertEqual(item.title, 'some title')

	@test_helper.pending
	def test_dont_remove_tags_when_there_is_no_matching_open_or_close_tag(self):
		item = Item(item_with_title('<notATag>some title'), 'feed-name')
		self.assertEqual(item.title, '<notATag>some title')
		
		item = Item(item_with_title('some title</notATag>'), 'feed-name')
		self.assertEqual(item.title, 'some title</notATag>')
		
		item = Item(item_with_title('<noEndTag>some title</noStartTag>'), 'feed-name')
		self.assertEqual(item.title, '<noEndTag>some title</noStartTag>')
	
	def test_remove_self_closing_tags(self):
		item = Item(item_with_title('<self_ending_tag />some title'), 'feed-name')
		self.assertEqual(item.title, 'some title')
		
		item = Item(item_with_title('<self_ending_tag/>some title'), 'feed-name')
		self.assertEqual(item.title, 'some title')

	def test_remove_multiple_tags(self):
		item = Item(item_with_title('<a>some</a> <a>title</a>'), 'feed-name')
		self.assertEqual(item.title, 'some title')
	
	def test_remove_nested_tags(self):
		item = Item(item_with_title('<div>some <div><a>title</a></div></div>'), 'feed-name')
		self.assertEqual(item.title, 'some title')
	
	def test_convert_html_entities(self):
		item = Item(item_with_title('caf&eacute;&#233;&#39;s'), 'feed-name')
		self.assertEqual(item.title, u'caf\xe9\xe9\'s')
	
	def test_strip_unicode_from_basename(self):
		item = Item(item_with_title('caf&eacute;&#39;s'), 'feed-name')
		self.assertTrue(' cafs .||' in item.basename)
		