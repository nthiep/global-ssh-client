""" 
	@module jsocket
	Contains JsonSocket json object message passing for client.

	This file is part of the jsocket package.
	Copyright (C) 2011 by Christopher Piekarski <chris@cpiekarski.com>
	Thank author!
"""
import socket, json, struct, time

class JsonSocket(object):
	def __init__(self, address, port):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._timeout = None
		self._address = address
		self._port = port
	def set_reuseaddr(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	def get_conn(self):
		return self.socket

	def connect(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		for i in range(10):
			try:
				self.socket.connect( (self._address, self._port) )
			except socket.error as msg:
				time.sleep(3)
				continue
			return True
		return False

	def bind(self, port):
		self.socket.bind( ("", port) )
	def send_obj(self, obj):
		msg = json.dumps(obj)
		if self.socket:
			try:
				self.socket.send(msg)
				return True
			except:
				pass
		return False
	def gethostname(self):
		return socket.gethostname()
	def getsockname(self):

		return self.socket.getsockname()
			
	def _read(self, size):
		data = self.socket.recv(size)
		return data

	def read_obj(self):
		msg = self._read(5120)
		return json.loads(msg)
	def _bind(self):
		self.socket.bind( ("",self._port) )

	def _listen(self):
		self.socket.listen(5)
	
	def _accept(self):
		return self.socket.accept()
	def set_timeout(self):
		self.socket.settimeout(self._timeout)

	def accept_connection(self):
		self._bind()
		self._listen()
		conn, addr = self._accept()
		return conn
	def close(self):
		self.socket.close()