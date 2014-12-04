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
		print data
		data = json.loads(data)
		udp.sendto("1", (data["host"], int(data["port"])))		
		udp.sendto("1", (data["host"], int(data["port"])))
		print "udp sendto", data["host"],":", data["port"]
		return int(data["port"])
	def tcp_udp(self, tcp, udp, target):
		tcp.listen(5)
		self.conn, addr = tcp.accept()
		print "accept connected", addr
		data = ' '
		while data:
			try:				
				data = self.conn.recv(1024)
				if data:
					udp.sendto(data, target)
				else:
					self.conn.shutdown(socket.SHUT_RD)
					udp.shutdown(socket.SHUT_WR)
			except Exception as e:
				print "Exception forward tcp-udp", e
				break
		tcp.close()
	def udp_tcp(self, udp, target, tcp):
		data = ' '
		while data:
			try:				
				data, addr = udp.recvfrom(1024)
				if data:
					if len(data) > 1:
						self.conn.sendall(data)
				else:
					print "close ssh"
					udp.shutdown(socket.SHUT_RD)
					self.conn.shutdown(socket.SHUT_WR)
			except Exception as e:
				print "Exception forward udp-tcp", e
				break
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
			if 1==1 or self.nat == "RAD" or self.mynat == "RAD" or ((self.nat == "ASC" or self.nat == "DESC") and (self.mynat == "ASC" or self.mynat == "DESC")):
				udp = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
				udp.bind(("", tport))
				udp_port = self.udp_connect(udp)
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
			thread.start_new_thread(self.tcp_udp, (fw_socket, udp, (peeradd, udp_port)))
			time.sleep(0.5)
			self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connect.connect((target, tport))
			thread.start_new_thread(self.udp_tcp, (udp, (peeradd, udp_port), self.conn))
			time.sleep(0.5)
			
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
			passwd = None
			try:
				k = paramiko.RSAKey.from_private_key_file(key_path)
				if self.parser.get('config', 'passconnect') == "yes":
					passwd = getpass.getpass('%s password: ' % peeradd)
			except paramiko.PasswordRequiredException:
				password = getpass.getpass('RSA key password: ')
				try:					
					k = paramiko.RSAKey.from_private_key_file(key_path, password)
				except:
					print "wrong RSA password Key"	
					passwd = getpass.getpass('%s password: ' % peeradd)
			except:
				print "not have RSAKey"
				passwd = getpass.getpass('%s password: ' % peeradd)

			print('*** Connecting... ***')
			if passwd is not None:
				client.connect(target, tport, username = self.user, password = passwd, sock=self.connect)
			else:
				client.connect(target, tport, username = self.user, pkey = k, sock=self.connect)

			chan = client.invoke_shell()
			print('***  Global SSH: ssh connected ***\n')
			conn = True
			while conn:
				cl_interactive.interactive_shell(chan)
				conn = False
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