#!/usr/bin/env python
#
# Name:			cl_handle
# Description:	keep connection to webservice
#

import json, socket, getpass
from threading import Thread
from ConfigParser import SafeConfigParser
from cl_bind import Bind
import cl_global
from websocket import create_connection
class Handle(Thread):
	"""docstring for Handle"""
	def __init__(self, username, password, address):
		super(Handle, self).__init__()
		self.daemon = True
		self.username = username
		self.password = password
		self.address = address
		self.parser = SafeConfigParser()
		self.parser.read('cl_config.cfg')
		self.sock_host = "ws://%s:%s" % (self.parser.get('websv', 'server'),self.parser.get('websv', 'port'))
		
	def process(self, data):
		if data != "ok":
			info = json.loads(data)
			if info['status'] == 200:
				hashcode = info['hashcode']
				port = info['port']
				me = info['me']
				peer = info['peer']
				address = info['address']
				localadd = info['localadd']
				connbind = Bind(hashcode, me, port, peer, address, localadd)
				connbind.start()

	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8',80))
		localadd = s.getsockname()[0]
		s.close()
		sock_path = self.sock_host + "/socklogin"
		ws = create_connection(sock_path)
		sshuser = getpass.getuser()
		info = json.dumps({"username" : self.username, "user": sshuser, "password": self.password, "address": self.address, "localadd": localadd})
		ws.send(info)
		while True:
			result =  ws.recv()
			if result:
				self.process(result)
			else:
				break
		cl_global.auth = None
		cl_global.user = None