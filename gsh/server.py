#!/usr/bin/env python
#
# Name:			Server
# Description:	create connect to ssh Server
#

from threading import Thread
import sys, thread, socket, json, getpass, uuid, time, struct
from ConfigParser import SafeConfigParser
from gsh import JsonSocket
from gsh import Connection

class Server(Thread):
	"""docstring for Server """
	def __init__(self, session):
		super(Server, self).__init__()
		self.daemon = True
		self.session = session
		self.connection = Connection(session)
	def run(self):
		data, address = self.connection.get_accept_connect()
		myaddr, myport = address
		if not self.connection.check_internal(data["me"], data["addr"]):
			if self.connection.test_local_connect(myport):
				return
		thread.start_new_thread(self.connection.listen, (myport,))
		self.connection.connecting(myport, data["addr"], data["port"])
		if self.connection.connect is not None:
			fw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			fw_socket.connect(("localhost", 22))
			thread.start_new_thread(self.connection.forward, (self.connection.connect, fw_socket))
			thread.start_new_thread(self.connection.forward, (fw_socket, self.connection.connect))
