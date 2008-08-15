#!/usr/bin/env python
# general includes
import sys, glob, urllib2

# local includes
import config
from db import DB
from item import Item
from misc import *
from output import *
from lib.GoogleReader import GoogleReader, CONST
import app_globals
import template


def reader_login():
	"""
	Login to google-reader with credentials in OPTIONS.
	Stores the logged-in reader in the global READER variable
	Raises exception if authentication fails
	"""
	if app_globals.OPTIONS['test']:
		info("using a mock google reader...")
		return

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
	status("TASK_TOTAL",4)
	status("TASK_PROGRESS", 0, "Authorizing")
	
	ensure_dir_exists(app_globals.OPTIONS['output_path'])
	ensure_dir_exists(app_globals.OPTIONS['output_path'] + '/' + app_globals.CONFIG['resources_path'])

	reader_login()

	status("TASK_PROGRESS", 1, "Syncing to google")

	line()
	app_globals.DATABASE = DB()
	app_globals.DATABASE.sync_to_google()
	app_globals.DATABASE.cleanup() # remove old _resources files
	
	if app_globals.OPTIONS['no_download']:
		info("not downloading any new items...")
	else:
		status("TASK_PROGRESS", 2, "Downloading new items")
		download_new_items()
	app_globals.DATABASE.close()

def retry_failed_items():
	status("TASK_PROGRESS", 3, "Re-trying failed feeds")
	for item in app_globals.DATABASE.get_items_that_had_errors():
		info("trying to re-download images for item: %s" % (item['title'],))
		item.download_images()
		item.save()

def download_new_items():
	"""
	Downloads new items from google reader
	"""
	item_number = 0
	feed_number = 0
	status("SUBTASK_TOTAL", len(app_globals.OPTIONS['tag_list']) * app_globals.OPTIONS['num_items'] * 2)
	for feed_tag in app_globals.OPTIONS['tag_list']:
		puts("Fetching maximum %s items from feed %s" % (app_globals.OPTIONS['num_items'], feed_tag))
		feed_unread_items = app_globals.READER.get_feed(None,
			CONST.ATOM_PREFIXE_LABEL + feed_tag,
			count = app_globals.OPTIONS['num_items'],
			exclude_target = CONST.ATOM_STATE_READ,	# get only unread items
			order = CONST.ORDER_REVERSE)			# oldest first

		feed_read_items = app_globals.READER.get_feed(None,
			CONST.ATOM_PREFIXE_LABEL + feed_tag,
			count = app_globals.OPTIONS['num_items'],
			exclude_target = CONST.ATOM_STATE_UNREAD,	# get only read items
			order = CONST.ORDER_REVERSE)				# newest first

		for feed in [feed_read_items, feed_unread_items]:
			item_number = feed_number * app_globals.OPTIONS['num_items']
			status("SUBTASK_PROGRESS", item_number)
			feed_number += 1

			for entry in feed.get_entries():
				item_number += 1
				status("SUBTASK_PROGRESS", item_number)
			
				debug(" -- %s -- " % app_globals.STATS['items'])
				app_globals.STATS['items'] += 1
		
				if entry is None:
					app_globals.STATS['failed'] += 1
					puts(" ** FAILED **")
					debug("(entry is None)")
					continue
		
				debug_verbose(entry.__repr__())
		
				item = Item(entry, feed_tag)
				state = app_globals.DATABASE.is_read(item.google_id)
				name = item.basename
		
				if state is None:
					if not item.is_read:
						try:
							puts("NEW: " + item.title)
							danger("About to output item")
							item.process()
							item.save()
							app_globals.STATS['new'] += 1
						except Exception,e:
							puts(" ** FAILED **: " + str(e))
							log_error("Failed processing item: %s" % repr(item), e)
							if in_debug_mode():
								raise
							app_globals.STATS['failed'] += 1
				else:
					if state == True or item.is_read:
						# item has been read either online or offline
						pus("READ: " + name)
						app_globals.STATS['read'] += 1
						danger("About to delete item")
						item.delete()
		
		line()
	
	info("%s NEW items" % app_globals.STATS['new'])
	info("%s items marked as read" % app_globals.STATS['read'])
	if app_globals.STATS['failed'] > 0:
		puts("%s items failed to parse" % app_globals.STATS['failed'])


def main():
	"""
	Main program entry point - loads config, parses otions and kicks off the sync process
	"""
	config.bootstrap()
	config.load()
	config.parse_options()
	log_start()
	config.check()
	
	execute()
	puts("Sync complete.")
	log_end()
	return 0


if __name__ == '__main__':
	sys.exit(main())
