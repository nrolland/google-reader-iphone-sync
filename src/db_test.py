# the tested module
from db import *

# test helpers
from lib.mock import Mock
import pickle
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest
import config

class DBTest(unittest.TestCase):

	def setUp(self):
		config.parse_options(['--test','--num-items=3','--verbose'])

		self.output_folder = 'test_entries'
		assert app_globals.OPTIONS['output_path'] == self.output_folder

		# but we're mocking things, so pretend to be running the real thing
		app_globals.OPTIONS['test'] = False

		read_files = ['read filea a.||a||.html', 'starred but deleted file c.||c||.html']
		remaining_files = ['retained file b.||b||.html', 'starred and retained file d.||d||.html']
		starred_files = ['starred but deleted file c.||c||.html', 'starred and retained file d.||d||.html']
		previously_downloaded_files = read_files + remaining_files
		
		# make it look like we've been run before:
		# previously seen items
		f = file(self.output_folder + '/.entries.pickle', 'w')
		pickle.dump([DB.get_key(x) for x in previously_downloaded_files], f)
		f.close()
		f = None
	
		# starred items
		write_file(self.output_folder + '/.starred', '\n'.join(starred_files + ['\t','  ']))
	
		# remaining items
		for f in remaining_files:
			touch_file(self.output_folder + '/' + f)

		files = os.listdir(self.output_folder) 
		assert files == ['.entries.pickle','.starred'] + remaining_files
		
		# initialise the DB
		app_globals.DATABASE = self.db = DB()

	def tearDown(self):
		rm_rf(self.output_folder)
	
	# ------------------------------------------------------------------

	def test_processing_folder_contents(self):
		(read, unread, starred) = (self.db.read, self.db.unread, self.db.starred)
		assert unread == ['b','d']
		assert starred == ['c','d']
		assert read == ['a','c']
		
		# read returns true, unread returns false. items we've never seen return none
		assert self.db.is_read('a') == True
		assert self.db.is_read('b') == False
		assert self.db.is_read('non_existant') is None

	
	def test_adding_items(self):
		self.db.add_item(OpenStruct(key='new_item'))
		assert self.db.unread == ['b','d','new_item']
	
	def test_google_sync(self):
		# mock out the google reader
		app_globals.READER = reader = Mock(['set_read','add_star'])
		reader.set_read.return_value = True
		reader.add_star.return_value = True
		
		self.db.sync_to_google()
		assert reader.method_calls == [
			('add_star', ('c',), {}),
			('add_star', ('d',), {}),
			('set_read', ('a',), {}),
			('set_read', ('c',), {})]
	
	def test_cleanup(self):
		res_folders = ['a','b','blah','blah2','c','d']
		ensure_dir_exists(self.output_folder + '/_resources')
		for res_folder in res_folders:
			ensure_dir_exists(self.output_folder + '/_resources/' + res_folder)
			touch_file(self.output_folder + '/_resources/' + res_folder + '/image.jpg')
	
		assert os.listdir(self.output_folder + '/_resources') == res_folders
		
		# clean up that mess!
		self.db.cleanup()
		
		assert os.listdir(self.output_folder + '/_resources') == ['b','d']
	
	def test_save(self):
		self.db.save()
		f = file(self.output_folder + '/.entries.pickle', 'r')
		assert pickle.load(f) == ['b','d']
		f.close()
		f = None
