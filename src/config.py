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


required_keys = ['user','password', 'tag_list']	


def parse_options(argv = None):
	"""
Usage:
  -n, --num-items=[val]  set the number of items to download (per feed)
  -v, --verbose          verbose output
  -c, --cautious         cautious mode - prompt before performing destructive actions
  -d, --no-download      don't download new items, just tell google reader about read items
  -T, --template         just update the template used in existing downloaded items
  -t, --test             run in test mode. Don't notify google reader of anything, and clobber "test_entries" for output
  --user=[username]      set the username
  --password=[pass]      set password
  --tag=[tag_name]       add a tag to the list of tags to be downloaded. Can be used multiple times
  --output-path=[path]   set the base output path (where items and resources are saved)
"""
	tag_list = []
	if argv is None:
		argv = sys.argv[1:]
		
	(opts, argv) = getopt(argv, "n:vCdthT", ['num-items=','verbose','cautious','no-download','test', 'help', 'template','user=','password=','tag=','output-path=','no-output'])
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
			from lib.mock import Mock
			app_globals.READER = Mock()
			print "Test mode enabled - using %s" % app_globals.CONFIG['test_output_dir']
		elif key == '-T' or key == '--template':
			app_globals.OPTIONS['template_only'] = True
			print "Just updating item templates..."
		elif key == '-h' or key == '--help':
			print parse_options.__doc__
			sys.exit(1)

		# settings that are usually put in yaml...
		elif key == '--user':
			set_opt('user', val);
		elif key == '--password':
			set_opt('password',val);
		elif key == '--output-path':
			set_opt('output_path',val)
		elif key == '--tag':
			tag_list.append(val)
			set_opt('tag_list', tag_list)
		elif key == '--no-output':
			set_opt('do_output', False)
		else:
			print "unknown option: %s" % (key,)
			print parse_options.__doc__
			sys.exit(1)

	if len(argv) > 0:
		app_globals.OPTIONS['num_items'] = argv[0]
		print "Number of items set to %s" % app_globals.OPTIONS['num_items']

	if app_globals.OPTIONS['test']:
		app_globals.OPTIONS['output_path'] = app_globals.CONFIG['test_output_dir']
		try_shell('rm -rf \'%s\'' % app_globals.CONFIG['test_output_dir'])
		try_shell('mkdir -p \'%s\'' % app_globals.CONFIG['test_output_dir'])


def set_opt(key, val):
#	print "setting %s = %s" % (key, val)
	app_globals.OPTIONS[key] = val

def load(filename = None):
	"""
	Loads config.yml (or CONFIG['user_config_file']) and merges ith with the global OPTIONS hash
	"""
	if filename is None:
		filename = app_globals.CONFIG['user_config_file']
	
	print "Loading configuration from %s" % filename

	try:
		f = file(filename,'r')
		conf = yaml.load(f)
	
		for key,val in conf.items():
			set_opt(key, val)
	except Exception, e:
		print "Config file failed to load: %s" % e

def check():
	for k in required_keys:
		if not k in app_globals.OPTIONS:
			print repr(app_globals.OPTIONS)
			raise Exception("Required setting \"%s\" is not set." % (k,))
