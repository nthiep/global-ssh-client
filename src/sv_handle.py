from threading import Thread
import datetime
import sv_lsclient
from sv_lsclient import Client
from sv_lsclient import Peer
from sv_frame import Frame
from sv_user import User
class Handle(Thread):

	def __init__(self,client_address, connection):		
		super(Handle, self).__init__()
		self.frame = Frame()
		self.daemon = True
		self.client_address = client_address
		self.connection = connection
		self.name = None
	def process(self, req):
		st = self.frame.recvreq(req)
		if st == 200:
			hashcode = self.frame.recvhash(req)
			if hashcode in sv_lsclient.loginrq:
				cl = Client(sv_lsclient.loginrq[hashcode], self.client_address, self.connection)
				sv_lsclient.lsclient.append(cl)
				self.name = sv_lsclient.loginrq[hashcode]
				del sv_lsclient.loginrq[hashcode]
				print "New connection started for %s:%d" % self.client_address
				u = User(self.name)
				u.addlogs(str(datetime.datetime.now()), 'logged in at %s:%d' % self.client_address)
			else:				
				self.connection.close()
			return
		elif st == 400:
			local, hashcode = self.frame.reqconn(req)
			for peer in sv_lsclient.lspeer:
				if peer.hashcode == hashcode:
					print "linked request connection with %s" % hashcode
					peerframea = self.frame.sendpeer(hashcode, peer.local, peer.addr, self.client_address)
					peerframeb = self.frame.sendpeer(hashcode, local, self.client_address, peer.addr)
					peer.connection.send(peerframea)
					sv_lsclient.lspeer.remove(peer)
					return peerframeb
			pe = Peer(hashcode, local, self.client_address, self.connection)
			sv_lsclient.lspeer.append(pe)
			return
		else:
			self.connection.send("bad request")	
			self.connection.close()

	def run(self):
		while True:
			req = self.connection.recv(1024)
			if len(req) == 0:
				break
			frm = self.process(req)
			if frm is not None:
				self.connection.send(frm)
		self.connection.close()
		for l in sv_lsclient.lsclient:
			if l.name == self.name:
				sv_lsclient.lsclient.remove(l)
