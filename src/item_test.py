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
