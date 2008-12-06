import thread, time
from output import *

# threaded decorator
# relies on the decorated method's instance having an initialised _lock variable
def locking(process):
	def fn(self, *args, **kwargs):
		self._lock.acquire()
		ret = process(self, *args, **kwargs)
		self._lock.release()
		return ret
	return fn

class ThreadPool:
	_max_count = 10
	_count = 0
	_action_buffer = []
	
	def __init__(self):
		self._lock = thread.allocate_lock()
	
	def _sleep(self, seconds = 1):
		self._lock.release()
		time.sleep(seconds)
		self._lock.acquire()
	
	@locking
	def spawn(self, function, on_success = None, on_error = None, *args, **kwargs):
		while self._count >= self._max_count:
			self._sleep()
		self._count += 1
		debug("there are currently %s threads running" % self._count)
		def function_with_callback(fn, args, **kwargs):
			try:
				ret = fn(*args, **kwargs)
				self._thread_finished(on_success)
			except StandardError, e:
				self._thread_error(e)
				if on_error is not None:
					on_error(e)
				else:
					raise
		thread.start_new_thread(function_with_callback, (function, args), **kwargs)
	
	@locking
	def _thread_error(self, e):
		self._count -= 1
		debug("thread raised an exception and ended")
		log_error(e)
		
	@locking
	def _thread_finished(self, next_action):
		self._action_buffer.append(next_action)
		self._count -= 1
		debug("thread finished - there remain %s threads" % (self._count,))
	
	@locking
	def collect(self):
		self._collect()
	
	@locking
	def collect_all(self):
		debug("waiting for %s threads to finish" % self._count)
		while self._count > 0:
			self._sleep()
		self._collect()

	# non-locking - for internal use only
	def _collect(self):
		for next_action in self._action_buffer:
			if next_action is not None:
				debug("calling action: %s" % (next_action,))
				next_action()
		self._action_buffer = []