"""
Exports:
DB class
"""
import pickle, re, urllib, glob, shutil
from sets import Set

# local imports
import app_globals
from misc import *
from item import MinimalItem

class DB:
	def __init__(self):
		# assume we've read everything that was left unread from last time
		self.unread = []
		self.read = self.load_previous_unread_items()
		self.starred = self.load_starred_items_file()
		
		# now look for still-unread items:
		file_extension = app_globals.file_extension()
		for f in glob.glob(app_globals.OPTIONS['output_path'] + '/*.' + file_extension):
			key = self.get_key(f)
			if not key:
				continue
			self.unread.append(key)
			try_remove(key, self.read)
		
		debug("unread:  " + str(self.unread))
		debug("read:    " + str(self.read))
		debug("starred: " + str(self.starred))
	
	def cleanup(self):
		res_prefix = "%s/%s/" % (app_globals.OPTIONS['output_path'], app_globals.CONFIG['resources_path'])
		glob_str = res_prefix + "*"
		current_keys = Set([os.path.basename(x) for x in glob.glob(glob_str)])
		unread_keys = Set(self.unread)
		
		current_but_read = current_keys.difference(unread_keys)
		if len(current_but_read) > 0:
			print "Cleaning up %s old resource directories" % len(current_but_read)
			danger("remove %s old resource directories" % len(current_but_read))
			for key in current_but_read:
				rm_rf(res_prefix + key)
	
	def add_item(self, item):
		self.unread.append(item.key)
		
	@staticmethod
	def get_key(s):
		"""
		>>> DB.get_key('blah.||this is the key, guys!||.html')
		'this is the key, guys!'
		"""
		match = re.search('\.\|\|([^|]*)\|\|\.[^.]*$', s)
		if match:
			return match.group(1)
		else:
			debug("Couldn't extract key from filename: %s" % s)
			return None
	
	def load_previous_unread_items(self):
		try:
			ret = load_pickle(app_globals.OPTIONS['output_path'] + '/' + app_globals.CONFIG['pickle_file'])
			return ret
		except:
			print "Note: loading of previous items failed"
			return []
	
	def load_starred_items_file(self):
		file_path = app_globals.OPTIONS['output_path'] + '/.starred'
		try:
			return [self.get_key(x.strip()) for x in file(file_path, 'r').readlines() if len(x.strip()) > 0]
		except:
			return []
		
	def save(self):
		filename = app_globals.OPTIONS['output_path'] + '/' + app_globals.CONFIG['pickle_file']
		try:
			shutil.move(filename, filename + '.bak')
		except:
			pass

		debug("Dumping \"unread items\":\n%s" % self.unread)
		save_pickle(self.unread, filename)
	
	def is_read(self, key):
		if key in self.read:
			return True
		if key in self.unread:
			return False
		return None
	
	@staticmethod
	def unencode_key(encoded_key):
		return urllib.unquote(encoded_key)
	
	@staticmethod
	def google_do_with_key(action, key):
		if app_globals.OPTIONS['test']:
			print "Not telling google about anything - we're testing!"
			return
		google_id = urllib.unquote(key)
		danger("Applying function %s to item %s" % (action, google_id))
		action(google_id)
	
	@staticmethod
	def mark_id_as_read(google_id):
		res = app_globals.READER.set_read(google_id)
		if not res:
			print "Failed to mark item as read"
			raise Exception("Failed to mark item as read")
	
	@staticmethod
	def mark_id_as_starred(google_id):
		res = app_globals.READER.add_star(google_id)
		if not res:
			print "Failed to add star to item"
			raise Exception("Failed to add star to item")

	def sync_to_google(self):
		print "Syncing with google..."
		self.mark_starred()
		self.mark_read()
	
	def mark_starred(self):
		if len(self.starred) > 0:
			print "Marking %s items as starred on google-reader" % len(self.starred)
			for key in self.starred:
				debug("marking as starred: %s" % key)
				self.google_do_with_key(self.mark_id_as_starred, key)
			debug("deleting .starred file")
			if not app_globals.OPTIONS['test']:
				os.remove(app_globals.OPTIONS['output_path'] + '/.starred')

	def mark_read(self):
		if len(self.read) > 0:
			print "Marking %s items as read on google-reader" % len(self.read)
			for key in self.read:
				debug("marking as read: %s" % key)
				self.google_do_with_key(self.mark_id_as_read, key)
				MinimalItem(self.unencode_key(key)).delete()

