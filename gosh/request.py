#!/usr/bin/env python
#
# Name:			cl_request
# Description:	process request
#

import sys, os, glob, socket, random, hashlib, time, urllib, urllib2, json, base64, getpass, re
from gosh import JsonSocket
from gosh import Output
from gosh import Client
from gosh import StunClient
from gosh.config import logger, save_machine, save_client, save_token, save_workgroup
from gosh import config

class Request(object):
	"""send request to server"""
	def __init__(self):
		self.out = Output()
		self.host = "https://%s" %(config.WS_SERVER)
	def setverbose(self):
		""" set enable verbose mode """
		logger.disabled = False
		return True
	def keepconnect(self):
		connect = JsonSocket(JsonSocket.TCP)
		if connect.connect(config.SERVER, config.PORT):
			data = ({"request": "keepconnect", "mac": config.MAC_ADDR, "private": config.PRIVATE,
			 "hostname": connect.gethostname(),"platform": config.PLATFORM, "ip": connect.getsockname()[0]})
			connect.send_obj(data)
			logger.debug("keepconnect: had send request")
			try:
				data = connect.read_obj()
			except Exception, e:
				logger.debug("keepconnect: Error %s" %e)
				return False
			if data["response"]:
				id_machine = data['id_machine']
				save_machine(id_machine)
				reload(config)
			else:
				logger.debug("keepconnect: %s" %data["message"])
				os._exit(1)
				return False
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
		values = {"grant_type": "password", "domain": domain, "password": password, 'id_machine': config.ID_MACHINE}
		data = json.dumps(values)
		header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			info = info[0]
			save_client(info["domain"], info["client_id"], info["client_secret"])
			reload(config)
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
		base64string = base64.encodestring('%s:%s' % (config.CLIENT_ID, config.CLIENT_SECRET)).replace('\n', '')
		header = {"Authorization": "Basic %s" % base64string}
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			expires_in = time.time() + int(info["expires_in"])
			save_token(info["access_token"], info["token_type"], expires_in, info["refresh_token"])
			reload(config)
			return True
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False
	def refresh_token(self):
		if config.EXPIRES_IN and config.EXPIRES_IN < time.time():
			path = "/api/o/token/"
			url = self.host + path
			values = {"grant_type": "refresh_token", "refresh_token": config.REFESH_TOKEN}
			data = urllib.urlencode(values)
			base64string = base64.encodestring('%s:%s' % (config.CLIENT_ID, config.CLIENT_SECRET)).replace('\n', '')
			header = {"Authorization": "Basic %s" % base64string}
			request_object = urllib2.Request(url, data, header)
			try:
				response = urllib2.urlopen(request_object)
				info = json.load(response)
				expires_in = time.time() + int(info["expires_in"])
				save_token(info["access_token"], info["token_type"], expires_in, info["refresh_token"])
				reload(config)
				return True
			except urllib2.HTTPError as e:
				print "* ERROR %s: %s" %(e.code, e.read())
			except Exception as e:
				print "* ERROR: Can connect to server %s" %e
		return False
	def authorization(self):
		self.refresh_token()
		if config.ACCESS_TOKEN:
			header = {}
			values = {"id_machine": config.ID_MACHINE, "request": "authorization"}
		elif config.WORKGROUP_ID:
			return self.join_workgroup(False)
		else:
			self.out.process(False)
			return False

		path = "/api/authorization/"
		url = self.host + path
		
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		request_object.add_header("Authorization", config.TOKEN_TYPE + " " + config.ACCESS_TOKEN)
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
		values = {"mac": config.MAC_ADDR, "workgroup": workgroup, "query": "CREATE"}
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			print info
			if workgroup:
				workgroup += "_"
			fname = config.WORK_DIR + workgroup + info["workgroup_id"]
			if not os.path.exists(os.path.dirname(fname)):
				os.makedirs(os.path.dirname(fname))
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
		values = {"mac": config.MAC_ADDR, "workgroup_id": workgroup_id,
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
		workgroup = glob.glob(config.WORK_DIR+"*")
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
			workgroup_id = config.WORKGROUP_ID
			workgroup_secret = config.WORKGROUP_SECRET
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
		values = {"id_machine": config.ID_MACHINE, "request": "JOIN",
			 "workgroup_id": workgroup_id, "workgroup_secret": workgroup_secret}
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			print info
			if info["status"] == "success":
				save_workgroup(workgroup_id, workgroup_secret)
				reload(config)
			return True
		
		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False


	def query_yn(self, question, default="yes"):
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
			key = self.check_file(workgroup)
		else:
			key = self.check_file(key_file[0])
		if not key:
			self.out.renetwork(False)
			return False
		self.out.renetwork(True)
		for n in key_file:
			print os.path.basename(n)
		if self.query_yn('do you want remove?'):
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
		if config.ACCESS_TOKEN:
			header = {"authorization": config.TOKEN_TYPE + " " + config.ACCESS_TOKEN}
			data = None
		elif config.WORKGROUP_ID:
			header = {}
			values = {"id_machine": config.ID_MACHINE,
			 "workgroup_id": config.WORKGROUP_ID, "workgroup_secret": config.WORKGROUP_SECRET}
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
		mac = config.MAC_ADDR
		host = ''
		if machine:		
			if self._check_ismac(machine):
				mac = machine
			else:
				mac = ''
				host = machine
		self.refresh_token()
		if config.ACCESS_TOKEN:
			join = "domain"
		elif config.WORKGROUP_ID:
			join = "workgroup"
		else:
			join = ''
			host = ''
			mac = config.MAC_ADDR

		header = {}
		values = {"mac": mac, "join": join , "host": host, "join": join,
		 "access_token": config.ACCESS_TOKEN, "workgroup_id": config.WORKGROUP_ID,
		 "workgroup_secret": config.WORKGROUP_SECRET}
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
	def _check_host_port(self, host):
		query = host.strip().split(":")
		if len(query) == 2 and query[1].isdigit():
			return query
		if len(query) == 7 and query[7].isdigit():
			return (host.strip()[:17], query[7])
		return False
	def _check_bind_port(self, bind):
		""" check if bind options have source port """
		query = bind.strip().split(":")
		if len(query) == 2 and query[0].isdigit() and query[1].isdigit():
			return query
		return False
	def connect(self, destination, options, args):
		""" connect request """
		destination_port 	= False
		destination_user	= False
		bind_source 		= False
		if options.bind:
			result = self._check_bind_port(options.bind)
			if result:
				bind_source, destination_port = result
			elif options.bind.isdigit():
				destination_port = options.bind
			else:
				self.out.bind(False)
				return False
		connect = JsonSocket(JsonSocket.TCP)		
		connect.set_reuseaddr()
		if options.port:
			destination_port = options.port
		if self._check_isuser(destination):
			destination_user, destination = self._check_isuser(destination)
		if self._check_host_port(destination): 
			destination, destination_port = self._check_host_port(destination)

		if connect.connect(config.SERVER, config.PORT):

			laddr, lport = connect.getsockname()
			data = {"request": "connect", "token": config.ACCESS_TOKEN, "workgroup_id": config.WORKGROUP_ID,
						"workgroup_secret": config.WORKGROUP_SECRET, "id_machine": config.ID_MACHINE,
						"destination": destination, "laddr": laddr,
						"lport": lport, "destination_port": destination_port }
			connect.send_obj(data)
			data = connect.read_obj()
			connect.close()
			if data["response"]:
				if data["choice"]:
					destination = self.out.connect(data)
					if destination:
						if destination_user:
							destination = "%s@%s" %(destination_user, destination)
						if destination_port:
							destination = "%s:%s" %(destination, destination_port)
						return self.connect(destination, options, args)
					return False
				client = Client()
				client.set_data(data, laddr, lport, destination_user, destination_port, options, args, bind_source)
				client.run()
				return True
			else:
				self.out.error(data["message"])
			logger.debug("connect: Error in connect")
		self.out.connect(False)
		return False
	def basic_connect(self, destination, options, args):
		""" connect by basic connect """
		self.out.basic_connect()
		destination_port 	= 22
		destination_user	= False
		if options.bind:
			result = self._check_bind_port(options.bind)
			if result:
				bind_source, destination_port = result
			elif options.bind.isdigit():
				destination_port = options.bind
			else:
				self.out.bind(False)
				return False

		if options.port:
			destination_port = options.port
		if self._check_isuser(destination):
			destination_user, destination = self._check_isuser(destination)
		connect_address = (destination, int(destination_port))
		client = Client()
		client.ssh_process(connect_address, destination_user, options, args)
		return True

	def nattype(self, mapping, filtering):
		""" return 12 type of nat """
		if not mapping:
			return 9
		if mapping==1:
			other = 0
		elif mapping==2:
			other = 3
		elif mapping==3:
			other = 6
		elif mapping==10:
			other = 9
		return other + filtering
	def natconfig(self):
		""" check nat discovery """
		stun = StunClient(StunClient.UDP)
		mapping, filtering = stun.NAT_Behavior_Discovery()
		nat = self.nattype(mapping, filtering)
		stun_tcp = StunClient(StunClient.TCP)
		mapping_tcp, filtering_tcp = stun_tcp.NAT_Behavior_Discovery()
		if not mapping_tcp:
			mapping_tcp = 3
		path = "/api/natconfig/"
		url = self.host + path
		header = {}
		values = {"id_machine": config.ID_MACHINE, "request": "NATCONFIG", "nat": nat, "nat_tcp": mapping_tcp}
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			if info["status"] == "success":
				self.out.process(True)
				return True
			self.out.process(False)

		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False
	def show_nat_type(self):
		""" show nat info """
		stun = StunClient(StunClient.UDP)
		self.out.processing()
		mapping, filtering = stun.NAT_Behavior_Discovery()
		self.out.show_nat_type(mapping, filtering, self.nattype(mapping, filtering))
		return True
	def logout_workgroup(self):
		""" logout workgroup """
		path = "/api/workgroup/authorization/"
		url = self.host + path
		header = {}
		values = {"id_machine": config.ID_MACHINE, "request": "LOGOUT",
			 "workgroup_id": config.WORKGROUP_ID, "workgroup_secret": config.WORKGROUP_SECRET}
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			if info["status"] == "success":
				save_workgroup("", "")
				reload(config)
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
		if config.ACCESS_TOKEN:
			header = {}
			values = {"id_machine": config.ID_MACHINE, "request": "logout"}
		elif config.WORKGROUP_ID:
			return self.logout_workgroup()
		else:
			self.out.process(False)
			return False

		path = "/api/authorization/"
		url = self.host + path
		
		data = urllib.urlencode(values)
		request_object = urllib2.Request(url, data, header)
		request_object.add_header("Authorization", config.TOKEN_TYPE + " " + config.ACCESS_TOKEN)
		try:
			response = urllib2.urlopen(request_object)
			info = json.load(response)
			if info["status"] == "success":
				save_token("", "", "", "")
				reload(config)
				self.out.logout(True)
				return True
			self.out.logout(False)

		except urllib2.HTTPError as e:
			print "* ERROR %s: %s" %(e.code, e.read())
		except Exception as e:
			print "* ERROR: Can connect to server %s" %e
		return False
