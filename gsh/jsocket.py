""" 
	@module jsocket
	Contains JsonSocket json object message passing for client.

	This file is part of the jsocket package.
	Copyright (C) 2011 by Christopher Piekarski <chris@cpiekarski.com>
	Thank author!
"""
import socket, json, struct, time, pickle
from gsh.lib.Crypto.Hash import MD5
from gsh.lib.Crypto.PublicKey import RSA
from gsh.lib.Crypto.Util import randpool
from gsh.lib.Crypto.Cipher import AES
from gsh.lib.Crypto import Random
from gsh.config import logging

class Secure(object):
	"""docstring for Secure"""
	def __init__(self):
		pass
	def setkey(self, key):
		self.key = key
	def rsakey(self):
		#generate the RSA key
		rand = randpool.RandomPool()
		RSAKey = RSA.generate(2048, rand.get_bytes) 
		RSAPubKey = RSAKey.publickey()
		return RSAKey, RSAPubKey

	def encrypt( self, raw ):
		BS = 16
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
		raw = pad(raw)
		iv = Random.new().read( AES.block_size )
		cipher = AES.new( self.key, AES.MODE_CBC, iv )
		return iv + cipher.encrypt( raw )

	def decrypt( self, enc ):
		unpad = lambda s : s[:-ord(s[len(s)-1:])]
		iv = enc[:16]
		cipher = AES.new(self.key, AES.MODE_CBC, iv )
		return unpad(cipher.decrypt( enc[16:] ))

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
		self.secure 	= Secure()
	def set_reuseaddr(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	def get_conn(self):
		return self.socket

	def connect(self, address, port):
		private, rsapub = self.secure.rsakey()
		if self.tcp:
			try:
				self.socket.connect( (address, port) )
				self.socket.send(pickle.dumps(rsapub))
				recv = self.socket.recv(1024)
				logging.debug("socket: connected to server")
			except socket.error as msg:
				logging.debug("socket: %s" %msg)
				logging.debug("socket: can not connect to server")
				return False
		else:
			try:
				self.socket.sendto((address, port), pickle.dumps(rsapub))
				recv, addr = socket.recvfrom(1024)
				logging.debug("socket: UDP connected to server")
			except socket.error as msg:
				logging.debug("socket: %s" %msg)
				logging.debug("socket: UDP can not connect to server")
				return False

		key = private.decrypt(recv)
		self.secure.setkey(key)
		return True

	def bind(self, port):
		self.socket.bind( ("", port) )
	def send_obj(self, obj):
		msg = json.dumps(obj)
		msg = self.secure.encrypt(msg)
		if self.socket:
			if self.tcp:
				self.socket.send(msg)
				return True
			elif(self.peer):
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
		return data


	def read_obj(self):
		msg = self._read(5120)
		msg = self.secure.decrypt(msg)
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