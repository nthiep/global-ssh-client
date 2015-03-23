#!/usr/bin/env python
#
# Name:			Client
# Description:	ssh client connection
#

import sys, socket, os, thread, time, json

from ConfigParser import SafeConfigParser
from gsh import Connection

class Client():
	"""docstring for Client"""
	def __init__(self, data, myaddr, myport):	
		self.data = data
		self.connection = Connection(self.data["session"])
		self.myaddr = myaddr
		self.myport = myport

	def accept(self):		
		conn = self.connection.accept()
		thread.start_new_thread(self.connection.forward, (self.connection.connect, conn))
		thread.start_new_thread(self.connection.forward, (conn, self.connection.connect))
	def run(self):

		if not self.connection.check_internal(self.data["me"], self.data["addr"]):
			print "lan"
			time.sleep(1)
			if self.connection.send_local(self.data["laddr"], int(self.data["lport"])):
				os.system("ssh %s" % self.data["laddr"])
				return				
		thread.start_new_thread(self.connection.listen, (self.myport,))
		self.connection.connecting(self.myport, self.data["addr"], int(self.data["port"]))

		if self.connection.connect is not None:
			print "hear is connect"
			thread.start_new_thread(self.accept, ())
			time.sleep(1)
			if self.connection.addr and self.connection.port:
				print "connection via port"
				os.system("ssh %s -p %d" % (self.connection.addr, self.connection.port))
		print "not allow"