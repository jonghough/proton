import unittest
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import vector3
from math import *

class TestVector2(unittest.TestCase):

    def test1(self):
        v = vector3.Vector3(0,1,0)
        u = vector3.Vector3(3,5,0)
        self.assertEqual(v.dot(u), 5)

    def test2(self):
        v = vector3.Vector3(10,10,10)
        self.assertTrue(abs(v.len() - sqrt(300)) < 0.001)

    def test3(self):
        v = vector3.Vector3(2.4, 3.5, -30.1)
        u = v + v
        self.assertEqual(u.x, 4.8)
        self.assertEqual(u.y, 7.0)
        self.assertEqual(u.z, -60.2)

    def test4(self):
        v = vector3.Vector3(1.7, 0.2, 1.1)
        w = vector3.Vector3(0.7, -0.2, 0.01)
        u = v - w
        self.assertEqual(u.x, 1.0)
        self.assertEqual(u.y, 0.4)
        self.assertEqual(u.z, 1.09)



if __name__ == '__main__':
    unittest.main()
