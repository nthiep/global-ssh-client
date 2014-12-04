#!/usr/bin/env python
#
# Name:			cl_request
# Description:	process request
#

import sys, os, socket, random, hashlib, time, urllib2, json, base64, uuid, getpass
from cl_handle import Handle
import cl_global
from ConfigParser import ConfigParser
from cl_ssh import SSH
class Request(object):
	"""send request to server"""
	def __init__(self):
		self.parser = ConfigParser()
		self.parser.read('cl_config.conf')
		try:
			self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
		except:
			self.mac = str(hex(uuid.getnode()))

		self.host = "http://%s:%s" % (self.parser.get('server', 'websv'),self.parser.get('server', 'webport'))
		self.cookie = None
	def register(self, user, pswd):
		path = "/register"
		url = self.host + path
		pswdcode = hashlib.sha1(pswd).hexdigest()
		jdata = json.dumps({"username": user, "password": pswdcode})
		request_object = urllib2.Request(url, jdata, {'Accept': 'application/json', 'Content-Type': 'application/json'})
		try:
			response = urllib2.urlopen(request_object)
			html_string = response.read()
			print html_string
			if self.check_auth(user, pswd):
				self.logout()
				return True
		except urllib2.HTTPError as e:
			print(e.read())
		except:
			print "error: can connect to server"
		return False

	def set_token(self, token):		
		self.parser.read('cl_config.conf')
		if not self.parser.has_option('config', 'token'):
			self.parser.add_section('config')
		self.parser.set('config', 'token', token)
		f = open('cl_config.conf', 'w')
		self.parser.write(f)
		f.close()
	def check_auth(self, user, pswd):
		path = "/login"
		url = self.host + path
		pswdcode = hashlib.sha1(pswd).hexdigest()
		host = socket.gethostname()
		request_object = urllib2.Request(url, "", {'Accept': 'application/json', 'Content-Type': 'application/json'})
		request_object.add_header('Authorization', '{"mac":"%s", "host":"%s", "username":"%s", "password":"%s"}' % (self.mac, host, user, pswdcode))
		try:
			response = urllib2.urlopen(request_object)
			self.cookie = response.headers.get('Set-Cookie')
			token = response.read()
			self.set_token(token)
			print "login as %s" % user
			return True
		except urllib2.HTTPError as e:
			print(e.read())
		except:
			print "error: can connect to server"
		return False
	def input_auth(self):
		print "login to server"
		user = raw_input('username: ')
		pswd = getpass.getpass('password: ')
		return self.check_auth(user, pswd)
	def check_nat(self):		
		self.parser.read('cl_config.conf')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		except:
			return
		lport = s.getsockname()[1]
		s.send(json.dumps({"request": "checknat", "mac": self.mac, "lport": lport}))
		s.close()

	def login(self):						#login server by token and check NAT

		self.parser.read('cl_config.conf')
		if not self.parser.has_option('config', 'token') or self.parser.get('config', 'token') is None:
			if not self.input_auth():
				return False	
		token = self.parser.get('config', 'token')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
		except:
			return False
		lport = s.getsockname()[1]
		s.send(json.dumps({"request": "login", "token": token, "mac": self.mac, "lport": lport, "host": socket.gethostname()}))
		res = s.recv(1024)
		try:
			res = json.loads(res)
		except:
			return False
		if "error" in res:
			if res["error"] == "login":			
				print "you log in another machine"
			elif res["error"] == "token":	
				print "token is not Accept"
				self.input_auth()
			return False
		else:
			cl_global.listpeer = res
			cl_global.connect = s
			hd = Handle(s)
			hd.start()
			self.check_nat()
			self.check_nat()
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

		self.parser.read('cl_config.conf')
		mac = self.checkpeer(peer)
		if not mac:
			print "peer not found"
			return
		token = self.parser.get('config', 'token')
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))		
		except:
			print "error: can connect to server"
			return
		laddr, lport = s.getsockname()
		s.send(json.dumps({"request": "connect", "token": token, "mac": mac, "mymac": self.mac, "lport": lport, "laddr": laddr}))
		data = s.recv(1024)
		s.close()
		data = json.loads(data)
		connssh = SSH(data["session"], data["user"], data["lport"], data["laddr"], data["port"], data["addr"], data["me"], lport, data["nat"], data["mynat"])
		connssh.start()
		connssh.join()
	def listpeer(self):
		self.parser.read('cl_config.conf')
		path = "/onlines"
		url = self.host + path
		token = self.parser.get('config', 'token')
		request_object = urllib2.Request(url, "", {'Accept': 'application/json', 'Content-Type': 'application/json'})
		if self.cookie is None:
			request_object.add_header('Authorization', '{"mac":"%s", "token":"%s"}' % (self.mac, token))
		else:
			request_object.add_header('cookie', self.cookie)
		try:
			response = urllib2.urlopen(request_object)
			data = json.load(response)
			i=1
			for l in data:
				p = str(i) + ". " + l["host"] + "\t(" + l["mac"] +")" 
				p += ("\t"+ "(me)" if l["mac"] == self.mac else "")
				print p
				i +=1
			cl_global.listpeer = data
			return True
		except urllib2.HTTPError as e:
			print(e.read())
		except:
			print "error: can connect to server"
	def uploadkey(self, peer, username, pswd):
		self.parser.read('cl_config.conf')		
		token = self.parser.get('config', 'token')
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
			jkey = json.dumps({"request": "upkey", "token": token, "mymac" : self.mac, "mac": mac, "key": f.read(), "username": username, "password": pswd})
			f.close()	
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				s.connect((self.parser.get('server', 'server'), int(self.parser.get('server', 'port'))))
			except:
				print "error: can connect to server"
				return
			s.send(jkey)
		else:
			print "you don't have public key(~/.ssh/id_rsa.pub)"

	def logs(self):
		self.parser.read('cl_config.conf')
		path = "/logs"
		url = self.host + path
		token = self.parser.get('config', 'token')
		request_object = urllib2.Request(url, "", {'Accept': 'application/json', 'Content-Type': 'application/json'})
		if self.cookie is None:
			request_object.add_header('Authorization', '{"mac":"%s", "token":"%s"}' % (self.mac, token))
		else:
			request_object.add_header('cookie', self.cookie)
		try:
			response = urllib2.urlopen(request_object)
			data = json.load(response)
			for x in data:
				print x['time'] + "\t" + x['mac'] + "  " + x['log']
			return True
		except urllib2.HTTPError as e:
			print(e.read())
		except:
			print "error: can connect to server"
	def logout(self):
		if cl_global.connect is not None:
			cl_global.connect.send(json.dumps({"request": "logout"}))
			cl_global.connect = None
			self.cookie = None