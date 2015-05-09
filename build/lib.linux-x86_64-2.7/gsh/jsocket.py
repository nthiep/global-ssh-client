""" 
	@module jsocket
	Contains JsonSocket json object message passing for client.

	This file is part of the jsocket package.
	Copyright (C) 2011 by Christopher Piekarski <chris@cpiekarski.com>
	Thank author!
"""
import socket, json, struct, time, pickle
from gsh.config import logger

class JsonSocket(object):
	## defined variable
	TCP = 'TCP'
	UDP = 'UDP'
	def __init__(self, protocol):
		self.tcp 		= False
		if protocol == 'TCP':
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp 	= True
		else:
			self.socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

		self.peer		= None
	def set_reuseaddr(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	def get_conn(self):
		return self.socket

	def connect(self, address, port):
		if self.tcp:
			try:
				self.socket.connect( (address, port) )
				logger.debug("socket: connected to server")
			except socket.error as msg:
				logger.debug("socket: %s" %msg)
				logger.debug("socket: can not connect to server")
				return False
		else:
			try:
				logger.debug("socket: UDP connected to server")
			except socket.error as msg:
				logger.debug("socket: %s" %msg)
				logger.debug("socket: UDP can not connect to server")
				return False
		return True

	def bind(self, port):
		self.socket.bind( ("", port) )
	def send_obj(self, obj, peer=False):
		msg = json.dumps(obj)
		if self.socket:
			if self.tcp:
				self.socket.send(msg)
				return True
			elif(self.peer):
				if peer:
					self.socket.sendto(peer, msg)
				else:
					self.socket.sendto(self.peer, msg)
				return True
		return False
	def gethostname(self):
		return socket.gethostname()
	def getsockname(self):

		return self.socket.getsockname()
			
	def _read(self, size):
		if self.tcp:
			data = self.socket.recv(size)
		else:
			data, self.addr = self.socket.recvfrom(size)
		if data:
			return data
		raise Exception('Socket Disconnect!')


	def read_obj(self):
		msg = self._read(5120)
		try:
			return json.loads(msg)
		except:
			return False
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