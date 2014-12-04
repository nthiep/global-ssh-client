#!/usr/bin/env python
#
# Name:			cl_handle
# Description:	keep connection to webservice
#

import os, time, thread, socket, json, uuid, crypt, getpass, spwd, re
from threading import Thread
from ConfigParser import ConfigParser
from cl_bind import Bind
import cl_global
class Handle(Thread):
	"""Handle keep conect with server"""
	def __init__(self, connection):
		super(Handle, self).__init__()
		self.daemon = True
		self.connection = connection
		self.parser = ConfigParser()
		self.parser.read('cl_config.conf')
		try:
			self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
		except:
			self.mac = str(hex(uuid.getnode()))
	def check_nat(self):
		self.parser.read('cl_config.conf')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		lport = s.getsockname()[1]
		s.send(json.dumps({"request": "checknat", "mac": self.mac, "lport": lport}))
		s.close()
	def reconnect(self):
		self.parser.read('cl_config.conf')	
		token = self.parser.get('config', 'token')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		except:
			return False
		lport = s.getsockname()[1]
		s.send(json.dumps({"request": "login", "token": token, "mac": self.mac, "lport": lport, "host": socket.gethostname()}))
		res = s.recv(1024)
		try:
			res = json.loads(res)
		except:
			return False
		if "error" in res:
			return False
		else:
			cl_global.listpeer = res
			cl_global.connect = s
			self.connection = s
			self.check_nat()
			self.check_nat()
			return True
		return False	

	def check_rsa(self, string, f):
		for line in f:
			if re.search("\b{0}\b".format(string),line):
				return True
		return False
	def process(self, data):
		try:
			data = json.loads(data)
		except:
			pass
		if 'status' in data:
			if data["status"] == "FIN":
				print "logout..."
				return False
			if data["status"] == "bind":
				connbind = Bind(data["session"])
				connbind.start()
			if data["status"] == "addkey":
				try:
					key = data["key"]
					key_auth = os.path.join(os.environ['HOME'], '.ssh', 'authorized_keys')
					f = open(key_auth, 'a')
					if self.check_rsa(key, f):
						f.write(key)
						f.close()
						print "addkey successful"
				except IOError:
					print "error: can't addkey to ~/.ssh/authorized_keys"
				except:
					print "error when add key"
		else:
			cl_global.listpeer = data
		return True

	def ping_server(self, sec):
		while True:
			try:
				self.connection.send(json.dumps({"request": "ping"}))
				time.sleep(sec)
			except:
				i = 1
				while not self.reconnect() and i <= 5:
					print "reconnect to server..."
					time.sleep(2 * i)
					i +=1
				if i >5:
					os._exit(1)
	def run(self):
		thread.start_new_thread(self.ping_server, (25,))
		while True:
			try:
				data = self.connection.recv(1024)
				if len(data) == 0:
					raise
				if not self.process(data):
					self.connection.close()
					raise
			except:
				i = 1
				while not self.reconnect() and i <= 5:
					print "reconnect to server..."
					time.sleep(2 * i)
					i +=1
				if i >5:
					os._exit(1)
		self.connection.close()