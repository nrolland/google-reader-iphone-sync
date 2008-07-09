import cgi, os, re, urllib2, sys
import cgitb; cgitb.enable()
from static import header, footer

import helpers
helpers.DEBUG = False
safe_mode = False # safe mode means we don't delete anything
from helpers import *

form = cgi.FieldStorage()
DEBUG = DEBUG or param(form, 'debug', None) is not None
dbg('-'*50)
dbg("FORM:",form)
action = param(form,'action','show')
dbg('ACTION:',action)


def get_nav_file(direction, current_file, path):
	"""
	Get the next/previous file in the given path (directory), relative to the current file name.
	Returns None when there are no more files in the requested direction.
	* direction is 'next' or 'prev'
	"""
	offset = 1 if direction == 'next' else -1
	files = file_list(path)
	try:
		current_pos = files.index(current_file)
	except:
		output(repr(form))
		output("sorry, couldn't find the current file (%s) in this directory" % str(current_file))
		return "./"

	try:
		new_pos = current_pos + offset
		if new_pos < 0 or new_pos >= len(files) or (not os.path.isfile(path + '/' + files[new_pos])):
			# we're out of bounds, or we hit a directory - just show the index
			return "./"
		else:
			return files[new_pos]
	except:
		output("sorry, couldn't find the " + direction + " file from " + str(current_file))
	return "./"

# --------------------------------------------------------------------
# setup globals
rel_path = param(form,'path','')
dbg("rel_path:",rel_path)
request_uri = env('REQUEST_URI')
dbg("request URI:", request_uri)
if '?' in request_uri:
	request_uri = request_uri.split('?',1)[0]
dbg("[trimmed] request URI:", request_uri)

# split (& clean) the request_URI
request_uri_parts = [x for x in request_uri.split('/') if len(x) > 1 and any([char != '.' for char in x])]
request_uri = '/' + '/'.join(request_uri_parts)
dbg("[cleaned] request URI:", request_uri)

# get the whole path, including document_root
path = env('DOCUMENT_ROOT') + request_uri
path_parts = path.split('/')
dbg("PATH:",path)

# directory path
dir_path = path_parts[:-1]

http_ref = env('HTTP_REFERER')
dbg("HTTP_REF:",http_ref)
if http_ref is not None:
	http_ref = re.sub('\?|#.*$','', http_ref)
	http_ref_file = urllib2.unquote(http_ref).split('/')[-1]

dbg("    - - -")

# --------------------------------------------------------------------
# now process all the action types
# why not have a switch statement, python?
if action == 'echo':
	output(urllib2.unquote(form.getfirst('text')))
# --------------------------------------------------------------------
elif action == 'show':
	dbg("show")
	title_link_parts = ['<a href="/">root</a>']
	for i in range(0, len(request_uri_parts)):
		title_link_parts.append('<a href="/' + url_in_html('/'.join(request_uri_parts[:i+1])) + '">' + request_uri_parts[i] + '</a>')
	title_link = "&nbsp;/&nbsp;".join(title_link_parts)
	
	output(header(dir_path[-1], title_link))

	for f in file_list(path):
		if f[0] == '.':
			continue
		output('<div>')
		url = url_in_html(f)
		# strip out ugly datestamps & google-reader tags
		display_file = re.sub('^[-|0-9]* ','', re.sub(' \.\|\|.*$','',f))
		if os.path.isdir(path +'/'+ f):
			output('<a href="' + url + '" class="folder"><li class="folder">')
			output('<img src="/.dirlist/icons/folder.gif" height="15" />')
			output(display_file)
			output('</li></a>')
		else:
			output('<a onclick="delete_fn(\'' + slashify_all_quotes(url) + '\', this);" class="del button">&ndash;</a>')
			output('<a href="' + url + '" ><li>' + display_file + '</li></a>')
		output('</div>')
	output('</ul>')
	output(footer)
# --------------------------------------------------------------------
elif action == 'delete' or action == 'delete_ref':
	dbg("DELETE")
	filename = urllib2.unquote(form.getfirst('file','')) if action == 'delete' else http_ref_file
	filename = filename.split('/')[-1]
	dbg("FILE:",filename)
	if not os.path.isfile(path + '/' + filename):
		output("file does not exist: " + path + '/' + filename)
	else:
		# grab the next file before this one disappears!
		next_file = get_nav_file('next', filename, path)
		if not safe_mode:
			os.remove(path +'/'+ filename)
		if action == 'delete':
			print 'OK'
		else:
			# continue on!
			if next_file is not None:
				redirect(next_file)
# --------------------------------------------------------------------
elif action == 'star_ref':
	dbg("STAR")
	filename = http_ref_file
	filename = filename.split('/')[-1]
	dbg("FILE:",filename)
	
	if not os.path.isfile(path + '/' + filename):
		dbg("No such file.")
		output("file does not exist: " + path + '/' + filename)
	else:
		# flag it for the backend
		append_to_file(path + '/.starred', filename)
		
		# and now for the front-end:
		next_file = get_nav_file('next', filename, path)
		if not safe_mode:
			os.remove(path + '/' + filename)

		# now we send a response
		dbg("SUCCESS!")
		if action == 'star':
			# ajax
			print 'OK'
		else:
			# redirect
			redirect(next_file)
			
# --------------------------------------------------------------------
elif action == 'next' or action == 'prev':
	redirect(get_nav_file(action, http_ref_file, path))
# --------------------------------------------------------------------

dbg('-'*50)

# print any output!
print_content()

# test / debug stuff:
#print "<hr />"; cgi.test()
