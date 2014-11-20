global lspeer
global session
lspeer = []
session = {}
class lsPeer(object):
	"""docstring for Peer"""
	def __init__(self, token, mac, connection):
		self.token = token
		self.mac = mac
		self.connection = connection