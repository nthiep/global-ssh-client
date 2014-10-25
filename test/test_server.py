import unittest
import sys, os,json
import hashlib
sys.path.insert(0, '..')
from sv_webservice import app
 
class Test_Server(unittest.TestCase):
    def test_home(self):
        # Use Flask's test client for our test.
        self.test_app = app.test_client()
        headers = [("content_type",'application/json'), ("Accept", 'application/json')]
        response = self.test_app.post('/',headers=headers)                                    
        self.assertEquals(response.status, "200 OK")
    def test_login_fail(self):
        self.test_app = app.test_client()
        response = self.test_app.post('/login',data={
                'username': 'hiep',
                'password': hashlib.sha1("hiep").hexdigest()
            })
		                                      
        self.assertEquals(response.status, "You login with wrong credentials")
    def test_login_pass(self):
        self.test_app = app.test_client()
        headers = [("content_type",'application/json'), ("Accept", 'application/json')]
        response = self.test_app.post('/login',
        	data=json.dumps({
                'username': 'sheldon@cooper.com',
                'password': 'howimetyourmother'
            }), headers = headers)
		                                  
        self.assertEquals(response.status, "200 OK")
if __name__ == '__main__':
    unittest.main()