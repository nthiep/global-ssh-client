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
	def addnetwork(self, data):
		if data:
			print "* RESULT: add network successfully!"
		else:
			print "* RESULT: add network is failed!"
	def renetwork(self, data, remove=False):
		if data:
			if remove:
				print "* RESULT: remove network successfully!"
				return
			print "* RESULT: network will be remove:"
		else:
			print "* RESULT: not network found!"
	def listmachine(self, data):
		if data["response"]:
			template = "{0:25}{1:20}{2:30}"
			print template.format("HOSTNAME", "MAC", "PLATFORM")
			for m in data["machine"]:
				print template.format(m["hostname"], m["mac"], m["platform"])
		else:
			print "* RESULT: no machine found"
	def connect(self, data):
		if not data:
			print "* RESULT: hostname not found"
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
		if not data:
			print "* RESULT: you are not login!"
			return
		if data["response"]:
			print "* RESULT: logout successful!"
			return
		print "* RESULT: logout failed!"
		return

