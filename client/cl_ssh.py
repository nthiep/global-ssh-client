#!/usr/bin/env python
#
# Name:			cl_ssh
# Description:	ssh connection
#

from threading import Thread
import sys, socket, os, thread, time
import getpass
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
	def __init__(self, user, lport, laddr, port, addr, me, myport, nat):	
		super(SSH, self).__init__()
		self.user = user
		self.lport = lport
		self.laddr = laddr
		self.port = port
		self.addr = addr
		self.me = me
		self.myport = myport
		self.nat = nat
		self.connect = None
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
	def run(self):
		connlan = False

		t = Thread(target=self.listen, args = (self.myport,))
		t.daemon = True
		t.start()
		if self.me == self.addr:
			target = self.laddr
			tport = self.lport
			check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			time.sleep(0.5)
			if check.connect_ex((target, tport)) == 0 and self.connect is None:
				connlan = True
				self.connect = check
				print "connected to %s:%d" % (target, tport)
		elif not connlan:
			print "not lan"
			target = self.addr
			tport = self.port
			if self.nat == "None":
				print "NAT None"
				self.connecting(self.myport, target, tport, True)
			elif self.nat == "ASC":
				print "NAT ASC"
				i=0
				while self.connect is None and i<10:
					self.connecting(self.myport, target, tport, False)
					tport +=1
					i +=1
			else:
				print "NAT DESC"
				i=0
				while self.connect is None and i<10 and tport>0:
					self.connecting(self.myport, target, tport, False)
					tport -=1
					i+=1
		if self.connect == None:
			print "can't connect"
			sys.exit(1)
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
			passwd = None
			try:
				no = set(['no','n'])
				k = paramiko.RSAKey.from_private_key_file(key_path)
				choice = raw_input('connect by RSAKey [Yes/no]: ').lower()
				if choice in no:
					passwd = getpass.getpass('%s password: ' % target)
			except paramiko.PasswordRequiredException:
				password = getpass.getpass('RSA key password: ')
				try:					
					k = paramiko.RSAKey.from_private_key_file(key_path, password)
				except:
					print "wrong RSA password Key"	
					passwd = getpass.getpass('%s password: ' % target)
			except:
				print "not have RSAKey"
				passwd = getpass.getpass('%s password: ' % target)

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