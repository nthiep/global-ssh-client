global lspeer
global session
lspeer = []
session = {}
class lsPeer(object):
	"""docstring for Peer"""
	def __init__(self, user, mac, connection):
		self.user = user
		self.mac = mac
		self.connection = connection