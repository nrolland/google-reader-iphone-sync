import glob, time, os, re, urllib

# local imports
import app_globals
from misc import *
import template

# processing modules
from lib.BeautifulSoup import BeautifulSoup
import process


def remove_the_damn_html_entities(s):
	# surely there should be a library method somewhere to decode these. But for our purposes we can just ditch them.
	return re.sub('&.{2,4};','',s)

def esc(s):   return urllib.quote(string)
def unesc(s): return urllib.unquote(s)

def ascii(s): return s.encode('ascii','ignore') if isinstance(s, unicode) else s
def utf8(s):  return s.encode('utf-8','ignore') if isinstance(s, unicode) else s

class MinimalItem:
	"""
	an empty item with skeleton functionality (that can be derived from its google_id)
	"""
	def __init__(self, google_id):
		self.item = {'google_id': google_id}
	
	def get_key(self):
		return urllib.quote(self.item['google_id'],safe='')
	key = property(get_key)
	
	def get_resources_path(self):
		return "%s/%s/%s" % (app_globals.OPTIONS['output_path'], app_globals.CONFIG['resources_path'], self.key)
	resources_path = property(get_resources_path)

	def delete(self):
		for f in glob.glob(app_globals.OPTIONS['output_path'] + '/*.' + self.key + '.*'):
			rm_rf(f)
		rm_rf(self.resources_path)


class Item(MinimalItem):
	"""
	A wrapper around a GoogleReader item
	"""
	def __init__(self, feedItem):
		self.item = feedItem

	def get_basename(self):
		tag_str = ''
		for cat in self.item['categories']:
			if re.search('ipod$', cat, re.I) is not None:
				tag_str = '[txt] '
		return utf8(
		time.strftime('%Y-%m-%d|%H-%M-%S', time.localtime(self.item['updated'])) + ' ' + tag_str +
			filter(lambda x: x not in '"\':#!+/$\\?*', ascii(remove_the_damn_html_entities(self.item['title'])))[:120] + ' .||' +
			self.key + '||' )
	basename = property(get_basename)

	
	def process(self):
		# setup:
		self.item['soup'] = BeautifulSoup(self.item['content'])
		try:
			self.item['base'] = url_dirname(item['original_id'])
		except:
			self.item['base'] = None
		
		# process
		self.item = process.insert_alt_text(self.item)
		self.item = process.download_images(
			self.item,
			dest_folder = self.resources_path,
			href_prefix = app_globals.CONFIG['resources_path'] + '/' + self.key + '/')
		
		# teardown
		self.item['content'] = self.item['soup'].prettify()
	
	def output(self):
		base = app_globals.OPTIONS['output_path'] + '/' + self.basename

		render_object = {
			'title_link':  '<a href="' + utf8(self.item['link']) + '">' + utf8(self.item['title']) + '</a>',
			'title_html':  '<title>' + utf8(self.item['title']) + '</title>',
			'content':     utf8(self.item['content']),
			'via':        'from tag <b>'+ self.feed_name +'</b>'
		}

		# create the "via" link
		try:
			render_object['via'] += '<br />url ' + re.sub('.*://', '', self.item['sources'].keys()[0]).replace('/',' / ').replace('=',' = ') + '<br /><br />'
		except:
			pass
		
		debug("rendering item to %s using template file %s" % (base + '.html', 'template/item.html'))
		template.create(render_object, 'template/item.html', base + '.html')
		
		app_globals.DATABASE.add_item(self)
	
	def get_is_read(self):
		return 'read' in self.item['categories']
	is_read = property(get_is_read)

