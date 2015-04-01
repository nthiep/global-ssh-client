""" 
	@module jsocket
	Contains JsonSocket json object message passing for client.

	This file is part of the jsocket package.
	Copyright (C) 2011 by Christopher Piekarski <chris@cpiekarski.com>
	Thank author!
"""
import socket, json, struct, time, pickle
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Util import randpool
from Crypto.Cipher import AES
from Crypto import Random
from gsh.config import logging

class JsonSocket(object):
	def __init__(self, address, port):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._timeout = None
		self._address = address
		self._port = port
		self.key = False
	def set_reuseaddr(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	def get_conn(self):
		return self.socket

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
	def rsakey(self):
		#generate the RSA key
		rand = randpool.RandomPool()
		RSAKey = RSA.generate(2048, rand.get_bytes) 
		RSAPubKey = RSAKey.publickey()
		return RSAKey, RSAPubKey
	def connect(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.socket.connect( (self._address, self._port) )
			self.private, rsapub = self.rsakey()
			self.socket.send(pickle.dumps(rsapub))
			recv = self.socket.recv(1024)
			self.key = self.private.decrypt(recv)
			logging.debug("socket: connected to server")
			return True
		except socket.error as msg:
			logging.debug("socket: %s" %msg)
			logging.debug("socket: can not connect to server")
			return False
		logging.debug("socket: can not connect to server")
		return False

	def bind(self, port):
		self.socket.bind( ("", port) )
	def send_obj(self, obj):
		msg = json.dumps(obj)
		msg = self.encrypt(msg)
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
		msg = self.decrypt(msg)
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