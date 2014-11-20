from threading import Thread
import datetime, hashlib, json
from sv_peer import Peer
from sv_lspeer import lspeer
class Handle(Thread):

	def __init__(self, token, mac, client_address, connection):
		super(Handle, self).__init__()
		self.daemon = True
		self.token = token
		self.mac = mac
		self.client_address = client_address
		self.connection = connection
		self.peer = Peer()
	def listpeer(self, token):
		ls = self.peer.lspeer(token)
		res = []
		for l in ls:
			res.append({'host': l["host"], 'mac' : l["mac"]})
		for p in lspeer:
			if p.token == token and p.mac != self.mac:
				p.connection.send(json.dumps(res))
			if p.token == token and p.mac == self.mac:
				lspeer.remove(p)
	def run(self):
		while True:
			try:
				data = self.connection.recv(1024)
				if len(data) == 0:
					break
			except:
				break
		self.peer.rmonline(self.token, self.mac)
		self.listpeer(self.token)
		self.connection.close()

