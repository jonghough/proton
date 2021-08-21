import math
from proton.protonmath.vector2 import *

class Matrix2(object):

    def __init__(self, a00, a01, a10, a11):
        self.items = [a00,a01,a10,a11]

    @staticmethod
    def init(items):
        return Matrix2(items[0], items[1], items[2], items[3])

    def at(self, i, j):
        return self.items[i * 2 + j]

    def set(self, i, j, val):
        self.items[i * 2 + j] = val

    def __add__(self, m2):
        l = [x + y for x,y in zip(self.items, m2.items)]
        return Matrix2(l)

    def __iadd__(self, m2):
        self = self.__add__(m2)
        return self

    def __sub__(self, m2):
        l = [x - y for x,y in zip(self.items, m2.items)]
        return Matrix2.init(l)

    def __isub__(self, m2):
        self = self.__sub__(m2)
        return self

    def __mul__(self, m2):
        a00 = self.at(0,0) * m2.at(0,0) + self.at(0,1) * m2.at(1,0)
        a01 = self.at(0,0) * m2.at(0,1) + self.at(0,1) * m2.at(1,1)
        a10 = self.at(1,0) * m2.at(0,0) + self.at(1,1) * m2.at(1,0)
        a11 = self.at(1,0) * m2.at(0,1) + self.at(1,1) * m2.at(1,1)
        return Matrix2(a00,a01,a10,a11)

    def __imul__(self,m2):
        self = self.__imul__(m2)
        return self

    def lmul(self, v):
        a00 = self.at(0,0) * v.x + self.at(0,1) * v.y
        a10 = self.at(1,0) * v.x + self.at(1,1) * v.y
        return Vector2(a00,a10)

    def rmul(self, v):
        a00 = self.at(0,0) * v.x + self.at(1,0) * v.y
        a10 = self.at(0,1) * v.x + self.at(1,1) * v.y
        return Vector2(a00,a10)

    def det(self):
        return self.at(0,0) * self.at(1,1) - self.at(0,1) * self.at(1,0)

    def transpose(self):
        a00 = self.at(0,0)
        a01 = self.at(1,0)
        a10 = self.at(0,1)
        a11 = self.at(1,1)
        return Matrix2(a00,a01,a10,a11)

    def inv(self):

        d = self.det()
        a00 = self.at(1,1) / d
        a01 = -self.at(0,1) / d
        a10 = -self.at(1,0) / d
        a11 = self.at(0,0) / d

        return Matrix2(a00,a01,a10,a11)