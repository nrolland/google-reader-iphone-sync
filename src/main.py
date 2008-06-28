#!/usr/bin/env python
# general includes
import sys

# local includes
from config import parse_options, load_config
from db import DB
from item import Item
from misc import *
from lib.GoogleReader import GoogleReader, CONST
import app_globals


def reader_login():
	"""
	Login to google-reader with credentials in OPTIONS.
	Stores the logged-in reader in the global READER variable
	Raises exception if authentication fails
	"""
	app_globals.READER = GoogleReader()
	app_globals.READER.identify(
		app_globals.OPTIONS['user'],
		app_globals.OPTIONS['password'])
	
	if not app_globals.READER.login():
		raise Exception("Login failed")



def execute():
	"""
	Logs in, syncs and downloads new items
	"""
	reader_login()

	line()
	app_globals.DATABASE = DB()
	app_globals.DATABASE.sync_to_google()

	if app_globals.OPTIONS['no_download']:
		print "not downloading any new items..."
	else:
		download_new_items()
	app_globals.DATABASE.save()


def download_new_items():
	"""
	Downloads new items from google reader
	"""
	for feed_tag in app_globals.OPTIONS['tag_list']:
		print "Fetching maximum %s items from feed %s" % (app_globals.OPTIONS['num_items'], feed_tag)
		feed = app_globals.READER.get_feed(None,
			CONST.ATOM_PREFIXE_LABEL + feed_tag,
			count = app_globals.OPTIONS['num_items'],
			exclude_target = CONST.ATOM_STATE_READ,	# get only unread items
			order = CONST.ORDER_REVERSE)			# oldest first
	
		for entry in feed.get_entries():
			debug(" -- %s -- " % app_globals.STATS['items'])
			app_globals.STATS['items'] += 1
		
			if entry is None:
				app_globals.STATS['failed'] += 1
				print " ** FAILED **"
				continue
		
			debug(entry.__repr__())
			debug('-' * 50)
		
			item = Item(entry)
			state = app_globals.DATABASE.is_read(item.key())
			name = item.basename()
		
			if state is None:
				if not item.is_read():
					try:
						print "NEW: " + name
						danger("About to output item")
						item.process()
						item.output()
						app_globals.STATS['new'] += 1
					except Exception,e:
						print " ** FAILED **: " + str(e)
						if app_globals.OPTIONS['verbose']:
							raise
						app_globals.STATS['failed'] += 1
			else:
				if state == True or item.is_read():
					# item has been read either online or offline
					print "READ: " + name
					app_globals.STATS['read'] += 1
					danger("About to delete item")
					item.delete()
		
		line()
	
	print "%s NEW items" % app_globals.STATS['new']
	print "%s items marked as read" % app_globals.STATS['read']
	if app_globals.STATS['failed'] > 0:
		print "(%s items failed to parse)" % app_globals.STATS['failed']


def main():
	"""
	Main program entry point - loads config, parses otions and kicks off the sync process
	"""
	load_config()
	parse_options()
	execute()

if __name__ == '__main__':
	sys.exit(main())
