import app_globals
import time, threading
import sys, os, time, traceback

lvl_default = 2

lvl_debug = 4
lvl_verbose = 3
lvl_info = 2
lvl_quiet = 1
lvl_silent = 0

logfile = None

def ascii(s): return s.encode('ascii','ignore') if isinstance(s, unicode) else str(s)
def utf8(s):  return s.encode('utf-8','ignore') if isinstance(s, unicode) else str(s)

def whereami_str():
	time_str = time.strftime('%H:%M:%S')
	thread_str = threading.currentThread().getName()
	return "[%s %s] " % (thread_str, time_str)

def puts_array(s, level=lvl_quiet):
	global logfile
	output_str = " ".join(map(ascii, s))
	if level >= lvl_verbose:
		output_str = whereami_str() + output_str
	if logfile is not None and (level < lvl_debug):
		print >> logfile, output_str
	if app_globals.OPTIONS.get('verbosity', lvl_debug) < level: return
	print output_str
	if app_globals.OPTIONS.get('flush_output', lvl_debug):
		sys.stdout.flush()

def puts(*s):
	puts_array(s, level=lvl_quiet)

def info(*s):
	puts_array(s, level=lvl_info)

def debug(*s):
	puts_array([' > '] + list(s), level=lvl_verbose)

def debug_verbose(*s):
	puts_array([' >>> '] + list(s), level=lvl_debug)
	
def log_error(description, exception):
	debug("-" * 50)
	debug("EXCEPTION LOG:", description)
	traceback.print_exc(file=logfile)
	debug("-" * 50, "\n\n")
	
def status(*s):
	"""output a machine-readable status message"""
	if app_globals.OPTIONS['show_status']:
		puts("STAT:%s" % ":".join([utf8(x) for x in s]))
	

subtask_progress = 0
def new_subtask(length):
	global subtask_progress
	subtask_progress = 0
	status("SUBTASK_TOTAL", length)
	status("SUBTASK_PROGRESS", 0)
	
def increment_subtask():
	global subtask_progress
	subtask_progress += 1
	status("SUBTASK_PROGRESS", subtask_progress)

# level is actually an output function, i.e. one of the above
def line(level = info):
	level('-' * 50)

def log_end():
	global logfile
	if logfile is not None:
		logfile.close()

def log_start():
	global logfile
	logfile = open(os.path.join(app_globals.OPTIONS['output_path'], 'GRiS.log'), 'w')
	debug("Log started at %s." % (time.ctime(),))
	try:
		vfile = file(os.path.join(app_globals.OPTIONS['output_path'], 'VERSION'), 'r')
		version = vfile.readline()
		vfile.close()
		debug("app version: %s" % (version,))
	except IOError,e:
		log_error("Failed to find app version", e)

def in_debug_mode():
	return app_globals.OPTIONS['verbosity'] >= lvl_debug

def backtrace():
	import traceback, sys
	print ''.join(traceback.format_stack(sys._getframe()))