# the tested module
from item import *

# test helpers
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


def test_minimal_item():
	itemid = 'tag:my_google_id'
	item = MinimalItem(itemid)
	assert item.key == 'tag%3A'
	assert item.resources_path == self.output_folder + '/_resources/tag%3Amy_google_id'
	ensure_dir_exists(item.resources_path)
	touch_file(item.resources_path + '/somefile')
	assert os.path.exists(item.resources_path) == True
	item.delete()
	assert os.path.exists(item.resources_path) == False

class ItemTest(unittest.TestCase):

	def setUp(self):
		self.output_folder = test_helper.init_output_folder()

		# initialise the DB mock
		app_globals.DATABASE = self.mock_db = Mock()

	def tearDown(self):
		rm_rf(self.output_folder)
		self.mock_db.clear()
	
	# ------------------------------------------------------------------

	def test_basename():
		item = Item(sample_item, 'feed-name')
		assert item.basename == '2008-06-24|11-00-09 Assembly Fail .||tag%3Agoogle.com%2C2005%3Areader%2Fitem%2Fdcb79527f18794d0||'
	
	def test_output():
		item = Item(sample_item, 'feed-name')
		import template
		template_mock = template.create = Mock()
		assert template_mock.call_args_list == [(
			({
				'content': '<div>\n <br />\n <p>\n  Thx Penntastic\n </p>\n <p>\n  <img src="_resources/tag%253Agoogle.com%252C2005%253Areader%252Fitem%252Fdcb79527f18794d0/assembly-fail.jpg" alt="fail owned pwned pictures" />\n </p>\n <img alt="" border="0" src="http://feeds.wordpress.com/1.0/categories/failblog.wordpress.com/1234/" />\n <img alt="" border="0" src="http://feeds.wordpress.com/1.0/tags/failblog.wordpress.com/1234/" />\n <a rel="nofollow" href="http://feeds.wordpress.com/1.0/gocomments/failblog.wordpress.com/1234/">\n  <img alt="" border="0" src="http://feeds.wordpress.com/1.0/comments/failblog.wordpress.com/1234/" />\n </a>\n <a rel="nofollow" href="http://feeds.wordpress.com/1.0/godelicious/failblog.wordpress.com/1234/">\n  <img alt="" border="0" src="http://feeds.wordpress.com/1.0/delicious/failblog.wordpress.com/1234/" />\n </a>\n <a rel="nofollow" href="http://feeds.wordpress.com/1.0/gostumble/failblog.wordpress.com/1234/">\n  <img alt="" border="0" src="http://feeds.wordpress.com/1.0/stumble/failblog.wordpress.com/1234/" />\n </a>\n <a rel="nofollow" href="http://feeds.wordpress.com/1.0/godigg/failblog.wordpress.com/1234/">\n  <img alt="" border="0" src="http://feeds.wordpress.com/1.0/digg/failblog.wordpress.com/1234/" />\n </a>\n <a rel="nofollow" href="http://feeds.wordpress.com/1.0/goreddit/failblog.wordpress.com/1234/">\n  <img alt="" border="0" src="http://feeds.wordpress.com/1.0/reddit/failblog.wordpress.com/1234/" />\n </a>\n <img alt="" border="0" src="_resources/tag%253Agoogle.com%252C2005%253Areader%252Fitem%252Fdcb79527f18794d0/b.gif" />\n</div>\n<img src="http://feeds.feedburner.com/~r/failblog/~4/318806514" height="1" width="1" />\n',
				'title_html': '<title>Assembly Fail</title>',
				'title_link': '<a href="http://feeds.feedburner.com/~r/failblog/~3/318806514/">Assembly Fail</a>',
				'via': u'from tag <b>feed-name</b><br />url feeds.feedburner.com / failblog<br /><br />'
			}, 'template/item.html', 'entries/2008-06-24|11-00-09 Assembly Fail .||tag%3Agoogle.com%2C2005%3Areader%2Fitem%2Fdcb79527f18794d0||.html'),{})]
		assert ('add_item', (item,), {}) in self.mock_db.method_calls
	
	def test_read():
		item = Item(sample_item, 'feed-name')
