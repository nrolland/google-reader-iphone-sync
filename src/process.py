from lib.BeautifulSoup import BeautifulSoup, Tag
import urllib2, re, os
from misc import *
from output import *

# don't bother downloading images smaller than this
MIN_IMAGE_BYTES = 512


image_extensions = ['jpg','jpeg','gif','png','bmp', 'tif','tiff']

def is_image(url):
	filetype = url.split('.')[-1].lower()
	if filetype not in image_extensions:
		return False
	return True

## processing modules:
def insert_alt_text(soup):
	"""
	insert bolded image title text after any image on the page
		>>> soup = BeautifulSoup('<p><img src="blah" title="some texts" /></p>')
		>>> insert_alt_text(soup)
		True
		>>> soup
		<p><img src="blah" title="some texts" /><p><b>(&nbsp;some texts&nbsp;)</b></p></p>
	"""
	images = soup.findAll('img',{'title':True})
	for img in images:
		title = img['title'].strip()
		if len(title) > 0:
			desc = BeautifulSoup('<p><b>(&nbsp;%s&nbsp;)</b></p>' % title)
			img.append(desc)
	return True

def strip_params_from_image_url(url):
	"""
	returns the url without query parameters, but only if the url location ends in a known image extension
	
		>>> strip_params_from_image_url('abc/de?x=y')
		'abc/de?x=y'
		>>> strip_params_from_image_url('abc/de.JPG?x=y')
		'abc/de.JPG'
		>>> strip_params_from_image_url('abc')
		'abc'
	"""
	if not '?' in url: return url
	location = url.split('?')[0]
	if is_image(location): return location
	return url

def insert_enclosure_images(soup, url_list):
	"""
	Insert a set of images (url_list) into the soup as html tags.
	A <br /> tag will be inserted before each added image.
	
	Images from the content will not be duplicated.
	If an image URL ends in a known image format (eg ".jpg"), query parameters will be stripped off when comparing URLs
	NOTE: no attempt is made to compare absolute / canonical URLs (it's just a string comparison)

	
		>>> from lib.mock import Mock
		>>> ensure_dir_exists = Mock()
		>>> import process
		>>> process.download_file = Mock()
		>>> process.download_file.return_value = "image.jpg"
		
		>>> soup = BeautifulSoup('<p>some text is here</p>')
		>>> insert_enclosure_images(soup, ['http://example.com/image.jpg', 'not-an-image.txt'])
		True
		>>> soup
		<p>some text is here</p><br /><img src="http://example.com/image.jpg" />

		>>> soup = BeautifulSoup('what about without a root element?')
		>>> insert_enclosure_images(soup, ['http://example.com/image.jpg', 'another-image.gif'])
		True
		>>> soup
		what about without a root element?<br /><img src="http://example.com/image.jpg" /><br /><img src="another-image.gif" />
		
		>>> soup = BeautifulSoup('<img src="a.gif" />')
		>>> insert_enclosure_images(soup, ['b.jpg', 'a.gif'])
		True
		>>> soup
		<img src="a.gif" /><br /><img src="b.jpg" />
		
		>>> soup = BeautifulSoup('<img src="a.gif?query=foo" />')
		>>> insert_enclosure_images(soup, ['a.gif?query=bar'])
		True
		>>> soup
		<img src="a.gif?query=foo" />

		>>> soup = BeautifulSoup('<img src="a?query=foo" />')
		>>> insert_enclosure_images(soup, ['a?query=bar'])
		True
		>>> soup
		<img src="a?query=foo" /><br /><img src="a?query=bar" />

	"""
	existing_image_urls = []
	for existing_image in soup.findAll('img'):
		try:
			existing_image_urls.append(strip_params_from_image_url(existing_image['src']))
		except KeyError: pass
	
	for image_url in [url for url in url_list if strip_params_from_image_url(url) not in existing_image_urls and is_image(url)]:
		img = Tag(soup, 'img')
		img['src'] = image_url
		soup.append(Tag(soup, 'br'))
		soup.append(img)
	return True
	

