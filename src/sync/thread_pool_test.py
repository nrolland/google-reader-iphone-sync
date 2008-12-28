# the tested module
from thread_pool import *

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
			self.assertTrue(lock.child('acquire').called.once())
		lock.child('release').action = check_locked
		lock.expects('release').once()
		lock.expects('acquire').once()
		func()
	
	def test_should_use_lock_for_spawn(self):
		self.assert_uses_a_lock_for(lambda: self.pool.spawn(lambda: 1 + 1))

	def test_should_use_lock_for_collect(self):
		self.assert_uses_a_lock_for(lambda: self.pool.collect())
		
	def test_should_use_lock_for_collect_all(self):
		self.assert_uses_a_lock_for(lambda: self.pool.collect_all())
		
	def test_sucessful_callback(self):
		success = mock_wrapper()
		success.is_expected.once()
		self.pool.spawn(lambda: 1 + 1, on_success = success.mock)
	
	@ignore
	def test_error_callback(self):
		pass
	
	@ignore
	def test_maximum_pool(self):
		pass
	
	@ignore
	def test_kill_of_old_threads_when_max_threads_reached(self):
		pass
	
	@ignore
	def test_ping_prolongs_kill(self):
		pass
	
	@ignore
	def test_callback_is_not_called_before_collect(self):
		pass
	
	@ignore
	def test_collect_all_waits_for_all_threads(self):
		pass
	
	
	
	