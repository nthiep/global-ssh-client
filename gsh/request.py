#!/usr/bin/env python
#
# Name:			cl_request
# Description:	process request
#

import sys, os, glob, socket, random, hashlib, time, urllib2, json, base64, uuid, getpass
#import cl_global
from ConfigParser import ConfigParser
#from cl_ssh import SSH
from gsh import JsonSocket
from gsh import Output
from gsh import Client
import platform
__CONFIG_FILE__ = "/etc/gsh/gsh.conf"
__KEY_FILE__ 	= "/etc/gsh/gsh.key"
__NET_DIR__		= "/etc/gsh/net/"
__SERVER__ 		= "localhost"
__PORT__	 	= 8080

class Request(object):
	"""send request to server"""
	def __init__(self):
		self.parser = ConfigParser()
		self.parser.read(__CONFIG_FILE__)
		try:
			self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
		except:
			self.mac = str(hex(uuid.getnode()))
		self.out = Output()
	def register(self, user, passwork, fullname ="", email="", website=""):
		connect = JsonSocket(__SERVER__, __PORT__)
		if connect.connect():
			pswd = hashlib.md5(passwork).hexdigest()
			data = ({"request": "register", "username": user, "passwork": pswd, "fullname": fullname, "email": email, "website": website})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			return True
		return False

	def save_token(self, token):
		f = open(__KEY_FILE__, 'w')
		f.write(token)
		f.close()
	def get_token(self):
		try:
			f = open(__KEY_FILE__, 'r')
			data = f.read()
			f.close()
			return data
		except:
			return False
	def login(self, user, passwork):
		connect = JsonSocket(__SERVER__, __PORT__)
		if connect.connect():

			pswd = hashlib.md5(passwork).hexdigest()
			data = ({"request": "login", "username": user, "passwork": pswd, "mac": self.mac})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			print data			
			self.save_token(data["response"])
			return True
		return False


	def authentication(self):						
		""" login server by token """

		connect = JsonSocket(__SERVER__, __PORT__)
		token = self.get_token()
		if token and connect.connect():
			data = ({"request": "authentication", "api": token, "mac": self.mac,
			 "hostname": connect.gethostname(),"platform": platform.platform()})
			connect.send_obj(data)
			data = connect.read_obj()
			print data
			return connect
		return False
	def authnetwork(self):						
		""" authnetwork network """

		connect = JsonSocket(__SERVER__, __PORT__)
		net = glob.glob(__NET_DIR__ + "*.net")
		if net and connect.connect():
			key = []
			for  n in net:
				f = open(n, 'r')
				k = f.read()
				key.append(k)
				f.close()
			data = ({"request": "authnetwork", "mac": self.mac,"netkey": key,
			 "hostname": connect.gethostname(),"platform": platform.platform()})
			connect.send_obj(data)
			data = connect.read_obj()
			print data
			return connect
		return False

	def createnetwork(self, netname=""):						
		""" add network """
		
		connect = JsonSocket(__SERVER__, __PORT__)
		if connect.connect():
			data = ({"request": "createnetwork", "netname": netname})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			print data["response"]
			fname = __NET_DIR__ + netname + "_"+ data["response"][:24] + ".net"
			f = open(fname, 'w')
			f.write(data["response"])
			f.close()
			return True
		return False

	def query_yn(question, default="yes"):
		"""
		Ask a yes/no question via raw_input() and return their answer.
		"""
		valid = {"yes": True, "y": True, "ye": True,
			"no": False, "n": False}
		if default is None:
			prompt = " [y/n] "
		elif default == "yes":
			prompt = " [Y/n] "
		elif default == "no":
			prompt = " [y/N] "
		else:
			raise ValueError("invalid default answer: '%s'" % default)

		while True:
			sys.stdout.write(question + prompt)
			choice = raw_input().lower()
			if default is not None and choice == '':
				return valid[default]
			elif choice in valid:
				return valid[choice]
			else:
				sys.stdout.write("Please respond with 'yes' or 'no' "
					"(or 'y' or 'n').\n")
	def renetwork(self, network = ""):
		""" remove network """
		net = glob.glob(__NET_DIR__ + "*.net")
		lsre = []
		for  n in net:
			if network in n:
				lsre.append(n)
		if len(lsre) == 0:
			print "not network to remove"
			return False
		print "net work will be remove:"
		for n in lsre:
			print os.path.basename(n)
		if self.query_yn('do you want remove? [y/n] '):
			key = []
			for  n in lsre:
				f = open(n, 'r')
				k = f.read()
				key.append(k)
				f.close()
				os.remove(n)
			data = ({"request": "renetwork", "mac": self.mac,"netkey": key})
			connect.send_obj(data)
			data = connect.read_obj()
			return True
		return False


	def listmachine(self):						
		""" get list machines """
		connect = JsonSocket(__SERVER__, __PORT__)
		token = self.get_token()
		if connect.connect():
			data = ({"request": "listmachine", "mac": self.mac, "key": token})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			self.out.listmachine(data)
			return True
		return False




	def connect(self, peer):

		connect = JsonSocket(__SERVER__, __PORT__)
		token = self.get_token()
		if connect.connect():
			laddr, lport = connect.getsockname()
			data = ({"request": "connect", "mac": self.mac, "key": token, "peer": peer, "laddr": laddr, "lport": lport })
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			self.out.connect(data)
			client = Client(data, laddr, lport)
			client.run()
			return True
		return False

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