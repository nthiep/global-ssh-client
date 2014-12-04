from threading import Thread
import datetime, hashlib, json
from sv_peer import Peer
from sv_lspeer import lspeer
class Handle(Thread):

	def __init__(self, mac, connection):
		super(Handle, self).__init__()
		self.daemon = True
		self.mac = mac
		self.connection = connection
		self.peer = Peer()
	def listpeer(self, mac):
		ls = self.peer.lspeer(mac)
		res = []
		for l in ls:
			res.append({'host': l["host"], 'mac' : l["mac"]})
		for p in lspeer:
			if p.mac != self.mac:
				p.connection.send(json.dumps(res))
			if p.mac == self.mac:
				lspeer.remove(p)
	def run(self):
		self.connection.settimeout(30)
		while True:
			try:
				data = self.connection.recv(1024)
				if len(data) == 0:
					break
				data = json.loads(data)
				if data["request"] == "logout":
					self.connection.send(json.dumps({"status": "FIN"}))
					break
				if data["request"] == "ping":
					self.connection.settimeout(30)
			except  Exception, e:
				print e
				break
		self.peer.rmonline(self.mac)
		self.listpeer(self.mac)
		self.connection.close()

