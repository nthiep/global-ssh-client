from threading import Thread
import sys
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
	def __init__(self, hashcode, peer, address, localadd):	
		super(SSH, self).__init__()
		self.hashcode = hashcode
		self.peer = peer
		self.address = address
		self.localadd = localadd

	def run(self):

		self.s.bind(("", lop))
		self.s.connect_ex(target)
		print "ssh connected to %s:%d" % target		
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			print('*** Connecting... ***')
			"""
			try:
				client.connect(tgh, tgp, sock=self.s)
			except:
				print "Error: SSH via public key False"
			"""
			client.connect(tgh, tgp, "hiep", ";'", sock=self.s)			
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