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
	config.parse_options(['--test','--num-items=3','--verbose','--verbose'])

	output_folder = '/tmp/GRiS/test_entries'
	assert app_globals.OPTIONS['output_path'] == output_folder
	assert type(app_globals.READER) == Mock

	return output_folder
