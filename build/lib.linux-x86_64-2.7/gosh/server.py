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
	def __init__(self, session, machine):
		super(Server, self).__init__()
		self.daemon = True
		self.session = session
		self.machine = machine
	def run(self):
		connection = Connection(self.session)
		result = connection.get_accept_connect(self.machine)
		if not result:
			logger.debug("Server: connection rejected incorrect data or machine not accept!")
			return False
		data, myaddr, myport = result
		external_addr		= data["external"]
		addr 				= data["addr"]
		port 				= int(data["port"])
		work 				= data["work"]
		destination_port 	= data["destination_port"]
		if connection.get_connect_server(external_addr, addr, port, work, myport, destination_port):
			logger.debug("Server: connection success")
			return
		logger.debug("Server: connection false")
