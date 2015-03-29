#!/usr/bin/env python
#
# Name:			cl_bind
# Description:	create connect and forward to ssh port
#

import sys, thread, socket, json, getpass, uuid, time, struct
from ConfigParser import SafeConfigParser
from gsh import JsonSocket
from gsh.config import *

class Connection(object):
	"""docstring for Connection"""
	def __init__(self, session):
		self.session = session
		
	def get_accept_connect(self):
		""" request connection to peer """
		connect = JsonSocket(SERVER, PORT)
		if not connect.connect():
			return False
		laddr, lport = connect.getsockname()
		data = {"request": "accept_connect", "session": self.session,
		"lport": lport, "laddr": laddr, "mac": MAC_ADDR}
		connect.send_obj(data)
		data = connect.read_obj()
		print data
		connect.close()
		return data, laddr, lport

	def tcp_forward(self, source, destination):
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

	def udp_tcp_forward(self, udp, target, tcp):
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
	def tcp_udp_forward(self, tcp, udp, target):
		data = ' '
		while data:
			try:				
				data = tcp.recv(1024)
				udp.sendto(data, target)
			except Exception as e:
				print "Exception forward tcp-udp", e
				break


	def accept_local(self, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(("", port))
		sock.settimeout(2.0)
		sock.listen(5)
		try:
			conn, addr = sock.accept()
			conn.send(self.session)
			res = conn.recv(1024)
			if res == 'F':
				conn.close()
				sock.close()
				return 10
			sock.settimeout(None)
			return conn
		except:
			return False

	def connect_direct(self, addr, port):
		""" connect to via direct """
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if not sock.connect_ex((addr, port)):
			return sock
		return False

	def connect_local(self, addr, port):
		""" check connect right local """
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(2.0)
		if not sock.connect_ex((addr, port)):
			data = sock.recv(1024)
			if data == self.session:
				sock.settimeout(None)
				return sock
		return False
	def listen_udp(self, lssock, udpsock, target):
		lssock.listen(5)
		try:
			conn, addr = lssock.accept()
			thread.start_new_thread(self.udp_tcp_forward, (udpsock, target, conn))
			thread.start_new_thread(self.tcp_udp_forward, (conn, udpsock, target))
		except:
			pass
		return False
	def listen_tcp(self, lssock, connsock):
		lssock.listen(5)
		try:
			conn, addr = lssock.accept()
			print "had accept"
			thread.start_new_thread(self.tcp_forward, (connsock, conn))
			thread.start_new_thread(self.tcp_forward, (conn, connsock))
		except Exception, e:
			print e
		return False
	def listen(self, myport):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(2.0)
		sock.bind(("", myport))
		print "listen on ", myport
		sock.listen(5)
		try:
			conn, addr = sock.accept()
			return conn
		except:
			pass
		return False
	def hole_connecting(self, myport, addr, port):
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		conn.bind(("", myport))
		err = 1
		i = 0
		conn.settimeout(5.0)
		while err != 0 and i < 10:
			err = conn.connect_ex((addr, port))
			i += 1
		if err == 0:			
			conn.settimeout(None)
			return conn

	def _multi_connect(self, myport, addr, port):
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)		
		conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		conn.bind(("", lport))
		conn.settimeout(1.0)
		if conn.connect_ex((target, tport)) == 0:
			return conn
		return False

	def asc_hole_connect(self, myport, addr, port):
		i=0
		conn = False
		while not conn and i < 10:
			conn = self._multi_connect(myport, addr, port)
			port += 1
			i +=1
		if conn:
			return conn
		return False
	def desc_hole_connect(self, myport, addr, port):
		i=0
		conn = False
		while not conn and i < 10:
			conn = self._multi_connect(myport, addr, port)
			port -= 1
			i +=1
		if conn:
			return conn
		return False

	def udp_hole_connect(self):
		connect = JsonSocket(SERVER, PORT)
		if not connect.connect():
			return False

		send_obj = ({"request": "udp_hole", "session": self.session})
		connect.send_obj(send_obj)
		recv_obj = connect.read_obj()
		port = recv_obj["port"]
		# stating udp hole punching
		udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		req = json.dumps({"session": self.session})
		udp.sendto( req, (SERVER, int(port)))
		peer, addr = udp.recvfrom(1024)
		print peer, addr
		peer = json.loads(peer)

		udp.sendto(self.session, (peer["host"], int(peer["port"])))
		print "udp sendto", peer["host"],":", peer["port"]
		recv, addr = udp.recvfrom( 1024 )
		print recv, addr
		if recv == self.session:
			udp.sendto(self.session, addr)
			print "udp connected"
		return udp, addr
	def relay_connect(self):
		""" connect to relay server """
		# get request connect to relay server
		connect = JsonSocket(SERVER, PORT)
		if connect.connect():
			send_obj = ({"request": "relay", "session": self.session})
			connect.send_obj(send_obj)

		# had connect relay
			return connect.get_conn()
		# can not connect to server
		return False

	def get_connect_process(self, myport, _addr, _port, _work):
		""" process data and connect method """

		# connect table
		#---------------------------------------------------------------------
		#			| Drect | Full cone | ascending or desc | symmetric
		# Direct 	| _dir 	| reversal 	| reversal	 		| reversal
		# Full cone | _dir 	| hole 		| multi hole 		| udp hole
		# D/ascen.. | _dir 	| multi hole| udp hole 			| relay
		# Symmetric	| _dir 	| udp hole 	| relay 			| relay
		# --------------------------------------------------------------------
		# if connect not work, it will connect via udp hole --> relay
		#

		_direct 	= "DRT"		# a connect direct to b
		_lssv 		= "LSV"		# listen if ssh port change
		_listen 	= "LIS"		# listenning of a
		_revers 	= "REV" 	# b connect direct to b
		_hole		= "HOL"		# hole punching
		_mhole		= "MHO"		# multi hole punching
		_mholed		= "MHD"		# multi hole punching use the connect via acessding port
		_uhole		= "UHO"		# multi hole punching use udp connect
		_relay 		= "REL"		# use relay server

		# a connect direct to b
		# if port 22 on b not working, connect via _port
		if _work == _direct:
			sock = self.connect_direct(_addr, 22)
			if sock:
				return 22
			# if ssh port is not allow, then use peer port
			sock = self.connect_direct(_addr, _port)
			if sock:
				return sock
			return False

		# a listening on port when a on the internet
		# b listenning on port when port 22 not working
		if _work == _listen or _work == _lssv:
			sock = self.listen(myport)
			if sock:
				return sock
			return False

		# b connect direct to a, then a use this connect to ssh to b
		if _work == _revers:
			sock = self.connect_direct(_addr, _port)
			if sock:
				return sock
			return False
		# a and b connect TCP hole punching
		if _work == _hole:
			sock = self.hole_connecting(myport, _addr, _port)
			if sock:
				return sock
			return False
		# a and b connect TCP multi hole punching when port ascending
		if _work == _mhole:
			sock = self.asc_hole_connect(myport, _addr, _port)
			if sock:
				return sock
			return False

		# a and b connect TCP multi hole punching when port descending
		if _work == _mholed:
			sock = self.desc_hole_connect(myport, _addr, _port)
			if sock:
				return sock
			return False

		# a and b connect UDP hole punching
		if _work == _uhole:
			sock, target = self.udp_hole_connect(myport, _addr, _port)
			if sock:
				return sock, target
			return False, False
		return False

	def get_connect_client(self, exaddr, addr, port, laddr, lport, work, myport):
		""" get port connected of client side """
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(("", 0))
		a, p = sock.getsockname()
		

		## connect if same nat
		if exaddr == addr:
			conn = self.connect_local(laddr, lport)
			if conn:
				conndr = self.connect_direct(laddr, 22)
				if conndr:
					conn.send('F')
					conndr.close()
					sock.close()
					return 22
				conn.send('T')
				thread.start_new_thread(self.listen_tcp, (sock, conn))
				return p



		## connect if different nat

		# use udp hole punching
		if work == "UHO":
			conn, target = self.get_connect_process(myport, addr, port, work)
		else:
			conn = self.get_connect_process(myport, addr, port, work)
		# use tcp hole punching
		if conn:
			# connect direct to port 22
			if conn == 22:
				sock.close()
				return 22
			# udp hole punching
			if work == "UHO":
				thread.start_new_thread(self.listen_udp, (sock, conn, target))
				return p
			# tcp hole punching
			thread.start_new_thread(self.listen_tcp, (sock, conn))
			return p

		# if can not connect peer to peer use hole punching
		# connect use relay server
		else:
			conn = self.relay_connect()
			if conn:				
				thread.start_new_thread(self.listen_tcp, (sock, conn))
				return p

		# if server had down or peer had disconnect
		# connect false
		return False
	def get_connect_server(self, exaddr, addr, port, work, myport):
		""" get port connected of client side """
		## get connection to ssh server
		sock = self.connect_direct(SSH_SERVER, SSH_PORT)
		if not sock:
			print "not ssh"
			return False
		## connect if same nat
		if exaddr == addr:
			conn = self.accept_local(myport)
			if conn:
				# if a can connect direct to port 22 of server
				if conn == 10:
					sock.close()
					return True
				# if port 22 had change to other port
				# relay port to ssh port				
				thread.start_new_thread(self.tcp_forward, (sock, conn))
				thread.start_new_thread(self.tcp_forward, (conn, sock))
				return True


		## connect if different nat

		# use udp hole punching
		if work == "UHO":
			conn, target = self.get_connect_process(myport, addr, port, work)
		else:
			conn = self.get_connect_process(myport, addr, port, work)
		## can connect to peer to peer
		if conn:
			if work == "UHO":
				thread.start_new_thread(self.udp_tcp_forward, (conn, target, sock))
				thread.start_new_thread(self.tcp_udp_forward, (sock, conn, target))
				return True
			thread.start_new_thread(self.tcp_forward, (sock, conn))
			thread.start_new_thread(self.tcp_forward, (conn, sock))
			return True
		else:

		## can not connect peer to peer
		# use relay server
			conn = self.relay_connect()
			if conn:				
				thread.start_new_thread(self.tcp_forward, (conn, sock))
				thread.start_new_thread(self.tcp_forward, (sock, conn))
				return True
		## if can not connect peer to peer
		# connect false
		return False
