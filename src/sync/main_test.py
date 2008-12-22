# the tested module
import main
from item import Item
from output import *

# test helpers
import test_helper
import item_test
from lib.mock import Mock
import unittest
import os
import signal
import commands
from misc import read_file, write_file

class MainTest(unittest.TestCase):
	def setUp(self):
		self.output_folder = test_helper.init_output_folder()
		self.db = app_globals.DATABASE = Mock()
	
	def tearDown(self):
		pass

	def test_item_feeds_being_updated(self):
		"""Items that already exist in the database should be updated with their new feed / tag (if it has changed)"""
		i = item_test.sample_item.copy()
		item = Item(item_test.sample_item)
		
		self.db.is_read.return_value = False
		main.process_item(item)
		self.assertTrue(self.db.is_read.called)
		self.db.is_read.reset()
		
		self.db.is_read.return_value = True
		item.feed_id = 'feedb'
		main.process_item(item)
		self.assertTrue(self.db.is_read.called)
		self.assertTrue(('update_feed_for_item',(item,),{}) in self.db.method_calls)

	def test_setup_should_report_pid(self):
		main.proctl = Mock()
		app_globals.OPTIONS['report_pid'] = True
		self.assertRaises(SystemExit, lambda: main.setup([]))
		self.assertTrue(main.proctl.report_pid.called)

	def test_setup_should_ensure_singleton(self):
		main.proctl = Mock()
		app_globals.OPTIONS['report_pid'] = False
		main.setup(['--user=a','--password=b'])
		self.assertTrue(main.proctl.ensure_singleton_process.called)
		