"""
this is test module for class in gshs
"""

import unittest
import os, sys
lib_path = os.path.abspath(os.path.join('..', ''))
sys.path.append(lib_path)
from gshs import Users
class Test_Userclass(unittest.TestCase):

    def setUp(self):
        self.user = Users()

    def test_getuser(self):
        # make sure get user from function
        self.assertEqual(self.user.getuser('hiep'), 'hiep')

if __name__ == '__main__':
    unittest.main()