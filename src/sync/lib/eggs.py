import sys, os, re

for file_ in os.listdir(os.path.dirname(__file__)):
	if re.search('.egg$', file_, re.IGNORECASE):
		sys.path.insert(0, os.path.join(os.path.dirname(__file__), file_))
