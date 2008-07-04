import cgi, os, re, urllib2, sys
import cgitb; cgitb.enable()
from static import header, footer

form = cgi.FieldStorage()


def env(key):
	try:
		return os.environ[key]
	except:
		return None

content = []
def output(s):
	if len(content) == 0:
		content.append("Content-type: text/html\n\n")
	content.append(s)
	
	
def slashify_dbl_quotes(u):
	return re.sub('\"','\\\\\"', re.sub('\\\\','\\\\\\\\',u))
	
def slashify_all_quotes(u):
	return re.sub('\'','\\\\\'', slashify_dbl_quotes(u))

def html_attr(s):
	return cgi.escape(s)

def url_safe(u):
	return urllib2.quote(u)

def url_in_html(u):
	return html_attr(url_safe(u))

def redirect(url):
	print "location: " + url_safe(url) + "\n\n"
	sys.exit(0)

rel_path = form.getfirst('path','')
request_uri = env('REQUEST_URI')
if '?' in request_uri:
	request_uri = request_uri.split('?',1)[0]
# split (& clean) the request_URI
request_uri_parts = [x for x in request_uri.split('/') if len(x) > 1 and any([char != '.' for char in x])]
request_uri = '/' + '/'.join(request_uri_parts)

# get the whole path, including document_root
path = env('DOCUMENT_ROOT') + request_uri
path_parts = path.split('/')

# directory path
dir_path = path_parts[:-1]

http_ref = env('HTTP_REFERER')
if http_ref is not None:
	http_ref = re.sub('\?|#.*$','', http_ref)
	http_ref_file = urllib2.unquote(http_ref).split('/')[-1]

# gotta have an action (default is "show")
action = form.getfirst('action')
if action is None:
	action = 'show'

def file_list(path):
	try:
		# strip out any dotfiles
		return [x for x in os.listdir(path) if x[0] != '.']
	except:
		return []

# now process all the action types
if action == 'show':
	title_link_parts = ['<a href="/">root</a>']
	for i in range(0, len(request_uri_parts)):
		title_link_parts.append('<a href="' + url_in_html('/'.join(request_uri_parts[:i+1])) + '">' + request_uri_parts[i] + '</a>')
	title_link = "&nbsp;/&nbsp;".join(title_link_parts)
	
	output(header(dir_path[-1], title_link))

	for f in file_list(path):
		if f[0] == '.':
			continue
		output('<div>')
		url = url_in_html(f)
		# strip out ugly datestamps & google-reader tags
		display_file = re.sub('^[^ ]* ','', re.sub(' \.\|\|.*$','',f))
		if os.path.isdir(path + f):
			output('<a href="' + url + '" ><li>' + display_file + '</li></a>')
		else:
			output('<a onclick="delete_fn(\'' + slashify_all_quotes(url) + '\', this);" class="del button">&ndash;</a>')
			output('<a href="' + url + '" ><li class="dir">' + display_file + '</li></a>')
		output('</div>')
	output('</ul>')
	output(footer)
		
elif action == 'delete' or action == 'delete_ref':
	filename =  form.getfirst('file','') if action == 'delete' else http_ref_file
	filename = '/' + filename.split('/')[-1]
	if not os.path.isfile(path + filename):
		output("file does not exist: " + path + filename)
	else:
		os.remove(path + filename)
		# continue on!
		action = 'next'
	
if action == 'next' or action == 'prev':
	offset = 1 if action == 'next' else -1
	files = file_list(path)
	try:
		current_file = http_ref_file
		current_pos = files.index(current_file)
		new_pos = current_pos + offset
		if new_pos < 0 or new_pos >= len(files) or (not os.path.isfile(path + '/' + files[new_pos])):
			# we're out of bounds, or we hit a directory - just show the index
			redirect("./")
		else:
			redirect(files[new_pos])
	except:
		output("sorry, couldn't find the next file")


for line in content:
	print line

# test / debug stuff:
#print "<hr />"; cgi.test()
