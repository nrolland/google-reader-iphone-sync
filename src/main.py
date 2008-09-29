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
from reader import Reader

TASK_PROGRESS = 0
def new_task(description=""):
	global TASK_PROGRESS
	status("TASK_PROGRESS", TASK_PROGRESS, description)
	TASK_PROGRESS += 1

def execute():
	"""
	Logs in, syncs and downloads new items
	"""
	steps = 4
	download_steps = 0
	if not app_globals.OPTIONS['no_download']:
		download_steps = len(app_globals.OPTIONS['tag_list'])
		if download_steps < 1: download_steps = 1
		steps += download_steps
	
	status("TASK_TOTAL",steps)
	new_task("Authorizing")
	
	ensure_dir_exists(app_globals.OPTIONS['output_path'])
	ensure_dir_exists(app_globals.OPTIONS['output_path'] + '/' + app_globals.CONFIG['resources_path'])
	
	app_globals.READER = Reader()
	app_globals.READER.save_tag_list()
	if app_globals.OPTIONS['tag_list_only']:
		info("Got all tags.")
		return

	app_globals.READER.validate_tag_list()

	new_task("Pushing status to google")

	line()
	app_globals.DATABASE = DB()
	app_globals.DATABASE.sync_to_google()
	
	if app_globals.OPTIONS['no_download']:
		info("not downloading any new items...")
	else:
		app_globals.DATABASE.prepare_for_download()
		download_new_items()
		new_task("Cleaning up old resources")
		app_globals.DATABASE.cleanup() # remove old _resources files

def retry_failed_items():
	new_task("Re-trying failed image downloads")
	for item in app_globals.DATABASE.get_items_that_had_errors():
		info("trying to re-download images for item: %s" % (item['title'],))
		item.download_images()
		item.save()

def download_feed(feed, feed_tag):
	item_number = 0
	status("SUBTASK_TOTAL", len(feed))
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
		process_item(item)

def process_item(item):
	state = app_globals.DATABASE.is_read(item.google_id)
	name = item.basename
	
	item_is_read = state is True or item.is_read
	if item_is_read:
		# item has been read either online or offline
		puts("READ: " + name)
		app_globals.STATS['read'] += 1
		danger("About to delete item")
		item.delete()

	already_seen = state is not None

	if already_seen:
		# we've already downloaded it
		app_globals.DATABASE.update_feed_for_item(item)
	else:
		try:
			puts("NEW: " + item.title)
			danger("About to output item")
			item.process()
			item.save()
			app_globals.STATS['new'] += 1
		except KeyboardInterrupt: raise
		except Exception,e:
			puts(" ** FAILED **: " + str(e))
			log_error("Failed processing item: %s" % repr(item), e)
			if in_debug_mode():
				raise
			app_globals.STATS['failed'] += 1
		
def download_new_items():
	"""
	Downloads new items from google reader across all feeds
	"""
	tag_list = app_globals.OPTIONS['tag_list']

	# special case: no tags specified so we download the global set
	if len(tag_list) == 0:
		tag_list = [None]
	
	status("SUBTASK_TOTAL", len(tag_list) * app_globals.OPTIONS['num_items'])

	for feed_tag in tag_list:
		line()
		_feed_tag = "[all items]" if feed_tag is None else feed_tag
		new_task("Downloading tag \"%s\"" % (_feed_tag,))
		puts("Fetching maximum %s items from feed %s" % (app_globals.OPTIONS['num_items'], _feed_tag))
		feed = app_globals.READER.get_tag_feed(feed_tag, oldest_first = app_globals.OPTIONS['newest_first'])
		download_feed(feed, _feed_tag)
		
	line()
	
	info("%s NEW items" % app_globals.STATS['new'])
	info("%s items marked as read" % app_globals.STATS['read'])
	if app_globals.STATS['failed'] > 0:
		puts("%s items failed to parse" % app_globals.STATS['failed'])


def setup(opts=None):
	if opts is None:
		opts = sys.argv[1:]
	config.bootstrap(opts)
	config.load()
	config.parse_options(opts)
	ensure_dir_exists(app_globals.OPTIONS['output_path'])
	log_start()
	config.check()

def main():
	"""
	Main program entry point - loads config, parses otions and kicks off the sync process
	"""
	setup()
	retval = 0
	try:
		execute()
		puts("Sync complete.")
	except KeyboardInterrupt:
		puts("Sync interrupted")
		status("Cancelled")
		retval = 1
	finally:
		app_globals.DATABASE.close()
		log_end()
	return retval


if __name__ == '__main__':
	sys.exit(main())
