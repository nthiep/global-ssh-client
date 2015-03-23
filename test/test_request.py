"""
this is test module for class in gshs
"""

import unittest
import os, sys, json
lib_path = os.path.abspath(os.path.join('..', ''))
sys.path.append(lib_path)
from gshs import Request
class Test_Request(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(Test_Request, self).__init__(*args, **kwargs)
		
	def setUp(self):
		pass

	def test_register(self):
		# test register user
		data = json.dumps({"username": "username", "passwork": "passwork", "fullname": "full name", "email": "e@mail", "website": "website.ws"})
		#self.assertFalse(self.rq.register(data))
	def test_login(self):
		# make sure get user from function
		data = json.dumps({"username": "username", "passwork": "passwork", "mac": "00:00:00:00"})
		#self.assertTrue(self.rq.login(data))
	def test_authen(self):
		# make sure get user from function
		rq = Request()
		data = json.dumps({"mac": "00:00:00:00", "api": "85119ca8cefdad9160f92cbb1c9a4184d1a4dba0", "hostname": "host", "platform": "linux"})
		self.assertTrue(rq.authentication(data))

if __name__ == '__main__':
    unittest.main()