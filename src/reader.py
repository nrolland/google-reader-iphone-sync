from misc import *
from output import *
import app_globals
from lib.GoogleReader import GoogleReader, CONST
import os

class ReaderError(StandardError):
	pass

class Reader:
	def __init__(self, user=None, password=None):
		if app_globals.OPTIONS['test']:
			from lib.mock import Mock
			debug("WARNING: using a mock google reader object")
			self.gr = Mock()
		else:
			self.gr = GoogleReader()
			self.login(user, password)

		self._tag_list = None

	def login(self, user=None, password=None):
		if user is None:
			user = app_globals.OPTIONS['user']
		if password is None:
			password = app_globals.OPTIONS['password']
		self.gr.identify(user, password)
		try:
			if not self.gr.login():
				raise RuntimeError("Login failed")
		except StandardError:
			raise RuntimeError("Login failed")
		
	def get_tag_list(self):
		if self._tag_list is None:
			tag_list = self.gr.get_tag_list()['tags']
			self._tag_list = [tag['id'].split('/')[-1] for tag in tag_list if '/label/' in tag['id']]
		return self._tag_list
	tag_list = property(get_tag_list)
		
	def validate_tag_list(self, user_tags = None):
		"""
		Raise an error if any tag (in config) does not exist in your google account
		"""
		if user_tags is None:
			user_tags = app_globals.OPTIONS['tag_list']
		for utag in user_tags:
			if utag not in self.tag_list:
				print "Valid tags are: %s" %(self.tag_list,)
				raise ValueError("No such tag: %r" % (utag,))

	def save_tag_list(self):
		write_file_lines(os.path.join(app_globals.OPTIONS['output_path'], 'tag_list'), self.tag_list)

	def get_tag_feed(self, tag = None, count=None, oldest_first = True):
		if tag is not None:
			tag = CONST.ATOM_PREFIXE_LABEL + tag
		kwargs = {'exclude_target': CONST.ATOM_STATE_READ}
		if oldest_first:
			kwargs['order'] = CONST.ORDER_REVERSE

		if count is None:
			count = app_globals.OPTIONS['num_items']

		return self.gr.get_feed(None, tag, count=count, **kwargs)
		
	# pass-through methods
	def passthrough(f):
		def pass_func(self, *args, **kwargs):
			return getattr(self.gr, f.__name__)(*args, **kwargs)
		return pass_func
	
	def passthrough_and_check(f):
		def pass_func(self, *args, **kwargs):
			result = getattr(self.gr, f.__name__)(*args, **kwargs)
			if result != 'OK':
				raise ReaderError("Result (%s) is not 'OK'" % (result,))
		pass_func.__name__ = f.__name__
		return pass_func
	
	@passthrough_and_check
	def set_read(): pass

	@passthrough_and_check
	def set_unread(): pass
	
	@passthrough_and_check
	def add_star(): pass
	
	@passthrough_and_check
	def del_star(): pass
	
	@passthrough_and_check
	def add_public(): pass
	
	@passthrough_and_check
	def del_public(): pass
	
	@passthrough
	def get_feed(): pass