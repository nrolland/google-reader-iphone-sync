"""
Exports:
DB class
"""
import pickle, re, urllib, glob, shutil, os
from sets import Set

# local imports
import app_globals
from misc import *
from output import *
from item import Item

import sqlite3 as sqlite

# to support data migration, we currently have all versions / modifications to the schema
# hopefully this won't become too ungainly
schema_history = [
	'CREATE TABLE items(google_id TEXT primary key, date TIMESTAMP, url TEXT, original_id TEXT, title TEXT, content TEXT, feed_name TEXT, is_read BOOLEAN, is_starred BOOLEAN, is_dirty BOOLEAN default 0)',
	'CREATE UNIQUE INDEX item_id_index on items(google_id)',
	'ALTER TABLE items ADD COLUMN had_errors BOOLEAN default 0',
	'ALTER TABLE items ADD COLUMN is_stale BOOLEAN default 0',
	'ALTER TABLE items ADD COLUMN tag_name BOOLEAN default ""',
	]

class VersionDB:
	@staticmethod
	def version(db):
		version = 0
		tables = map(first, db.execute('select tbl_name from sqlite_master').fetchall())
		if 'db_version' in tables:
			version = int(first(db.execute('select version from db_version').fetchone()))
		else:
			db.execute('CREATE TABLE db_version(version INT)')
			db.execute('INSERT INTO db_version(version) VALUES (0)')
		return version

	@staticmethod
	def migrate(db, schema_history):
		version = VersionDB.version(db)
		unapplied_schema_steps = schema_history[version:]
		if len(unapplied_schema_steps) > 0:
			info("Your database is at version %s, the latest is version %s. Upgrading" % (version, len(schema_history)))
			print unapplied_schema_steps
			for step in unapplied_schema_steps:
				info("Appling the following query to your database:\n%s" % (step,))
				db.execute(step)
				version += 1
				db.execute('update db_version set version = ?', (version,))
			debug("database is up to date! (version %s)" % len(schema_history))
			db.commit()
		return len(unapplied_schema_steps)


class DB:
	def __init__(self, filename = 'items.sqlite'):
		if app_globals.OPTIONS['test']:
			filename = os.path.dirname(filename) + 'test_' + os.path.basename(filename)
		self.filename = filename = os.path.join(app_globals.OPTIONS['output_path'], os.path.basename(filename))
		debug("db @ %s" % filename)
		self.db = sqlite.connect(filename)

		# commit immediately after statements.
		# doing commits every now and then seems buggy, and we don't need it.
		self.db.isolation_level = "IMMEDIATE"

		self.schema = {
			'columns': [
				('google_id','TEXT primary key'),
				('date', 'TIMESTAMP'),
				('url', 'TEXT'),
				('original_id', 'TEXT'),
				('title', 'TEXT'),
				('content', 'TEXT'),
				('feed_name', 'TEXT'),
				('tag_name', 'TEXT'),
				('is_read', 'BOOLEAN'),
				('is_starred', 'BOOLEAN'),
				('is_dirty', 'BOOLEAN default 0'),
				('had_errors', 'BOOLEAN default 0'),
				('is_stale', 'BOOLEAN default 0'),
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
		debug_verbose("SQL statement: %s" % stmt)
		if data is not None:
			debug_verbose("    data: %r" % (data,))
			result = self.db.execute(stmt, data)
		else:
			result = self.db.execute(stmt)

		return result
	
	def erase(self):
		if not app_globals.OPTIONS['test']:
			raise Exception("erase() called, but we're not in test mode...")
		self.sql('delete from items')

	def reset(self):
		self.erase()
		self.setup_db()
	
	def tables(self):
		return [row[0] for row in self.db.execute('select name from sqlite_master where type = "table"')]

	def setup_db(self):
		global schema_history
		if VersionDB.migrate(self.db, schema_history) > 0:
			self.reload()
		
	def add_item(self, item):
		self.sql("insert into items (%s) values (%s)" % (', '.join(self.cols), ', '.join(['?'] * len(self.cols))),
			[getattr(item, attr) for attr in self.cols])
	
	def remove_item(self, item):
		google_id = item.google_id
		self.sql("delete from items where google_id = ?", (google_id,))
	
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
	
	def get_item_count(self, condition=None, args=None):
		sql = "select count(*) from items"
		if condition is not None:
			sql += " where %s" % condition
		cursor = self.sql(sql, args)
		return cursor.next()[0]

	def get_items_that_had_errors(self):
		return self.get_items(condition='had_errors = 1')
	
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
				val = unicode(val)
			item[self.cols[i]] = val
		return Item(raw_data = item)
	
	def cleanup(self):
		"""Clean up any stale items / resources"""
		self.cleanup_stale_items()
		self.cleanup_resources_directory()
		
	def close(self):
		"""close the db"""
		debug("closing DB")
		# despite our insistance of "IMMEDIATE" isolation level, this seems to be necessary
		self.db.commit()
		self.db.close()
		self.db = None

	def is_read(self, google_id, mark_as_fresh = True):
		"""
		check if an item is marked as read in the DB.
		If the id is not in the database, returns None
		"""
		debug('is_read = %s' % (google_id))
		cursor = self.sql('select is_read from items where google_id = ?', (google_id,))
		try:
			is_read = cursor.next()[0] == 1 # truth is 1 in sqlite's mind
			if mark_as_fresh:
				self.mark_item_as_fresh(google_id)
			return is_read
		except StopIteration:
			return None
		
	def update_feed_for_item(self, item):
		self.sql('update items set tag_name = ? where google_id = ?', (item.tag_name, item.google_id))
	
	def sync_to_google(self):
		puts("Syncing with google...")
		status("SUBTASK_TOTAL", self.get_item_count('is_dirty = 1'))
		item_number = 0
		for item in self.get_items('is_dirty = 1'):
			debug('syncing item state \"%s\"' % item.title)
			item.save_to_web()
			self.update_item(item)

			item_number += 1
			status("SUBTASK_PROGRESS",item_number)

		for item in self.get_items('is_read = 1'):
			debug('deleting item \"%s\"' % item.title)
			item.delete()
		danger("about to delete %s read items from db" % self.get_item_count('is_read = 1'))
		self.sql('delete from items where is_read = 1')
		
	def prepare_for_download(self):
		self.sql('update items set is_stale = ?', (True,))
	
	def mark_item_as_fresh(self, item_id):
		self.sql('update items set is_stale = ? where google_id = ?', (False, item_id))
		
	def cleanup_stale_items(self):
		self.sql('delete from items where is_stale = ?', (True,))
	
	def cleanup_resources_directory(self):
		res_prefix = "%s/%s/" % (app_globals.OPTIONS['output_path'], app_globals.CONFIG['resources_path'])
		glob_str = res_prefix + "*"
		current_keys = Set([os.path.basename(x) for x in glob.glob(glob_str)])
		unread_keys = Set([Item.escape_google_id(row[0]) for row in self.sql('select google_id from items where is_read = 0')])

		current_but_read = current_keys.difference(unread_keys)
		if len(current_but_read) > 0:
			puts("Cleaning up %s old resource directories" % len(current_but_read))
			danger("remove %s old resource directories" % len(current_but_read))
			for key in current_but_read:
				rm_rf(res_prefix + key)

