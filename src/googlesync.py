#!/usr/bin/env python
from GoogleReader import GoogleReader, CONST

#standard modules
import time
import sys
import os
import re
import glob
import urllib
import pickle
import yaml
from getopt import getopt
from BeautifulSoup import BeautifulSoup, Tag

CONFIG = {
	'pickle_file': '.entries.pickle',
	'user_config_file': 'config.yml',
}

OPTIONS = {
	'output_path': 'entries',
	'num_items':    300,
	'no_download':  False,
	'verbose':      False,
	'cautious':     False,
}

STATS = {
	'items':  0,
	'failed': 0,
	'new':    0,
	'read':   0,
}

READER = None
db = None

def danger(desc):
	global OPTIONS
	if not OPTIONS['cautious']: return
	response = raw_input("%s. Continue? " % desc)
	if not re.match('[yY]', response):
		print "Aborted."
		sys.exit(2)
		raise Exception("We should never get here!")
	debug("Continuing...")

def debug(s):
	global OPTIONS
	if not OPTIONS['verbose']: return
	print ' > ' + str(s)

def remove_the_damn_html_entities(s):
	return re.sub('&.{2,4};','',s)

def esc(s):
	return urllib.quote(string)

def unesc(s):
	return urllib.unquote(s)
	
def ascii(s):
	return s.encode('ascii','ignore')

def line():
	print '-' * 50

def try_remove(elem, lst):
	try:
		lst.remove(elem)
	except:
		pass

	

def test():
	items = [
		{'author': u'pizzaburger',
		 'categories': {u'user/-/label/03-comics---imagery': u'03-comics---imagery',
		                u'user/-/state/com.google/fresh': u'fresh',
		                u'user/-/state/com.google/reading-list': u'reading-list'},
		 'content': u'<div><br><p>Thx Penntastic</p>\n<p><img src="http://failblog.files.wordpress.com/2008/06/assembly-fail.jpg" alt="fail owned pwned pictures"></p>\n<img alt="" border="0" src="http://feeds.wordpress.com/1.0/categories/failblog.wordpress.com/1234/"> <img alt="" border="0" src="http://feeds.wordpress.com/1.0/tags/failblog.wordpress.com/1234/"> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/gocomments/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/comments/failblog.wordpress.com/1234/"></a> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/godelicious/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/delicious/failblog.wordpress.com/1234/"></a> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/gostumble/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/stumble/failblog.wordpress.com/1234/"></a> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/godigg/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/digg/failblog.wordpress.com/1234/"></a> <a rel="nofollow" href="http://feeds.wordpress.com/1.0/goreddit/failblog.wordpress.com/1234/"><img alt="" border="0" src="http://feeds.wordpress.com/1.0/reddit/failblog.wordpress.com/1234/"></a> <img alt="" border="0" src="http://stats.wordpress.com/b.gif?host=failblog.org&amp;blog=2441444&amp;post=1234&amp;subd=failblog&amp;ref=&amp;feed=1"></div><img src="http://feeds.feedburner.com/~r/failblog/~4/318806514" height="1" width="1">',
		 'crawled': 1214307453013L,
		 'google_id': u'tag:google.com,2005:reader/item/dcb79527f18794d0',
		 'link': u'http://feeds.feedburner.com/~r/failblog/~3/318806514/',
		 'original_id': u'http://failblog.wordpress.com/?p=1234',
		 'published': 1214269209.0,
		 'sources': {u'feed/http://feeds.feedburner.com/failblog': u'tag:google.com,2005:reader/feed/http://feeds.feedburner.com/failblog'},
		 'summary': u'',
		 'title': u'Assembly Fail',
		 'updated': 1214269209.0}
	]
	
	for i in items:
		theItem  = Item(i)
		print theItem.basename()

## processing modules:
def insert_alt_text(item):
	soup = item['soup']
	images = soup.findAll('img',{'title':True})
	for img in images:
		desc = BeautifulSoup('<p><b>( %s )</b></p>' % img['title'])
		img.append(desc)
	return item

