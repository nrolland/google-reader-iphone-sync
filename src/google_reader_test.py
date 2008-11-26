import main

# test helpers
import test_helper
from test_helper import *
import unittest
import config
import app_globals
from reader import Reader, CONST

# These are (relatively) long running tests, which require an active google reader account and network connection.
# They should be separated from the main tests for this reason, but currenly they aren't.
class GoogleReaderLiveTest(unittest.TestCase):

	def setUp(self):
		config.load('../config.yml')
		config.bootstrap(['-vv'])
		# make sure we're not mocking out google reader
		app_globals.OPTIONS['test'] = False
		config.parse_options(['--output-path=/tmp/gris-test', '--num-items=1'])
		config.check()
		self.reader = app_globals.READER = Reader()
		
	def tearDown(self):
		rm_rf('/tmp/gris-test')
	
	# these don't explicitly check anything, their acceptance is by virtue of not throwing any exceptions
	def test_standard_tag(self):
		main.download_feed(self.reader.get_tag_feed('i-am-a-tag-without-spaces'),'feed')
		
	def test_tag_with_spaces(self):
		main.download_feed(self.reader.get_tag_feed('i am a tag with lots of spaces'),'feed')
	
	@test_helper.pending
	def test_tag_with_all_manner_of_crazy_characters_except_spaces(self):
		main.download_feed(main.get_feed_from_tag('abc\'"~!@#$%^&*()-+_=,.<>?/\\'))

	@test_helper.pending	
	def test_tag_with_non_ascii_characters(self):
		main.download_feed(main.get_feed_from_tag(u'caf\xe9'))

	# helper for the below test
	def get_tag_items(self, tag, is_read = None):
		kwargs = {}
		if is_read is not None:
			kwargs['exclude_target'] = CONST.ATOM_STATE_UNREAD if is_read else CONST.ATOM_STATE_READ
		feed = CONST.ATOM_PREFIXE_LABEL + tag
		return list(self.reader.get_feed(None, feed, count=1, **kwargs).get_entries())
			
	# For this test to pass, you need to have exactly one item tagged with "gris-test" in your google reader account.
	# I'm afraid you're on your own setting this up - doing it in code is just too cumbersome.
	@pending("behaviour is not reliable")
	def test_changing_item_status(self):
		pass
		# entries = self.get_tag_items('gris-test')
		# assert len(entries) == 1
		# entry = entries[0]
		# entry_id = entry['google_id']
		# 
		# # make sure it's unread
		# self.reader.set_unread(entry_id)
		# entries = self.get_tag_items('gris-test', is_read = False)
		# assert len(entries) == 1
		# entry = entries[0]
		# assert entry_id == entry['google_id']
		# 
		# # now mark it as read
		# self.reader.set_read(entry_id)
		# entries = self.get_tag_items('gris-test', is_read = True)
		# entry = entries[0]
		# assert len(entries) == 1
		# assert entry_id == entry['google_id']
		# entry = entries[0]
