# the tested module
from db import *
from item import Item
from output import *
import os

# test helpers
import test_helper
from lib.mock import Mock
import pickle
from StringIO import StringIO
from lib.OpenStruct import OpenStruct
import unittest
import config

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
		'had_errors' : False
		}
	args.update(kwargs)
	return OpenStruct(**args)

def test_migrated_persistance():
	# make sure the migrations actually get saved to disk.
	# You might not think this would be a necessary test, but you'd be surprised...
	fname = '/tmp/test_items.sqlite'
	schema = ['create table items(id TEXT)', 'create table items2(id TEXT)']
	try:
		os.remove(fname)
	except:
		pass # that's ok...
	db = sqlite.connect(fname)
	assert VersionDB.migrate(db, schema) == 2 # 2 steps applied
	db.close()
	
	db = sqlite.connect(fname)
	assert VersionDB.migrate(db, schema) == 0
	
	db.close()
	os.remove(fname)

class VersionDBTest(unittest.TestCase):
	def setUp(self):
		self.output_folder = test_helper.init_output_folder()
		self.db = sqlite.connect(':memory:')
		assert self.tables() == []
	
	def tearDown(self):
		self.db.close()
		self.db = None
		
	def tables(self):
		return map(first, self.db.execute('select name from sqlite_master where type = \'table\'').fetchall())
	
	def test_zero_migration(self):
		assert VersionDB.migrate(self.db, []) == 0
		assert self.tables() == ['db_version']
		assert VersionDB.version(self.db) == 0
		assert self.tables() == ['db_version']

	def test_zero_up_migration(self):
		assert VersionDB.migrate(self.db, ['create table items(id TEXT)', 'create table items2(id TEXT)']) == 2 # 2 steps applied
		assert sorted(self.tables()) == ['db_version', 'items', 'items2']
		assert VersionDB.version(self.db) == 2

		# make sure it's idempotent
		assert VersionDB.migrate(self.db, ['create table items(id TEXT)', 'create table items2(id TEXT)']) == 0 # 0 steps applied
		assert sorted(self.tables()) == ['db_version', 'items', 'items2']
		assert VersionDB.version(self.db) == 2
	
	def test_nonzero_migration(self):
		schema = ['create table items(id TEXT)']
		assert VersionDB.migrate(self.db, schema) == 1 # 1 step applied
		assert sorted(self.tables()) == ['db_version', 'items']
		assert VersionDB.version(self.db) == 1

		schema.append('create table items2(id TEXT)')
		assert VersionDB.migrate(self.db, schema) == 1 # 1 more step applied
		assert sorted(self.tables()) == ['db_version', 'items', 'items2']
		assert VersionDB.version(self.db) == 2
	
	def test_invalid_migration(self):
		schema = ['create_table items(id TEXT)']
		self.assertRaises(sqlite.OperationalError, VersionDB.migrate, self.db, ['clearly this is invalid sql'])
		assert VersionDB.version(self.db) == 0


class DBTest(unittest.TestCase):

	def setUp(self):
		self.output_folder = test_helper.init_output_folder()

		# initialise the DB
		app_globals.DATABASE = self.db = DB('test.sqlite')
		print "running db reset: %r" % self.db
		self.db.reset()
		self.assertEqual( sorted(self.db.tables()), ['db_version','items'] )
		
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

	def test_deleting_an_item(self):
		a = fake_item(google_id = 'a')
		b = fake_item(google_id = 'b')
		self.db.add_item(a)
		self.db.add_item(b)
		items = list(self.db.get_items())
		assert len(items) == 2
		
		# now remove it
		self.db.remove_item(a)
		items = list(self.db.get_items())
		assert len(items) == 1
		assert items[0].google_id == 'b'
	
	def test_deleting_old_items(self):
		old_1 = fake_item(google_id = 'old_1', date = '20060812140000') # 2006
		old_2 = fake_item(google_id = 'old_2', date = '20070812140000') # 2007
		new_1 = fake_item(google_id = 'new_1', date = '20080812140000') # 2008 - this is where we'll slice it
		new_2 = fake_item(google_id = 'new_2', date = '20080812140000') # identical to new_1
		new_3 = fake_item(google_id = 'new_3', date = '20090812140000') # 2009
		
		old_items = [old_1, old_2]
		new_items = [new_1, new_2, new_3]
		all_items = old_items + new_items

		for the_item in all_items:
			self.db.add_item(the_item)
		
		self.assertEqual(google_ids(self.db.get_items_list()), google_ids(all_items))
		self.db.delete_items_older_than(new_1)
		print google_ids(self.db.get_items_list())
		
		self.assertEqual(google_ids(self.db.get_items_list()), google_ids(new_items))
		print google_ids(self.db.get_items_list())
	
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
		
		self.db.add_item(fake_item(google_id = 'b', title='item b', is_read = False, is_dirty = True))
		self.db.add_item(fake_item(google_id = 'd', title='item d', is_read = False, is_dirty = True))
		self.db.add_item(fake_item(google_id = 'c', title='item c', is_starred = True, is_read = True, is_dirty = True))

		self.db.sync_to_google()
		assert reader.method_calls == [
			('set_read', ('c',), {}),
			('add_star', ('c',), {})]
		
		assert self.db.get_items_list('is_dirty = 1') == []
		# c should have been deleted because it was read
		assert sorted(map(lambda x: x.title, self.db.get_items_list('is_dirty = 0'))) == ['item b','item d']
		self.db.reload()
		# check that changes have been saved
		assert sorted(map(lambda x: x.title, self.db.get_items_list('is_dirty = 0'))) == ['item b','item d']
	
	def test_google_sync_failures(self):
		self.db.add_item(fake_item(google_id = 'b', is_read = True, is_dirty = True))
		app_globals.READER.set_read.return_value = False
		self.assertRaises(Exception, self.db.sync_to_google)
		
		# item should still be marked as read
		assert self.db.get_items_list('is_dirty = 0') == []
		assert len(self.db.get_items_list('is_dirty = 1')) == 1
	
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
