import os
import sys
import unittest

from proton.protonmath.matrix3 import Matrix3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from matrix3 import *

class TestMatrix3(unittest.TestCase):


    def test1(self):
        m1 = Matrix3(1,2,3,1,2,3,-1,6,3) # singular
        determinant = m1.det()
        self.assertEqual(determinant, 0)

    def test2(self):
        m1 = Matrix3(1,1,1,1,1,1,1,1,1)
        m2 = Matrix3(2,1,2,1,2,1,2,1,2)
        m3 = m1 * m2
        self.assertEqual(m3.at(0,0),5)

    def test3(self):
        m1 = Matrix3(1,2,5,0,3,1,0,1,-1)
        m2 = Matrix3(3,4,2,1,3,3,-5,2,4)
        m3 = m1 * m2
        self.assertEqual(m3.at(0,1), 20)

    def test4(self):
        m1 = Matrix3(1.0,0.0,0.0,0.0, 1.0, 0.0, 0.0,0.0, 1.0)
        m2 = m1.inverse()
        m3 = m1 * m2
        self.assertEqual(m3.at(0,0), 1)
        self.assertEqual(m3.at(0,1), 0)

    def test5(self):
        m1 = Matrix3(12.0,1.5,-5.2,2.5, 2.5, 10.5, 7.0,-0.5, -1.0)
        m2 = m1.inverse()
        m3 = m1 * m2
        self.assertTrue(abs(m3.at(0,0) - 1) < 0.001)
        self.assertTrue(abs(m3.at(0,1) - 0) < 0.001)

