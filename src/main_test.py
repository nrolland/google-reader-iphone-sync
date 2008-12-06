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
	
	def mock_singular_process(self, aggressive=False, file_pid = '1234', command_response = (0,'1234')):
		app_globals.OPTIONS['aggressive'] = aggressive
		filename = "%s/sync.pid" % (app_globals.OPTIONS['output_path'],)
		write_file(filename, file_pid)
		commands.getstatusoutput = Mock()
		commands.getstatusoutput.return_value = command_response
		os.kill = Mock()
		return filename
	
	def test_singular_process_when_file_doesnt_exit(self):
		filename = self.mock_singular_process(aggressive = False)
		try:
			os.remove(filename)
		except: pass
		main.ensure_singleton_process()
		
		# it should succeed, and write our pid to the file
		self.assertEqual(read_file(filename), str(os.getpid()))

	def test_singular_process_when_file_is_not_an_integer(self):
		filename = self.mock_singular_process(aggressive = False, file_pid = '')
		
		main.ensure_singleton_process()
		self.assertFalse(os.kill.called)

		# it should succeed, and write our pid to the file
		self.assertEqual(read_file(filename), str(os.getpid()))

	def test_submissive_singular_process_when_file_is_valid(self):
		filename = self.mock_singular_process(aggressive = False, file_pid=' 1234\n', command_response=(0,'1234'))
		
		self.assertRaises(SystemExit, main.ensure_singleton_process)

		self.assertEqual(commands.getstatusoutput.call_args, (("ps ux | grep -v grep | grep 'python.*GRiS' | awk '{print $2}'",),{}))
		self.assertFalse(os.kill.called)
		self.assertEqual(read_file(filename), ' 1234\n') # file should be unchanged

	def test_aggressive_singular_process_should_continue_when_kill_works(self):
		filename = self.mock_singular_process(aggressive = True, file_pid='1234', command_response=(0,'567\n1234\n8910'))
		
		main.ensure_singleton_process()
		self.assertEqual(os.kill.call_args_list, [((1234, signal.SIGKILL),{})])
		self.assertEqual(read_file(filename), str(os.getpid()))
	
	def test_aggressive_singular_process_should_exit_when_kill_fails(self):
		filename = self.mock_singular_process(aggressive = True, file_pid='1234', command_response=(0,'567\n1234\n8910'))
		def raise_(error_cls, msg):
			raise OSError, msg
		os.kill = Mock(side_effect = lambda: raise_(OSError, '[Errno 3] No such process'))
		
		self.assertRaises(SystemExit, main.ensure_singleton_process)
		self.assertEqual(os.kill.call_args_list, [((1234, signal.SIGKILL),{})])
		self.assertEqual(read_file(filename), '1234') # contents should be unchanged

	def test_aggressive_singular_process_should_do_nothing_when_pid_is_not_gris(self):
		filename = self.mock_singular_process(aggressive = True, file_pid='1234', command_response=(0,'3456'))
		main.ensure_singleton_process()
		self.assertFalse(os.kill.called)
		self.assertEqual(commands.getstatusoutput.call_args, (("ps ux | grep -v grep | grep 'python.*GRiS' | awk '{print $2}'",),{}))
		self.assertEqual(read_file(filename), str(os.getpid()))

	def test_aggressive_singular_process_should_abort_when_running_pids_cannot_be_parsed(self):
		filename = self.mock_singular_process(aggressive = True, file_pid='1234', command_response=(0,'1234\nxyz'))
		self.assertRaises(SystemExit, main.ensure_singleton_process)
		self.assertFalse(os.kill.called)
		self.assertEqual(read_file(filename), '1234')
		
	def test_aggressive_singular_process_should_abort_when_running_pids_cannot_be_parsed(self):
		filename = self.mock_singular_process(aggressive = True, file_pid='1234', command_response=(0,'1234\nxyz'))
		self.assertRaises(SystemExit, main.ensure_singleton_process)
		self.assertFalse(os.kill.called)
		self.assertEqual(read_file(filename), '1234')

	def test_aggressive_singular_process_should_abort_when_get_pid_command_fails(self):
		filename = self.mock_singular_process(aggressive = True, file_pid='1234', command_response=(1,'3456'))
		self.assertRaises(SystemExit, main.ensure_singleton_process)
		self.assertFalse(os.kill.called)
		self.assertEqual(read_file(filename), '1234')

	def test_aggressive_singular_process_should_do_nothing_when_pid_is_self(self):
		filename = self.mock_singular_process(aggressive = True, file_pid=str(os.getpid()))

		os.kill = Mock()
		main.ensure_singleton_process()
		self.assertFalse(commands.getstatusoutput.called)
		self.assertFalse(os.kill.called)
