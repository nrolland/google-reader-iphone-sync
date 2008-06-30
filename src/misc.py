import app_globals

import os, re, sys

def danger(desc):
	"""
	if cautious mode is enabled, pauses execution of the script until the user types "yes" (or presses return).
	Any other input will cause the program to terminate with error status 2
	"""
	if not app_globals.OPTIONS['cautious']: return
	response = raw_input("%s. Continue? " % desc)
	if not re.match('[yY]|(^$)', response):
		print "Aborted."
		sys.exit(2)
		raise Exception("We should never get here!")
	debug("Continuing...")

def debug(s):
	"""
	print out things when verbose mode is enabled
	"""
	if not app_globals.OPTIONS['verbose']: return
	print ' > ' + str(s)


def line():
	print '-' * 50

def try_remove(elem, lst):
	try:
		lst.remove(elem)
	except:
		pass

def try_shell(cmd):
	"""
	Execute a shell command. if it returns a non-zero (error) status, raise an exception
	"""
	debug("running command: " + cmd)
	if os.system(cmd) != 0:
		raise Exception("shell command failed:\n%s" % cmd)

def url_dirname(url):
	"""
	returns everything before and including the last slash in a URL
	"""
	return '/'.join(url.split('/')[:-1]) + '/'

import os
def ensure_dir_exists(path):
	"""
	takes a path, and ensures all drectories exist
	"""
	dirs = [x for x in os.path.split(path) if len(x) > 0]
	active_dirs = []
	for d in dirs:
		active_dirs.append(d)
		location = os.path.join(*active_dirs)
		if not os.path.exists(location):
			os.mkdir(location)

def rm_rf(path):
	danger("About to remove ENTIRE path below:\n%s" % path)
	if os.path.exists(path):
		os.system("rm -rf '%s'" % re.sub("'","\\\\'", path))

def slashify_dbl_quotes(s):
	return s.replace('\\','\\\\').replace('"','\\"')
