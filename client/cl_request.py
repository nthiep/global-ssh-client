#!/usr/bin/env python
#
# Name:			cl_request
# Description:	process request
#

import sys, os, socket, random, hashlib, time, urllib2, json, base64, uuid
from cl_handle import Handle
import cl_global
from ConfigParser import SafeConfigParser
from cl_ssh import SSH
class Request(object):
	"""send request to server"""
	def __init__(self):
		self.parser = SafeConfigParser()
		self.parser.read('cl_config.conf')		#read config file
		self.connection = None					#connection handle
		self.token = self.parser.get('config', 'token')
		try:
			self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
		except:
			self.mac = str(hex(uuid.getnode()))
	def login(self):							#login server by token and check NAT
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		lport = s.getsockname()[1]
		s.send(json.dumps({"request": "login", "token": self.token, "mac": self.mac, "lport": lport, "host": socket.gethostname()}))
		res = s.recv(1024)
		res = json.loads(res)
		if "status" in res:
			if res["status"] == "check":
				sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sc.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
				sc.send(json.dumps({"request": "checknat", "token": self.token, "mac": self.mac, "host": socket.gethostname()}))
				resc = sc.recv(1024)
				resc = json.loads(resc)
				if "status" in resc:
					if resc["status"] == "error":
						return False
				else:
					cl_global.listpeer = resc
					self.connection = sc
					hd = Handle(sc)
					hd.start()
					s.close()
					return True
			elif res["status"] == "error":
				return False
		else:
			cl_global.listpeer = res
			self.connection = s
			hd = Handle(s)
			hd.start()
			return True
		return False
	def checkpeer(self, peer):
		peer -= 1
		if peer < 0:
			return False
		try:
			mac = cl_global.listpeer[peer]["mac"]
			return mac
		except:
			return False
	def connect(self, peer):					#connect to peer in list of peer
		mac = self.checkpeer(peer)
		if not mac:
			print "peer not found"
			return
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		r = random.getrandbits(128)
		session = hashlib.sha1(str(r)).hexdigest()
		laddr, lport = s.getsockname()
		s.send(json.dumps({"request": "connect", "session": session, "token": self.token, "mac": mac, "mymac": self.mac, "lport": lport, "laddr": laddr}))
		print "recv data from request"
		data = s.recv(1024)
		print data
		s.close()
		data = json.loads(data)
		connssh = SSH(data["user"], data["lport"], data["laddr"], data["port"], data["addr"], data["me"], lport, data["nat"])
		connssh.start()
		connssh.join()
	def listpeer(self):
		i=1
		for l in cl_global.listpeer:
			p = str(i) + ". " + l["host"] + "\t(" + l["mac"] +")" 
			p += ("\t"+ "(me)" if l["mac"] == self.mac else "")
			print p
			i +=1
	def uploadkey(self, peer):
		key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa.pub')
		if os.path.exists(key_path):
			mac = self.checkpeer(peer)
			if not mac:
				print "peer not found"
				return			
			try:					
				f = open(key_path, 'r')
			except:
				print "error: can't open file ~/.ssh/id_rsa.pub"
			jkey = json.dumps({"request": "upkey", "token": self.token, "mymac" : self.mac, "mac": mac, "key": f.read()})
			f.close()			
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
			s.send(jkey)
		else:
			print "you don't have public key(~/.ssh/id_rsa.pub)"

	def logs(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		s.send(json.dumps({"request": "logs", "token": self.token}))
		try:
			data = s.recv(1024)
			data = json.loads(data)
			for x in data:
				print x['time'] + "\t" + x['mac'] + " - " + x['log']
		except:
			print "error: json data"