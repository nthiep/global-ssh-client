global lsclient
lsclient = []
class Client(object):
	"""docstring for client"""
	def __init__(self, name, addr, localadd, connection):
		self.name = name
		self.addr = addr
		self.local = localadd
		self.connection = connection