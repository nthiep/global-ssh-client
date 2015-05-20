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
	def logout(self, data):
		if data:
			print "* RESULT: logout successful!"
			return
		print "* RESULT: logout failed!"
		return
	def process(self, data):
		if data:			
			print "* RESULT: process successful!"
			return		
		print "* RESULT: can not process!"

