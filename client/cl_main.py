#!/usr/bin/env python
#
# Name: 		Global SSH Client
# Description:	help connect ssh between client behind NAT.
#				ssh use paramiko
# project 2
#
# Author: 		Nguyen Thanh Hiep - Nguyen Huu Dinh
# Time: 		2014/10
# Requirements: paramiko, ecdsa, websocket_client
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
	if not request.checkconnection():
		sys.exit(1)
	parser = OptionParser(description='global-ssh help connect ssh to peer behind NAT',
                                   prog='global-ssh',
                                   version='global-ssh 1.1',
                                   usage='%prog [-h] or [--help] to view help\n\t[-q] to quit program')
	group = OptionGroup(parser, "register and login")
	group.add_option("-r", "--register", 
		help="register account: -r username -p password", metavar="username")
	group.add_option("-l", "--login",
        help="login: -l username -p password", metavar="username")
	group.add_option("-p", "--password",
        help="use with register or login", metavar="password")
	group.add_option("-w", "--logout", action ='store_true', default=False,
        help="logout Server")
	parser.add_option_group(group)


	group = OptionGroup(parser, "connect to peer")
	group.add_option("-c", "--connect",
        help="start connect ssh to peer", metavar="peername")
	group.add_option("-u", "--upload", action ='store_true', default=False,
        help="upload public key to Server",)
	group.add_option("-k", "--key",
        help="add public key of peer", metavar="peer")
	parser.add_option_group(group)

	group = OptionGroup(parser, "show infomation of username")
	group.add_option("-f", "--friend", action ='store_true', default=False,
        help="show all list friend")
	group.add_option("-o", "--online", action ='store_true', default=False,
        help="show list friend online")
	group.add_option("-g", "--logs", action ='store_true', default=False,
        help="show logs")
	parser.add_option_group(group)

	group = OptionGroup(parser, "information of friends")
	group.add_option("-m", "--mail", action ='store_true', default=False,
        help="show all list friend request")
	group.add_option("-i", "--info", metavar="peername",
        help="view info of friend")
	group.add_option("-j", "--addf", metavar="peername",
        help="add a friend")
	group.add_option("-v", "--accept", metavar="peername",
        help="accept a request peer as friend")
	group.add_option("-x", "--denied", metavar="peername",
        help="denied a request peer")
	parser.add_option_group(group)

	parser.add_option("-q", "--quiet",
	 action="store_true", default=False, help="exit program")

	(options, args) = parser.parse_args()
	processparser(options)
	inhist = ".inhist"
	try:
		readline.read_history_file(inhist)
	except IOError:
		pass
	import atexit
	atexit.register(readline.write_history_file, inhist)
	while True:
		try:
			if cl_global.user is not None:
				inp = raw_input("%s@global-ssh$> " % cl_global.user)
			else:
				inp = raw_input("global-ssh$> ")
			try: 
				(options, args) = parser.parse_args(shlex.split(inp))
				processparser(options)
			except:
				pass
		except KeyboardInterrupt:
			print "\nquitting...."
			sys.exit(1)
	del os, histfile

def processparser(options):
	if options.register is not None:
		if options.password is None:
			pswd = getpass.getpass('Password for %s: ' % options.register)			
			repswd = getpass.getpass('confirm password: ')
			if pswd != repswd:
				print 'error: confirm password not match'
				return
		else:
			pswd = options.password
		request.register(options.register, pswd)
	if options.login is not None:
		if options.password is None:
			pswd = getpass.getpass('Password for %s:' % options.login)
		else:
			pswd = options.password
		request.login(options.login, pswd)
	if options.connect is not None:		
		request.connect(options.connect)
	if options.upload:		
		request.uploadkey()
	if options.key is not None:
		request.addkey(options.key)

	if options.friend:
		request.friends()
	if options.online:
		request.onlines()
	if options.logs:
		request.logs()
	if options.mail:
		request.friendrq()

	if options.addf is not None:
		request.addfriendrq(options.addf)
	if options.info is not None:
		request.info(options.info)
	if options.accept is not None:
		request.accept(options.accept)
	if options.denied is not None:		
		request.denied(options.denied)
	if options.logout:
		request.logout()
	if options.quiet:
		print "\nquitting...."
		os._exit(1)

Main()