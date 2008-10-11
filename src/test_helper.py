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
		'tag_name' : 'tagname',
		'date' : '20080812140000',
		'content' : '<h1>content!</h1>',
		'had_errors' : False,
		'is_stale': False,
		'is_shared': False,
		}
	args.update(kwargs)
	return OpenStruct(**args)


################ generic test helpers ################
import sys

def pending(function_or_reason):
	def wrap_func(func, reason = None):
		reason_str = "" if reason is None else " (%s)" % reason
		def actually_call_it(*args, **kwargs):
			fn_name = func.__name__
			try:
				func(*args, **kwargs)
				print >> sys.stderr, "%s%s PASSED unexpectedly " % (fn_name, reason_str),
			except:
				print >> sys.stderr, "[[[ PENDING ]]]%s ... " % (reason_str,),
		actually_call_it.__name__ = func.__name__
		return actually_call_it
	
	if callable(function_or_reason):
		# we're decorating a function
		return wrap_func(function_or_reason)
	else:
		# we've been given a description - return a decorator
		def decorator(func):
			return wrap_func(func, function_or_reason)
		return decorator
