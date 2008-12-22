import unittest
import commands
import signal

from lib.mock import Mock
import app_globals
import output
from misc import *
import test_helper

import proctl

class GetPidTest(unittest.TestCase):
	def setUp(self):
		self.filename = "%s/sync.pid" % (app_globals.OPTIONS['output_path'],)
		self._backup_getpid = proctl.get_running_pid
	
	def tearDown(self):
		proctl.get_running_pid = self._backup_getpid

	def _mock_command(self, response):
		commands.getstatusoutput = Mock()
		commands.getstatusoutput.return_value = response
		
	def mock_pid_file(self, file_pid = '1234', command_response = (0,'1234')):
		write_file(self.filename, file_pid)
		self._mock_command(command_response)

	def mock_pid_process(self, aggressive=False, pid=1234, file_pid = None, command_response = (0,'')):
		app_globals.OPTIONS['aggressive'] = aggressive
		proctl.get_running_pid = Mock()
		proctl.get_running_pid.return_value = pid

		if file_pid is None:
			file_pid = str(pid)
		
		write_file(self.filename, file_pid)
		self._mock_command(command_response)
		os.kill = Mock()

	def fail(self):
		raise RuntimeError
		
	def test_get_pid_should_raise_IOError_when_file_doesnt_exist(self):
		self.mock_pid_file()
		try:
			os.remove(self.filename)
		except: pass
		self.assertRaises(IOError, proctl.get_running_pid)

	def test_get_pid_should_raise_ValueError_when_file_is_not_an_integer(self):
		self.mock_pid_file(file_pid = '')
		self.assertRaises(ValueError, proctl.get_running_pid)

	def test_get_pid_when_file_is_an_integer_with_whitespace(self):
		self.mock_pid_file(file_pid = ' 1234 \n', command_response=(0,'1234'))
		self.assertEqual(1234, proctl.get_running_pid())

	def test_get_pid_when_pid_is_valid_and_running(self):
		self.mock_pid_file(file_pid='1234\n', command_response=(0,'1234'))
		self.assertEqual(1234, proctl.get_running_pid())
		self.assertEqual(commands.getstatusoutput.call_args, (("ps ux | grep -v grep | grep 'python.*GRiS' | awk '{print $2}'",),{}))

	def test_get_pid_should_return_none_when_pid_is_not_gris(self):
		self.mock_pid_file(file_pid='1234', command_response=(0,'3456'))
		self.assertEqual(None, proctl.get_running_pid())

	def test_get_pid_should_raise_when_running_pids_cannot_be_parsed(self):
		self.mock_pid_file(file_pid='1234', command_response=(0,'1234\nxyz'))
		self.assertRaises(RuntimeError, proctl.get_running_pid)

	def test_get_pid_should_raise_when_get_ps_command_fails(self):
		self.mock_pid_file(file_pid='1234', command_response=(1,'3456'))
		self.assertRaises(RuntimeError, proctl.get_running_pid)

	def test_get_pid_should_return_none_when_pid_is_self(self):
		self.mock_pid_file(file_pid=str(os.getpid()))
		self.assertEqual(None, proctl.get_running_pid())

class ReportProcessTest(GetPidTest):
	def setUp(self):
		super(self.__class__, self).setUp()
		print dir(output)
		app_globals.OPTIONS['verbosity'] = output.lvl_quiet
		self._stdout = sys.stdout
		sys.stdout = Mock()
	
	def tearDown(self):
		sys.stdout = self._stdout
		super(self.__class__, self).tearDown()

	def test_should_report_pid_if_there_is_a_running_process(self):
		self.mock_pid_process(pid=1234)
		proctl.report_pid()
		self.assertEqual(sys.stdout.write.call_args_list, [(('1234',), {}), (('\n',), {})])
		
	def test_should_print__none__if_there_is_no_pid_running(self):
		self.mock_pid_process(pid=None)
		proctl.report_pid()
		self.assertEqual(sys.stdout.write.call_args_list, [(('None',), {}), (('\n',), {})])
		
	def test_should_print__none__if_there_is_an_error(self):
		proctl.get_running_pid = self.fail
		proctl.report_pid()
		self.assertEqual(sys.stdout.write.call_args_list, [(('None',), {}), (('\n',), {})])

class SingularProcessTest(GetPidTest):
	
	# aggressive ensure_singleton_process
	def test_aggressive_singular_process_should_continue_when_kill_works(self):
		self.mock_pid_process(aggressive = True, pid=1234, file_pid = '1234')
		
		proctl.ensure_singleton_process()
		self.assertEqual(os.kill.call_args_list, [((1234, signal.SIGKILL),{})])
		self.assertEqual(read_file(self.filename), str(os.getpid()))
	
	def test_aggressive_singular_process_should_exit_when_kill_fails(self):
		self.mock_pid_process(aggressive = True, pid=1234, command_response=(0,'567\n1234\n8910'))
		def raise_(error_cls, msg):
			raise OSError, msg
		os.kill = Mock(side_effect = lambda: raise_(OSError, '[Errno 3] No such process'))
		
		self.assertRaises(SystemExit, proctl.ensure_singleton_process)
		self.assertEqual(os.kill.call_args_list, [((1234, signal.SIGKILL),{})])
		self.assertEqual(read_file(self.filename), '1234') # contents should be unchanged
		
	def test_aggressive_singular_process_should_write_file_when_running_pids_raises(self):
		self.mock_pid_process(aggressive = True)
		proctl.get_running_pid = self.fail
		proctl.ensure_singleton_process()
		self.assertFalse(os.kill.called)
		self.assertEqual(read_file(self.filename), str(os.getpid()))
		
	def test_aggressive_singular_process_should_write_pid_file_when_running_pids_returns_none(self):
		self.mock_pid_process(aggressive = True, pid=None)
		proctl.ensure_singleton_process()
		self.assertFalse(os.kill.called)
		self.assertEqual(read_file(self.filename), str(os.getpid()))

	# submissive ensure_singleton_process
	def test_submissive_singular_process_when_pid_is_valid(self):
		self.mock_pid_process(aggressive = False, pid=1234)

		self.assertRaises(SystemExit, proctl.ensure_singleton_process)
		
		self.assertFalse(os.kill.called)
		self.assertEqual(read_file(self.filename), '1234') # file should be unchanged

	def test_submissive_should_not_write_pid_file_when_running_pid_raises(self):
		self.mock_pid_process(aggressive = False)
		self.mock_pid_file(file_pid='1234')
		proctl.get_running_pid = self.fail
		self.assertRaises(SystemExit, proctl.ensure_singleton_process)
		self.assertEqual(read_file(self.filename), '1234')
		