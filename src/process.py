from lib.BeautifulSoup import BeautifulSoup
import urllib2, re, os
from misc import *
from output import *

## processing modules:
def insert_alt_text(soup):
	"""
	insert bolded image title text after any image on the page
	
		>>> insert_alt_text( BeautifulSoup('<p><img src="blah" title="some texts" /></p>') )
		<p><img src="blah" title="some texts" /><p><b>( some texts )</b></p></p>
	"""
	images = soup.findAll('img',{'title':True})
	for img in images:
		desc = BeautifulSoup('<p><b>( %s )</b></p>' % img['title'])
		img.append(desc)
	return soup

def download_images(soup, dest_folder, href_prefix, base_href = None):
	"""
	Download all referenced images to the {dest} folder
	Replace href attributes with {href_prefix}/output_filename
	
		>>> from lib.mock import Mock
		>>> ensure_dir_exists = Mock()
		>>> import process
		>>> process.download_file = Mock()

		>>> soup = BeautifulSoup('<img src="http://google.com/image.jpg?a=b&c=d"/>')
		>>> download_images(soup, 'dest_folder', 'local_folder/')
		<img src="local_folder/image.jpg" />
	
		# (make sure the file was downloaded from the correct URL:)
		>>> process.download_file.call_args
		((u'http://google.com/image.jpg?a=b&c=d', u'dest_folder/image.jpg'), {})
	"""
	images = soup.findAll('img',{'src':True})
	
	if len(images) > 0:
		ensure_dir_exists(dest_folder)
	for img in images:
		debug("Processing image link: " + img['src'])
		href = absolute_url(img['src'], base_href)
		
		filename = get_filename(img['src'])
		output_filename = dest_folder + '/' + filename
		
		i = 2
		while(os.path.exists(output_filename)):
			output_filename = dest_folder + '/' + filename + '-' + str(i)
			i += 1

		try:
			download_file(href, output_filename)
			img['src'] = urllib2.quote(href_prefix + filename)
		except Exception, e:
			info("Image %s failed to download: %s" % (img['src'], e))
	
	return soup



###############################
#   here be helper methods:   #
###############################

def absolute_url(url, base = None):
	"""
	grab the absolute URL of a link that comes from {base}
	
		>>> absolute_url('http://abcd')
		'http://abcd'
		>>> absolute_url('abcd','http://google.com/stuff/file')
		'http://google.com/stuff/abcd'
		>>> absolute_url('abcd','http://google.com/stuff/file/')
		'http://google.com/stuff/file/abcd'
		>>> absolute_url('/abcd','http://google.com/stuff/file')
		'http://google.com/abcd'
	"""
	if re.match('[a-zA-Z]+://', url):
		return url
	
	if base is None:
		raise Exception("No base given, and \"%s\" is a relative URL!" % url)
	if re.match('/', url):
		protocol, path = base.split('://',1)
		server = path.split('/',1)[0]
		return protocol + '://' + server + url
	if not base[-1] == '/':
		# base is not a directory - so grab everything before the last slash:
		base = url_dirname(base)
	return base + url

def get_filename(url):
	url = url.split('?',1)[0]
	try:
		return url.split('/')[-1]
	except:
		return urllib2.escape(url)


import socket

image_extensions = ['jpg','jpeg','gif','png','bmp']

def download_file(url, outfile=None):
	"""
	Download an arbitrary URL. If outfile is given, contents are written to that file.
	If oufile is not given, returns the contents of the file as a string.
	"""
	# timeout in seconds
	socket.setdefaulttimeout(30)

	debug("downloading file: " + url)
	dl = urllib2.urlopen(url)
	headers = dl.headers

	filetype = None

	try:
		if headers.getmaintype().lower() == 'image':
			filetype = headers.subtype
	except: pass

	if filetype is None:
		try: filetype = outfile.split('.')[-1].lower()
		except: pass
	
	if filetype not in image_extensions:
		debug("not downloading image of type: %s" % filetype)
		dl.close()
		return
	
	contents = dl.read()
	dl.close()

	if outfile is not None:
		out = open(outfile,'w')
		out.write(contents)
	else:
		return contents