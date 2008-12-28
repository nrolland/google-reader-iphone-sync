import thread, time, threading
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

class ThreadAction(threading.Thread):
	def __init__(self, func, on_error = None, on_success = None, name=None, *args, **kwargs):
		super(self.__class__, self).__init__(group=None, target=None, name=name, args=(), kwargs={})
		self.args = args
		self.kwargs = kwargs
		self.func = func
		self.on_error = on_error
		self.on_success = on_success
		self.name = name
		self._killed = False
		self._lock = thread.allocate_lock()

	def kill(self):
		self._killed = True
	
	def run(self):
		if self._killed: return
		if self.name is not None:
			threading.currentThread().setName(self.name)
		
		try:
			self.func(*self.args, **self.kwargs)
		except StandardError, e:
			if self._killed: return
			if self.on_error is not None:
				self.on_error(e)
			else:
				raise
			
		if self._killed: return
		if self.on_success() is not None:
			self.on_success()
	

class ThreadPool:
	_max_count = 10
	_threads = []
	_global_count = 0
	_action_buffer = []
	
	def __init__(self):
		self._lock = thread.allocate_lock()

	def _get_count(self):
		return len(self._threads)
	_count = property(_get_count)
	
	def _sleep(self, seconds = 1):
		self._lock.release()
		time.sleep(seconds)
		self._lock.acquire()
	
	@locking
	def spawn(self, function, on_success = None, on_error = None, *args, **kwargs):
		while self._count >= self._max_count:
			self._sleep()

		debug("there are currently %s threads running" % self._count)
		self._global_count += 1
		thread_id = "thread %s" % (self._global_count,)

		action = ThreadAction(
			function,
			on_error = self._thread_error,
			name = thread_id,
			*args, **kwargs)
		action.on_success = lambda: self._thread_finished(action, on_success)
		self._threads.append(action)
		action.start()
	
	@locking
	def _thread_error(self, e, trace):
		self._count -= 1
		log_error("thread raised an exception and ended", e)
		
	@locking
	def _thread_finished(self, thread, next_action):
		self._action_buffer.append(next_action)
		self._count -= 1
		debug("thread finished - there remain %s threads" % (self._count,))
	
	@locking
	def collect(self):
		self._collect()
	
	@locking
	def collect_all(self):
		silence_threshold = 20
		debug("waiting for %s threads to finish" % self._count)
		sleeps = 0
		last_count = self._count
		while self._count > 0:
			self._sleep(1)
			
			if last_count == self._count:
				sleeps += 1
				if sleeps > silence_threshold:
					debug("no threads have completed in the past %s seconds. killing them" % (silence_threshold,))
					for thread_ in self._threads:
						thread_.kill()
					debug("%s threads forcibly killed - onwards!" % (last_count,))
					self._threads = []
					break
			else:
				sleeps = 0
			last_count = self._count
			
		self._collect()

	# non-locking - for internal use only
	def _collect(self):
		for next_action in self._action_buffer:
			if next_action is not None:
				debug("calling action: %s" % (next_action,))
				next_action()
		self._action_buffer = []
