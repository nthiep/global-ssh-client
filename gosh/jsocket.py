""" 
Contains JsonSocket json object message passing for client.
tcp and udp protocol
"""
import socket, json, struct, time, pickle
from gosh.config import logger

class JsonSocket(object):
	## defined protocol
	TCP = 'TCP'
	UDP = 'UDP'
	def __init__(self, protocol):
		self.tcp 		= False
		if protocol == 'TCP':
			self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp 	= True
		else:
			self.socket_obj = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
	def set_reuseaddr(self):
		self.socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	def get_conn(self):
		return self.socket_obj

	def connect(self, address, port, udpconnect=False):
		if self.tcp:
			try:
				logger.debug("socket: connecting to server %s:%d" %(address, port))
				self.socket_obj.connect( (address, port) )
				logger.debug("socket: connected to server %s:%d" %(address, port))

			except socket.error as msg:
				logger.debug("socket: %s" %msg)
				logger.debug("socket: can not connect to server")
				return False
		else:
			try:
				if udpconnect:
					self.socket_obj.connect( (address, port) )
				self.peer = (address, port)
				logger.debug("socket: UDP connected to server")
			except socket.error as msg:
				logger.debug("socket: %s" %msg)
				logger.debug("socket: UDP can not connect to server")
				return False
		return True

	def bind(self, port):
		self.socket_obj.bind( ("", port) )
		return self.socket_obj.getsockname()[1]
	def send_obj(self, obj, peer=False):
		msg = json.dumps(obj)
		if self.socket_obj:
			if self.tcp:
				self.socket_obj.send(msg)
				return True
			elif peer:
				self.socket_obj.sendto(msg, peer)
				return True
			elif self.peer:
				self.socket_obj.sendto(msg, self.peer)
				return True
		return False
	def gethostname(self):
		return socket.gethostname()
	def getsockname(self):

		return self.socket_obj.getsockname()
			
	def _read(self, size):
		if self.tcp:
			data = self.socket_obj.recv(size)
		else:
			data, self.addr = self.socket_obj.recvfrom(size)
		if data:
			return data
		raise Exception('Socket Disconnect!')


	def read_obj(self):
		msg = self._read(5120)
		try:
			return json.loads(msg)
		except:
			return False

	def _listen(self):
		self.socket_obj.listen(5)
	
	def _accept(self):
		return self.socket_obj.accept()
	def set_timeout(self, timeout):
		self.socket_obj.settimeout(timeout)

	def accept_connection(self):
		self._listen()
		conn, addr = self._accept()
		return conn
	def close(self):
		self.socket_obj.close()