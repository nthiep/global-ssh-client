#!/usr/bin/env python
#
# Name:			Client
# Description:	ssh client connection
#
import os
from gsh import Connection

class Client():
	"""docstring for Client"""
	def __init__(self, data, myaddr, myport, user):	
		self.data  	= data
		self.myaddr = myaddr
		self.myport = myport
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

		port = self.connection.get_connect_client(exaddr, addr, port, laddr, lport, work, self.myport)
		if not port:
			print "not connection"
			return
		if port == 22:
			# connect direct
			if exaddr == addr:
			# connect direct local network
				os.system("ssh %s%s" % (self.user, laddr))
				return
			os.system("ssh %s%s" % (self.user, addr))
			return
		os.system("ssh %s%s -p %d" % (self.user, "localhost", port))
		#
		#------------------------------------------------------------------------
		#