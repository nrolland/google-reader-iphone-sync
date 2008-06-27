# These are some defaults. They get overrided / extended by config.py

CONFIG = {
	'pickle_file': '.entries.pickle',
	'user_config_file': 'config.yml',
	'test_output_dir': 'test_entries',
}

OPTIONS = {
	'output_path': 'entries',
	'num_items':    300,
	'no_download':  False,
	'verbose':      False,
	'cautious':     False,
	'test':         False
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

