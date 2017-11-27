# -*- coding: utf-8 -*-

import sys
import os
import shutil

from distutils.core import setup

RUNS_ON_WINDOWS = sys.platform in ('nt', 'win32')

if os.path.exists('dist'):
	print("Removing old 'dist' directory")
	shutil.rmtree('dist')

if RUNS_ON_WINDOWS:
	import py2exe

	# If run without args, build executables, in quiet mode.
	if len(sys.argv) == 1:
		sys.argv.append("py2exe")
		sys.argv.append("-q")

	class Target:
		def __init__(self, **kw):
			self.__dict__.update(kw)
			self.company_name = "uib GmbH"
			self.copyright = "uib GmbH"
			self.version = ""
			f = open(self.script, 'r')
			for line in f.readlines():
				if (line.find("__version__") != -1):
					self.version = line.split('=', 1)[1].strip()[1:-1]
					break
			f.close()
			if not self.version:
				print >> sys.stderr, "Failed to find version of script '%s'" % self.script

	hwaudit = Target(
		name="hwaudit",
		description="hardware invent",
		script="hwaudit.py",
		icon_resources=[(1, "hwaudit.ico")]
	)

	################################################################
	# COM pulls in a lot of stuff which we don't want or need.
	excludes = [
		"pywin", "pywin.debugger", "pywin.debugger.dbgcon",
		"pywin.dialogs", "pywin.dialogs.list",
		"Tkconstants", "Tkinter", "tcl", "_imagingtk",
		"PIL._imagingtk", "ImageTk", "PIL.ImageTk", "FixTk"
	]

	setup_opts = {
		"options": {
			"py2exe": {
				"compressed": 1,
				# "bundle_files": 1,
				"optimize": 2,
				"excludes": excludes,
				"packages": ["OPSI"]
			}
		},
		"data_files": [],
		"zipfile": "lib/library.zip",
		"console": [hwaudit],
	}

else:
	setup_opts = {}

setup(**setup_opts)

if RUNS_ON_WINDOWS:
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "!!!   On the target machine always replace exe AND lib   !!!"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
