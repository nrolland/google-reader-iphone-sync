from mocktest import *
import config
import test_helper
from misc import *

import os

class ConfigTest(TestCase):
	def setUp(self):
		self.yaml_file = '/tmp/gris_config.yml'
		self.plist_file = '/tmp/gris_config.plist'
		self.__options = app_globals.OPTIONS.copy()
	
	def rm(self, f):
		try: os.remove(f)
		except OSError: pass
		
	def tearDown(self):
		self.rm(self.yaml_file)
		self.rm(self.plist_file)
		app_globals.OPTIONS = self.__options
		
	def test_should_not_fail_setting_any_options(self):
		for opt in config.all_options[1]:
			opt = '--' + opt
			args = [opt]
			if opt.endswith('='):
				args = [opt[:-1], '123']

			if opt == '--help':
				try: config.bootstrap([opt])
				except SystemExit: pass
				continue
				
			print "bootstrapping with %s" % args
			config.bootstrap(args)
			print "configging with %s" % args
			config.parse_options(args)
		
	def test_should_load_plist(self):
		write_file(self.plist_file, """<?xml version="1.0" encoding="UTF-8"?>
			<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
			<plist version="1.0">
				<dict>
					<key>num_items</key>
					<integer>5</integer>
				</dict> 
			</plist>
			 """)
		config.load(self.plist_file)
		self.assertEqual(config.app_globals.OPTIONS['num_items'], 5) 
		
	def test_should_load_yaml(self):
		write_file(self.yaml_file, "num_items: 1234")
		config.load(self.yaml_file)
		self.assertEqual(config.app_globals.OPTIONS['num_items'], 1234)
	
	def test_should_set_global_options(self):
		config.app_globals.OPTIONS = {'foo':1}
		config.set_opt('foo',2)
		self.assertEqual(config.app_globals.OPTIONS['foo'], 2)

	def test_should_not_set_nonexistant_global_options(self):
		config.app_globals.OPTIONS = {'foo':1}
		config.set_opt('bar',2)
		self.assertFalse('bar' in app_globals.OPTIONS.keys())
		