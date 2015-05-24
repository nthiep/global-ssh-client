#!/usr/bin/env python
#
# Name:			output module
# Description:	print all respone message of server
#

class Output(object):
	""" print output to screen """
	def __init__(self):
		pass
	def register(self, data):
		if data["response"]:
			print "* RESULT: registered successfully!"
		else:
			print "* RESULT: registered is failed!"
	def authuser(self, data):
		if data["response"]:
			print "* RESULT: login successfully!"
		else:
			print "* RESULT: login is failed!"
	def join_domain(self, data):
		if data:
			print "* RESULT: join domain successfully!"
		else:
			print "* RESULT: can't join this domain!"
	def addnetwork(self, data):
		if data:
			print "* RESULT: Add network successfully!"
		else:
			print "* RESULT: Add network is failed!"
	def renetwork(self, data, remove=False):
		if data:
			if remove:
				print "* RESULT: remove network successfully!"
				return
			print "* RESULT: network will be remove:"
		else:
			print "* RESULT: NOT Network Found!"

	def info_machine(self, data):
		if data:
			print "* MAC ADDRESS:\t %s" %data["mac"]
			print "* JOIN NETWORK:\t %s" %data["join"]
			print "* GATEWAY:\t %s" %data["gateway"]
			print "* NAT TYPE:\t %s" %data["nat"]
			print "* ADD TIME:\t %s" %data["added"]
			print "* HOSTNAME:\t %s" %data["hostname"]
			print "* PLATFORM:\t %s" %data["platform"]
			print "* IP ADDRESS:\t %s" %data["ip"]
		else:
			print "* RESULT: CAN'T SHOW INFORMATION!"
	def listmachine(self, data):
		if data:
			try:
				template = "{0:25}{1:20}{2:30}"
				print template.format("HOSTNAME", "MAC", "PLATFORM")
				for m in data:
					print template.format(m["hostname"], m["mac"], m["platform"])
			except:
				print "* RESULT: No Machine found"
		else:
			print "* RESULT: No Machine found!"

	def connect(self, data):
		if not data:
			print "* RESULT: Hostname not found!"
			return False
		else:
			i = 1
			template = "{0:25}{1:20}{2:30}"
			print template.format("HOSTNAME", "MAC", "PLATFORM")
			for m in data["machine"]:
				print template.format(m["hostname"], m["mac"], m["platform"])
			maxhost = len(data["machine"])
			host = raw_input("please choice your machine (1-%d) " %maxhost)
			if host in range(1,maxhost):
				return data["machine"][host-1]["mac"]
			else:
				return False
	def basic_connect(self):
		print "* NOT Connect Global SSH *"
		print "* Basic SSH Connecting...."
	def show_nat_type(self, mapping, filtering, nattype):
		""" show nat infomation """
		info_mapping = ["N/A",  "Endpoint Independent Mapping", "Address Dependent Mapping",\
			"Address and Port Dependent Mapping","","","","","","","Internet"]
		info_filtering = ["N/A", "Endpoint Independent Filtering",\
				"Address Dependent Filtering",  "Address and Port Dependent Filtering"]
		print "* ============================ *"		
		print "* NAT TYPE DEFINED IN RFC 5780 *"
		print "* Mapping Behavior:\t %s" %info_mapping[mapping]
		print "* Filtering Behavior:\t %s" %info_filtering[filtering]
		print "* NAT TYPE:\t %s" %nattype
		print "* ============================ *"
		print "* NAT TYPE DEFINED IN RFC 3489 *"
		nat_old = ["N/A", "Full Cone", "Port Restricted Cone", "Port Restricted Cone", "Symmetric"]
		if mapping == 1:
			print "* NAT TYPE:\t %s" %nat_old[filtering]
		elif mapping == 3 and filtering == 3:
			print "* NAT TYPE:\t %s" %nat_old[4]
		else:
			print "* NAT TYPE:\t N/A (NOT DEFINED)"
		return True

	def bind(self, data):
		if not bind:
			print "* ERROR: bind port not valid!"
			print "* INFO: use [bindsource:]bindport"
			return True
	def logout(self, data):
		if data:
			print "* RESULT: logout successful!"
			return
		print "* RESULT: logout failed!"
		return
	def processing(self):
		print "* Please wait processing...."
	def process(self, data):
		if data:			
			print "* RESULT: process successful!"
			return		
		print "* RESULT: can not process!"
	def error(self, error):
		print "* ERROR: %s" %error

