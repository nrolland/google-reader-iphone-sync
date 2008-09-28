# the tested module
from item import *

# test helpers
from lib.mock import Mock
import pickle
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest
import config
from reader import Reader

def init_output_folder():
	output_folder = '/tmp/GRiS/test_entries'
	config.parse_options(['--test','--num-items=3','--verbose','--verbose', '--verbose', '--output-path=%s' % output_folder])

	assert app_globals.OPTIONS['output_path'] == output_folder
	ensure_dir_exists(output_folder)
	app_globals.READER = Reader()
	assert type(app_globals.READER.gr) == Mock

	return output_folder

def google_ids(item_list):
	return [x.google_id for x in sorted(item_list)]

def fake_item(**kwargs):
	args = {
		'google_id' : 'sample_id',
		'title' : 'title',
		'url' : 'http://example.com/post/1',
		'original_id': 'http://www.exampleblog.com/post/1',
		'is_read' : False,
		'is_dirty' : False,
		'is_starred' : False,
		'feed_name' : 'feedname',
		'date' : '20080812140000',
		'content' : '<h1>content!</h1>',
		'had_errors' : False,
		'is_stale': False,
		}
	args.update(kwargs)
	return OpenStruct(**args)


################ generic test helpers ################
import sys

def pending(original_function, reason = None):
	def test_the_original_function(*args, **kwargs):
		fn_name = original_function.__name__
		reason_str = "" if reason is None else " (%s)" % reason
		try:
			original_function(*args, **kwargs)
			print >> sys.stderr, "%s %sPASSED unexpectedly" % (fn_name, reason_str)
		except Exception, e:
			print >> sys.stderr, "PENDING%s: %s raised error: %s" % (reason_str, fn_name, e)
	return test_the_original_function
