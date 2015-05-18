import struct, socket, time, logging
from gosh.config import STUN_SERVER, STUN_PORT
from gosh import JsonSocket


#=============================================================================
#   STUN Client
# ============================================================================
class StunClient(object):
	## defined protocol
	TCP='TCP'
	UDP='UDP'
	def __init__(self, pro):
		self.tcp=False
		if pro == 'TCP':
			self.tcp = True
			self.port = None
		else:
			self.sock = None


	def NAT_Behavior_Discovery(self):
		mapping = self.mapping_behavior()
		if self.tcp:
			self.port = None
		elif self.sock:
			self.sock.close()
			self.sock = None
		if self.tcp:
			filtering = 0
		else:
			filtering = self.filtering_behavior()
			if self.sock:
				self.sock.close()
				self.sock = None
		return mapping, filtering
	def CreateMessage(self, changeip=False, changeport=False):
		""" create message binding request"""
		data = {}
		data["STUN-TYPE"] = 'BINDING_REQUEST'
		data["CHANGE-REQUEST"] = 'CHANGE-REQUEST'
		data["CHANGE-IP"] = changeip
		data["CHANGE-PORT"] = changeport
		return data
	
	def binding_request(self, server, port, request, mapping=False):
		""" check nat type """
		udpconnect = False
		if self.tcp:
			self.sock = JsonSocket(JsonSocket.TCP)
			self.sock.set_reuseaddr()
			if self.port:
				self.sock.bind(self.port)
				print "bind on port %d" %self.port
			else:
				self.port = self.sock.bind(0)
		else:
			if not self.sock:
				self.sock = JsonSocket(JsonSocket.UDP)
			if mapping:
				udpconnect = True
		self.sock.set_timeout(3)
		if self.sock.connect(server, port, udpconnect):
			self.sock.send_obj(request)
			try:
				data = self.sock.read_obj()
			except Exception, e:
				print e
				return False
			self.local_addr = self.sock.getsockname()
			print self.local_addr
			if self.tcp:
				self.sock.close()
			else:
				self.sock.set_timeout(None)
			if 'BINDING-RESPONSE' in data:
				return False
			return data
		return False

	def mapping_behavior(self):
		"""  mapping behavior testing nat """
		message = self.CreateMessage()
		data = self.binding_request(STUN_SERVER, STUN_PORT, message, True)
		if not data:
			return False
		#=============================================
		#   TEST I
		# ============================================
		LOCAL_ADDR	= "%s:%d" % self.local_addr
		TEST_I = data['XOR-MAPPED-ADDRESS']
		OTHER_SERVER, OTHER_PORT = data['OTHER-ADDRESS'].split(":")
		if LOCAL_ADDR == TEST_I:
			return 0x10
		else:
		#=============================================
		#   TEST II
		# ============================================

			message = self.CreateMessage()
			data = self.binding_request(OTHER_SERVER, STUN_PORT, message, True)
			if not data:
				return False
			TEST_II = data['XOR-MAPPED-ADDRESS']
			if TEST_I == TEST_II:
				return 0x01
			else:
		#=============================================
		#   TEST III
		# ============================================
				message = self.CreateMessage()
				data = self.binding_request(OTHER_SERVER, int(OTHER_PORT), message, True)
				if not data:
					return False
				TEST_III = data['XOR-MAPPED-ADDRESS']
				if TEST_II == TEST_III:
					return 0x02
				else:
					if self.tcp:
						port1 = int(TEST_I.split(":")[1])
						port2 = int(TEST_II.split(":")[1])
						port3 = int(TEST_III.split(":")[1])
						if abs(port2-port1) < 5 and abs(port3-port1) <5:
							if port1 < port2 < port3:
								return 0x04
							elif port1 > port2 > port3:
								return 0x05
					return 0x03



	def filtering_behavior(self):
		""" filtering behavior testing nat """

		#=============================================
		#   TEST I
		# ============================================
		message = self.CreateMessage()
		data = self.binding_request(STUN_SERVER, STUN_PORT, message)
		if not data:
			return False
		#=============================================
		#   TEST II
		# ============================================

		message = self.CreateMessage(changeip=True, changeport=True)
		data = self.binding_request(STUN_SERVER, STUN_PORT, message)
		if data:
			return 0x01
		else:

		#=============================================
		#   TEST III
		# ============================================
			message = self.CreateMessage(changeip=False, changeport=True)
			data = self.binding_request(STUN_SERVER, STUN_PORT, message)
			if data:
				return 0x02
			else:
				return 0x03
