# process control
import commands
import signal

import app_globals
from misc import *

def get_pid_filename():
	return "%s/sync.pid" % (app_globals.OPTIONS['output_path'],)

def write_pid_file(filename):
	write_file(filename, str(os.getpid()))

def report_pid():
	none = 'None'
	try:
		pid = get_running_pid()
		if pid is None:
			print none
		else:
			print pid
	except Exception, e:
		log_error(e, "Error getting running pid")
		print none

def get_running_pid():
	"""
	@throws: IOError, ValueError, RuntimeError
	"""
	filename =  get_pid_filename()
	try:
		pid = int(read_file(filename).strip())
	except (IOError, ValueError), e:
		e.message = ("Couldn't load PID file at %s: %s" % (filename, e.message))
		raise
	
	if pid == os.getpid():
		# it's me! it must have been stale, and happened to be reused. we don't want to kill it
		return None
	
	status, output = commands.getstatusoutput("ps ux | grep -v grep | grep 'python.*GRiS' | awk '{print $2}'") # classy!
	if output.endswith("Operation not permitted"):
		puts(commands.getstatusoutput("uname -a"))
		# this is hopefully just on the simulator
		puts("Error fetching running pids: %s" % (output,))
		puts(" - This is known to happen on the iphone simulator.")
		puts(" - if you see it on a real device, please file a bug report")
		status, output = (0, '') # lets just pretend it worked, and everything is fine
		#TODO: clean
		raise RuntimeError("Error fetching running pids: %s" % (output,))
	if status != 0:
		raise RuntimeError("could not execute pid-checking command. got status of %s, output:\n%s" % (status, output))
	
	running_pids = output.split()
	try:
		running_pids = [int(x) for x in running_pids if len(x) > 0]
	except ValueError, e:
		raise RuntimeError("one or more pids could not be converted to an integer: %r" % (running_pids,))
	
	if pid in running_pids:
		return pid
	return None

def ensure_singleton_process():
	"""
	ensure only one sync process is ever running.
	if --aggressive is given as a flag, this process will kill the existing one
	otherwise, it will exit when there is already a process running
	"""
	aggressive = app_globals.OPTIONS['aggressive']
	pid = None
	try:
		pid = get_running_pid()
	except RuntimeError, e:
		log_error(e, "Error fetching current PID")
		if not aggressive:
			sys.exit(2)
	
	if pid is not None:
		if not aggressive:
			puts("There is already a sync process running, pid=%s" % (pid,))
			sys.exit(2)
		else:
			try:
				debug("killing PID %s " %(pid,))
				os.kill(pid, signal.SIGKILL)
			except OSError, e:
				msg = "couldn't kill pid %s - %s" % (pid,e)
				puts(msg)
				sys.exit(2)

	# if we haven't exited by now, we're the new running pid!
	filename =  get_pid_filename()
	write_pid_file(filename)
