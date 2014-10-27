import sys, os, hashlib, time, urllib2, json, base64
from cl_handle import Handle
import cl_global
from ConfigParser import SafeConfigParser
from cl_ssh import SSH
class Request(object):
	"""docstring for Request"""
	def __init__(self):
		self.parser = SafeConfigParser()
		self.parser.read('cl_config.cfg')
		self.host = "http://%s:%s" % (self.parser.get('websv', 'server'),self.parser.get('websv', 'port'))

	def checkconnection(self):
		path = "/"
		url = self.host + path
		jdata = json.dumps({"request":"check"})
		request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
		try:
			response = urllib2.urlopen(request_object)
			print response.read()
			return True
		except:
			print "can not connect to webservice"
			return False

	def register(self, user, pswd):		
		path = "/register"
		url = self.host + path
		pswdcode = hashlib.sha1(pswd).hexdigest()
		jdata = json.dumps({"username": user, "password":pswdcode})
		request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
		try:
			response = urllib2.urlopen(request_object)
			html_string = response.read()
			print html_string
		except urllib2.HTTPError as e:
			print(e.read())
		except:
			print "error: can connect to server"

	def login(self, user, pswd):
		if cl_global.user is not None:
			print "you had login"
			return
		path = "/login"
		url = self.host + path
		pswdcode = hashlib.sha1(pswd).hexdigest()
		jdata = json.dumps({'request':'login'})
		request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})

		base64string = base64.encodestring('%s:%s' % (user, pswdcode)).replace('\n', '')
		request_object.add_header('Authorization', 'Basic %s' % base64string)
		try:
			response = urllib2.urlopen(request_object)
			try:		
				data = json.load(response)
			except ValueError:
				print "Error json "
				return
			if 'error' in data:
				print data["error"]
				return			
			cl_global.auth = base64string
			cl_global.user = user
			address = data["address"]
			sock_path
			print "you logining as %s" % user
		except urllib2.HTTPError as e:
			print(e.read())
		except:
			print "error: can connect to server"

	def connect(self, peer):
		if cl_global.user is not None:
			path = "/connect"
			url = self.host + path
			jdata = json.dumps({"peer": peer})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				data = json.load(response)
				if data['status'] == 200:
					hashcode = data['hashcode']
					peer = data['peer']
					address = data['address']
					localadd = data['localadd']
					connssh = SSH(hashcode, peer, address, localadd)
					connssh.start()
					connssh.join()
				else:
					print data['response']
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!"

	def uploadkey(self):
		if cl_global.user is not None:
			key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa.pub')
			if os.path.exists(key_path):
				f = open(key_path, 'r')
				path = "/uploadkey"
				url = self.host + path
				jdata = json.dumps({"key": f.read()})
				f.close()
				request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
				request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
				try:
					response = urllib2.urlopen(request_object)
					data = response.read()
					print data
				except urllib2.HTTPError as e:
					print(e.read())
				except:
					print "error: can connect to server"
			else:
				print "you don't have public key(~/.ssh/id_rsa.pub)"
		else:
			print "you must login first!"


	def addkey(self, peer):
		if cl_global.user is not None:
			path = "/addkey"
			url = self.host + path
			jdata = json.dumps({"peer": peer})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				data = json.load(response)
				if 'error' in data[0]:
					print data[0]["error"]
					return
				else:
					key = data[0]['key']
					key_auth = os.path.join(os.environ['HOME'], '.ssh', 'authorized_keys')
					f = open(key_auth, 'a')
					f.write(key)
					f.close()
					print "addkey successful"
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!"

	def friends(self):
		if cl_global.user is not None:
			path = "/friends"
			url = self.host + path
			jdata = json.dumps({"request":"friends"})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				data = json.load(response)
				if 'error' in data[0]:
					print data[0]["error"]
					return
				for x in data:
					print x['friend'] + "\t" + x["status"]
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!"
	def onlines(self):
		if cl_global.user is not None:
			path = "/onlines"
			url = self.host + path
			jdata = json.dumps({"request":"onlines"})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				data = json.load(response)
				if not data:
					print "no friend onlines"
					return
				if 'error' in data[0]:
					print data[0]["error"]
					return							
				for x in data:
					print x['friend'] + "\t" + x["status"]
			except urllib2.HTTPError as e:
				print(e.read())
			
		else:
			print "you must login first!"
	def logs(self):
		if cl_global.user is not None:		
			path = "/logs"
			url = self.host + path
			jdata = json.dumps({"request":"logs"})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				data = json.load(response)
				if 'error' in data[0]:
					print data[0]["error"]
					return
				for x in data:
					print x['time'] + "\t" + x["logs"]
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!" 
	def friendrq(self):
		if cl_global.user is not None:
			path = "/friendrq"
			url = self.host + path
			jdata = json.dumps({"request":"friendrq"})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				data = json.load(response)
				if 'error' in data[0]:
					print data[0]["error"]
					return
				for x in data:
					print x['request'] + "\t" + x["time"]
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!"


	def info(self, peer):
		if cl_global.user is not None:
			path = "/user/%s" % peer
			url = self.host + path
			jdata = json.dumps({"request":"info"})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				data = json.load(response)
				if 'error' in data[0]:
					print data[0]["error"]
					return
				print "%s infomation:" % peer				
				print "status: %s" % data[0]['status']
				print "public key:\n %s" % data[0]['key']
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server" 
		else:
			print "you must login first!"

	def addfriendrq(self, peer):
		if cl_global.user is not None:
			path = "/add"
			url = self.host + path
			jdata = json.dumps({"peer": peer})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				html = response.read()
				print html
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!"
	def accept(self, peer):
		if cl_global.user is not None:
			path = "/accept"
			url = self.host + path
			jdata = json.dumps({"peer": peer})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				html = response.read()
				print html
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!"
	def denied(self, peer):
		if cl_global.user is not None:
			path = "/denied"
			url = self.host + path
			jdata = json.dumps({"peer": peer})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				html = response.read()
				print html
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!"

	def logout(self):
		if cl_global.user is not None:
			path = "/logout"
			url = self.host + path
			jdata = json.dumps({"request": "logout"})
			request_object = urllib2.Request(url, jdata, {'Content-Type': 'application/json'})
			request_object.add_header("Authorization", "Basic %s" % cl_global.auth)
			try:
				response = urllib2.urlopen(request_object)
				html = response.read()
				cl_global.auth = None
				cl_global.user = None
				print html
			except urllib2.HTTPError as e:
				print(e.read())
			except:
				print "error: can connect to server"
		else:
			print "you must login first!"