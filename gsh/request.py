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

	def setverbose(self):
		""" set enable verbose mode """
		logging.disabled = False
	def keepconnect(self):
		connect = JsonSocket(JsonSocket.TCP)
		if connect.connect(SERVER, PORT):
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
		connect = JsonSocket(JsonSocket.TCP)
		if connect.connect(SERVER, PORT):
			pswd = hashlib.md5(passwork).hexdigest()
			data = ({"request": "register", "username": user, "passwork": pswd, "fullname": fullname, "email": email, "website": website})
			connect.send_obj(data)
			logging.debug("register: had send request")
			data = connect.read_obj()
			connect.close()
			self.out.register(data)
			logging.debug("register: recv response")
			return True
		return False

	def save_token(self, token):
		f = open(KEY_FILE, 'w')
		f.write(token)
		f.close()
	def del_token(self):
		try:
			os.remove(KEY_FILE)
			return True
		except:
			return False
	def get_token(self):
		try:
			f = open(KEY_FILE, 'r')
			data = f.read()
			f.close()
			return data
		except:
			return False
	def login(self, user, passwork):
		connect = JsonSocket(JsonSocket.TCP)
		if connect.connect(SERVER, PORT):
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

		connect = JsonSocket(JsonSocket.TCP)
		apikey = self.get_token()
		if not apikey:
			return False
		if connect.connect(SERVER, PORT):
			data = ({"request": "authuser", "apikey": apikey, "mac": MAC_ADDR})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			self.out.authuser(data)
			logging.debug("authuser: recv response")
			return True
		return False
	def authnetwork(self):						
		""" authnetwork network """

		connect = JsonSocket(JsonSocket.TCP)
		net = glob.glob(os.path.join(NET_DIR, "*.net"))
		if not net:
			return False
		if connect.connect(SERVER, PORT):
			key = []
			for  n in net:
				f = open(n, 'r')
				k = f.read()
				key.append(k)
				f.close()
			data = ({"request": "authnetwork", "mac": MAC_ADDR, "netkey": key})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("authnetwork: recv response")
			return True
		return False

	def createnetwork(self, netname=""):						
		""" create network """
		
		connect = JsonSocket(JsonSocket.TCP)
		if connect.connect(SERVER, PORT):
			data = ({"request": "createnetwork", "netname": netname})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("createnetwork: recv %s" %str(data))
			if netname:
				netname += "_"
			fname = NET_DIR + netname + data["response"][:24] + ".net"
			f = open(fname, 'w')
			f.write(data["response"])
			f.close()
			return True
		return False

	def check_file(self, path):
		try:
			open(path, 'r')
			data = f.read()
			f.close()
			return data
		except:
			pass
		return False
	def addnetwork(self, network):
		""" add network """
		key = self.check_file(network)
		connect = JsonSocket(JsonSocket.TCP)
		if not key:
			key = network
		if connect.connect(SERVER, PORT):
			data = ({"request": "addnetwork", "mac": MAC_ADDR, "netkey": key})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logging.debug("addnetwork: recv response")
			if data["response"]:
				fname = NET_DIR + data["netname"] + "_"+ key[:24] + ".net"
				f = open(fname, 'w')
				f.write(key)
				f.close()
				logging.debug("addnetwork: add key file")
				self.out.addnetwork(True)

				return self.authnetwork()
			self.out.addnetwork(False)
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
		for n in net:
			if network in n:
				lsre.append(n)
		if len(lsre) == 0:
			self.out.renetwork(False)
			return False
		self.out.renetwork(True)

		for n in lsre:
			print os.path.basename(n)
		if self.query_yn('do you want remove? [y/n] '):
			connect = JsonSocket(JsonSocket.TCP)
			if connect.connect(SERVER, PORT):
				key = []
				for  n in lsre:
					f = open(n, 'r')
					k = f.read()
					key.append(k)
					f.close()
					os.remove(n)
				data = ({"request": "renetwork", "mac": MAC_ADDR, "netkey": key})
				connect.send_obj(data)
				data = connect.read_obj()
				connect.close()
				logging.debug("renetwork: recv response")
				self.out.renetwork(True, True)
				return True
		return False


	def listmachine(self):						
		""" get list machines """
		connect = JsonSocket(JsonSocket.TCP)
		apikey = self.get_token()
		if connect.connect(SERVER, PORT):
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
	def _check_division(self, host):
		q = isuser.strip().split(":")
		if len(q) == 2:
			return q[0], q[1]
		if len(q) == 7:
			return host.strip()[:17], q[7]
		return False, False

	def connect(self, peer, options, args):
		connect = JsonSocket(JsonSocket.TCP)
		apikey = self.get_token()
		if connect.connect(SERVER, PORT):
			sport = False
			if options.port:
				sport = options.port
			q = self._check_isuser(peer)
			macpeer = False
			user 	= False
			sfile 	= False
			if q:
				user, peer = q
			q, = self._check_division(peer)
			if q:
				peer, s = self._check_division(peer)
				if s.isdigit():
					sport = int(s)
				else:
					if options.service == "scp":
						sfile = s
			if self._check_ismac(peer):
				macpeer = peer	
			laddr, lport = connect.getsockname()
			data = ({"request": "connect", "mac": MAC_ADDR, "apikey": apikey,
			 "peer": peer, "macpeer": macpeer, "laddr": laddr, "lport": lport, "sport": sport })
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
						return self.connect(macpeer, port)
					return False
				client = Client(data, laddr, lport, user, options, args, sfile)
				client.run()
				return True
			self.out.connect(False)
		return False

	def checknat_conn(self, port, lport=False, udp = False):
		""" check nat connection to the server """
		if udp:
			connect = JsonSocket(JsonSocket.UDP)
		else:
			connect = JsonSocket(JsonSocket.TCP)
		connect.set_reuseaddr()
		if lport:
			connect.bind(lport)
		if connect.connect(SERVER, port):
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
				if data["isudp"]:
					data = self.checknat_conn(int(data["port"], lport, True))
				else:
					data = self.checknat_conn(int(data["port"]), lport)
				logging.debug("checknat: checknat")
			logging.debug("checknat: checknat success")
			return True
		return False
		
	def logs(self):
		pass
	def logout(self):
		""" logout server use apikey """

		connect = JsonSocket(JsonSocket.TCP)
		apikey = self.get_token()
		if not apikey:			
			self.out.logout(False)
			return False
		if connect.connect(SERVER, PORT):
			data = ({"request": "logout", "apikey": apikey, "mac": MAC_ADDR})
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			if data["response"]:
				if self.del_token():
					logging.debug("logout: delete key file success!")
				else:
					logging.debug("logout: can not delete key!")			
			self.out.logout(data)
			logging.debug("logout: Done!")
			return True
		return False