from misc import *
import app_globals
import re

import pdb

def update(obj, input_filename, output_filename = None, restrict_to=None):
	if output_filename is None:
		output_filename = input_filename
	_process(obj, input_filename, output_filename, restrict_to)
	
def create(obj, input_filename, output_filename = None, restrict_to=None):
	if output_filename is None:
		outut_filename = input_filename + ".html"
	_process(obj, input_filename, output_filename, restrict_to)

def get_str(obj):
	"""
	Get a string value from an arbitrary object.
	If it's callable, try to call it. If that fails, just convert it to a string.
	"""
	if obj is None:
		return ""
	try:
		res = str(obj())
	except Exception:
 		res = str(obj)
	return res

def process_string(subject_str, obj, restrict_to = None):
	"""
	Replaces {variable} substitutions that are within HTML comments.
	The replacement includes html-comment markers so that the value can be replaced / updated if desired.

	>>> process_string("<!--{content}-->", {'content':"la la la"})
	"<!--{content=}-->la la la<!--{=content}-->"

	>>> process_string("<!-- #{content=} -->previous\ncontent<!-- #{=content} -->", {'content':"new value"})
	"<!--{content=}-->new value<!--{=content} -->"

	# the restrict_to argument limits the set of keys that will be interpreted:
	>>> process_string("<!--{content}-->", {'content':"new value"}, ['other_key'])
	"<!--{content}-->"
	>>>
	"""
	# do expanded first, otherwise you'll expand it and match it again with expanded_re!
	for matcher_func in (_expanded_regex, _unexpanded_regex):
		matcher = matcher_func() # evaluate it
		matches = matcher.finditer(subject_str)
		for match in matches:
			object_property = match.groupdict()['tag']
			debug("object property: " + object_property)
			if (restrict_to is None or object_property in restrict_to):
				attr = get_attribute(obj, object_property)
				if attr is not None:
					# do the replacement!
					debug("substituting property: " + object_property)
					replacement_matcher = matcher_func(object_property)
					subject_str = replacement_matcher.sub('<!--{\g<tag>=}-->' + get_str(attr) + '<!--{=\g<tag>}-->', subject_str)
				else:
					debug("object does not respond to " + object_property)
				
	return subject_str

default_tagex = '[a-zA-Z0-9_]+'
def _unexpanded_regex(tagex = None):
	global default_tagex
	if tagex is None:
		tagex = default_tagex
	return re.compile('<!--\{(?P<tag>' + tagex + ')\}-->')

def _expanded_regex(tagex = None):
	global default_tagex
	if tagex is None:
		tagex = default_tagex
	return re.compile('<!--\{(?P<tag>' + tagex + ')=\}-->.*?<!--\{=(?P=tag)\}-->', re.DOTALL) # the dot can match newlines


####################################################################################
# internal methods only below - use the above methods to interact with this module #
####################################################################################

def _process(obj, input_filename, output_filename, restrict_to):
	infile = file(input_filename, 'r')
	contents = infile.read()
	contents = process_string(contents, obj, restrict_to)
	infile.close()
	outfile = file(output_filename, 'w')
	outfile.write(contents)


def get_attribute(obj, attr):
	"""
	Much like the built-in getattr, except:
	 - it returns None on failure
	 - it tries dictionary lookups if no attribute is found
	"""
	
	ret = None
	try:
		ret = getattr(obj, attr)
	except Exception:
		try:
			ret = obj[attr]
		except Exception:
			pass
	return ret


if __name__ == '__main__':
	app_globals.OPTIONS['verbose'] = True
	# just print out some 
	print _process_string("<!--{content}-->", {'content':"la la la"})
	print "\n\n"
	print _process_string("<!-- #{content=} -->previous\ncontent<!-- #{=content} -->", {'content':"new value"})
