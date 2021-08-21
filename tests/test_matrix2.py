import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


from proton.protonmath.matrix2 import Matrix2

class TestMatrix2(unittest.TestCase):


    def test1(self):
        m1 = Matrix2(1,2,1,2) # singular
        determinant = m1.det()
        self.assertEqual(determinant, 0)

    def test2(self):
        m1 = Matrix2(1,1,1,1)
        m2 = Matrix2(2,1,2,1)
        m3 = m1 * m2
        self.assertEqual(m3.at(0,0),4)

    def test3(self):
        m1 = Matrix2(1,2,5,0)
        m2 = Matrix2(3,4,2,1)
        m3 = m1 * m2
        self.assertEqual(m3.at(0,1), 6)

    def test4(self):
        m1 = Matrix2(1.0,6.0,4.0,-5.0)
        m2 = m1.inv()
        m3 = m1 * m2
        self.assertEqual(m3.at(0,0), 1)
        self.assertEqual(m3.at(0,1), 0)
