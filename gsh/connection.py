#!/usr/bin/env python
#
# Name:			cl_bind
# Description:	create connect and forward to ssh port
#

from threading import Thread
import sys, thread, socket, json, getpass, uuid, time, struct
from ConfigParser import SafeConfigParser
from gsh import JsonSocket

_SERVER_	= "localhost"
_PORT_		= 8080
class Connection(object):
	"""docstring for Connection"""
	def __init__(self, session):
		self.session = session
		self.connect = None
		self.addr 	 = None
		self.port 	 = None
		try:
			self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
		except:
			self.mac = str(hex(uuid.getnode()))
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

	def accept(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(("", 0))
		self.addr, self.port = sock.getsockname()
		sock.listen(5)
		conn, addr = sock.accept()
		return conn
	def listen(self, myport):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(5.0)
		sock.bind(("", myport))
		print "listen on ", myport
		sock.listen(5)
		try:
			conn, addr = sock.accept()
			if self.connect is None:
				self.connect = conn
				print "accepted connect from ", addr
		except:
			print "not connect"
	def connecting(self, myport, addr, port):
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		conn.bind(("", myport))
		err = 1
		i = 0
		conn.settimeout(5.0)
		while err != 0 and i < 10:
			err = conn.connect_ex((addr, port))
			i += 1
		if err == 0 and self.connect is None:			
			conn.settimeout(None)
			self.connect = conn			
			print "connected to %s:%d" % (addr, port)
	def udp_connect(self, udp):
		udp.sendto(json.dumps({"session": self.session}) ,(self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		data, addr = udp.recvfrom(1024)
		print data, addr
		data = json.loads(data)
		if self.mynat == "RAD":
			time.sleep(1)
		udp.sendto(self.session, (data["host"], int(data["port"])))
		print "udp sendto", data["host"],":", data["port"]
		recv, addr = udp.recvfrom( 1024 )
		print recv, addr
		if recv == self.session:
			if self.mynat != "RAD":
				udp.sendto(self.session, addr)
			print "udp connected"
		return addr

	def test_local_connect(self, port):
		conn = JsonSocket("", port)
		conn.set_reuseaddr()
		conn = conn.accept_connection()
		conn.settimeout(2)
		data = conn.recv(1024)
		data = json.loads(data)
		if data == self.session:
			conn.close()
			return True
		return False
	def send_local(self, addr, port):
		conn = JsonSocket(addr, port)
		conn.connect()
		if conn.send_obj(self.session):
			conn.close()
			return True
		return False
	def get_accept_connect(self):
		""" request connection to peer """
		connect = JsonSocket(_SERVER_, _PORT_)
		if not connect.connect():
			return False
		address = connect.getsockname()
		laddr, lport = address
		data = {"request": "accept_connect", "session": self.session,
		"lport": lport, "laddr": laddr, "mac": self.mac}
		connect.send_obj(data)
		data = connect.read_obj()
		print data
		connect.close()
		return data, address

	def check_internal(self, addr, remote):
		if addr == remote:
			return True
		return False


