# These are some defaults and other globals.
# anything in OPTIONS can be overrided / extended by config.py in reaction to command-line or config.yml input

CONFIG = {
	'pickle_file': '.entries.pickle',
	'user_config_file': 'config.yml',
	'test_output_dir': 'test_entries',
	'resources_path': '.resources',
	'convert_to_pdf': False,
}

OPTIONS = {
	'output_path':   'entries',
	'num_items':     300,
	'no_download':   False,
	'verbose':       False,
	'cautious':      False,
	'test':          False,
	'screen_width':  320,
	'screen_height': 480,
	'template_only': False,
}

STATS = {
	'items':  0,
	'failed': 0,
	'new':    0,
	'read':   0,
}

# These ones get set to useful values in main.py

READER = None
DATABASE = None

def file_extension():
	return 'pdf' if CONFIG['convert_to_pdf'] else 'html'
