#!/usr/bin/env python
#
# Name:			cl_ssh
# Description:	ssh connection
#

from threading import Thread
import sys, socket, os, thread, time, json
import getpass
from ConfigParser import SafeConfigParser
os.sys.path.append('../client')
import paramiko
import traceback
try:
    import cl_interactive
except ImportError:
    from . import cl_interactive
paramiko.util.log_to_file('cl_ssh.log')
class SSH(Thread):
	"""docstring for ssh"""
	def __init__(self, session, user, lport, laddr, port, addr, me, myport, nat, mynat):	
		super(SSH, self).__init__()
		self.user = user
		self.lport = lport
		self.laddr = laddr
		self.port = port
		self.addr = addr
		self.me = me
		self.myport = myport
		self.nat = nat
		self.mynat = mynat
		self.connect = None
		self.session = session
		self.conn = None
		self.parser = SafeConfigParser()
		self.parser.read('cl_config.conf')
	def listen(self, port):		
		ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)		
		ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		ls.bind(("", port))
		print "listen on " ,port
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
	def tcp_udp(self, tcp, udp, target):
		tcp.listen(5)
		conn, addr = tcp.accept()
		print "accept connected", addr
		data = ' '
		thread.start_new_thread(self.udp_tcp, (udp, target, conn))
		while data:
			data = conn.recv(1024)
			if data:
				udp.sendto(data, target)
			else:
				print "close tcp-udp"
				conn.shutdown(socket.SHUT_RD)
				udp.shutdown(socket.SHUT_WR)
	def udp_tcp(self, udp, target, tcp):
		data = ' '
		while data:
			data, addr = udp.recvfrom(1024)
			if data:
				tcp.sendall(data)
			else:
				print "close udp_tcp"
				udp.shutdown(socket.SHUT_RD)
				tcp.shutdown(socket.SHUT_WR)

	def run(self):
		connlan = False
		connudp = False
		if self.me == self.addr:
			print "connect in LAN"		
			t = Thread(target=self.listen, args = (self.myport,))
			t.daemon = True
			t.start()
			target = self.laddr
			tport = self.lport
			check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			time.sleep(0.5)
			if check.connect_ex((target, tport)) == 0 and self.connect is None:
				connlan = True
				self.connect = check
				print "connected to %s:%d" % (target, tport)
		elif not connlan:
			target = self.addr
			tport = self.port
			if self.nat == "RAD" or self.mynat == "RAD" or ((self.nat == "ASC" or self.nat == "DESC") and (self.mynat == "ASC" or self.mynat == "DESC")):
				udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				udp.bind(("", tport))
				udp_target = self.udp_connect(udp)
				connudp = True
			else:				
				t = Thread(target=self.listen, args = (self.myport,))
				t.daemon = True
				t.start()
				if self.nat == "None":
					self.connecting(self.myport, target, tport, True)
				elif self.nat == "ASC":
					i=0
					while self.connect is None and i<10:
						self.connecting(self.myport, target, tport, False)
						tport +=1
						i +=1
				else:
					i=0
					while self.connect is None and i<10 and tport>0:
						self.connecting(self.myport, target, tport, False)
						tport -=1
						i+=1
		if self.connect == None and not connudp:
			print "can't connect"
			sys.exit(1)

		peeradd = target
		if connudp:
			target = "127.0.0.1"
			fw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			fw_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			fw_socket.bind(("", tport))
			thread.start_new_thread(self.tcp_udp, (fw_socket, udp, udp_target))
			
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
			passwd = None
			k = None
			try:
				if self.parser.get('config', 'passconnect') == "yes":
					raise
				k = paramiko.RSAKey.from_private_key_file(key_path)
			except paramiko.PasswordRequiredException:
				password = getpass.getpass('RSA key password: ')
				try:					
					k = paramiko.RSAKey.from_private_key_file(key_path, password)
				except:
					print "wrong RSA password Key"	
					passwd = getpass.getpass('%s password: ' % peeradd)
			except:
				passwd = getpass.getpass('%s password: ' % peeradd)

			print('*** Connecting... ***')
			client.connect(target, tport, username = self.user, password = passwd, pkey = k, sock=self.connect)

			chan = client.invoke_shell()
			print('***  Global SSH: ssh connected ***\n')
			conn = True
			while conn:
				cl_interactive.interactive_shell(chan)
				conn = False
			print "interactive_shell break"
			chan.close()
			client.close()
		except paramiko.AuthenticationException:
			print "Authentication False"
			sys.exit(1)
		except Exception as e:
			print('*** Caught exception: %s: %s' % (e.__class__, e))
			traceback.print_exc()
			try:
				client.close()
			except:
				pass
			sys.exit(1)
