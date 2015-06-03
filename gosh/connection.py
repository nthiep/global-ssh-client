#!/usr/bin/env python
#
# Name:			connection module
# Description:	create connection peer to peer or relay
#

import sys, thread, socket, json, getpass, uuid, time, struct
from ConfigParser import SafeConfigParser
from select import select
from gosh import JsonSocket
from gosh import config
from gosh.config import logger
class Connection(object):
	"""docstring for Connection"""
	def __init__(self, session):
		self.session	= session
		self.dest_port 		= 22
		self.tcp_timeout	= 5.0
		self.udp_timeout 	= 10.0
	def get_accept_connect(self, machine):
		""" request connection to peer """
		reload(config)
		if (config.MAC_ACCESS == 'true' and machine.lower() not in config.MAC_LIST) \
			or (config.MAC_ACCESS == 'false' and machine.lower() in config.MAC_LIST):
			data = {"request": "accept_connect", "session": self.session,
					"id_machine": config.ID_MACHINE, "mac_accept": False}
			connect = JsonSocket(JsonSocket.TCP)
			connect.connect(config.SERVER, config.PORT)
			connect.send_obj(data)
			data = connect.read_obj()
			logger.debug("get_accept_connect: not accept machine")
			connect.close()
			return False
		else:
			connect = JsonSocket(JsonSocket.TCP)
			connect.set_reuseaddr()
			if connect.connect(config.SERVER, config.PORT):			
				laddr, lport = connect.getsockname()
				data = {"request": "accept_connect", "session": self.session,
				"lport": lport, "laddr": laddr, "id_machine": config.ID_MACHINE, "mac_accept": True}			
				connect.send_obj(data)
				logger.debug("get_accept_connect: had send request")
				data = connect.read_obj()
				logger.debug("get_accept_connect: recv %s" %str(data))
				connect.close()
				if not data["response"]:
					return False
				return (data, laddr, lport)
			return False
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
		sys.exit(1)

	def udp_tcp_forward(self, udp, target, tcp):
		data = ' '		
		while data:
			try:				
				data, addr = udp.recvfrom(1024)
				if data == self.session:
						continue
				if len(data) > 1:
					tcp.sendall(data)
				else:
					print data
			except Exception as e:
				print e
				logger.debug("udp-tcp: disconnect")
				break
		sys.exit(1)
	def tcp_udp_forward(self, tcp, udp, target):
		data = ' '
		while data:
			try:				
				data = tcp.recv(1024)
				udp.sendto(data, target)
			except Exception as e:
				print e
				logger.debug("udp-tcp: disconnect")
				break
		sys.exit(1)


	def accept_local(self, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(("", port))
		sock.settimeout(self.tcp_timeout)
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
		sock.settimeout(self.tcp_timeout)
		if not sock.connect_ex((addr, port)):			
			logger.debug("connect_direct: connected to %s:%d" %(addr, port))
			sock.settimeout(None)
			return sock

		logger.debug("accept_local: can not connect to %s:%d" %(addr, port))
		return False

	def connect_local(self, addr, port):
		""" check connect right local """
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(self.tcp_timeout)
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
		sock.settimeout(self.tcp_timeout)
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
		conn.settimeout(self.tcp_timeout)
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

	def udp_hole_connect_sending(self, udp, t):
		while not self.UDP_HOLE:
			udp.sendto(self.session, self.udp_hole_addr)
			time.sleep(t)
	def udp_hole_connect(self):
		connect = JsonSocket(JsonSocket.TCP)
		if not connect.connect(config.SERVER, config.PORT):
			return False

		send_obj = ({"request": "udp_hole", "session": self.session})
		connect.send_obj(send_obj)
		logger.debug("udp_hole_connect: request to server")
		recv_obj = connect.read_obj()
		print recv_obj
		port = recv_obj["port"]
		logger.debug("udp_hole_connect: recv port from server: %d" %port)
		# stating udp hole punching

		logger.debug("udp_hole_connect: stating connection")
		udp = JsonSocket(JsonSocket.UDP)
		req = {"session": self.session}
		udp.set_timeout(self.udp_timeout)
		udp.connect(config.SERVER, port)
		udp.send_obj( req )		
		logger.debug("udp_hole_connect: send udp to server %d" %port)
		try:
			peer = udp.read_obj()
		except:
			logger.debug("udp_hole_connect: peer not response")
			return False
		print peer
		logger.debug("udp_hole_connect: recv %s:%s" %(peer["host"], peer["port"]))
		udp = udp.get_conn()
		udp.sendto(self.session, (peer["host"], int(peer["port"])))
		logger.debug("udp_hole_connect: udp sendto peer")
		self.UDP_HOLE = False
		self.udp_hole_addr = (peer["host"], int(peer["port"]))
		thread.start_new_thread(self.udp_hole_connect_sending, (udp, 0.2))
		try:
			data, self.udp_hole_addr = udp.recvfrom( 1024 )
			logger.debug("udp_hole_connect: recvfrom peer %s:%d" %self.udp_hole_addr)
		except Exception, e:
			print e
			logger.debug("udp_hole_connect: can not connect")
			self.UDP_HOLE = True
			return False
		if data == self.session:
			udp.sendto(self.session, self.udp_hole_addr)
			logger.debug("udp_hole_connect: got connection")
			udp.settimeout(None)
			self.UDP_HOLE = True
			return (udp, self.udp_hole_addr)

		self.UDP_HOLE = True
		logger.debug("udp_hole_connect: can not connect")
		return False
	def relay_connect(self):
		""" connect to relay server """
		# get request connect to relay server
		connect = JsonSocket(JsonSocket.TCP)
		if connect.connect(config.SERVER, config.PORT):
			send_obj = ({"request": "relay", "session": self.session})
			connect.send_obj(send_obj)
			logger.debug("relay_connect: send request to server")

			# had connect relay
			return connect.get_conn()
		# can not connect to server

		logger.debug("relay_connect: can not relay connect")
		return False

	def get_connect_process(self, myport, addr, port, work):
		""" process data and connect method """

		# connect table of different nat RFC 3489
		#----------------------------------------------------------------------------------
		# NATA/NATB	| Drect | Full cone | Restricted Cone 	| Port Restricted 	| symmetric
		# Direct 	| dir 	| reversal 	| reversal	 		| reversal			| reversal
		# Full cone | dir 	| direct	| reversal	 		| reversal			| reversal
		# R Cone 	| dir 	| direct 	| udp hole 			| udp hole			| udp hole
		# P R Cone	| dir 	| direct 	| udp hole			| udp hole			| relay
		# Symmetric	| dir 	| direct 	| udp hole 			| relay				| relay
		# --------------------------------------------------------------------------------
		# if connect not work, it will connect via udp hole --> relay
		# nat type 1 - 12 view RFC 5389, RFC 5780
		# nat tcp type 1-5 and 10
		# connect table of different nat RFC 5780
		# NATA/NATB

		DIRECT 	= "DRT"		# a connect direct to b
		LSSV	= "LSV"		# listen if ssh port change
		LISTEN 	= "LIS"		# listenning of a
		REVERS 	= "REV" 	# b connect direct to b
		THOLE	= "THO"		# hole punching
		MHOLE	= "MHO"		# multi hole punching
		MHOLED	= "MHD"		# multi hole punching use the connect via acessding port
		UHOLE	= "UHO"		# multi hole punching use udp connect
		RELAY 	= "REL"		# use relay server

		logger.debug("connect_process: work %s" %work)
		# a connect direct to b
		# if port 22 on b not working, connect via port
		if work == DIRECT:
			sock = self.connect_direct(addr, self.dest_port)
			logger.debug("connect_process: direct to %s port 22" %addr)
			if sock:				
				logger.debug("connect_process: connected")
				return self.dest_port
			# if ssh port is not allow, then use peer port
			logger.debug("connect_process: not connect port 22")
			sock = self.connect_direct(addr, port)			
			logger.debug("connect_process: direct to port %d" %port)
			if sock:
				logger.debug("connect_process: connected")
				return sock

			logger.debug("connect_process: not connect direct")
			return False

		# a listening on port when a on the internet
		# b listenning on port when ssh port not working
		if work == LISTEN or work == LSSV:

			logger.debug("connect_process: listenning my port %d" %myport)
			sock = self.listen(myport)
			if sock:
				logger.debug("connect_process: got connection")
				return sock

			logger.debug("connect_process: not connection")
			return False

		# b connect direct to a, then a use this connect to ssh to b
		if work == REVERS:

			logger.debug("connect_process: connect reversal %s:%d" %(addr, port))
			sock = self.connect_direct(addr, port)
			if sock:				
				logger.debug("connect_process: got connection")
				return sock

			logger.debug("connect_process: not connection")
			return False
		# a and b connect TCP hole punching
		if work == THOLE:
			logger.debug("connect_process: hole connect")
			sock = self.hole_connecting(myport, addr, port)
			if sock:
				logger.debug("connect_process: got connection")
				return sock				
			logger.debug("connect_process: not connect")
			return False
		# a and b connect TCP multi hole punching when port ascending
		if work == MHOLE:
			logger.debug("connect_process: multi hole asc connect")
			sock = self.asc_hole_connect(myport, addr, port)
			if sock:
				logger.debug("connect_process: got connection")
				return sock
			logger.debug("connect_process: not connection")
			return False

		# a and b connect TCP multi hole punching when port descending
		if work == MHOLED:
			logger.debug("connect_process: multi hole desc connect")
			sock = self.desc_hole_connect(myport, addr, port)
			if sock:
				logger.debug("connect_process: got connection")
				return sock
			logger.debug("connect_process: not connection")
			return False

		# a and b connect UDP hole punching
		if work == UHOLE:
			logger.debug("connect_process: udp hole punching connect")
			result = self.udp_hole_connect()
			if result:
				conn, target = result
				logger.debug("connect_process: got connection")
				return conn, target

			logger.debug("connect_process: not connection")
			return False, False

		logger.debug("connect_process: request relay connect")
		return False

	def get_connect_client(self, exaddr, addr, port, laddr, lport, work, myport, dest_port, bind_source):
		""" get port connected of client side """
		if work == 'REV':
			work == 'LIS'
		if dest_port:
			self.dest_port = int(dest_port)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if bind_source:
			try:
				logger.debug("connect_client: try bind on port %d" %bind_source)
				sock.bind(("", int(bind_source)))
			except:
				logger.debug("connect_client: ERROR can not bind on port %d" %bind_source)
				sock.bind(("", 0))
		else:
			sock.bind(("", 0))
		bind_addr, bind_port = sock.getsockname()
		logger.debug("connect_client: create listen port %d" %bind_port)

		## connect if same nat
		if exaddr == addr:
			logger.debug("connect_client: connect in same nat")
			conn = self.connect_local(laddr, lport)
			if conn:
				logger.debug("connect_client: got connect local")
				conndr = self.connect_direct(laddr, self.dest_port)
				if conndr:					
					logger.debug("connect_client: got connect local direct")
					conn.send('F')
					conndr.close()
					sock.close()
					return (laddr, self.dest_port)

				logger.debug("connect_client: got connect local via port")
				conn.send('T')
				thread.start_new_thread(self.listen_tcp, (sock, conn))
				return (config.LOCALHOST, bind_port)

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
			if conn == self.dest_port:
				sock.close()
				logger.debug("connect_client: connect direct direct nat")
				return (addr, self.dest_port)
			# udp hole punching
			if work == "UHO":
				logger.debug("connect_client: connection udp")
				thread.start_new_thread(self.listen_udp, (sock, conn, target))
				return (config.LOCALHOST, bind_port)
			# tcp hole punching

			logger.debug("connect_client: connection tcp")
			thread.start_new_thread(self.listen_tcp, (sock, conn))
			return (config.LOCALHOST, bind_port)

		# if can not connect peer to peer use hole punching
		# connect use relay server
		else:
			logger.debug("connect_client: relay connect")
			conn = self.relay_connect()
			if conn:
				logger.debug("connect_client: got relay connection")				
				thread.start_new_thread(self.listen_tcp, (sock, conn))
				return (config.LOCALHOST, bind_port)

		logger.debug("connect_client: not connection to peer")
		# if server had down or peer had disconnect
		# connect false
		return False
	def get_connect_server(self, exaddr, addr, port, work, myport, dest_port):
		""" get port connected of client side """
		## get connection to ssh server
		if work == 'DRT':
			work == 'LSV'
		if not dest_port:
			dest_port = config.SSH_PORT

		sock = self.connect_direct(config.SSH_SERVER, dest_port)

		if not sock:
			logger.debug("connect_server: can not connect ssh server %d" %dest_port)
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
				logger.debug("connect_server: connect udp hole punching")
				thread.start_new_thread(self.udp_tcp_forward, (conn, target, sock))
				thread.start_new_thread(self.tcp_udp_forward, (sock, conn, target))
				return True

			logger.debug("connect_server: connect tcp hole punching")
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
			logger.debug("connect_server: not relay connection")
		## if can not connect peer to peer
		# connect false

		logger.debug("connect_server: not connection")
		return False

#=============================================================================
#   END CONNECTION
# ============================================================================