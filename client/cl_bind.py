from threading import Thread
import thread, socket
from ConfigParser import SafeConfigParser
class Bind(Thread):
	"""docstring for Bind"""
	def __init__(self, hashcode, me, port, peer, address, localadd):
		super(Bind, self).__init__()
		self.daemon = True
		self.cancelled = False
		self.hashcode = hashcode
		self.me = me
		self.port = port
		self.peer = peer
		self.address = address
		self.localadd = localadd

		self.parser = SafeConfigParser()
		self.parser.read('cl_config.cfg')
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
	def forward(self, source, destination):
		string = ' '
		while string:
			string = source.recv(1024)
			if string:
				destination.sendall(string)
			else:
				source.shutdown(socket.SHUT_RD)
				destination.shutdown(socket.SHUT_WR)
		
	def run(self):
		if self.me == self.address:
			target = self.localadd
		else:
			target = self.address
		self.s.bind(("", self.port + 1))
		self.s.connect_ex((target, self.port))
		print "bind connected to %s:%d" % (target, self.port)
		#start bind ssh
		fw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		fw_socket.connect((self.parser.get('ssh', 'local'), int(self.parser.get('ssh', 'port'))))
		thread.start_new_thread(self.forward, (self.s, fw_socket))
		thread.start_new_thread(self.forward, (fw_socket, self.s))