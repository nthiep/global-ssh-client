#!/usr/bin/env python
#
# Name:			sv_user
# Description:	database
#

import os, datetime
import pymongo
from pymongo import Connection
class User():
	def __init__(self):
		cn = Connection("database")
		self.db = cn.app30915045

	def user(self, username):
		q = {"user": username}		
		us = self.db.users.find_one(q)
		return us
	def check(self, username):		
		q = { "user": username }
		us = self.db.users.find_one(q)
		if us:
			return True
		return False
	def check_token(self, mac, token):
		q = {"mac": mac, "token": token}
		tk = self.db.tokens.find_one(q)
		if tk:
			return tk
		return False
	def add_token(self, mac, host, token, user):
		t = self.db.tokens.find_one({"mac": mac})
		if t:
			self.db.tokens.update({"mac": mac}, {'$set':{"host": host, "token": token, "user": user}})
		else:
			self.db.tokens.insert({"mac": mac, "host": host, "token": token, "user": user})
		return True		
	def register(self, username, pswd):
		q = {"user": username, "pass": pswd}		
		self.db.users.insert(q)
	def auth(self, username, pswd):
		q = {"user": username}		
		us = self.db.users.find_one(q)
		if us["pass"] == pswd:
			return True
		return False
	def machine(self, username):
		q = {"user": username}
		data = self.db.tokens.find(q)
		return data
	def onlines(self, username):
		q = {"user": username}
		data = self.db.onlines.find(q).sort("host")
		return data
	
	def logs(self, username):
		data = self.db.logs.find({"user": username}).sort("time",pymongo.DESCENDING)
		return data
	def addlog(self, user, mac, log):
		u = self.db.tokens.find_one({"mac": mac})
		time = str(datetime.datetime.now())
		q = {"time": time, "user": u["user"], "mac" : mac, "log": log}
		self.db.logs.insert(q)
