import unittest
import sys
sys.path.insert(0, '../src')

class Test_Client(unittest.TestCase):
    def test_key(self):
        self.assertEqual(res.reqframe(100), 'd\x00')
if __name__ == '__main__':
    unittest.main()