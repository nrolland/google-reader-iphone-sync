import app_globals

import os, re, sys

def danger(desc):
	if not app_globals.OPTIONS['cautious']: return
	response = raw_input("%s. Continue? " % desc)
	if not re.match('[yY]|(^$)', response):
		print "Aborted."
		sys.exit(2)
		raise Exception("We should never get here!")
	debug("Continuing...")

def debug(s):
	if not app_globals.OPTIONS['verbose']: return
	print ' > ' + str(s)


def line():
	print '-' * 50

def try_remove(elem, lst):
	try:
		lst.remove(elem)
	except:
		pass


"""
Execute a shell command. if it returns a non-zero (error) status, raise an exception
"""
def try_shell(cmd):
	debug("running command: " + cmd)
	if os.system(cmd) != 0:
		raise Exception("shell command failed:\n%s" % cmd)
