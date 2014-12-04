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
		cn = Connection("database")
		self.db = cn.app30915045

	def check_token(self, mac, token):
		q = {"mac": mac, "token": token}
		tk = self.db.tokens.find_one(q)
		if tk:
			return tk
		return False
	def login(self, mac, lport, port):
		timestamp = datetime.datetime.now()
		utc_timestamp = datetime.datetime.utcnow()
		self.db.logins.ensure_index("time" ,expireAfterSeconds= 10)
		lg = self.db.logins.find_one({"mac": mac})
		if lg:
			self.db.logins.update({"mac" : mac}, {'$set':{"lport": lport, "port": port}})
		else:
			self.db.logins.insert({"time": utc_timestamp, "mac" : mac, "lport": lport, "port": port})
	def checklogin(self, mac):		
		q = {"mac" : mac}
		pe = self.db.logins.find_one(q)
		if pe:
			return pe
		return False
	def online(self, user, mac, host):
		self.db.onlines.insert({"user": user, "mac" : mac, "host": host, "nat": "RAD"})

	def addnat(self, mac, nat):
		self.db.onlines.update({"mac": mac}, {'$set':{"nat": nat}})
	def checkconnect(self, mymac, mac):
		q = {"mac" : mymac }
		pe = self.db.onlines.find_one(q)
		if pe:
			user = pe["user"]
			q = self.db.onlines.find_one({"user": user, "mac": mac})
			if q:
				return True
		return False
	def rmonline(self, mac):
		q = {"mac" : mac}
		self.db.onlines.remove(q)
	def rm_all(self):
		self.db.onlines.remove()
	def info(self, mac):
		q = { "mac" : mac }
		p = self.db.onlines.find_one(q)
		if p:
			return p
		return False
	def udp_session(self, session, addr, port):
		timestamp = datetime.datetime.now()
		utc_timestamp = datetime.datetime.utcnow()
		self.db.udpsessions.ensure_index("time",expireAfterSeconds = 10)
		self.db.udpsessions.insert({"time": utc_timestamp, "session": session, "addr": addr, "port": port})
	def check_udp_session(self, session):
		q = { "session": session}
		se = self.db.udpsessions.find_one(q)
		if se:
			return se
		return False
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
	def lspeer(self, user):
		q = {"user": user}
		data = self.db.onlines.find(q).sort("host")
		return data
	def addlog(self, mac, log):
		u = self.db.tokens.find_one({"mac": mac})
		time = str(datetime.datetime.now())
		q = {"time": time, "user": u["user"], "mac" : mac, "log": log}
		self.db.logs.insert(q)
