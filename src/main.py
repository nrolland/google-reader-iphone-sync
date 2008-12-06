#!/usr/bin/env python
# general includes
import sys, glob, urllib2, signal, os, commands

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
from thread_pool import ThreadPool

TASK_PROGRESS = 0
def new_task(description=""):
	global TASK_PROGRESS
	status("TASK_PROGRESS", TASK_PROGRESS, description)
	TASK_PROGRESS += 1

def handle_signal(signum, stack):
	debug("Signal caught: %s" % (signum,))
	status("TASK_PROGRESS", TASK_PROGRESS, "Cancelled")
	cleanup()
	
def cleanup():
	if app_globals.DATABASE is not None:
		app_globals.DATABASE.close()
	log_end()
	
def init_signals():
	signal.signal(signal.SIGINT, handle_signal)
	signal.signal(signal.SIGTERM, handle_signal)

def save_db_state():
	puts("saving database state...")
	app_globals.DATABASE.close()
	app_globals.DATABASE = DB()

def execute():
	"""
	Logs in, syncs and downloads new items
	"""
	steps = 3
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
	
	# we now have something we need to clean up on interrupt:
	init_signals()
	
	app_globals.DATABASE.sync_to_google()
	
	if app_globals.OPTIONS['no_download']:
		info("not downloading any new items...")
	else:
#		retry_failed_items() # TODO: Re-enable this
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
	item_thread_pool = ThreadPool()
	for entry in feed.get_entries():
		item_number += 1
		status("SUBTASK_PROGRESS", item_number)
	
		app_globals.STATS['items'] += 1

		if entry is None:
			app_globals.STATS['failed'] += 1
			puts(" ** FAILED **")
			debug("(entry is None)")
			continue
		
		debug_verbose(entry.__repr__())
		item = Item(entry, feed_tag)
		process_item(item, item_thread_pool)
		item_thread_pool.collect()
	item_thread_pool.collect_all()

def error_reporter_for_item(item):
	def error_report(exception):
		puts(" ** FAILED **: " + str(exception))
		log_error("Failed processing item: %s" % repr(item), exception)
		if in_debug_mode():
			raise exception
		app_globals.STATS['failed'] += 1
	return error_report

def process_item(item, item_thread_pool = None):
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
			app_globals.STATS['new'] += 1
			if item_thread_pool is None:
				item.process()
				item.save()
			else:
				item_thread_pool.spawn(item.process, on_success = item.save, on_error = error_reporter_for_item(item))

		except StandardError,e:
			error_reporter_for_item(item)(e)
		
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
		save_db_state()
		_feed_tag = "All Items" if feed_tag is None else feed_tag
		new_task("Downloading tag \"%s\"" % (_feed_tag,))
		puts("Fetching maximum %s items from feed %s" % (app_globals.OPTIONS['num_items'], _feed_tag))
		feed = app_globals.READER.get_tag_feed(feed_tag, oldest_first = not app_globals.OPTIONS['newest_first'])
		download_feed(feed, _feed_tag)
		
	line()
	
	info("%s NEW items" % app_globals.STATS['new'])
	info("%s items marked as read" % app_globals.STATS['read'])
	if app_globals.STATS['failed'] > 0:
		puts("%s items failed to parse" % app_globals.STATS['failed'])

def ensure_singleton_process():
	"""
	ensure only one sync process is ever running.
	if --aggressive is given as a flag, this process will kill the existing one
	otherwise, it will exit when there is already a process running
	"""
	filename = "%s/sync.pid" % (app_globals.OPTIONS['output_path'],)
	try:
		pid = int(read_file(filename).strip())
	except (IOError, ValueError):
		write_pid_file(filename)
		return
	
	if pid == os.getpid():
		# it's me! it must have been stale, and happened to be reused. we don't want to kill it
		return
	
	status, output = commands.getstatusoutput("ps ux | grep -v grep | grep 'python.*GRiS' | awk '{print $2}'") # classy!
	if output.endswith("Operation not permitted"):
		# this is hopefully just on the simulator
		puts("Error fetching running pids: %s" % (output,))
		puts(" - This is known to happen on the iphone simulator.")
		puts(" - if you see it on a real device, please file a bug report")
		status, output = (0, '') # lets just pretend it worked, and everything is fine
	if status != 0:
		puts("could not execute pid-checking command. got status of %s, output:\n%s" % (status, output))
		sys.exit(2)
	
	running_pids = output.split()
	try:
		running_pids = [int(x) for x in running_pids if len(x) > 0]
	except ValueError:
		puts("one or more pids could not be converted to an integer: %r" % (running_pids,))
		sys.exit(2)
	
	if pid in running_pids:
		if not app_globals.OPTIONS['aggressive']:
			puts("There is already a sync process running, pid=%s" % (pid,))
			sys.exit(2)
		else:
			try:
				debug("killing PID %s " %(pid,))
				os.kill(pid, signal.SIGKILL)
			except OSError, e:
				msg = "couldn't kill pid %s - %s" % (pid,e)
				puts(msg)
				sys.exit(2)
	# if we haven't exited by now, we're the new running pid!
	write_pid_file(filename)

def write_pid_file(filename):
	write_file(filename, str(os.getpid()))

def setup(opts=None):
	"""Parse options. If none given, opts is set to sys.argv"""
	if opts is None:
		opts = sys.argv[1:]
	config.bootstrap(opts)
	config.load()
	config.parse_options(opts)
	ensure_dir_exists(app_globals.OPTIONS['output_path'])
	log_start()
	ensure_singleton_process()
	config.check()
	init_signals()

def main():
	"""
	Main program entry point - loads config, parses otions and kicks off the sync process
	"""
	setup()
	execute()
	puts("Sync complete. cleaning up")
	cleanup()
	print "Sync complete."
	return 0

if __name__ == '__main__':
	sys.exit(main())
