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
	app_globals.READER = Reader()
	assert type(app_globals.READER.gr) == Mock

	return output_folder
