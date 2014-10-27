import socket
import threading
from ConfigParser import SafeConfigParser
from cl_frame import Frame
class Peer(object):
	"""docstring for Bind"""
	def __init__(self, hashcode):
		self.hashcode = hashcode
		self.parser = SafeConfigParser()
		self.parser.read('cl_config.cfg')
		self.addr = (self.parser.get('server', 'server'), 
					int(self.parser.get('server', 'port')))
		self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	def process(self):
		frame = Frame()
		self.s.connect((self.addr))
		lo_addr = self.s.getsockname()
		frm = frame.connframe(lo_addr, self.hashcode)
		self.s.send(frm)
		data = self.s.recv(1024)
		res = frame.recvres(data)
		hashcode, lo_tar, public, target = frame.recvpeer(data)
		return hashcode, lo_addr, lo_tar, public, target
