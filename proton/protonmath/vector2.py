import math


class Vector2(object):

    def __init__(self,_x,_y):
        #super(Vector2, self).__init__()
        self.x = _x
        self.y = _y

    def dot(self, v2):
        return self.x * v2.x + self.y * v2.y

    def len(self):
        return math.sqrt(self.dot(self))

    def mul(self, f):
        self.x *= f
        self.y *= f

    def __add__(self, v2):
        return Vector2(self.x + v2.x, self.y + v2.y)

    def __rmul__(self, f):
        return Vector2(self.x * f, self.y * f)

    def __sub__(self, v2):
        return Vector2(self.x - v2.x, self.y - v2.y)

    def __mul__(self, v2):
        if isinstance(v2, self.__class__):
            return self.dot(v2)
        else:
            return v2 * self

    def magnitude(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        l = self.len()
        if l < 0.00001:
            return Vector2(0,0)
        else:
            return Vector2(self.x / l, self.y / l)

    def normalized(self):
        l = self.len()
        self.x /= l
        self.y /= l

    @staticmethod
    def proj(v1, v2):
        v2norm = v2.normalize()
        d = v1.dot(v2norm)
        return Vector2(v2norm.x *d , v2norm.y * d)

    @staticmethod
    def dist(v1, v2):
        return math.sqrt((v1.x - v2.x) * (v1.x - v2.x) + (v1.y - v2.y) * (v1.y - v2.y))
