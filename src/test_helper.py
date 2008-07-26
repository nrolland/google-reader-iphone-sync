# the tested module
from item import *

# test helpers
from lib.mock import Mock
import pickle
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest
import config

def init_output_folder():
	config.parse_options(['--test','--num-items=3','--verbose'])

	output_folder = 'test_entries'
	assert app_globals.OPTIONS['output_path'] == output_folder

	# but we're mocking things, so pretend to be running the real thing
	app_globals.OPTIONS['test'] = False
	
	return output_folder
