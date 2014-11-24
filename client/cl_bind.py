#!/usr/bin/env python
#
# Name:			cl_bind
# Description:	create connect and forward to ssh port
#

from threading import Thread
import sys, thread, socket, json, getpass, uuid, time, struct
from ConfigParser import SafeConfigParser
class Bind(Thread):
	"""docstring for Bind"""
	def __init__(self, session):
		super(Bind, self).__init__()
		self.daemon = True
		self.cancelled = False
		self.session = session
		self.parser = SafeConfigParser()
		self.parser.read('cl_config.conf')
		try:
			self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
		except:
			self.mac = str(hex(uuid.getnode()))
		self.connect = None
	def forward(self, source, destination):
		string = ' '
		while string:
			try:				
				string = source.recv(1024)
				if string:
					destination.sendall(string)
				else:
					source.shutdown(socket.SHUT_RD)
					destination.shutdown(socket.SHUT_WR)
			except Exception as e:
				print "Exception forward", e
				break

	def listen(self, port):
		ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	
		ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		ls.bind(("", port))
		print "listen on ", port
		ls.listen(5)
		ls, cl = ls.accept()
		if self.connect is None:
			self.connect = ls
			print "accepted connect from ", cl
	def connecting(self, lport, target, tport, nat):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		s.bind(("", lport))
		print "send ", tport
		err = 1
		if nat:
			i = 0
			s.settimeout(5.0)
			while err != 0 and i < 10:
				err = s.connect_ex((target, tport))
				i += 1
		else:
			s.settimeout(1.0)
			err = s.connect_ex((target, tport))
		if err == 0 and self.connect is None:			
			s.settimeout(None)
			self.connect = s			
			print "connected to %s:%d" % (target, tport)
	def run(self):
		sb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sb.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sb.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		laddr, lport = sb.getsockname()
		user = getpass.getuser()
		sb.send(json.dumps({"user": user, "request": "connect", "session": self.session,
		"token": self.parser.get('config', 'token'), "lport": lport, "laddr": laddr, "mymac": self.mac}))
		data = sb.recv(1024)
		sb.close()
		print data
		data = json.loads(data)
		connlan = False
		t = Thread(target=self.listen, args = (lport,))
		t.daemon = True
		t.start()
		if data["me"] == data["addr"]:
			target = data["laddr"]
			tport = data["lport"]
			check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			time.sleep(0.5)
			if check.connect_ex((target, tport)) == 0 and self.connect is None:
				connlan = True
				self.connect = check
				print "connected to %s:%d" % (target, tport)
		elif not connlan:
			print "not lan"
			target = data["addr"]
			tport = data["port"]
			if data["nat"] == "None":
				print "NAT None"
				self.connecting(lport, target, tport, True)
			elif data["nat"] == "ASC":			    
				print "NAT ASC"
				i = 0
				while self.connect is None and i < 10:
					self.connecting(lport, target, tport, False)
					tport +=1
					i +=1
			else:
				print "NAT DESC"
				i = 0
				while self.connect is None and i <10:
					self.connecting(lport, target, tport, False)
					tport -=1
					i+=1
		if self.connect == None:
			print "can't connect"
			sys.exit(1)
		print "have connect"
		#start bind ssh
		fw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		fw_socket.connect((self.parser.get('config', 'sshd'), int(self.parser.get('config', 'sshp'))))
		thread.start_new_thread(self.forward, (self.connect, fw_socket))
		thread.start_new_thread(self.forward, (fw_socket, self.connect))
