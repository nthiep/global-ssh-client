#!/usr/bin/env python
#
# Name:			Server
# Description:	create connect to ssh Server
#

from threading 	import Thread
from gosh 		import Connection
from gosh.config import logger

class Server(Thread):
	"""docstring for Server """
	def __init__(self, session):
		super(Server, self).__init__()
		self.daemon = True
		self.session = session
	def run(self):
		connection = Connection(self.session)
		data, myaddr, myport = connection.get_accept_connect()
		if not data:
			return
		exaddr 		= data["external"]
		addr 		= data["addr"]
		port 		= int(data["port"])
		work 		= data["work"]
		sport 		= data["sport"]
		if connection.get_connect_server(exaddr, addr, port, work, myport, sport):
			logger.debug("Server: connection success")
			return
		logger.debug("Server: connection false")
