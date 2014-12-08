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
					print "close bind"
					source.shutdown(socket.SHUT_RD)
					destination.shutdown(socket.SHUT_WR)
			except Exception as e:
				print "Exception forward bind", e
				break
	def udp_tcp(self, udp, target, tcp):
		data = ' '
		while data:
			try:				
				data, addr = udp.recvfrom(1024)
				if data:
					if len(data) > 1:
						tcp.sendall(data)
					else:
						print data
				else:
					print "close bind"
					udp.shutdown(socket.SHUT_RD)
					tcp.shutdown(socket.SHUT_WR)
			except Exception as e:
				print "Exception forward udp-tcp", e
				break
	def tcp_udp(self, tcp, udp, target):
		data = ' '
		while data:
			try:				
				data = tcp.recv(1024)
				udp.sendto(data, target)
			except Exception as e:
				print "Exception forward tcp-udp", e
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
	def udp_connect(self, udp):
		udp.sendto(json.dumps({"session": self.session}) ,(self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		data, addr = udp.recvfrom(1024)
		print data
		data = json.loads(data)
		time.sleep(1)
		udp.sendto(self.session, (data["host"], int(data["port"])))
		print "udp sendto", data["host"],":", data["port"]
	    data, addr = sockfd.recvfrom( 1024 )
	    print data, addr
	    if data == self.session:
			print "udp connected"
		return int(data["port"])
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
		connudp = False
		if data["me"] == data["addr"]:
			print "Connect by LAN Network"			
			t = Thread(target=self.listen, args = (lport,))
			t.daemon = True
			t.start()
			target = data["laddr"]
			tport = data["lport"]
			check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			time.sleep(0.5)
			if check.connect_ex((target, tport)) == 0 and self.connect is None:
				connlan = True
				self.connect = check
				print "connected to %s:%d" % (target, tport)
		elif not connlan:
			target = data["addr"]
			tport = data["port"]
			if 1==1 or data["nat"] == "RAD" or data["mynat"] == "RAD" or ((data["nat"] == "ASC" or data["nat"] == "DESC") and (data["mynat"] == "ASC" or data["mynat"] == "DESC")):
				udp = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
				udp.bind(("", tport))
				udp_port = self.udp_connect(udp)
		 		connudp = True
			else:				
				t = Thread(target=self.listen, args = (lport,))
				t.daemon = True
				t.start()
				if data["nat"] == "None":
					self.connecting(lport, target, tport, True)
				elif data["nat"] == "ASC":
					i = 0
					while self.connect is None and i < 10:
						self.connecting(lport, target, tport, False)
						tport +=1
						i +=1
				else:
					i = 0
					while self.connect is None and i <10:
						self.connecting(lport, target, tport, False)
						tport -=1
						i+=1
		if self.connect == None and not connudp:
			print "can't connect"
			sys.exit(1)
		if connudp:
			self.connect = udp
		fw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		fw_socket.connect((self.parser.get('config', 'sshd'), int(self.parser.get('config', 'sshp'))))
		
		if connudp:
			thread.start_new_thread(self.udp_tcp, (self.connect, (target, udp_port), fw_socket))
			thread.start_new_thread(self.tcp_udp, (fw_socket, self.connect, (target, udp_port)))
		else:
			thread.start_new_thread(self.forward, (self.connect, fw_socket))
			thread.start_new_thread(self.forward, (fw_socket, self.connect))
