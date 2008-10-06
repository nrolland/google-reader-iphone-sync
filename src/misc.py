import app_globals
from output import *

import os, re, sys, shutil, pickle

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

def try_remove(elem, lst):
	"""
	Try to remove an element from a list. If it fails, nobody has to know...
	"""
	try:
		lst.remove(elem)
	except ValueError:
		pass
	
def try_lookup(obj, key):
	try:
		return obj[key]
	except KeyError:
		return None

def matches_any_regex(s, regexes, flags = 0):
	"""
		>>> matches_any_regex('abcd',['.*f','agg'])
		False
		>>> matches_any_regex('abCD',['bce?d','qwert'], flags=re.IGNORECASE)
		True
	"""
	regexes = [re.compile(regex, flags) if isinstance(regex, str) else regex for regex in regexes]
	return any([regex.search(s) for regex in regexes])


def try_shell(cmd):
	"""
	Execute a shell command. if it returns a non-zero (error) status, raise an exception
	
		>>> try_shell('[ 0 = 0 ]')
		>>> try_shell('[ 0 = 1 ]')
		Traceback (most recent call last):
		RuntimeError: shell command failed:
		[ 0 = 1 ]
	"""
	debug("running command: " + cmd)
	if os.system(cmd) != 0:
		raise RuntimeError("shell command failed:\n%s" % cmd)

def url_dirname(url):
	"""
	returns everything before and including the last slash in a URL
	"""
	return '/'.join(url.split('/')[:-1]) + '/'

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
	"""
		>>> os.system('mkdir /tmp/blah && touch /tmp/blah/foo')
		0
		>>> os.path.isdir('/tmp/blah')
		True
		>>> rm_rf('/tmp/blah')
		>>> os.path.isdir('/tmp/blah')
		False
		>>> rm_rf('/tmp/blah')
	"""
	danger("About to remove ENTIRE path below:\n%s" % path)
	if os.path.exists(path):
		shutil.rmtree(path, ignore_errors = True)

def slashify_dbl_quotes(s):
	r"""
		>>> print slashify_dbl_quotes('\\ "')
		\\ \"
	"""
	return s.replace('\\','\\\\').replace('"','\\"')

def slashify_single_quotes(s):
	r"""
	>>> print slashify_single_quotes("\\ '")
	\\ \'
	"""
	return s.replace('\\','\\\\').replace("'","\\'")

def write_file(filename, content):
	f = file(filename, 'w')
	f.write(utf8(content))
	f.close()

def write_file_lines(filename, content):
	f = file(filename, 'w')
	for line in content:
		f.write(utf8(line))
		if not line.endswith("\n"):
			f.write("\n")
	f.close()

def read_file_lines(filename):
	f = file(filename,'r')
	ret = [unicode(line, 'utf-8') for line in f.readlines()]
	f.close()
	return ret

def touch_file(name):
	ensure_dir_exists(os.path.dirname(name))
	write_file(name, '\n')
	
def save_pickle(obj, filename):
	"""
	Save pickled version of `obj` to the file named `filename`
	
		>>> save_pickle({'key':'value'}, '/tmp/test_pickle')
		>>> load_pickle('/tmp/test_pickle')
		{'key': 'value'}
	"""
	f = file(filename,'w')
	ret = pickle.dump(obj, f)
	f.close()

def load_pickle(filename):
	"""
	Load an object from a pickle file named `filename`

		>>> save_pickle({'key':'value'}, '/tmp/test_pickle')
		>>> load_pickle('/tmp/test_pickle')
		{'key': 'value'}
	"""
	f = file(filename,'r')
	obj = pickle.load(f)
	f.close()
	return obj


def first(l):
	"""
	get the first element in a list/tuple, or return the original element if it's not subscriptable
	>>> first([1,2])
	1
	>>> first("bob")
	'b'
	>>> first(23)
	23
	"""
	try:
		return l[0]
	except TypeError, e:
		return l
