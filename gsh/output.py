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
			print "registered successfully!"
		else:
			print "registered is failed!"

	def listmachine(self, data):
		if data["usermac"]:
			print "username"
			for m in data["usermac"]:
				print m["hostname"] + "\t" + m["mac"] + "\t" + m["platform"]
		if data["netmac"]:
			print "network"
			for m in data["netmac"]:
				print m["hostname"] + "\t" + m["mac"] + "\t" + m["platform"]
	def connect(self, data):
		print data		