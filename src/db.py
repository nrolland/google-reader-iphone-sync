"""
Exports:
DB class
"""
import pickle, re, urllib, glob, shutil, os
from sets import Set

# local imports
import app_globals
from misc import *
from item import Item

import sqlite3 as sqlite
class DB:
	def __init__(self, filename = 'items.sqlite'):
		if app_globals.OPTIONS['test']:
			filename = os.path.dirname(filename) + 'test_' + os.path.basename(filename)
		self.filename = filename = os.path.join(app_globals.OPTIONS['output_path'], os.path.basename(filename))
		print "db @ %s" % filename
		self.db = sqlite.connect(filename)

		# commit immediately after statements.
		# doing commits every now and then seems buggy, and we don't need it.
		self.db.isolation_level = "IMMEDIATE"

		self.schema = {
			'columns': [
				('google_id','TEXT primary key'),
				('date', 'TIMESTAMP'),
				('url', 'TEXT'),
				('title', 'TEXT'),
				('content', 'TEXT'),
				('feed_name', 'TEXT'),
				('is_read', 'BOOLEAN'),
				('is_starred', 'BOOLEAN'),
				('is_dirty', 'BOOLEAN default 0'),
			],
			'indexes' : [ ('item_id_index', 'items(google_id)') ]
		}
		self.cols = [x for (x,y) in self.schema['columns']]
		self.setup_db()

	def reload(self):
		"""
		reload the database
		"""
		self.close()
		self.db = sqlite.connect(self.filename)

	def sql(self, stmt, data = None):
		debug("SQL statement: %s" % stmt)
		if data is not None:
			debug("    data: %r" % (data,))
			result = self.db.execute(stmt, data)
		else:
			result = self.db.execute(stmt)

		return result
	
	def erase(self):
		if not app_globals.OPTIONS['test']:
			raise Exception("erase() called, but we're not in test mode...")
		self.sql('drop table if exists items')

	def reset(self):
		self.erase()
		self.setup_db()
	
	def tables(self):
		return [row[0] for row in self.db.execute('select name from sqlite_master where type = "table"')]

	def setup_db(self):
		# "if not exists" is broken in subtle and weird ways in pysqlite - this would be ideal:
		#col_str = 'create table if not exists items(' < code as below... > ')'
		
		# so we just use this:
		col_str = 'create table items('
		col_str += ', '.join(' '.join(x) for x in self.schema['columns'])
		col_str += ')'

		# and catch the exception if it fails
		try:
			self.db.execute(col_str)
		except sqlite.OperationalError:
			pass
		
		index_strs = ['create unique index if not exists %s on %s;' % (col, typestr) for (col, typestr) in self.schema['indexes']]
		for index_str in index_strs:
			self.sql(index_str)

	def add_item(self, item):
		self.sql("insert into items (%s) values (%s)" % (', '.join(self.cols), ', '.join(['?'] * len(self.cols))),
			[getattr(item, attr) for attr in self.cols])

	def update_item(self, item):
		self.sql("update items set is_read=?, is_starred=?, is_dirty=? where google_id=?",
			(item.is_read, item.is_starred, item.is_dirty, item.google_id));

	def get_items(self, condition=None, args=None):
		sql = "select * from items"
		if condition is not None:
			sql += " where %s" % condition
		cursor = self.sql(sql, args)
		for row_tuple in cursor:
			yield self.item_from_row(row_tuple)
	
	def get_items_list(self, *args, **kwargs):
		return [x for x in self.get_items(*args, **kwargs)]

	def item_from_row(self, row_as_tuple):
		i = 0
		item = {}
		for i in range(len(row_as_tuple)):
			val = row_as_tuple[i]
			col_description = self.schema['columns'][i][1]
			if 'BOOLEAN' in col_description:
				# convert to a python boolean
				val = val == 1
			else:
				val = str(val)
			item[self.cols[i]] = val
		return Item(raw_data = item)
	
	def cleanup(self):
		"""Clean up any hanging resources (for items that have been deleted)"""
		self.cleanup_resources_directory()
		
	def close(self):
		"""close the db"""
		debug("closing DB")
		# despite our insistance of "IMMEDIATE" isolation level, this seems to be necessary
		self.db.commit()
		self.db.close()
		self.db = None

	def is_read(self, google_id):
		"""
		check if an item is marked as read in the DB.
		If the id is not in the database, returns None
		"""
		cursor = self.sql('select is_read from items where google_id = ?', (google_id,))
		try:
			return cursor.next()[0] == 1 # truth is 1 in sqlite's mind
		except StopIteration:
			return None
	
	def sync_to_google(self):
		print "Syncing with google..."
		for item in self.get_items('is_dirty = 1'):
			debug('syncing item state \"%s\"' % item.title)
			item.save_to_web()
			self.update_item(item)
		for item in self.get_items('is_read = 1'):
			debug('deleting item \"%s\"' % item.title)
			item.delete()
		danger("about to delete items from db")
		self.sql('delete from items where is_read = 1')
	
	def cleanup_resources_directory(self):
		res_prefix = "%s/%s/" % (app_globals.OPTIONS['output_path'], app_globals.CONFIG['resources_path'])
		glob_str = res_prefix + "*"
		current_keys = Set([os.path.basename(x) for x in glob.glob(glob_str)])
		unread_keys = Set([Item.escape_google_id(row[0]) for row in self.sql('select google_id from items where is_read = 0')])

		current_but_read = current_keys.difference(unread_keys)
		if len(current_but_read) > 0:
			print "Cleaning up %s old resource directories" % len(current_but_read)
			danger("remove %s old resource directories" % len(current_but_read))
			for key in current_but_read:
				rm_rf(res_prefix + key)

