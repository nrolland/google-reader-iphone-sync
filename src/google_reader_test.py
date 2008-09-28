# the tested module
from lib import GoogleReader

import main

# test helpers
import test_helper
from lib.mock import Mock
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest
import config
import app_globals
from reader import Reader

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
		pass
		# rm_rf('/tmp/gris-test')
	
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
