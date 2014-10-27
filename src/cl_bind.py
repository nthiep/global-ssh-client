from threading import Thread
import thread
from ConfigParser import SafeConfigParser
class Bind(Thread):
	"""docstring for Bind"""
	def __init__(self, hashcode, peer, address, localadd):
		super(Bind, self).__init__()
		self.daemon = True
		self.cancelled = False
		self.hashcode = hashcode
		self.peer = peer
		self.address = address
		self.localadd = localadd

		self.parser = SafeConfigParser()
		self.parser.read('cl_config.cfg')
		
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
		
		self.s.bind(("", lop))
		self.s.connect_ex(target)
		#start bind ssh
		fw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		fw_socket.connect((self.parser.get('ssh', 'local'), int(self.parser.get('ssh', 'port'))))
		thread.start_new_thread(self.forward, (self.s, fw_socket))
		thread.start_new_thread(self.forward, (fw_socket, self.s))
