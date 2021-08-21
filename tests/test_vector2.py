import unittest
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import vector2
from math import *

class TestVector2(unittest.TestCase):

    def test1(self):
        v = vector2.Vector2(0,1)
        u = vector2.Vector2(3,5)
        self.assertEqual(v.dot(u), 5)

    def test2(self):
        v = vector2.Vector2(10,10)
        self.assertTrue(abs(v.len() - sqrt(200)) < 0.001)

    def test3(self):
        v = vector2.Vector2(2.4, 3.5)
        u = v + v
        self.assertEqual(u.x, 4.8)
        self.assertEqual(u.y, 7.0)

    def test4(self):
        v = vector2.Vector2(1.7, 0.2)
        w = vector2.Vector2(0.7, -0.2)
        u = v - w
        self.assertEqual(u.x, 1.0)
        self.assertEqual(u.y, 0.4)



if __name__ == '__main__':
    unittest.main()
