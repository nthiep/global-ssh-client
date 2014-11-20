#!/usr/bin/env python
#
# Name: 		Global SSH Client
# Description:	help connect ssh between client behind NAT.
#				ssh use paramiko
# project 2
#
# Author: 		Nguyen Thanh Hiep - Nguyen Huu Dinh
# Time: 		2014/10
# Requirements: paramiko, ecdsa
#

import shlex
import sys
import os
import time
import readline
from optparse import OptionParser
from optparse import OptionGroup
import getpass
from cl_request import Request
import cl_global
request = Request()
def Main():
	print "---Welcome to Global SSH Client---"
	print ".................................."
	if not request.login():
		print "error while login"
		sys.exit(1)
	parser = OptionParser(description='global-ssh help connect ssh to peer behind NAT',
                                   prog='global-ssh',
                                   version='global-ssh 1.2',
                                   usage='%prog [-h] or [--help] to view help\n\t[-q] to quit program')
	

	group = OptionGroup(parser, "connect to peer")	#create group of parser
	group.add_option("-c", "--connect", type="int",
        help="start connect ssh to peer", metavar="peer") # add option parser
	group.add_option("-k", "--key", type = "int",
        help="add public key of peer", metavar="peer")
	parser.add_option_group(group)

	group = OptionGroup(parser, "show infomation of peer")
	group.add_option("-l", "--list", action ='store_true', default=False,
        help="show all list peer")
	group.add_option("-g", "--logs", action ='store_true', default=False,
        help="show logs")
	parser.add_option_group(group)

	parser.add_option("-q", "--quiet",
	 action="store_true", default=False, help="exit program")

	(options, args) = parser.parse_args()	#read parser from agv example: gssh -c 1
	processparser(options)					#process parser
	inhist = ".inhist"
	try:
		readline.read_history_file(inhist)
	except IOError:
		pass
	import atexit
	atexit.register(readline.write_history_file, inhist)	#read history input
	while True:
		try:
			inp = raw_input("global-ssh$ ")				#print input
			try:				
				(options, args) = parser.parse_args(shlex.split(inp))	#read input from raw_input
				processparser(options)						#process parser
			except:
				pass
		except KeyboardInterrupt:
			print "\nquitting...."
			sys.exit(1)
	del os, histfile

def processparser(options):
	if options.connect is not None:		
		request.connect(options.connect)
	if options.list:
		request.listpeer()
	if options.key is not None:
		request.uploadkey(options.key)
	if options.logs:
		request.logs()
	if options.quiet:
		print "\nquitting...."
		os._exit(1)

Main()