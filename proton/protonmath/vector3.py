import math

class Vector3(object):

    def __init__(self,_x,_y,_z):
        super(Vector3, self).__init__()
        self.x = _x
        self.y = _y
        self.z = _z

    def dot(self, v2):
        return self.x * v2.x + self.y * v2.y + self.z * v2.z

    def len(self):
        return math.sqrt(self.dot(self))

    def mul(self, f):
        self.x *= f
        self.y *= f
        self.y *= f

    def __add__(self, v2):
        return Vector3(self.x + v2.x, self.y + v2.y, self.z + v2.z)

    def __sub__(self, v2):
        return Vector3(self.x - v2.x, self.y - v2.y, self.z - v2.z)

    def __mul__(self, v2):
        return self.dot(v2)

    def normalize(self):
        l = self.len()
        return Vector3(self.x / l, self.y / l, self.z / l)