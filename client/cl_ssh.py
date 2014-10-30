#!/usr/bin/env python
#
# Name:			cl_ssh
# Description:	ssh connection
#

from threading import Thread
import sys, socket, os
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
	def __init__(self, hashcode, user, me, port, peer, address, localadd):	
		super(SSH, self).__init__()
		self.hashcode = hashcode
		self.user = user
		self.me = me
		self.port = port
		self.peer = peer
		self.address = address
		self.localadd = localadd

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def run(self):
		if self.me == self.address:
			target = self.localadd
		else:
			target = self.address
		self.s.bind(("", self.port))
		err = self.s.connect_ex((target, self.port + 1))
		i = 0
		while err != 0 and i < 20:
			err = self.s.connect_ex((target, self.port + 1))
			i += 1
		if err != 0:
			print "can't connect"
			sys.exit(1)
		print "ssh connected to %s:%d" % (target, self.port + 1)
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
			try:
				k = paramiko.RSAKey.from_private_key_file(key_path)
			except paramiko.PasswordRequiredException:
				password = getpass.getpass('RSA key password: ')
				k = paramiko.RSAKey.from_private_key_file(key_path, password)
			print('*** Connecting... ***')
			client.connect(target, self.port +1, username = self.user, pkey = k, sock=self.s)			
			chan = client.invoke_shell()
			print('***  Global SSH: ssh connected ***\n')
			conn = True
			while conn:
				cl_interactive.interactive_shell(chan)
				conn = False
			chan.close()
			client.close()
		except paramiko.AuthenticationException:
			print "ssh authentication public key failed, peer not allow public key."
		except Exception as e:
			print('*** Caught exception: %s: %s' % (e.__class__, e))
			traceback.print_exc()
			try:
				client.close()
			except:
				pass
			sys.exit(1)