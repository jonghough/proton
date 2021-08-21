from proton.protonmath.vector3 import *
from proton.protonmath.matrix2 import *
from proton.protonmath.vector2 import *

class Matrix3(object):

    def __init__(self,a00,a01,a02,a10,a11,a12,a20,a21,a22):
        self.items = [a00,a01,a02,a10,a11,a12,a20,a21,a22]

    @staticmethod
    def init(items):
        return Matrix3(items[0], items[1], items[2], \
                        items[3], items[4], items[5], \
                        items[6], items[7], items[8])


    @staticmethod
    def identity():
        return Matrix3(1,0,0,0,1,0,0,0,1)

    @staticmethod
    def zeros():
        return Matrix3(0,0,0,0,0,0,0,0,0)

    def at(self, i, j):
        return self.items[i * 3 + j]

    def set(self, i, j, val):
        self.items[i * 3 + j] = val


    def col2Vector2(self, i):
        return Vector2(self.at(0,i), self.at(1,i))

    def col2Vector3(self, i):
        return Vector3(self.at(0, i), self.at(1, i), self.at(2,i))

    def __add__(self, m2):
        l = [x + y for x,y in zip(self.items, m2.items)]
        return Matrix3.init(l)

    def __iadd__(self,m2):
        self = self.__add__(m2)
        return self

    def __sub__(self, m2):
        l = [x - y for x,y in zip(self.items, m2.items)]
        return Matrix3.init(l)

    def __isub__(self,m2):
        self = self.__sub__(m2)
        return self

    def __mul__(self, m2):
        a00 = self.at(0,0) * m2.at(0,0) + self.at(0,1) * m2.at(1,0) + self.at(0,2) * m2.at(2,0)
        a01 = self.at(0,0) * m2.at(0,1) + self.at(0,1) * m2.at(1,1) + self.at(0,2) * m2.at(2,1)
        a02 = self.at(0,0) * m2.at(0,2) + self.at(0,1) * m2.at(1,2) + self.at(0,2) * m2.at(2,2)

        a10 = self.at(1,0) * m2.at(0,0) + self.at(1,1) * m2.at(1,0) + self.at(1,2) * m2.at(2,0)
        a11 = self.at(1,0) * m2.at(0,1) + self.at(1,1) * m2.at(1,1) + self.at(1,2) * m2.at(2,1)
        a12 = self.at(1,0) * m2.at(0,2) + self.at(1,1) * m2.at(1,2) + self.at(1,2) * m2.at(2,2)

        a20 = self.at(2,0) * m2.at(0,0) + self.at(2,1) * m2.at(1,0) + self.at(2,2) * m2.at(2,0)
        a21 = self.at(2,0) * m2.at(0,1) + self.at(2,1) * m2.at(1,1) + self.at(2,2) * m2.at(2,1)
        a22 = self.at(2,0) * m2.at(0,2) + self.at(2,1) * m2.at(1,2) + self.at(2,2) * m2.at(2,2)
        return Matrix3(a00,a01,a02,a10,a11,a12,a20,a21,a22)

    def __imul__(self,m2):
        self = self.__mul__(m2)
        return self

    def lmul(self, v):
        x = self.at(0,0) * v.x + self.at(0,1) * v.y + self.at(0,2) * v.z
        y = self.at(1,0) * v.x + self.at(1,1) * v.y + self.at(1,2) * v.z
        z = self.at(2,0) * v.x + self.at(2,1) * v.y + self.at(2,2) * v.z
        return Vector3(x,y,z)

    def rmul(self, v):
        x = self.at(0,0) * v.x + self.at(1,0) * v.y + self.at(2,0) * v.z
        y = self.at(0,1) * v.x + self.at(1,1) * v.y + self.at(2,1) * v.z
        z = self.at(0,2) * v.x + self.at(1,2) * v.y + self.at(2,2) * v.z
        return Vector3(x,y,z)

    def minor(self, i, j):
        minors = []
        for x in range(0,3):
            for y in range(0, 3):
                if x == i or y == j:
                    continue
                else:
                    minors.append(self.at(x,y))

        return Matrix2.init(minors)

    def transpose(self):
        transitems = [ \
                self.at(0,0), self.at(1,0), self.at(2,0), \
                self.at(0,1), self.at(1,1), self.at(2,1), \
                self.at(0,2), self.at(1,2), self.at(2,2) ]
        return Matrix3.init(transitems)

    def det(self):
        return self.at(0,0) * (self.at(1,1) * self.at(2,2) - self.at(1,2) * self.at(2,1)) - \
                self.at(0,1) * (self.at(1,0) * self.at(2,2) - self.at(1,2) * self.at(2,0)) + \
                self.at(0,2) * (self.at(1,0) * self.at(2,1) - self.at(1,1) * self.at(2,0))

    def inverse(self):
        d = self.det()
        trans = self.transpose()
        invitems = []
        for i in range(0,3):
            for j in range(0,3):
                minorm = trans.minor(i,j)
                minordet = minorm.det() / d
                invitems.append(minordet * ((-1.0) ** (i + j)))

        return Matrix3.init(invitems)

