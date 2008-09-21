import glob, time, os, re, urllib

# local imports
import app_globals
from misc import *
from output import *
import template

# processing modules
from lib.BeautifulSoup import BeautifulSoup
import process


def esc(s):   return urllib.quote(string)
def unesc(s): return urllib.unquote(s)

def strip_html_tags(s):
	double_tag_match = re.compile('<(?P<tagname>[a-zA-Z0-9]+)[^<>]*>(?P<content>.*?)</(?P=tagname)>', re.DOTALL)
	single_tag_match = re.compile('<(?P<tagname>[a-zA-Z0-9]+)[^<>]*/>', re.DOTALL)
	
	while re.search(double_tag_match, s) is not None:
		s = re.sub(double_tag_match, '\g<content>', s)
		print s
	s = re.sub(single_tag_match, '', s)
	return s

class Item:
	"""
	A wrapper around a GoogleReader item
	"""
	def __init__(self, feed_item = None, feed_name = '(unknown)', raw_data = None):
		self.had_errors = False
		if feed_item is not None:
			try: self.feed_name = feed_item['feed_name']
			except:
				self.feed_name = feed_name
			self.title = strip_html_tags(feed_item['title'])
			self.title = unicode(BeautifulSoup(self.title, convertEntities = BeautifulSoup.HTML_ENTITIES))
			self.google_id = feed_item['google_id']
			self.date = time.strftime('%Y%m%d%H%M%S', time.localtime(float(feed_item['updated'])))
			self.is_read = 'read' in feed_item['categories']
			self.is_starred = 'starred' in feed_item['categories']
			self.url = feed_item['link']
			self.content = feed_item['content']
			self.original_id = feed_item['original_id']
			self.is_dirty = False
			self.is_stale = False
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
			filter(lambda x: x not in '"\':#!+/$\\?*', ascii(self.title))[:120] + ' .||' +
			self.safe_google_id + '||' )

	def soup_setup(self):
		self.soup = BeautifulSoup(self.content)
		try:
			self.base = url_dirname(self.original_id)
		except:
			self.base = None
	
	def soup_teardown(self):
		self.soup 
		self.content = self.soup.prettify()
		
	def process(self):
		debug("item %s -> process()" % self.title)
		self.soup_setup()

		# process
		process.insert_alt_text(self.soup)
		self.download_images(need_soup = False)
		
		# save changes back as content
		self.soup_teardown()
	
	def download_images(self, need_soup=True):
		self.had_errors = False
		if need_soup:
			self.soup_setup()
		
		success = process.download_images(self.soup,
			dest_folder = self.resources_path,
			href_prefix = app_globals.CONFIG['resources_path'] + '/' + self.safe_google_id + '/',
			base_href = self.base)
		if not success:
			self.had_errors = True

		if need_soup:
			self.soup_teardown()
	
	def save(self):
		app_globals.DATABASE.add_item(self)

	def delete(self):
		app_globals.DATABASE.remove_item(self)
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
