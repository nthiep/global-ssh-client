#!/usr/bin/env python
#
# Name:			cl_request
# Description:	process request
#

import sys, os, glob, socket, random, hashlib, time, urllib2, json, base64, getpass, re
from gsh import JsonSocket
from gsh import Output
from gsh import Client
from gsh.config import *

class Request(object):
	"""send request to server"""
	def __init__(self):
		self.out = Output()

	def keepconnect(self):
		connect = JsonSocket(SERVER, PORT)
		if connect.connect():
			data = ({"request": "keepconnect", "mac": MAC_ADDR,
			 "hostname": connect.gethostname(),"platform": PLATFORM})
			connect.send_obj(data)
			logging.debug("keepconnect: had send request")
			data = connect.read_obj()
			logging.debug("keepconnect: recv %s" %str(data))
			return connect
		logging.debug('keepconnect: can not connect')
		return False
	def register(self, user, passwork, fullname ="", email="", website=""):
		connect = JsonSocket(SERVER, PORT)
		if connect.connect():
			pswd = hashlib.md5(passwork).hexdigest()
			data = ({"request": "register", "username": user, "passwork": pswd, "fullname": fullname, "email": email, "website": website})
			connect.send_obj(data)
			logging.debug("register: had send request")
			data = connect.read_obj()
			connect.close()
			logging.debug("register: recv %s" %str(data))
			return True
		return False

	def save_token(self, token):
		f = open(KEY_FILE, 'w')
		f.write(token)
		f.close()
	def get_token(self):
		try:
			f = open(KEY_FILE, 'r')
			data = f.read()
			f.close()
			return data
		except:
			return False
	def login(self, user, passwork):
		connect = JsonSocket(SERVER, PORT)
		if connect.connect():
			pswd = hashlib.md5(passwork).hexdigest()
			data = ({"request": "login", "username": user, "passwork": pswd, "mac": MAC_ADDR})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("login: recv %s" %str(data))
			if data["response"]:		
				self.save_token(data["token"])
				return self.authuser()
		return False


	def authuser(self):						
		""" login server by apikey """

		connect = JsonSocket(SERVER, PORT)
		apikey = self.get_token()
		if not apikey:
			return False
		if connect.connect():
			data = ({"request": "authuser", "apikey": apikey, "mac": MAC_ADDR})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("authuser: recv %s" %str(data))
			return True
		return False
	def authnetwork(self):						
		""" authnetwork network """

		connect = JsonSocket(SERVER, PORT)
		net = glob.glob(NET_DIR + "*.net")
		if not net:
			return False
		if connect.connect():
			key = []
			for  n in net:
				f = open(n, 'r')
				k = f.read()
				key.append(k)
				f.close()
			data = ({"request": "authnetwork", "mac": MAC_ADDR,"netkey": key})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("authnetwork: recv %s" %str(data))
			return True
		return False

	def createnetwork(self, netname=""):						
		""" add network """
		
		connect = JsonSocket(SERVER, PORT)
		if connect.connect():
			data = ({"request": "createnetwork", "netname": netname})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("createnetwork: recv %s" %str(data))
			fname = NET_DIR + netname + "_"+ data["response"][:24] + ".net"
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
		net = glob.glob(NET_DIR + "*.net")
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
			data = ({"request": "renetwork", "mac": MAC_ADDR,"netkey": key})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("renetwork: recv %s" %str(data))
			return True
		return False


	def listmachine(self):						
		""" get list machines """
		connect = JsonSocket(SERVER, PORT)
		apikey = self.get_token()
		if connect.connect():
			data = ({"request": "listmachine", "mac": MAC_ADDR, "apikey": apikey})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("listmachine: recv data")
			self.out.listmachine(data)
			return True
		return False

	def _check_ismac(self, ismac):
		if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", ismac.lower()):
			return True
		return False
	def _check_isuser(self, isuser):
		q = isuser.strip().split("@")
		if len(q) == 2:
			return q
		return False

	def connect(self, peer):
		connect = JsonSocket(SERVER, PORT)
		apikey = self.get_token()
		if connect.connect():
			q = self._check_isuser(peer)
			macpeer = False
			user 	= False
			if q:
				user, peer = q
			if self._check_ismac(peer):
				macpeer = peer	
			laddr, lport = connect.getsockname()
			data = ({"request": "connect", "mac": MAC_ADDR,
				 "apikey": apikey, "peer": peer, "macpeer": macpeer, "laddr": laddr, "lport": lport })
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("connect: recv %s" %str(data))
			if data["response"]:
				if data["choice"]:
					macpeer = self.out.connect(data)
					if macpeer:
						if user:
							macpeer = user + "@" + macpeer
						return self.connect(macpeer)
					return False
				client = Client(data, laddr, lport, user)
				client.run()
				return True
			self.out.connect(False)
		return False

	def checknat_conn(self, port, lport=False):
		""" check nat connection to the server """
		connect = JsonSocket(SERVER, port)
		connect.set_reuseaddr()
		if lport:
			connect.bind(lport)
		if connect.connect():
			if not lport:
				laddr, lport = connect.getsockname()
				data = ({"request": "checknat", "mac": MAC_ADDR,
					"laddr": laddr, "lport": lport })
				connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			return data, lport
		return False

	def checknat(self):
		""" check nat connection to the server """
		data, lport = self.checknat_conn(PORT)
		if data:
			while data["check"]:
				data = self.checknat_conn(int(data["port"]), lport)
				logging.debug("checknat: checknat")
			return True
		return False
		
	def logs(self):
		pass
	def logout(self):
		if cl_global.connect is not None:
			cl_global.connect.send(json.dumps({"request": "logout"}))
			cl_global.connect = None
			self.cookie = None