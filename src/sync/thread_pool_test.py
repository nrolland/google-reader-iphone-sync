import time

# the tested module
from thread_pool import *
import thread_pool

# test helpers
import test_helper
import lib
from mocktest import *
from lib.mock import Mock
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest

class ThreadPoolTest(TestCase):

	def setUp(self):
		self.pool = ThreadPool()

	def tearDown(self):
		pass
		
	def assert_uses_a_lock_for(self, func):
		lock = mock_on(self.pool)._lock
		def check_locked():
			self.assertTrue(lock.child('acquire').called)
		lock.child('release').action = check_locked
		func()
		self.assertTrue(lock.child('release').called)
		self.assertTrue(lock.child('acquire').called)
	
	def sleep(self, secs = 1):
		time.sleep(secs)
	
	def raise_(self, ex):
		raise ex
		
	def action(self, f = lambda: 1):
		self.action_happened = False
		def do_action():
			print "action started"
			try:
				f()
			finally:
				self.action_happened = True
		return do_action
		
	
	def wait_for_action(self):
		while not self.action_happened:
			print "waiting..."
			time.sleep(0.1)
		
	# -- actual tests --

	@ignore
	def test_should_use_lock_for_spawn(self):
		self.assert_uses_a_lock_for(lambda: self.pool.spawn(self.sleep))

	@ignore
	def test_should_use_lock_for_collect(self):
		self.assert_uses_a_lock_for(lambda: self.pool.collect())
		
	@ignore
	def test_should_use_lock_for_collect_all(self):
		self.assert_uses_a_lock_for(lambda: self.pool.collect_all())
		
	def test_sucessful_callback_on_next_collect(self):
		success = mock_wrapper()
		self.pool.spawn(self.action(), on_success = success.mock)
		self.wait_for_action()
		self.assertFalse(success.called)
		self.pool.collect()
		self.assertTrue(success.called.once())

	def test_standard_error_callback(self):
		success = mock_wrapper().named('success')
		fail = mock_wrapper().named('fail')
		
		self.pool.spawn(self.action(lambda: self.raise_(ValueError)), on_success = success.mock, on_error = fail.mock)
		self.wait_for_action()
		self.pool.collect()
		
		self.assertTrue(fail.called.once())
		self.assertTrue(success.called.no_times())

	def test_should_log_standard_error_when_no_error_callback_given(self):
		success = mock_wrapper().named('success')
		self.error_logged = False
		def errd(e):
			self.error_logged = True

		mock_on(thread_pool).log_error.with_action(lambda desc, e: errd(e)).is_expected.once()
		
		self.pool.spawn(self.action(lambda: self.raise_(ValueError)), on_success = success.mock)
		self.wait_for_action()
		self.pool.collect()
		
		self.assertTrue(success.called.no_times())
	
	def test_should_not_catch_nonstandard_errors(self):
		success = mock_wrapper().named('success')
		fail = mock_wrapper().named('fail')
		
		class Dummy(Exception):
			pass

		self.pool.spawn(self.action(lambda: self.raise_(Dummy)), on_success = success.mock, on_error = fail.mock)
		self.wait_for_action()
		self.pool.collect()
		
		self.assertTrue(fail.called.no_times())
		self.assertTrue(success.called.no_times())
	
	@ignore
	def test_kill_of_old_threads_when_max_threads_reached(self):
		pass
	
	@ignore
	def test_ping_prolongs_kill(self):
		pass
	
	@ignore
	def test_collect_all_waits_for_all_threads(self):
		pass
	
	
	
	