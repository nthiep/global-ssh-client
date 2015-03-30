#!/usr/bin/env python
#
# Name:			Server
# Description:	create connect to ssh Server
#

from threading 	import Thread
from gsh 		import Connection
from gsh.config import logging

class Server(Thread):
	"""docstring for Server """
	def __init__(self, session):
		super(Server, self).__init__()
		self.daemon = True
		self.session = session
		self.connection = Connection(session)
	def run(self):
		data, myaddr, myport = self.connection.get_accept_connect()
		if not data:
			return
		exaddr 		= data["external"]
		addr 		= data["addr"]
		port 		= int(data["port"])
		work 		= data["work"]
		if self.connection.get_connect_server(exaddr, addr, port, work, myport):
			logging.debug("Server: connection success")
			return
		logging.debug("Server: connection false")