class Item:
	def __init__(self, feedItem):
		self.item = feedItem

	def key(self):
		return urllib.quote(self.item['google_id'],safe='')
		
	def basename(self):
		tag_str = ''
		for cat in self.item['categories']:
			if re.search('ipod$', cat, re.I) is not None:
				tag_str = '[txt] '
		return e(
		time.strftime('%Y-%m-%d', time.localtime(self.item['updated'])) + ' ' + tag_str +
			filter(lambda x: x not in '"\':+/$\\?*', ascii(remove_the_damn_html_entities(self.item['title'])))[:120] + ' .||' +
			self.key() + '||' )
	
	def process(self):
		return ## TODO: why doesn't this work? :'(
		self.item['soup'] = BeautifulSoup(self.item['content'])
		self.item = insert_alt_text(self.item)
		self.item['content'] = self.item['soup'].prettify()
	
	def output(self):
		global OPTIONS, db
		base = OPTIONS['output_path'] + '/' + self.basename()
		f = open(base + '.html', 'w')
		if f is None:
			raise Exception("File open failed: " + base + '.html')
		
		try:
			f.writelines([
				'<html>',
				'	<head>',
				'		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />',
				'		<title>' + e(self.item['title']) + '</title>',
				'		<link rel="stylesheet" href="../src/style.css" type="text/css" />',
				'	</head>',
				'	<body>'])

			f.writelines([
				'<a href="' + e(self.item['link']) + '">',
					tag('h3',self.item['title']),
				'</a>'])
			
			f.write(tag('br'))
		
			try:
				url = ' via ' + re.sub('.*://', '', self.item['sources'].keys()[0]).replace('/',' / ').replace('=',' = ')
				f.write(tag('em', url))
				f.write(tag('br'))
				f.write(tag('br'))
			except:
				pass
		
			f.write(tag('div', self.item['content']))
		
			f.writelines([
				'	</body>',
				'</html>'])
			f.close()
		
			debug("converting to pdf")
		
			# convert to pdf:
			cmd = 'python src/html2pdf.py "%s" "%s"' % (base + '.html', base + '.pdf')
			
			debug("command: " + cmd)
			ret = os.system(cmd)
			debug("command returned: " + str(ret))
			if ret == 0:
				db.add_item(self)
			else:
				print "pdf conversion failed"
		finally:
			os.remove(base + '.html')
	
	def is_read(self):
		return 'read' in self.item['categories']
	
	def mark_as_read(self):
		global READER, OPTIONS
		for f in glob.glob(OPTIONS['output_path'] + '/*.' + self.key() + '.*'):
			print "Removing file: " + f
			danger('remove file')
			os.remove(f)

def mark_id_as_read(google_id):
	global READER
	res = READER.set_read(google_id)
	if not res:
		print "Failed to mark item as read"
		raise Exception("Failed to mark item as read")


class DB:
	def __init__(self):
		global OPTIONS
		# assume we've read everything that was left unread from last time
		self.unread = []
		self.read = self.load_previous_unread_items()
		
		# now look for still-unread items:
		for f in glob.glob(OPTIONS['output_path'] + '/*.pdf'):
			key = self.get_key(f)
			if not key:
				continue
			self.unread.append(key)
			try_remove(key, self.read)
		
		debug("unread: " + str(self.unread))
		debug("read:   " + str(self.read))
	
	def add_item(self, item):
		self.unread.append(item.key())
		
	def get_key(self, str):
		match = re.search('\.\|\|([^|]*)\|\|\.[^.]*$', str)
		if match:
			return match.group(1)
		else:
			debug("Couldn't extract key from filename: %s" % str)
			return None
	
	def load_previous_unread_items(self):
		global OPTIONS, CONFIG
		try:
			f = file(OPTIONS['output_path'] + '/' + CONFIG['pickle_file'],'r')
			ret = pickle.load(f)
			f.close()
			return ret
		except:
			print "Note: loading of previous items failed"
			return []
		
	def save(self):
		global OPTIONS, CONFIG
		f = file(OPTIONS['output_path'] + '/' + CONFIG['pickle_file'],'w')
		ret = pickle.dump(self.unread, f)
		f.close()
		return ret
	
	def is_read(self, key):
		if key in self.read:
			return True
		if key in self.unread:
			return False
		return None
	
	def mark_key_as_read(self, key):
		google_id = urllib.unquote(key)
		try:
			danger("Marking item %s as read" % google_id)
			mark_id_as_read(google_id)
		except:
			print "Failed to mark item %s as read" % google_id
	
	def sync_to_google(self):
		print "Syncing with google..."
		if len(self.read) == 0: return
		print "Marking %s items as read on google-reader" % len(self.read)
		for key in self.read:
			self.mark_key_as_read(key)
	
	
