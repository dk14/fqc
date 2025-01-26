import unittest

from clacomp import *
from hamicomp import *

class Testing(unittest.TestCase):
    def test_classic(self):
        a = 'some'
        b = 'some'
        self.assertEqual(a, b)

if __name__ == '__main__':
    unittest.main()