from threading import Thread
import os, sys, socket, time
import getpass
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
		target = self.address
		self.s.bind(("", self.port))
		self.s.connect_ex((target, self.port + 1))
		time.sleep(1)
		print "ssh connected to %s:%d" % (target, self.port + 1)
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
			print('*** Connecting... ***')
			client.connect(target, self.port +1, username="user", password="pass", sock=self.s)			
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