def download_images(soup, dest_folder, href_prefix, base_href = None):
	"""
	Download all referenced images to the {dest} folder
	Replace href attributes with {href_prefix}/output_filename
	
		>>> from lib.mock import Mock
		>>> ensure_dir_exists = Mock()
		>>> import process
		>>> process.download_file = Mock()
		>>> process.download_file.return_value = "image.jpg"
		
		>>> soup = BeautifulSoup('<img src="http://google.com/image.jpg?a=b&c=d"/>')
		>>> download_images(soup, 'dest_folder', 'local_folder/')
		True
		>>> soup
		<img src="local_folder/image.jpg" />
	
		# (make sure the file was downloaded from the correct URL:)
		>>> process.download_file.call_args
		((u'http://google.com/image.jpg?a=b&c=d', 'image.jpg'), {'base_path': 'dest_folder'})
	"""
	images = soup.findAll('img',{'src':True})
	success = True
	
	if len(images) > 0:
		ensure_dir_exists(dest_folder)
	for img in images:
		href = absolute_url(img['src'], base_href)
		
		filename = get_filename(img['src'])
		try:
			filename = download_file(href, filename, base_path=dest_folder)
			if filename is not None:
				img['src'] = urllib2.quote(href_prefix + filename)
		except StandardError, e:
			info("Image %s failed to download: %s" % (img['src'], e))
			success = False
	
	return success



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
		>>> absolute_url('abcd','http://google.com/stuff/folder/')
		'http://google.com/stuff/folder/abcd'
		>>> absolute_url('/abcd','http://google.com/stuff/file')
		'http://google.com/abcd'
	"""
	if re.match('[a-zA-Z]+://', url):
		return url
	
	if base is None:
		raise ValueError("No base given, and \"%s\" is a relative URL!" % url)
	if re.match('/', url):
		protocol, path = base.split('://',1)
		server = path.split('/',1)[0]
		return protocol + '://' + server + url
	if not base[-1] == '/':
		# base is not a directory - so grab everything before the last slash:
		base = url_dirname(base)
	return base + url

def get_filename(url):
	""" TODO: doctests """
	url = url.split('?',1)[0] # chomp query strings
	url = url.split('/')[-1]
	return urllib2.quote(url)

def unique_filename(output_filename, base_path=None):
	"""
	get the next filename for a pattern that doesn't already exist

		>>> base='/tmp/filetest/'
		>>> rm_rf(base)
		>>> unique_filename(base+'filename.x.txt')
		'/tmp/filetest/filename.x.txt'
		>>> touch_file(_)
		>>> unique_filename(base+'filename.x.txt')
		'/tmp/filetest/filename.x-2.txt'
		>>> touch_file(_)
		>>> touch_file('/tmp/filetest/filename.x-3.txt')
		
	use a base_path to specify a full path for file-checking purposes,
	but which isn't included in the return value
	
		>>> unique_filename('filename.x.txt', base)
		'filename.x-4.txt'
	"""
	i = 2
	base, ext = os.path.splitext(output_filename)
	while os.path.exists(os.path.join(base_path, output_filename) if base_path else output_filename):
		output_filename = "%s-%s%s" % (base, i, ext)
		i += 1
	return output_filename


import socket
def download_file(url, output_filename=None, base_path='', allow_overwrite=False):
	"""
	Download an arbitrary URL. If output_filename is given, contents are written a file that looks a lot like output_filename.
	If output_filename does not contain an extension matching the file's reported mime-type, such an extension will be added.
	If allow_overwrite is set to true, this function will overwrite any existing file at output_filename.
	Otherwise, it will find a unique filename to create using the pattern <base>-n.<ext> for n in 2 ... inf
	
	Files are only downloaded if their mime-type is "image/x" where x is in the image_extensions list.
	
	Returns: - The filename that contents were written to.
	         - The contents of the file as a string if output_filename is not given
	         - None if the file was not downloaded (because its type is not in image_extensions)
	"""
	# timeout in seconds
	socket.setdefaulttimeout(20)

	dl = urllib2.urlopen(url)
	headers = dl.headers

	filetype = None

	try:
		if headers.getmaintype().lower() == 'image':
			filetype = headers.subtype
	except StandardError: pass
	
	try:
		if int(headers['Content-Length']) < MIN_IMAGE_BYTES:
			debug("not downloading image - it's only %s bytes long" % headers['Content-Length'])
			dl.close()
			return None
	except StandardError: pass
	
	if filetype is None:
		filetype = output_filename.split('.')[-1].lower()
	
	if filetype not in image_extensions:
		debug("not downloading image of type: %s" % filetype)
		dl.close()
		return None
	
	if not output_filename.lower().endswith('.' + filetype):
		output_filename += '.' + filetype
	
	if not allow_overwrite:
		output_filename = unique_filename(output_filename, base_path=base_path)

	debug("downloading file: " + url)
	contents = dl.read()
	dl.close()

	if output_filename is not None:
		full_path = os.path.join(base_path, output_filename) if base_path else output_filename
		out = open(full_path,'w')
		out.write(contents)
		return output_filename
	else:
		return contents
