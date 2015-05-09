#!/usr/bin/env python
#
# Name:			cl_bind
# Description:	create connect and forward to ssh port
#

import sys, thread, socket, json, getpass, uuid, time, struct
from ConfigParser import SafeConfigParser
from select import select
from gsh import JsonSocket
from gsh.config import *

class Connection(object):
	"""docstring for Connection"""
	def __init__(self, session):
		self.session	= session
		self.sport 		= 22
	def get_accept_connect(self):
		""" request connection to peer """
		connect = JsonSocket(JsonSocket.TCP)
		connect.set_reuseaddr()
		if not connect.connect(SERVER, PORT):
			return False
		laddr, lport = connect.getsockname()
		data = {"request": "accept_connect", "session": self.session,
		"lport": lport, "laddr": laddr, "mac": MAC_ADDR}
		connect.send_obj(data)
		logger.debug("get_accept_connect: had send request")
		data = connect.read_obj()
		logger.debug("get_accept_connect: recv %s" %str(data))
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
					logger.debug("tcp_forward: disconnect")
					source.shutdown(socket.SHUT_RD)
					destination.shutdown(socket.SHUT_WR)
			except Exception as e:
				logger.debug("tcp_forward: disconnect %s" %str(e))
				break

	def udp_tcp_forward(self, udp, target, tcp):
		data = ' '		
		while data:
			try:				
				data, addr = udp.recvfrom(1024)
				if data:
					if data == self.session:
						continue
					if len(data) > 1:
						tcp.sendall(data)
					else:
						print data
				else:
					logger.debug("udp-tcp: disconnect")
					udp.shutdown(socket.SHUT_RD)
					tcp.shutdown(socket.SHUT_WR)
			except Exception as e:
				logger.debug("udp-tcp: disconnect")
				break
	def tcp_udp_forward(self, tcp, udp, target):
		data = ' '
		while data:
			try:				
				data = tcp.recv(1024)
				udp.sendto(data, target)
			except Exception as e:
				logger.debug("udp-tcp: disconnect")
				break


	def accept_local(self, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(("", port))
		sock.settimeout(2.0)
		sock.listen(5)

		logger.debug("accept_local: listening on port %d" %port)
		try:
			conn, addr = sock.accept()			
			logger.debug("accept_local: accept connect %s:%d" %addr)
			conn.send(self.session)
			res = conn.recv(1024)
			if res == 'F':
				conn.close()
				sock.close()				
				logger.debug("accept_local: disconnect")
				return 10
			sock.settimeout(None)			
			logger.debug("accept_local: return connect")
			return conn
		except:			
			logger.debug("accept_local: not connection")
			return False

	def connect_direct(self, addr, port):
		""" connect to via direct """
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if not sock.connect_ex((addr, port)):			
			logger.debug("connect_direct: connected to %s:%d" %(addr, port))
			return sock

		logger.debug("accept_local: can not connect to %s:%d" %(addr, port))
		return False

	def connect_local(self, addr, port):
		""" check connect right local """
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(2.0)
		if not sock.connect_ex((addr, port)):			
			logger.debug("connect_local: connected to %s:%d" %(addr, port))
			data = sock.recv(1024)
			if data == self.session:
				sock.settimeout(None)				
				logger.debug("connect_local: connect true machine")
				return sock		
		logger.debug("connect_local: can not connect to %s:%d" %(addr, port))
		return False
	def listen_udp(self, lssock, udpsock, target):
		lssock.listen(5)		
		logger.debug("listen_udp: listening on port %d" %(lssock.getsockname()[1]))
		try:
			conn, addr = lssock.accept()			
			logger.debug("listen_udp: got connection from %s:%d" %addr)
			thread.start_new_thread(self.udp_tcp_forward, (udpsock, target, conn))
			thread.start_new_thread(self.tcp_udp_forward, (conn, udpsock, target))
			return True
		except Exception, e:			
			logger.debug("listen_udp: got error %s" %str(e))
		logger.debug("listen_udp: not connection")
		return False
	def listen_tcp(self, lssock, connsock):
		lssock.listen(5)		
		logger.debug("listen_tcp: listening on port %d" %(lssock.getsockname()[1]))
		try:
			conn, addr = lssock.accept()			
			logger.debug("listen_tcp: got connection %s:%d" %addr)
			thread.start_new_thread(self.tcp_forward, (connsock, conn))
			thread.start_new_thread(self.tcp_forward, (conn, connsock))
			return True
		except Exception, e:			
			logger.debug("listen_tcp: error %s" %str(e))
		return False
	def listen(self, myport):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(2.0)
		sock.bind(("", myport))		
		logger.debug("listen: listening on port %d" %myport)
		sock.listen(5)
		try:
			conn, addr = sock.accept()			
			logger.debug("listen: got connection form %s:%d" %addr)
			return conn
		except:
			pass
		logger.debug("listen: not connection")
		return False
	def hole_connecting(self, myport, addr, port):
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		conn.bind(("", myport))		
		logger.debug("hole_connecting: listening %d" %myport)
		logger.debug("hole_connecting: connect to %s:%d" %(addr, port))
		err = 1
		i = 0
		conn.settimeout(5.0)
		while err != 0 and i < 10:
			err = conn.connect_ex((addr, port))			
			logger.debug("hole_connecting: trying connect %d" %i)
			i += 1
		if err == 0:			
			conn.settimeout(None)			
			logger.debug("hole_connecting: got connection")
			return conn		
		logger.debug("hole_connecting: can not connection")
		return False

	def _multi_connect(self, myport, addr, port):
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)		
		conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		logger.debug("multi_connect: connection port %d" %port)
		conn.bind(("", myport))
		conn.settimeout(1.0)
		if conn.connect_ex((addr, port)) == 0:			
			logger.debug("multi_connect: got connection")
			return conn

		logger.debug("multi_connect: can not connection")
		return False

	def asc_hole_connect(self, myport, addr, port):
		i=0
		conn = False
		while not conn and i < 10:
			conn = self._multi_connect(myport, addr, port)			
			logger.debug("asc_hole_connect: trying connect %d" %i)
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
			logger.debug("desc_hole_connect: trying connect %d" %i)
			port -= 1
			i +=1
		if conn:
			return conn
		return False

	def udp_hole_connect(self):
		connect = JsonSocket(JsonSocket.TCP)
		if not connect.connect(SERVER, PORT):
			return False

		send_obj = ({"request": "udp_hole", "session": self.session})
		connect.send_obj(send_obj)
		logger.debug("udp_hole_connect: request to server")
		recv_obj = connect.read_obj()
		port = recv_obj["port"]		
		logger.debug("udp_hole_connect: recv port from server: %d" %port)
		# stating udp hole punching

		logger.debug("udp_hole_connect: stating connection")
		udp = JsonSocket(JsonSocket.UDP)
		req = {"session": self.session}
		udp.connect(SERVER, port)
		udp.send_obj( req )		
		logger.debug("udp_hole_connect: send udp to server %d" %port)
		peer = udp.read_obj()		
		peer = json.loads(peer)
		logger.debug("udp_hole_connect: recv %s:%s" %(peer["host"], peer["port"]))

		udp.sendto(self.session, (peer["host"], int(peer["port"])))
		logger.debug("udp_hole_connect: udp sendto peer")
		addr = (peer["host"], int(peer["port"]))
		while True:
			read,_,_ = select( [0, udp], [], [] )
			if 0 in read:
				udp.sendto(self.session, addr )
			elif udp in read:
				data, addr = udp.recvfrom( 1024 )
				logger.debug("udp_hole_connect: recvfrom peer %s:%d" %(addr))
				if data == self.session:
					udp.sendto(self.session, addr)
					logger.debug("udp_hole_connect: got connection")
					return udp, addr
		logger.debug("udp_hole_connect: can not connect")
		return False, False
	def relay_connect(self):
		""" connect to relay server """
		# get request connect to relay server
		connect = JsonSocket(JsonSocket.TCP)
		if connect.connect(SERVER, PORT):
			send_obj = ({"request": "relay", "session": self.session})
			connect.send_obj(send_obj)
			logger.debug("relay_connect: send request to server")

			# had connect relay
			return connect.get_conn()
		# can not connect to server

		logger.debug("relay_connect: can not relay connect")
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

		logger.debug("connect_process: work %s" %_work)
		# a connect direct to b
		# if port 22 on b not working, connect via _port
		if _work == _direct:
			sock = self.connect_direct(_addr, self.sport)
			logger.debug("connect_process: direct to %s port 22" %_addr)
			if sock:				
				logger.debug("connect_process: connected")
				return self.sport
			# if ssh port is not allow, then use peer port
			logger.debug("connect_process: not connect port 22")
			sock = self.connect_direct(_addr, _port)			
			logger.debug("connect_process: direct to port %d" %_port)
			if sock:
				logger.debug("connect_process: connected")
				return sock

			logger.debug("connect_process: not connect direct")
			return False

		# a listening on port when a on the internet
		# b listenning on port when ssh port not working
		if _work == _listen or _work == _lssv:

			logger.debug("connect_process: listenning my port %d" %myport)
			sock = self.listen(myport)
			if sock:
				logger.debug("connect_process: got connection")
				return sock

			logger.debug("connect_process: not connection")
			return False

		# b connect direct to a, then a use this connect to ssh to b
		if _work == _revers:

			logger.debug("connect_process: connect reversal %s:%d" %(_addr, _port))
			sock = self.connect_direct(_addr, _port)
			if sock:				
				logger.debug("connect_process: got connection")
				return sock

			logger.debug("connect_process: not connection")
			return False
		# a and b connect TCP hole punching
		if _work == _hole:
			logger.debug("connect_process: hole connect")
			sock = self.hole_connecting(myport, _addr, _port)
			if sock:
				logger.debug("connect_process: got connection")
				return sock				
			logger.debug("connect_process: not connect")
			return False
		# a and b connect TCP multi hole punching when port ascending
		if _work == _mhole:
			logger.debug("connect_process: multi hole asc connect")
			sock = self.asc_hole_connect(myport, _addr, _port)
			if sock:
				logger.debug("connect_process: got connection")
				return sock
			logger.debug("connect_process: not connection")
			return False

		# a and b connect TCP multi hole punching when port descending
		if _work == _mholed:
			logger.debug("connect_process: multi hole desc connect")
			sock = self.desc_hole_connect(myport, _addr, _port)
			if sock:
				logger.debug("connect_process: got connection")
				return sock
			logger.debug("connect_process: not connection")
			return False

		# a and b connect UDP hole punching
		if _work == _uhole:
			logger.debug("connect_process: udp hole punching connect")
			sock, target = self.udp_hole_connect()
			if sock:
				logger.debug("connect_process: got connection")
				return sock, target

			logger.debug("connect_process: not connection")
			return False, False

		logger.debug("connect_process: request relay connect")
		return False

	def get_connect_client(self, exaddr, addr, port, laddr, lport, work, myport, sport):
		""" get port connected of client side """
		if sport:
			self.sport = int(sport)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(("", 0))
		a, p = sock.getsockname()
		logger.debug("connect_client: create listen port %d" %p)

		## connect if same nat
		if exaddr == addr:
			logger.debug("connect_client: connect in same nat")
			conn = self.connect_local(laddr, lport)
			if conn:
				logger.debug("connect_client: got connect local")
				conndr = self.connect_direct(laddr, self.sport)
				if conndr:					
					logger.debug("connect_client: got connect local direct")
					conn.send('F')
					conndr.close()
					sock.close()
					return self.sport

				logger.debug("connect_client: got connect local via port")
				conn.send('T')
				thread.start_new_thread(self.listen_tcp, (sock, conn))
				return p

			logger.debug("connect_client: not connect local")


		logger.debug("connect_client: connection different nat")
		## connect if different nat

		# use udp hole punching
		if work == "UHO":
			conn, target = self.get_connect_process(myport, addr, port, work)
		else:
			conn = self.get_connect_process(myport, addr, port, work)
		# use tcp hole punching
		if conn:
			logger.debug("connect_client: got connection")
			# connect direct to port 22
			if conn == self.sport:
				sock.close()
				return self.sport
			# udp hole punching
			if work == "UHO":
				logger.debug("connect_client: connection udp")
				thread.start_new_thread(self.listen_udp, (sock, conn, target))
				return p
			# tcp hole punching

			logger.debug("connect_client: connection tcp")
			thread.start_new_thread(self.listen_tcp, (sock, conn))
			return p

		# if can not connect peer to peer use hole punching
		# connect use relay server
		else:
			logger.debug("connect_client: relay connect")
			conn = self.relay_connect()
			if conn:
				logger.debug("connect_client: got relay connection")				
				thread.start_new_thread(self.listen_tcp, (sock, conn))
				return p

		logger.debug("connect_client: not connection")
		# if server had down or peer had disconnect
		# connect false
		return False
	def get_connect_server(self, exaddr, addr, port, work, myport, sport):
		""" get port connected of client side """
		## get connection to ssh server
		if sport.isdigit():
			sport = int(sport)
		else:
			sport = SSH_PORT

		sock = self.connect_direct(SSH_SERVER, sport)

		if not sock:
			logger.debug("connect_server: can not connect ssh server %d" %sport)
			return False
		## connect if same nat
		if exaddr == addr:			
			logger.debug("connect_server: connect local")
			conn = self.accept_local(myport)
			if conn:
				# if a can connect direct to port 22 of server
				if conn == 10:
					sock.close()					
					logger.debug("connect_server: got connect local")
					return True
				# if port 22 had change to other port
				# relay port to ssh port				
				logger.debug("connect_server: got connect local via port")				
				thread.start_new_thread(self.tcp_forward, (sock, conn))
				thread.start_new_thread(self.tcp_forward, (conn, sock))
				return True
			logger.debug("connect_server: not connect local")


		## connect if different nat

		logger.debug("connect_server: connect different nat")
		# use udp hole punching
		if work == "UHO":
			conn, target = self.get_connect_process(myport, addr, port, work)
		else:
			conn = self.get_connect_process(myport, addr, port, work)
		## can connect to peer to peer
		if conn:
			if work == "UHO":
				logger.debug("connect_server: connect udp")
				thread.start_new_thread(self.udp_tcp_forward, (conn, target, sock))
				thread.start_new_thread(self.tcp_udp_forward, (sock, conn, target))
				return True

			logger.debug("connect_server: connect tcp")
			thread.start_new_thread(self.tcp_forward, (sock, conn))
			thread.start_new_thread(self.tcp_forward, (conn, sock))
			return True
		else:
			logger.debug("connect_server: got relay connection")
			## can not connect peer to peer
			# use relay server
			conn = self.relay_connect()
			if conn:
				logger.debug("connect_server: got connect relay")				
				thread.start_new_thread(self.tcp_forward, (conn, sock))
				thread.start_new_thread(self.tcp_forward, (sock, conn))
				return True			
			logger.debug("connect_server: not connect relay")
		## if can not connect peer to peer
		# connect false

		logger.debug("connect_server: not connection")
		return False
