#!/usr/bin/env python
#
# Name:			Client
# Description:	ssh client connection
#
import os, sys, getpass, time
from gosh 		import Connection
from gosh.config import logger, windows
class Client():
	"""docstring for Client"""
	def __init__(self, data, myaddr, myport, destination_user, destination_port, options, args, bind_source):	
		self.data  			= data
		self.myaddr 		= myaddr
		self.myport 		= myport
		self.destination_port 	= destination_port
		self.options		= options
		self.args 			= args
		self.bind_source 	= bind_source
		self.user = "%s@" %destination_user if destination_user else ""
	def run(self):
		external_addr 		= self.data["external"]
		addr 				= self.data["addr"]
		port 				= int(self.data["port"])
		laddr 				= self.data["laddr"]
		lport 				= int(self.data["lport"])
		work 				= self.data["work"]

		connection = Connection(self.data["session"])
		connect_address = connection.get_connect_client(external_addr,\
						addr, port, laddr, lport, work, self.myport, self.destination_port, bind_source)
		if not connect_address:
			logger.debug("client: can not connect")
			return False

		if options.bind:
			logger.debug("client: connection created at %s:%d" %connect_address)
			sys.stdout.write('* INFO: Processing...')
			while True:
				try:
					sys.stdout.write('.')
					time.sleep(10)
				except KeyboardInterrupt:
					print 'END PROCESS!'
					break
			return True
		if os.system('ssh -V') or windows:
			logger.debug("client: SSH connect use ssh client to %s:%d" %connect_address)
			self.ssh_client(connect_address)
			return True
		else:
			tunnel 	= "-L %s " %self.options.tunnel if self.options.tunnel 	else ""
			identity= "-i %s " %self.options.identity if self.options.identity 	else ""
			verbose = "-v "	 if self.options.verbose else ""
			
			arguments = tunnel + verbose + identity
			args = ' '.join(self.args[2:])
			connect_host, connect_port = connect_address
			logger.debug("client: SSH connect use open ssh to %s%s -p %d" %(self.user, connect_host, connect_port))
			os.system("ssh %s %s%s -p %d %s" % (arguments, self.user, connect_host, connect_port, args))

			return True

	def ssh_client(self, connect_address):		
		from gosh import interactive
		import paramiko
		import traceback
		paramiko.util.log_to_file( os.path.join(os.environ['HOME'], 'gosh.log'))
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
			if self.user == "":
				self.user = getpass.getuser()
			passwd = None
			key = None
			try:
				if self.parser.get('config', 'passconnect') == "yes":
					raise
				key = paramiko.RSAKey.from_private_key_file(key_path)
			except paramiko.PasswordRequiredException:
				password = getpass.getpass('RSA key password: ')
				try:					
					key = paramiko.RSAKey.from_private_key_file(key_path, password)
				except:
					print "wrong RSA password Key"	
					passwd = getpass.getpass('%s password: ' % peeradd)
			except:
				passwd = getpass.getpass('%s password: ' % peeradd)

			print('*** Global SSH Connecting... ***')
			client.connect(connect_address[0], int(connect_address[1]), username = self.user, password = passwd, pkey = key)

			chan = client.invoke_shell()
			print('*** Global SSH: SSH Connected ***\n')
			conn = True
			while conn:
				interactive.interactive_shell(chan)
				conn = False
			print "interactive shell break!"
			chan.close()
			client.close()
		except paramiko.AuthenticationException:
			print "SSH Authentication failed!"
			sys.exit(1)
		except Exception as e:
			print('*** Caught exception: %s: %s' % (e.__class__, e))
			traceback.print_exc()
			try:
				client.close()
			except:
				pass
			sys.exit(1)
#=============================================================================
#   END CLIENT
# ============================================================================