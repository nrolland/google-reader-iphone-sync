import cgi, os, re, urllib2, sys

def dbg(*msg):
	global DEBUG
	if DEBUG:
		print " ".join(map(str, msg))

def param(form, key, default=None):
	# Sometimes form.getfirst throws an exception even when you
	# specify a default. That is not what I would expect nor like.
	try:
		return form.getfirst(key, default)
	except:
		return default

def env(key):
	try:
		return os.environ[key]
	except:
		return None

content = []
def output(s):
	global content
	if len(content) == 0:
		content.append("Content-type: text/html\n\n")
	content.append(s)

def print_content():
	for line in content:
		print line


def append_to_file(f, text):
	dbg("appending to file:",f)
	fl = file(f, 'a')
	fl.write(text + '\n')
	fl.close()
	dbg("appending done!")

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

def file_list(path):
	try:
		# strip out any dotfiles
		return [x for x in os.listdir(path) if x[0] != '.']
	except:
		return []