def e(s):
	return s.encode('utf-8','ignore')

def tag(name, content = None, attrs=None):
	s = "<" + name
	
	if attrs is not None:
		for key,val in attrs.items():
			s += ' %s="%s"' % (key,val)
		
	if content is None:
		s += " />"
		return s
	s += '>' + e(content) + '</' + name + '>'
	return s

def download_new_items():
	global READER, OPTIONS, CONFIG, STATS, db
		
	for feed_tag in OPTIONS['tag_list']:
		print "Fetching maximum %s items from feed %s" % (OPTIONS['num_items'], feed_tag)
		feed = READER.get_feed(None,
			CONST.ATOM_PREFIXE_LABEL + feed_tag,
			count=OPTIONS['num_items'],
			exclude_target = CONST.ATOM_STATE_READ,	# get only unread items
			order = CONST.ORDER_REVERSE)			# oldest first
	
		for entry in feed.get_entries():
			debug(" -- %s -- " % STATS['items'])
			STATS['items'] += 1
		
			if entry is None:
				STATS['failed'] += 1
				print " ** FAILED **"
				continue
		
			debug(entry.__repr__())
			debug('-' * 50)
		
			item = Item(entry)
			state = db.is_read(item.key())
			name = item.basename()
		
			if state is None:
				if not item.is_read():
					try:
						print "NEW: " + name
						danger("About to output item")
						item.process()
						item.output()
						STATS['new'] += 1
					except Exception,e:
						print " ** FAILED **: " + str(e)
						if OPTIONS['verbose']:
							raise e
						STATS['failed'] += 1
			else:
				if state == True or item.is_read():
					# item has been read either online or offline
					print "READ: " + name
					STATS['read'] += 1
					danger("About to mark item as read")
					item.mark_as_read()
		
		line()
	
	print "%s NEW items" % STATS['new']
	print "%s items marked as read" % STATS['read']
	if STATS['failed'] > 0:
		print "(%s items failed to parse)" % STATS['failed']
		
	
def parse_options(argv = None):
	global OPTIONS

	if argv is None:
		argv = sys.argv[1:]
		
	(opts, argv) = getopt(argv, "c:vCn:d", ['conf', 'verbose', 'cautious', 'num-entries','no-download'])
	for (key,val) in opts:
		if key == '-v' or key == '--verbose':
			OPTIONS['verbose'] = True
			debug("Verbose mode enabled...")
		elif key == '-c' or key == '--config-file':
			OPTIONS['user_config_file'] = val
		elif key == '-C' or key == '--cautious':
			OPTIONS['cautious'] = True
			OPTIONS['verbose']  = True
			print "Cautious mode enabled..."
		elif key == '-n' or key == '--num-feeds':
			OPTIONS['num_items'] = int(val)
			print "Number of items set to %s" % OPTIONS['num_items']
		elif key == '-d' or key == '--no-download':
			OPTIONS['no_download'] = True
			print "Downloading turned off.."

	
	if len(argv) > 0:
		OPTIONS['num_items'] = argv[0]
		print "Number of items set to %s" % OPTIONS['num_items']

def reader_login():
	global READER, OPTIONS
	READER = GoogleReader()
	READER.identify(OPTIONS['user'], OPTIONS['password'])
	
	if not READER.login():
		raise Exception("Login failed")


def execute():
	global READER, OPTIONS, db
	
	reader_login()

	line()
	db = DB()
	db.sync_to_google()

	if OPTIONS['no_download']:
		print "not downloading any new items..."
	else:
		download_new_items()
	db.save()

def load_config(filename = None):
	global OPTIONS
	if filename is None:
		filename = CONFIG['user_config_file']
	
	print "Loading configuration from %s" % filename
	
	f = file(filename,'r')
	conf = yaml.load(f)
	
	# whitelist of keys we accept
	optional_keys = ['num_items','output_path']
	required_keys = ['user','password', 'tag_list']
	for key,val in conf.items():
		if key in required_keys or key in optional_keys:
			OPTIONS[key] = val
	
	for k in required_keys:
		if not k in OPTIONS:
			raise "Required setting \"%s\" is not set (in %s)." % (k, filename)

def main():
	parse_options()
	load_config()
	execute()

if __name__ == '__main__':
	sys.exit(main())