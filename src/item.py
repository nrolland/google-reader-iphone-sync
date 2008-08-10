import glob, time, os, re, urllib

# local imports
import app_globals
from misc import *
from output import *
import template

# processing modules
from lib.BeautifulSoup import BeautifulSoup
import process


def remove_the_damn_html_entities(s):
	# surely there should be a library method somewhere to decode these. But for our purposes we can just ditch them.
	return re.sub('&.{2,4};','',s)

def esc(s):   return urllib.quote(string)
def unesc(s): return urllib.unquote(s)

class Item:
	"""
	A wrapper around a GoogleReader item
	"""
	def __init__(self, feed_item = None, feed_name = '(unknown)', raw_data = None):
		if feed_item is not None:
			try: self.feed_name = feed_item['feed_name']
			except:
				self.feed_name = feed_name
			self.title = feed_item['title']
			self.google_id = feed_item['google_id']
			self.date = time.strftime('%Y%m%d%H%M%S', time.localtime(feed_item['updated']))
			self.is_read = 'read' in feed_item['categories']
			self.is_starred = 'starred' in feed_item['categories']
			self.url = feed_item['link']
			self.content = feed_item['content']
			self.original_id = feed_item['original_id']
			self.is_dirty = False
		else:
			# just copy the dict's keys to my instance vars
			for key,value in raw_data.items():
				setattr(self, key, value)
		
		# calculated attributes that aren't stored in the DB
		self.safe_google_id = Item.escape_google_id(self.google_id)
		self.resources_path = "%s/%s/%s" % (app_globals.OPTIONS['output_path'], app_globals.CONFIG['resources_path'], self.safe_google_id)
		self.basename = self.get_basename()
	
	@staticmethod
	def unescape_google_id(safe_google_id):
		return urllib.unquote(safe_google_id)

	@staticmethod
	def escape_google_id(unsafe_google_id):
		return urllib.quote(unsafe_google_id, safe='')

	def get_basename(self):
		return utf8(
			self.date + ' ' +
			filter(lambda x: x not in '"\':#!+/$\\?*', ascii(remove_the_damn_html_entities(self.title)))[:120] + ' .||' +
			self.safe_google_id + '||' )

	def process(self):
		debug("item %s -> process()" % self.title)
		# setup:
		soup = BeautifulSoup(self.content)
		try:
			base = url_dirname(self.original_id)
		except:
			base = None

		# process
		soup = process.insert_alt_text(soup)
		soup = process.download_images(soup,
			dest_folder = self.resources_path,
			href_prefix = app_globals.CONFIG['resources_path'] + '/' + self.safe_google_id + '/',
			base_href = base)
		
		# save changes back as content
		self.content = soup.prettify()
	
	def save(self):
		if app_globals.OPTIONS['do_output']:
			base = app_globals.OPTIONS['output_path'] + '/' + self.basename

			render_object = {
				'title_link':  '<a href="' + utf8(self.url) + '">' + utf8(self.title) + '</a>',
				'title_html':  '<title>' + utf8(self.title) + '</title>',
				'content':     utf8(self.content),
				'via':        'from tag <b>'+ utf8(self.feed_name) +'</b>'
			}

			# create the "via" link
			try:
				render_object['via'] += '<br /><em>' + re.sub('.*://([^/]+).*', '\\1', self.original_id) + '</em><br /><br />'
			except:
				pass
		
			debug("rendering item to %s using template file %s" % (base + '.html', 'template/item.html'))
			template.create(render_object, 'template/item.html', base + '.html')

		else: 
			debug("Not outputting any files")
		self.add_to_db()
	
	def add_to_db(self):
		app_globals.DATABASE.add_item(self)

	def delete(self):
		for f in glob.glob(app_globals.OPTIONS['output_path'] + '/*.' + self.safe_google_id + '.*'):
			rm_rf(f)
		rm_rf(self.resources_path)

	def save_to_web(self):
		if not self.is_dirty:
			return
		
		# actions are effects to apply in order to ensure the web has been updated with our current state
		# i.e anything that the user *can* change must be set here
		actions = []
		# read status
		if self.is_read:
			actions.append(app_globals.READER.set_read)

		# stars
		if self.is_starred:
			actions.append(app_globals.READER.add_star)

		# apply the actions
		for action in actions:
			result = Item.google_do_with_id(action, self.google_id)
			if not result:
				msg = "Failed to apply function %s" % action
				info(msg)
				raise Exception(msg)
		
		self.is_dirty = False

	@staticmethod
	def google_do_with_id(action, google_id):
		debug("Applying function %s to item %s" % (action, google_id))
		danger("Applying function %s to item %s" % (action, google_id))
		return action(google_id)
