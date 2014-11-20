#!/usr/bin/env python
#
# Name:			sv_user
# Description:	database
#

import os, datetime
import pymongo
from pymongo import Connection
class Peer():
	def __init__(self):
		cn = Connection("mongodb://nthiep:16081992761312nth@linus.mongohq.com:10092/app30915045")
		self.db = cn.app30915045
	def login(self, token, mac, lport, port):
		timestamp = datetime.datetime.now()
		utc_timestamp = datetime.datetime.utcnow()
		self.db.logins.ensure_index("time" ,expireAfterSeconds= 10)
		self.db.logins.insert({"time": utc_timestamp, "token": token, "mac" : mac, "lport": lport, "port": port})
	def checklogin(self, token, mac):		
		q = { "token": token, "mac" : mac }
		pe = self.db.logins.find_one(q)
		if pe:
			return pe
		return False
	def online(self, token, mac, host, nat):
		self.db.onlines.insert({"token": token, "mac" : mac, "host": host, "nat": nat})
	def checkonline(self, token, mac):
		q = { "token": token, "mac" : mac }
		pe = self.db.onlines.find_one(q)
		if pe:
			return pe
		return False
	def rmonline(self, token, mac):
		q = { "token": token, "mac" : mac }
		self.db.onlines.remove(q)
	def info(self, token, mac):
		q = { "token": token, "mac" : mac }
		p = self.db.onlines.find_one(q)
		return p
	def session(self, session, lport, laddr, port, addr, nat):
		timestamp = datetime.datetime.now()
		utc_timestamp = datetime.datetime.utcnow()
		self.db.sessions.ensure_index("time",expireAfterSeconds = 10)
		self.db.sessions.insert({"time": utc_timestamp, "session": session, "lport" : lport, "laddr": laddr, "port": port, "addr": addr, "nat": nat})
	def checksession(self, session):
		q = { "session": session}
		se = self.db.sessions.find_one(q)
		if se:
			return se
		return False
	def lspeer(self, token):
		q = {"token": token}
		data = self.db.onlines.find(q).sort("host")
		return data
	def addlog(self, token, mac, log):
		time = str(datetime.datetime.now())
		q = {"time": time, "token": token, "mac" : mac, "log": log}
		self.db.logs.insert(q)
	def logs(self, token):
		q = {"token": token}
		data = self.db.logs.find(q).sort("time",pymongo.DESCENDING)
		return data