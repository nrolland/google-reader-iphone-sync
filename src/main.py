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
	
	try:
		if not app_globals.READER.login():
			raise Exception("Login failed")
	except:
		raise Exception("Login failed")



def execute():
	"""
	Logs in, syncs and downloads new items
	"""
	status("TASK_TOTAL",5)
	status("TASK_PROGRESS", 0, "Authorizing")
	
	ensure_dir_exists(app_globals.OPTIONS['output_path'])
	ensure_dir_exists(app_globals.OPTIONS['output_path'] + '/' + app_globals.CONFIG['resources_path'])

	reader_login()
	check_for_valid_tags()

	status("TASK_PROGRESS", 1, "Syncing to google")

	line()
	app_globals.DATABASE = DB()
	app_globals.DATABASE.sync_to_google()
	
	if app_globals.OPTIONS['no_download']:
		info("not downloading any new items...")
	else:
		status("TASK_PROGRESS", 2, "Downloading new items")
		download_new_items()

	status("TASK_PROGRESS", 3, "Cleaning up old resources")
	app_globals.DATABASE.cleanup() # remove old _resources files
	app_globals.DATABASE.close()

def retry_failed_items():
	status("TASK_PROGRESS", 4, "Re-trying failed feeds")
	for item in app_globals.DATABASE.get_items_that_had_errors():
		info("trying to re-download images for item: %s" % (item['title'],))
		item.download_images()
		item.save()

def check_for_valid_tags():
	"""
	Raise an error if any tag (in config) does not exist in your google account
	"""
	user_tags = app_globals.OPTIONS['tag_list']
	google_tags = app_globals.READER.get_tag_list()['tags']
	google_tags = [tag['id'].split('/')[-1] for tag in google_tags]
	for utag in user_tags:
		if utag not in google_tags:
			raise Exception("No such tag: %s" % (utag,))

def get_feed_from_tag(feed_tag):
	if feed_tag is not None:
		feed_tag = CONST.ATOM_PREFIXE_LABEL + feed_tag
	
	return app_globals.READER.get_feed(None,
		feed_tag,
		count = app_globals.OPTIONS['num_items'],
		exclude_target = CONST.ATOM_STATE_READ,	# get only unread items
		order = CONST.ORDER_REVERSE)			# oldest first

first_item = True
def download_feed(feed, feed_tag, feed_number=0):
	global first_item
	item_number = feed_number * app_globals.OPTIONS['num_items']
	status("SUBTASK_PROGRESS", item_number)

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
		
		if first_item:
			info("Deleting items older than %s" % (item.date,))
			app_globals.DATABASE.delete_items_older_than(item)
			first_item = False
		
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

def download_new_items():
	"""
	Downloads new items from google reader across all feeds
	"""
	feed_number = 0
	tag_list = app_globals.OPTIONS['tag_list']

	# special case: no tags specified so we download the global set
	if len(tag_list) == 0:
		tag_list = [None]
	
	status("SUBTASK_TOTAL", len(tag_list) * app_globals.OPTIONS['num_items'])

	
	for feed_tag in tag_list:
		line()
		_feed_tag = "[all items]" if feed_tag is None else feed_tag
		puts("Fetching maximum %s items from feed %s" % (app_globals.OPTIONS['num_items'], _feed_tag))
		feed = get_feed_from_tag(feed_tag)
		download_feed(feed, _feed_tag, feed_number)
		feed_number += 1
		
	line()
	
	info("%s NEW items" % app_globals.STATS['new'])
	info("%s items marked as read" % app_globals.STATS['read'])
	if app_globals.STATS['failed'] > 0:
		puts("%s items failed to parse" % app_globals.STATS['failed'])


def setup():
	config.bootstrap()
	config.load()
	config.parse_options()
	ensure_dir_exists(app_globals.OPTIONS['output_path'])
	log_start()
	config.check()

def main():
	"""
	Main program entry point - loads config, parses otions and kicks off the sync process
	"""
	setup()
	execute()
	puts("Sync complete.")
	log_end()
	return 0


if __name__ == '__main__':
	sys.exit(main())
