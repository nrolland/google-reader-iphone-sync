"""
Exports:
CONFIG
OPTIONS
parse_options()
load_config()
"""
from getopt import getopt
import yaml, sys

# local imports
from misc import *
import app_globals


def parse_options(argv = None):
	"""
Usage:
  -n, --num-items=[val]  set the number of items to download (per feed)
  -v, --verbose          verbose output
  -c, --cautious         cautious mode - prompt before performing destructive actions
  -d, --no-download      don't download new items, just tell google reader about read items
  -N, --nav-only         just update navigational links in existing downloaded items
  -t, --test             run in test mode. Don't notify google reader of anything, and clobber "test_entries" for output
"""
	if argv is None:
		argv = sys.argv[1:]
		
	(opts, argv) = getopt(argv, "n:vCdthN", ['num-items=','verbose','cautious','no-download','test', 'help', 'nav-only'])
	for (key,val) in opts:
		if key == '-v' or key == '--verbose':
			app_globals.OPTIONS['verbose'] = True
			debug("Verbose mode enabled...")
		elif key == '-C' or key == '--cautious':
			app_globals.OPTIONS['cautious'] = True
			app_globals.OPTIONS['verbose']  = True
			print "Cautious mode enabled..."
		elif key == '-n' or key == '--num-items':
			app_globals.OPTIONS['num_items'] = int(val)
			print "Number of items set to %s" % app_globals.OPTIONS['num_items']
		elif key == '-d' or key == '--no-download':
			app_globals.OPTIONS['no_download'] = True
			print "Downloading turned off.."
		elif key == '-t' or key == '--test':
			app_globals.OPTIONS['test'] = True
			print "Test mode enabled - using %s" % app_globals.CONFIG['test_output_dir']
		elif key == '-N' or key == '--nav-only':
			app_globals.OPTIONS['nav_only'] = True
			print "Just updating item navigation links..."
		elif key == '-h' or key == '--help':
			print parse_options.__doc__
			sys.exit(1)

	if len(argv) > 0:
		app_globals.OPTIONS['num_items'] = argv[0]
		print "Number of items set to %s" % app_globals.OPTIONS['num_items']

	if app_globals.OPTIONS['test']:
		app_globals.OPTIONS['output_path'] = app_globals.CONFIG['test_output_dir']
		try_shell('rm -rf \'%s\'' % app_globals.CONFIG['test_output_dir'])
		try_shell('mkdir -p \'%s\'' % app_globals.CONFIG['test_output_dir'])


def load_config(filename = None):
	"""
	Loads config.yml (or CONFIG['user_config_file']) and merges ith with the global OPTIONS hash
	"""
	if filename is None:
		filename = app_globals.CONFIG['user_config_file']
	
	print "Loading configuration from %s" % filename
	
	f = file(filename,'r')
	conf = yaml.load(f)
	
	required_keys = ['user','password', 'tag_list']
	for key,val in conf.items():
		app_globals.OPTIONS[key] = val
	
	for k in required_keys:
		if not k in app_globals.OPTIONS:
			raise "Required setting \"%s\" is not set (in %s)." % (k, filename)
