#!/usr/bin/env python
"""
Usage: py2pdf.py input [output]
OPTIONS:
 -v :     verbose output
 -w :     width of output
 -h :     height of output
"""

from Foundation import *
from PyObjCTools import AppHelper

from ScriptingBridge import SBApplication
import WebKit

from getopt import getopt

import os
import sys
import re

WIDTH = 320
HEIGHT = 480
VERBOSE = False

def debug(s):
	global VERBOSE
	if VERBOSE:
		print ' > ' + str(s)

class WebViewDelegate(NSObject):
	def initWithOutputFile_(self, outfile):
		self.outfile = outfile
		return self
		
	def webView_didFinishLoadForFrame_(self, view, frame):
		if frame != view.mainFrame():
			debug("non-main frame returned from render")
			return
		debug("web view finished loading")
		printWebView(view, self.outfile)
		debug("output file saved")
		AppHelper.stopEventLoop()
	
	def webView_didFailLoadWithError_forFrame_(self, view, err, frame):
		debug("webview load failed: " + str(err))
		AppHelper.stopEventLoop()
		sys.exit(1)


def printWebView(view, outFile):
	webView = view.mainFrame().frameView().documentView();
	debug("generating PDF data")
	data = webView.dataWithPDFInsideRect_(webView.bounds())
	debug("writing PDF data to output file")
	data.writeToFile_atomically_(outFile, True)

def convert(htmlfile, outputfile):
	global WIDTH, HEIGHT
	debug("Input:  " + htmlfile)
	debug("Output: " + outputfile)
	debug("Window size: %s x %s" % (WIDTH, HEIGHT))

	view = WebKit.WebView.alloc()
	view.initWithFrame_frameName_groupName_(((0,0),(WIDTH,HEIGHT)),None, None)
	delegate = WebViewDelegate.alloc()
	delegate.initWithOutputFile_(outputfile)
	view.setFrameLoadDelegate_(delegate)
	u = url(htmlfile)
	debug("url = " + str(u))
	view.mainFrame().loadRequest_(NSURLRequest.requestWithURL_(u))
	# pass control to AppKit
	debug("running event loop...")
	AppHelper.runConsoleEventLoop(installInterrupt = True)

def url(s):
	if re.match('[^:]*://',s):
		u = NSURL.URLWithString_(s)
	else:
		s = os.path.expanduser(s)
		if s[0] != '/':
			s = os.path.join(os.getcwd(),s)
		u = NSURL.fileURLWithPath_(s)
	return u


def main(argv = None):
	global VERBOSE, WIDTH, HEIGHT
	if argv is None:
		argv = sys.argv[1:]

	(opts, argv) = getopt(argv, "vw:h:")
	for (key,val) in opts:
		if key == '-v':
			VERBOSE = True
			debug("Verbose mode enabled...")
		elif key == '-w':
			WIDTH = int(val)
		elif key == '-h':
			HEIGHT = int(val)
	
	
	args = len(argv)
	
	if args < 1 or args > 2:
		print "Incorrect number of arguments"
		print __doc__
		return 2

	infile = argv[0]
	if args > 1:
		outfile = argv[1]
	else:
		outfile = os.path.basename(infile) + ".pdf"
		debug("no output filename given. Using " + outfile)
	
	convert(infile, outfile)
	return 0

if __name__ == "__main__":
	try:
		ret = main()
	except Exception,e:
		print "Exception: " + str(e)
		ret = 3
	sys.exit(ret)
		
