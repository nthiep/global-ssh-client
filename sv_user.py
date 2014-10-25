import os
import pymongo
from pymongo import Connection
class User():
	def __init__(self, username):
		
		self.client = MongoClient()
		self.db = self.client['global-ssh']	
	def check(self):		
		q = { "user": self.username }
		us = self.db.users.find_one(q)
		if us:
			return True
		return False

	def register(self, pswd):
		q = {"user": self.username, "pass": pswd}		
		lsuser = self.db.users
		lsuser.insert(q)
	def auth(self, pswd):
		q = {"user": self.username}		
		lsuser = self.db.users
		us = lsuser.find_one(q)
		if us["pass"] == pswd:
			return True
		return False

	def checkfriendrq(self, user):		
		q = {"user": self.username, "request": user}
		frq = self.db.friendrq
		rq = frq.find_one(q)
		if rq:
			return True
		return False
	def lsfriendrq(self):		
		q = {"user": self.username}
		frq = self.db.friendrq
		data = frq.find(q)
		return data
	def addfiendrq(self, user, time):
		q = {"user": self.username, "request": user, "time": time}
		frq = self.db.friendrq
		frq.insert(q)
	def rmfriendrq(self, user):		
		q = {"user": self.username, "request": user}
		frq = self.db.friendrq
		frq.remove(q)

	def addfriend(self, friend):
		q = {"user": self.username, "friend": friend}
		fr = self.db.friend
		fr.insert(q)
		r = {"user": self.username, "request": friend}
		frq = self.db.friendrq
		frq.remove(r)
	def addlogs(self, time, log):
		q = {"user": self.username, "time": time, "logs": log}
		lg = self.db.logs
		lg.insert(q)
	def checkfriend(self, friend):
		if self.username == friend:
			return True
		q = {"user": self.username, "friend": friend}
		p = {"user": friend, "friend": self.username}
		frienddb = self.db.friend
		data1 = frienddb.find_one(q)
		data2 = frienddb.find_one(p)
		if data1 or data2:
			return True
		return False
	def lsfriend(self):
		q = {"user": self.username}
		p = {"friend": self.username}
		frienddb = self.db.friend
		data1 = frienddb.find(q)
		data2 = frienddb.find(p)
		return data1, data2

	def logs(self):
		q = {"user": self.username}
		lg = self.db.logs
		data = lg.find(q).sort("time",pymongo.DESCENDING)
		return data

	def uploadkey(self, key):
		us = self.db.keys
		i = us.find_one({"user": self.username})
		if i:
			us.update({"user": self.username}, {"key": key})
			return
		us.insert({"user": self.username, "key": key})
	def downloadkey(self):
		us = self.db.keys
		key = us.find_one({"user": self.username})
		return key