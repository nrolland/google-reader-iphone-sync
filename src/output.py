import app_globals
import sys

lvl_default = 2

lvl_debug = 4
lvl_verbose = 3
lvl_info = 2
lvl_quiet = 1
lvl_silent = 0

def puts_array(s, level=lvl_quiet):
	if app_globals.OPTIONS['verbosity'] < level: return
	print " ".join(s)
	if app_globals.OPTIONS['flush_output']:
		sys.stdout.flush()

def puts(*s):
	puts_array(s, level=lvl_quiet)

def info(*s):
	puts_array(s, level=lvl_info)

def debug(*s):
	puts_array([' > '] + list(s), level=lvl_verbose)

def debug_verbose(*s):
	puts_array([' >>> '] + list(s), level=lvl_debug)

# level is actually an output function, i.e. one of the above
def line(level = info):
	level('-' * 50)

def in_debug_mode():
	return app_globals.OPTIONS['verbosity'] >= lvl_debug