#!/usr/bin/env python
#
# Name:			cl_request
# Description:	process request
#

import sys, os, glob, socket, random, hashlib, time, urllib, urllib2, json, base64, getpass, re
from gsh import JsonSocket
from gsh import Output
from gsh import Client
from gsh.config import *

class Request(object):
	"""send request to server"""
	def __init__(self):
		self.out = Output()
		self.host = "http://%s:%d" %(WS_SERVER, WS_PORT)
	def setverbose(self):
		""" set enable verbose mode """
		logger.disabled = False
	def keepconnect(self):
		connect = JsonSocket(JsonSocket.TCP)
		if connect.connect(SERVER, PORT):
			data = ({"request": "keepconnect", "mac": MAC_ADDR, "private": PRIVATE,
			 "hostname": connect.gethostname(),"platform": PLATFORM, "ip": connect.getsockname()[0]})
			connect.send_obj(data)
			logger.debug("keepconnect: had send request")
			data = connect.read_obj()
			if not data:
				return False
			logger.debug("keepconnect: recv %s" %str(data["response"]))
			return connect
		logger.debug('keepconnect: can not connect')
		return False
	def register(self, domain, password):
		path = "/api/signup/"
		url = self.host + path
		values = {"username": domain, "password": password}
		data = json.dumps(values)
		header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			print response.read()
			return True
		except urllib2.HTTPError as e:
			print "* ERROR: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False
	def _check_domain(self, domain):
		d = domain.strip().split(".")
		if len(d) == 2:
			return domain
		elif len(d) == 1:
			return "root." + domain
		return False
	def join_domain(self, domain, password):
		domain = self._check_domain(domain)
		if not domain:
			self.out.join_domain(False)
			return False
		path = "/api/join/"
		url = self.host + path
		values = {"grant_type": "password", "domain": domain, "password": password, 'mac': MAC_ADDR}
		data = json.dumps(values)
		header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			info = info[0]
			save_client(info["domain"], info["client_id"], info["client_secret"])
			if self.get_token(domain, password):
				if self.authorization():
					self.out.join_domain(True)
					return True
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		self.out.join_domain(False)
		return False

	def get_token(self, domain, password):
		path = "/api/o/token/"
		url = self.host + path
		values = {"grant_type": "password", "username": domain, "password": password}
		data = urllib.urlencode(values)
		base64string = base64.encodestring('%s:%s' % (CLIENT_ID, CLIENT_SECRET)).replace('\n', '')
		header = {"Authorization": "Basic %s" % base64string}
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			expires_in = time.time() + int(info["expires_in"])
			save_token(info["access_token"], info["token_type"], expires_in, info["refresh_token"])
			return True
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False
	def refresh_token(self):
		if EXPIRES_IN and EXPIRES_IN < time.time():
			path = "/api/o/token/"
			url = self.host + path
			values = {"grant_type": "refresh_token", "refresh_token": REFESH_TOKEN}
			data = urllib.urlencode(values)
			base64string = base64.encodestring('%s:%s' % (CLIENT_ID, CLIENT_SECRET)).replace('\n', '')
			header = {"Authorization": "Basic %s" % base64string}
			request_object = urllib2.Request(url, data, header)
			try:
				response = urllib2.urlopen(request_object)
				info = json.load(response)
				expires_in = time.time() + int(info["expires_in"])
				save_token(info["access_token"], info["token_type"], expires_in, info["refresh_token"])
				return True
			except urllib2.HTTPError as e:
				print "* ERROR %s: %s" %(e.code, e.read())
			except Exception as e:
				print "* ERROR: Can connect to server %s" %e
		return False
	def authorization(self):
		from gsh.config import *
		self.refresh_token()
		if ACCESS_TOKEN:
			header = {}
			values = {"mac": MAC_ADDR, "request": "authorization"}
		elif WORKGROUP_ID:
			return self.join_workgroup(False)
		else:
			self.out.process(False)
			return False

		path = "/api/authorization/"
		url = self.host + path
		
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		request_object.add_header("Authorization", TOKEN_TYPE + " " + ACCESS_TOKEN)
		try:
			response = urllib2.urlopen(request_object)
			return True
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False


	def create_workgroup(self, workgroup=""):						
		""" create workgroup """
		
		path = "/api/workgroup/"
		url = self.host + path
		header = {}
		values = {"mac": MAC_ADDR, "workgroup": workgroup, "query": "CREATE"}
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			print info
			if workgroup:
				workgroup += "_"
			fname = WORK_DIR + workgroup + info["workgroup_id"]
			f = open(fname, 'w')
			f.write(info["workgroup_id"]+os.linesep+info["workgroup_secret"])
			f.close()
			return True
		
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False
	def delete_workgroup(self, workgroup_id, workgroup_secret):						
		""" delete workgroup """
		
		path = "/api/workgroup/"
		url = self.host + path
		header = {}
		values = {"mac": MAC_ADDR, "workgroup": workgroup_id,
		 "workgroup_secret": workgroup_secret, "query": "DELETE"}
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			return True
		
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False


	def check_file(self, path):
		try:
			with open(path, 'r') as f:
				content = f.read().splitlines()
			if len(content) != 2:
				return False
			f.close()
			return content
		except:
			pass
		return False

	def get_file(self, name):
		workgroup = glob.glob(WORK_DIR)
		ls = []
		for w in workgroup:
			if name in w:
				ls.append(w)
		if len(ls) == 0:
			return False
		return ls
	def join_workgroup(self, workgroup):
		""" join workgroup """
		if not workgroup:
			workgroup_id = WORKGROUP_ID
			workgroup_secret = WORKGROUP_SECRET
		else:
			key_file = self.get_file(workgroup)
			if not key_file:
				key = self.check_file(workgroup)
			else:
				key = self.check_file(key_file[0])
			if not key:
				return False
			workgroup_id = key[0]
			workgroup_secret = key[1]

		path = "/api/workgroup/authorization/"
		url = self.host + path
		header = {}
		values = {"mac": MAC_ADDR, "request": "JOIN",
			 "workgroup_id": workgroup_id, "workgroup_secret": workgroup_secret}
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			print info
			if info["status"] == "success":
				save_workgroup(key[0], key[1])
			return True
		
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
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
	def remove_workgroup(self, workgroup = ""):
		""" remove network """
		
		key_file = self.get_file(workgroup)
		if not key_file:
			self.out.renetwork(False)
			return False
		self.out.renetwork(True)
		for n in key_file:
			print os.path.basename(n)
		if self.query_yn('do you want remove? [y/n] '):
			for  n in key_file:
				key = self.check_file(n)
				if not key:
					continue
				self.delete_workgroup(key[0], key[1])
				os.remove(n)
			self.out.renetwork(True, True)
			return True
		return False


	def listmachine(self):						
		""" get list machines """
		self.refresh_token()
		if ACCESS_TOKEN:
			header = {"authorization": TOKEN_TYPE + " " + ACCESS_TOKEN}
			data = None
		elif WORKGROUP_ID:
			header = {}
			values = {"mac": MAC_ADDR, "workgroup_id": WORKGROUP_ID, "workgroup_secret": WORKGROUP_SECRET}
			data = urllib.urlencode(values)
		else:
			self.out.listmachine(False)
			return False
		path = "/api/machine/"
		url = self.host + path		
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			self.out.listmachine(json.load(response))
			return True
		
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		self.out.listmachine(False)
		return False
	def info_machine(self, machine=False):						
		""" get info of machines """
		mac = MAC_ADDR
		host = ''
		if machine:		
			if self._check_ismac(machine):
				mac = machine
			else:
				mac = ''
				host = machine
		self.refresh_token()
		if ACCESS_TOKEN:
			join = "domain"
		elif WORKGROUP_ID:
			join = "workgroup"
		else:
			join = ''
			host = ''
			mac = MAC_ADDR

		header = {}
		values = {"mac": mac, "join": join , "host": host, "join": join,
		 "access_token": ACCESS_TOKEN, "workgroup_id": WORKGROUP_ID, "workgroup_secret": WORKGROUP_SECRET}
		data = urllib.urlencode(values)
		path = "/api/machine/info/"
		url = self.host + path		
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			self.out.info_machine(json.load(response))
			return True
		
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
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
		q = host.strip().split(":")
		if len(q) == 2:
			return q[0], q[1]
		if len(q) == 7:
			return host.strip()[:17], q[7]
		return False, False

	def connect(self, peer, options, args):
		connect = JsonSocket(JsonSocket.TCP)		
		connect.set_reuseaddr()
		if connect.connect(SERVER, PORT):
			sport 	= False
			macpeer = False
			user 	= False
			sfile 	= False
			if options.port:
				sport = options.port
			q = self._check_isuser(peer)
			if q:
				user, peer = q
			p, s = self._check_division(peer)
			if p:
				if s.isdigit():
					sport = int(s)
				else:
					if options.service == "scp":
						sfile = s
				if self._check_ismac(p):
					macpeer = p
			else:
				if self._check_ismac(peer):
					macpeer = peer
			laddr, lport = connect.getsockname()
			data = ({"request": "connect", "token": ACCESS_TOKEN, "workgroup_id": WORKGROUP_ID,
						"workgroup_secret": WORKGROUP_SECRET, "mac": MAC_ADDR, "peer": peer,
						"macpeer": macpeer, "laddr": laddr, "lport": lport, "sport": sport })
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			logger.debug("connect: recv %s" %str(data))
			if data["response"]:
				if data["choice"]:
					macpeer = self.out.connect(data)
					if macpeer:
						if user:
							macpeer = user + "@" + macpeer
						return self.connect(macpeer, port)
					return False
				client = Client(data, laddr, lport, user, sport, options, args, sfile)
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
				logger.debug("checknat: checknat")
			logger.debug("checknat: checknat success")
			return True
		return False
		
	def logout_workgroup(self):
		""" logout workgroup """
		workgroup_id = WORKGROUP_ID
		workgroup_secret = WORKGROUP_SECRET
		path = "/api/workgroup/authorization/"
		url = self.host + path
		header = {}
		values = {"mac": MAC_ADDR, "request": "LOGOUT",
			 "workgroup_id": workgroup_id, "workgroup_secret": workgroup_secret}
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			if info["status"] == "success":
				save_workgroup("", "")
				self.out.logout(True)
				return True
			self.out.logout(False)

		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False
	def logout(self):
		self.refresh_token()
		if ACCESS_TOKEN:
			header = {}
			values = {"mac": MAC_ADDR, "request": "logout"}
		elif WORKGROUP_ID:
			return self.logout_workgroup()
		else:
			self.out.process(False)
			return False

		path = "/api/authorization/"
		url = self.host + path
		
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		request_object.add_header("Authorization", TOKEN_TYPE + " " + ACCESS_TOKEN)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			if info["status"] == "success":
				save_token("", "", "", "")
				self.out.logout(True)
				return True
			self.out.logout(False)

		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False
