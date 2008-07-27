# the tested module
from db import *
from item import Item

# test helpers
import test_helper
from lib.mock import Mock
import pickle
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest
import config

def fake_item(**kwargs):
	args = {
		'google_id' : 'sample_id',
		'title' : 'title',
		'url' : 'http://example.com/post/1',
		'is_read' : False,
		'is_dirty' : False,
		'is_starred' : False,
		'feed_name' : 'feedname',
		'date' : 'date',
		'content' : '<h1>content!</h1>'
		}
	args.update(kwargs)
	return OpenStruct(**args)


class DBTest(unittest.TestCase):

	def setUp(self):
		self.output_folder = test_helper.init_output_folder()

		# initialise the DB
		app_globals.DATABASE = self.db = DB()
		print "running db reset: %r" % self.db
		self.db.reset()
		assert self.db.tables() == ['items']
		
	def tearDown(self):
		self.db.close()
		rm_rf(self.output_folder)
	
	# ------------------------------------------------------------------

	def test_adding_items(self):
		# add to DB
		input_item = fake_item()
		self.db.add_item(input_item)
		
		# grab it out
		items = list(self.db.get_items())
		assert len(items) == 1
		item = items[0]
		
		# and check it still looks the same:
		for attr in ['url','title','feed_name','google_id','is_read','is_dirty','is_starred','date','content']:
			assert getattr(item, attr) == getattr(input_item, attr)

		# test updating
		item.is_read = True
		self.db.update_item(item)
		items = list(self.db.get_items())
		assert len(items) == 1
		item = items[0]
		assert item.is_read == True

	
	def test_is_read(self):
		assert self.db.is_read('sample_id') == None
		self.db.add_item(fake_item())
		assert self.db.is_read('sample_id') == False
		self.db.sql('update items set is_read = 1 where google_id = "sample_id"')
		assert self.db.is_read('sample_id') == True
	
	def test_google_sync(self):
		# mock out the google reader
		reader = app_globals.READER
		reader.set_read.return_value = True
		reader.add_star.return_value = True
		reader.set_unread.return_value = True
		reader.del_star.return_value = True
		
		self.db.add_item(fake_item(google_id = 'b', is_read = False, is_dirty = True))
		self.db.add_item(fake_item(google_id = 'd', is_read = False, is_dirty = True))
		self.db.add_item(fake_item(google_id = 'c', is_starred = True, is_read = True, is_dirty = True))

		self.db.sync_to_google()
		assert reader.method_calls == [
			('set_unread', ('b',), {}),
			('del_star', ('b',), {}),
			('set_unread', ('d',), {}),
			('del_star', ('d',), {}),
			('set_read', ('c',), {}),
			('add_star', ('c',), {})]
		
		assert self.db.get_items_list('is_dirty = 1') == []
		assert len(self.db.get_items_list('is_dirty = 0')) == 3
		reader.reset()
	
	def test_google_sync_failures(self):
		self.db.add_item(fake_item(google_id = 'b', is_read = True, is_dirty = True))
		app_globals.READER.set_read.return_value = False
		self.assertRaises(Exception, self.db.sync_to_google)
	
	def test_cleanup(self):
		res_folders = ['a','b','blah','blah2','c','d']
		ensure_dir_exists(self.output_folder + '/_resources')
		for res_folder in res_folders:
			ensure_dir_exists(self.output_folder + '/_resources/' + res_folder)
			touch_file(self.output_folder + '/_resources/' + res_folder + '/image.jpg')
	
		assert os.listdir(self.output_folder + '/_resources') == res_folders
		
		# insert some existing items
		self.db.add_item(fake_item(google_id = 'b', is_read = False))
		self.db.add_item(fake_item(google_id = 'd', is_read = False))
		self.db.add_item(fake_item(google_id = 'c', is_read = True))
		
		# clean up that mess!
		self.db.sync_to_google() # remove all the read items
		self.db.cleanup()
		
		assert os.listdir(self.output_folder + '/_resources') == ['b','d']
