# the tested module
from reader import *
from output import *
import os

# test helpers
import test_helper
from lib.mock import Mock
import pickle
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest
import config

def mock_tag_list(reader, tag_list):
	reader.gr.get_tag_list = Mock()
	reader.gr.get_tag_list.return_value = {'tags':[{'id': tag_value} for tag_value in tag_list]}

class ReaderTest(unittest.TestCase):
	def setUp(self):
		self.output_folder = test_helper.init_output_folder()
		assert self.output_folder.startswith('/tmp')
		self.reader = Reader()
	
	def tearDown(self):
		assert self.output_folder.startswith('/tmp')
#		rm_rf(self.output_folder)
		
	def test_saving_unicode_in_tags(self):
		mock_tag_list(self.reader, [u'com.google/label/caf\xe9'])
		self.reader.save_tag_list()
		self.assertEqual(read_file_lines(os.path.join(self.output_folder, 'tag_list')), [u'caf\xe9\n'])
	
	def test_comparing_unicode_tags(self):
		config.parse_options(['--tag=caf\xc3\xa9']) # cafe in utf-8
		mock_tag_list(self.reader, [u'com.google/label/caf\xe9'])
		self.assertEqual(app_globals.OPTIONS['tag_list'], [u'caf\xe9'])
		self.reader.validate_tag_list()

	def test_saving_special_characters_in_tags(self):
		tag_name = 'com.google/label/and\\or\'"!@#$%^&*()_+'
		mock_tag_list(self.reader, [tag_name])
		self.reader.save_tag_list()
		print "tag list is: %s" % (read_file_lines(os.path.join(self.output_folder, 'tag_list')),)
		self.assertEqual(read_file_lines(os.path.join(self.output_folder, 'tag_list')), ['and\\or\'"!@#$%^&*()_+\n'])
		
	def test_should_ignore_tags_without__label_(self):
		"""should ignore tags without '/label/'"""
		tag_name = 'not a label'
		mock_tag_list(self.reader, [tag_name])
		self.assertEqual(self.reader.tag_list, [])
		
	def test_should_pass_through_get_feed(self):
		self.reader.get_feed(1, 2, 3, x=5)
		self.assertTrue( ('get_feed', (1,2,3), {'x':5}) in self.reader.gr.method_calls )
	
	def test_get_tag_feed_should_get_all_items(self):
		self.reader.get_tag_feed()
		self.assertTrue(
			('get_feed',
				(None, None),
				{'count': app_globals.OPTIONS['num_items'], 'order':CONST.ORDER_REVERSE, 'exclude_target': CONST.ATOM_STATE_READ})
			in self.reader.gr.method_calls )
	
	def test_get_tag_feed_should_get_single_tag(self):
		self.reader.get_tag_feed('blah')
		print self.reader.gr.method_calls
		self.assertTrue(
			('get_feed',
				(None, CONST.ATOM_PREFIXE_LABEL + 'blah'),
				{'count': app_globals.OPTIONS['num_items'], 'order':CONST.ORDER_REVERSE, 'exclude_target': CONST.ATOM_STATE_READ})
			in self.reader.gr.method_calls )

	def test_get_tag_feed_should_support_newest_first(self):
		self.reader.get_tag_feed(oldest_first = False)
		self.assertTrue(
			('get_feed',
				(None, None),
				{'count': app_globals.OPTIONS['num_items'], 'exclude_target': CONST.ATOM_STATE_READ})
			in self.reader.gr.method_calls )