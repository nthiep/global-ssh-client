from threading import Thread
import sys, socket
import getpass
from paramiko.py3compat import input
import paramiko
import traceback
try:
    import cl_interactive
except ImportError:
    from . import cl_interactive
paramiko.util.log_to_file('cl_ssh.log')
class SSH(Thread):
	"""docstring for ssh"""
	def __init__(self, hashcode, me, port, peer, address, localadd):	
		super(SSH, self).__init__()
		self.hashcode = hashcode
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
		while err != 0 and i <10:
			err = self.s.connect_ex((target, self.port + 1))
			i +=1
		print "ssh connected to %s:%d" % (target, self.port + 1)
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			print('*** Connecting... ***')
			client.connect(target, self.port +1 , sock=self.s)			
			chan = client.invoke_shell()
			print('***  Global SSH: ssh connected ***\n')
			conn = True
			while conn:
				cl_interactive.interactive_shell(chan)
				conn = False
			chan.close()
			client.close()			
			return False
		except Exception as e:
			print('*** Caught exception: %s: %s' % (e.__class__, e))
			traceback.print_exc()
			try:
				client.close()
			except:
				pass
			sys.exit(1)