# These are some defaults and other globals.
# anything in OPTIONS can be overrided / extended by config.py in reaction to command-line or config.yml input

import output

CONFIG = {
	'pickle_file': '.entries.pickle',
	'user_config_file': 'config.yml',
	'test_output_dir': 'test_entries',
	'resources_path': '_resources',
}

OPTIONS = {
	'output_path':   '/tmp/GRiS_test',
	'num_items':     300,
	'no_download':   False,
	'cautious':      False,
	'test':          False,
	'screen_width':  320,
	'screen_height': 480,
	'template_only': False,
	'flush_output':  False,
	'verbosity':     output.lvl_default,
	'tag_list_only': False,
	'newest_first':  False,
	'show_status':   False,
	'aggressive':    False,
	'tag_list':      [],
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

