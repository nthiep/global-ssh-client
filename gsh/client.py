#!/usr/bin/env python
#
# Name:			Client
# Description:	ssh client connection
#
import os
from gsh 		import Connection
from gsh.config import logging
class Client():
	"""docstring for Client"""
	def __init__(self, data, myaddr, myport, user, sport, options, args, sfile):	
		self.data  	= data
		self.myaddr = myaddr
		self.myport = myport
		self.sport 	= sport
		self.options= options
		self.args 	= args
		self.sfile 	= sfile
		if user:
			self.user = user + "@"
		else:
			self.user = ""
		self.connection = Connection(self.data["session"])
	def run(self):
		exaddr 		= self.data["external"]		
		addr 		= self.data["addr"]
		port 		= int(self.data["port"])
		laddr 		= self.data["laddr"]
		lport 		= int(self.data["lport"])
		work 		= self.data["work"]

		port = self.connection.get_connect_client(exaddr, addr, port, laddr, lport, work, self.myport, self.sport)
		if not port:
			logging.debug("client: can not connect")
			return
		if self.sport:
			print "* RESULT: *Port binding on* \t localhost:%d" %port
			return
		service = self.options.service
		sfile = (":" + self.sfile)  if self.sfile  else ""
		identity= ("-i " +self.options.identity) if self.options.identity else ""
		verbose = "-v"  if self.options.verbose  else ""
		command = self.options.command if self.options.command and len(self.args)<=1  else ""
		
		arguments = verbose + identity + command
		args = ' '.join(self.args[1:])
		if port == 22:
			# connect direct
			logging.debug("client: connect to %s%s" %(self.user, addr))
			os.system("%s %s%s%s %s %s" % (service, self.user, addr, sfile, arguments, args))
			return
		logging.debug("client: connect to %slocalhost:%d" %(self.user, port))
		os.system("%s %s%s%s -p %d %s %s" % (service, self.user, "localhost", sfile, port, arguments, args))
		#
		#------------------------------------------------------------------------
		#