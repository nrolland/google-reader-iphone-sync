from lib.BeautifulSoup import BeautifulSoup
import urllib2, re, os
from misc import *

## processing modules:
def insert_alt_text(item):
	"""
	insert bolded image title text after any image on the page
	"""
	soup = item['soup']
	images = soup.findAll('img',{'title':True})
	for img in images:
		desc = BeautifulSoup('<p><b>( %s )</b></p>' % img['title'])
		img.append(desc)
	return item


def download_images(item, dest_folder, href_prefix):
	"""
	Download all referenced images to the {dest} folder
	Replace href attributes with {href_prefix}/output_filename
	"""
	soup = item['soup']
	images = soup.findAll('img',{'src':True})
	try:
		base = item['base']
	except:
		base = None
	if len(images) > 0:
		ensure_dir_exists(dest_folder)
	for img in images:
		debug("Processing image link: " + img['src'])
		href = absolute_url(img['src'], base)
		
		filename = get_filename(href)
		output_filename = dest_folder + '/' + filename
		
		i = 2
		while(os.path.exists(output_filename)):
			output_filename = dest_folder + '/' + filename + '-' + str(i)
			i += 1

		download_file(href, output_filename)
		img['src'] = urllib2.quote(href_prefix + filename)
	return item



###############################
#   here be helper methods:   #
###############################

def absolute_url(url, base = None):
	"""
	grab the absolute URL of a link that comes from {base}
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
# timeout in seconds
socket.setdefaulttimeout(30)

def download_file(url, outfile=None):
	"""
	Download an arbitrary URL. If outfile is given, contents are written to that file.
	If oufile is not given, returns the contents of the file as a string.
	"""
	debug("downloading file: " + url)
	dl = urllib2.urlopen(url)
	contents = dl.read()

	if outfile is not None:
		out = open(outfile,'w')
		out.write(contents)
	else:
		return contents