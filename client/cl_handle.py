#!/usr/bin/env python
#
# Name:			cl_handle
# Description:	keep connection to webservice
#

import os, socket, json
from threading import Thread
from ConfigParser import SafeConfigParser
from cl_bind import Bind
import cl_global
class Handle(Thread):
	"""Handle keep conect with server"""
	def __init__(self, connection):
		super(Handle, self).__init__()
		self.daemon = True
		self.connection = connection
	def process(self, data):
		print data
		try:
			data = json.loads(data)
		except:
			return
		if 'status' in data:
			if data["status"] == "bind":
				connbind = Bind(data["session"])
				connbind.start()
			if data["status"] == "addkey":
				try:
					key = data["key"]
					key_auth = os.path.join(os.environ['HOME'], '.ssh', 'authorized_keys')
					f = open(key_auth, 'a')
					f.write(key)
					f.close()
					print "addkey successful"
				except IOError:
					print "error: can't addkey to ~/.ssh/authorized_keys"
		else:
			cl_global.listpeer = data
	def run(self):
		while True:
			data = self.connection.recv(1024)
			if len(data) == 0:
				break
			self.process(data)
		self.connection.close()