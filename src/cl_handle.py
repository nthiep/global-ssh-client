import json
from threading import Thread
from ConfigParser import SafeConfigParser
from cl_bind import Bind
import cl_global
from websocket import create_connection
class Handle(Thread):
	"""docstring for Handle"""
	def __init__(self, username, password, address):
		super(Handle, self).__init__()
		self.daemon = True
		self.username = username
		self.password = password
		self.address = address
		self.parser = SafeConfigParser()
		self.parser.read('cl_config.cfg')
		self.sock_host = "ws://%s:%s" % (self.parser.get('websv', 'server'),self.parser.get('websv', 'port'))
		
	def process(self, data):
			info = json.load(data)
			if info['status'] == 200:
				hashcode = info['hashcode']
				peer = info['peer']
				address = info['address']
				localadd = info['localadd']

				connbind = Bind(hashcode, peer, address, localadd)
				connbind.start()

	def run(self):
		sock_path = self.sock_host + "/socklogin"
		ws = create_connection(sock_path)
		info = json.dumps({"username" : self.username, "password": self.password, "address": self.address})
		ws.send(info)
		while True:
			result =  ws.recv()
		ws.close()
