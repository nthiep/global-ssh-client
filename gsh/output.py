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