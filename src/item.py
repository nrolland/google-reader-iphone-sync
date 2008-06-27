"""
Exports:
Item class
"""
import glob, time, os, re, urllib

# local imports
import app_globals
from misc import *

# processing modules
from lib.BeautifulSoup import BeautifulSoup
from process import insert_alt_text


def remove_the_damn_html_entities(s):
	return re.sub('&.{2,4};','',s)

def esc(s):   return urllib.quote(string)
def unesc(s): return urllib.unquote(s)

"""
Encode string in ASCII
"""	
def ascii(s):
	return s.encode('ascii','ignore')

"""
encode string in utf-8
"""
def e(s):
	return s.encode('utf-8','ignore') if isinstance(s, unicode) else s

"""
make an HTML tag
eg:

>>> tag("br")
"<br />"
>>> tag("p", content="blah", attrs={"class": "highlight"}
"<p class="highlight">blah</p>"
"""
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
		self.item['soup'] = BeautifulSoup(self.item['content'])
		self.item = insert_alt_text(self.item)
		self.item['content'] = self.item['soup'].prettify()
	
	def output(self):
		base = app_globals.OPTIONS['output_path'] + '/' + self.basename()
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
			cmd = 'python src/html2pdf.py ' + \
				'-w ' + str(int(app_globals.OPTIONS['screen_width'])) + \
				' -h '+ str(int(app_globals.OPTIONS['screen_height'])) + \
				' "' + base + '.html" "'+ base +'.pdf"'
			debug("command: " + cmd)
			# i like to shell out for this, because sometimes it segfaults. I guess pyObjC isn't 100% stable...
			ret = os.system(cmd)
			debug("command returned: " + str(ret))
			if ret == 0:
				app_globals.DATABASE.add_item(self)
			else:
				print "pdf conversion failed"
		finally:
			os.remove(base + '.html')
	
	def is_read(self):
		return 'read' in self.item['categories']
	
	def delete(self):
		for f in glob.glob(app_globals.OPTIONS['output_path'] + '/*.' + self.key() + '.*'):
			print "Removing file: " + f
			danger('remove file')
			os.remove(f)
