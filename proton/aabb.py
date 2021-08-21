from proton.protonmath.matrix2 import *
from proton.protonmath.matrix3 import *
from proton.protonmath.vector2 import *

from proton.protonmath.vector3 import *

'''
Actually OBB, but called AABB.
'''


class AABB(object):
    def __init__(self, dimensions):
        self.worldtransform = Matrix3.identity()
        self.dims = dimensions
        self.calcbounds()
        self.normals = (Vector2(1, 0), Vector2(0, 1))
        self.myprojection1 = (0, 0)
        self.myprojection2 = (0, 0)

    def calcbounds(self):
        p1 = self.worldtransform.lmul(
            Vector3(self.dims.x / 2.0, self.dims.y / 2.0, 1))
        p2 = self.worldtransform.lmul(
            Vector3(self.dims.x / 2.0, -self.dims.y / 2.0, 1))
        p3 = self.worldtransform.lmul(
            Vector3(-self.dims.x / 2.0, self.dims.y / 2.0, 1))
        p4 = self.worldtransform.lmul(
            Vector3(-self.dims.x / 2.0, -self.dims.y / 2.0, 1))

        self.q1 = Vector2(p1.x, p1.y)
        self.q2 = Vector2(p2.x, p2.y)
        self.q3 = Vector2(p3.x, p3.y)
        self.q4 = Vector2(p4.x, p4.y)

    def column(self, i):
        return self.worldtransform.col2Vector2(i)

    def columnnormalized(self, i):
        return self.worldtransform.col2Vector2(i).normalize()

    def center(self):
        return self.worldtransform.col2Vector2(2)

    def calcnormals(self):
        """
        Calculates the normal vectors at the current time, and the min max projection of the
        bounding box's corners onto these vectors.
        :return:
        """
        self.normals = (Vector2(self.worldtransform.at(0, 0), self.worldtransform.at(1, 0)).normalize(),
                        Vector2(self.worldtransform.at(0, 1), self.worldtransform.at(1, 1)).normalize())
        a = self.get_bounds_of_projection(self.normals[0])
        self.myprojection1 = a
        b = self.get_bounds_of_projection(self.normals[1])
        self.myprojection2 = b

    def get_normals(self):
        """
        Returns the normal vectors.
        :return:
        """
        return self.normals

    @staticmethod
    def find_intersection_point(box1, box2):

        b1 = [(box1.q1, box1.q2), (box1.q1, box1.q3),
              (box1.q4, box1.q2), (box1.q4, box1.q3)]
        b2 = [(box2.q1, box2.q2), (box2.q1, box2.q3),
              (box2.q4, box2.q2), (box2.q4, box2.q3)]

        for i in range(0, 4):
            for j in range(0, 4):
                v1 = b1[i]
                v2 = b2[j]

                denom = ((v1[0].x - v1[1].x) * (v2[0].y - v2[1].y) -
                         (v1[0].y - v1[1].y) * (v2[0].x - v2[1].x))
                if abs(denom) < 0.00001:
                    continue
                else:
                    x = ((v1[0].x * v1[1].y - v1[0].y * v1[1].x) * (v2[0].x - v2[1].x) - (v1[0].x - v1[1].x) * (
                        v2[0].x * v2[1].y - v2[0].y * v2[1].x)) / \
                        denom

                    y = ((v1[0].x * v1[1].y - v1[0].y * v1[1].x) * (v2[0].y - v2[1].y) - (v1[0].y - v1[1].y) * (
                        v2[0].x * v2[1].y - v2[0].y * v2[1].x)) / \
                        denom

                    if min(v1[0].x, v1[1].x) <= x and x <= max(v1[0].x, v1[1].x):
                        return (x, y)

        return None

    def get_bounds_of_projection(self, projvec):
        """
        Gets the maximum and minimum bounds of the bounding box's
        projection onto the given projection vector
        :param projvec: projection vector
        :return: (min, max) tuple
        """

        q1proj = Vector2.proj(self.q1, projvec).dot(projvec)
        q2proj = Vector2.proj(self.q2, projvec).dot(projvec)
        q3proj = Vector2.proj(self.q3, projvec).dot(projvec)
        q4proj = Vector2.proj(self.q4, projvec).dot(projvec)

        maxv = max([q1proj, q2proj, q3proj, q4proj])
        minv = min([q1proj, q2proj, q3proj, q4proj])

        return (minv, maxv)

    @staticmethod
    def is_collide(box1, box2):
        T = box2.center() - box1.center()
        # T = Vector2(T.dot(box1.column(0)), T.dot(box1.column(1)))
        p1 = box1.worldtransform.lmul(Vector3(box1.dims.x / 2.0, 0, 0))
        b1_e0 = Vector2(p1.x, p1.y)

        p1 = box1.worldtransform.lmul(Vector3(0, box1.dims.y / 2.0, 0))
        b1_e1 = Vector2(p1.x, p1.y)

        p2 = box2.worldtransform.lmul(Vector3(box2.dims.x / 2.0, 0, 0))
        b2_e0 = Vector2(p2.x, p2.y)

        p2 = box2.worldtransform.lmul(Vector3(0, box2.dims.y / 2.0, 0))
        b2_e1 = Vector2(p2.x, p2.y)

        # separation 1, box1 x dir
        t = b1_e0.normalize().dot(T)
        r1 = b1_e0.len()  # box1.dims.x / 2.0
        r2 = (b2_e0).len() * abs(box1.columnnormalized(0).dot(box2.columnnormalized(0))) + (b2_e1).len() * \
            abs(box1.columnnormalized(
                0).dot(
                box2.columnnormalized(
                    1)))

        if abs(t) > r1 + r2:
            return None

        # separation 2, box1 y dir
        t = b1_e1.normalize().dot(T)
        r1 = b1_e1.len()  # box1.dims.y / 2.0
        r2 = (b2_e0).len() * abs(box1.columnnormalized(1).dot(box2.columnnormalized(0))) + (b2_e1).len() * \
            abs(box1.columnnormalized(
                1).dot(
                box2.columnnormalized(
                    1)))

        if abs(t) > r1 + r2:
            return None

        # separation 3, box2 x dir
        t = b2_e0.normalize().dot(
            T)  # abs(T.x * (box1.column(0).dot(box2.column(0))) + T.y * (box1.column(1).dot(box2.column(0))))
        r2 = b2_e0.len()  # box2.dims.x / 2.0
        r1 = (b1_e0).len() * abs(box1.columnnormalized(0).dot(box2.columnnormalized(0))) + (b1_e1).len() * \
            abs(box1.columnnormalized(
                1).dot(
                box2.columnnormalized(
                    0)))
        if abs(t) > r1 + r2:
            return None

        # separation 4, box2 y dir
        t = b2_e1.normalize().dot(
            T)  # abs(T.x * (box1.column(0).dot(box2.column(1))) + T.y * (box1.column(1).dot(box2.column(1))))
        r2 = b2_e1.len()  # box2.dims.y / 2.0
        r1 = (b1_e0).len() * abs(box1.columnnormalized(0).dot(box2.columnnormalized(1))) + (b1_e1).len() * \
            abs(box1.columnnormalized(
                1).dot(
                box2.columnnormalized(
                    1)))

        if abs(t) > r1 + r2:
            return None

        # separation 5, cross
        # t = abs(T.y * (box1.columnnormalized(0).dot(box2.columnnormalized(0)) - T.x * (box1.columnnormalized(1).dot(box2.columnnormalized(0)))))
        # r1 = (box1.dims.x / 2.0) * abs(box1.columnnormalized(1).dot(box2.columnnormalized(0))) + (box1.dims.y / 2.0) * \
        #                                                                      abs(box1.columnnormalized(0).dot(
        #                                                                          box2.columnnormalized(0)))
        # if abs(t) > r1:
        #     return None

        # # separation 5, cross
        # t = abs(T.y * (box1.column(0).dot(box2.column(1)) - T.x * (box1.column(1).dot(box2.column(1)))))
        # r1 = (box1.dims.x / 2.0) * abs(box1.column(1).dot(box2.column(1))) + (box1.dims.y / 2.0) * \
        #                                                                          abs(box1.column(0).dot(
        #                                                                              box2.column(1)))
        # if abs(t) > r1:
        #     return None

        return AABB.find_intersection_point(box1, box2)

    def iscolliding(self, box2):
        """
        Dectermines if this bounding box is colliding with the other
        bounding box
        :param other: other bounding box.
        :return: true, if colliding, false otherwise.
        """
        box1 = self
        mynormals = box1.get_normals()
        # otnormals = other.get_normals()

        myproj1 = box1.myprojection1
        otproj1 = box2.get_bounds_of_projection(mynormals[0])

        myproj2 = box1.myprojection2
        otproj2 = box2.get_bounds_of_projection(mynormals[1])

        if myproj1[1] < otproj1[0] or otproj1[1] < myproj1[0]:
            return None
        elif myproj2[1] < otproj2[0] or otproj2[1] < myproj2[0]:
            return None

        otproj1 = box2.myprojection1
        myproj1 = box1.get_bounds_of_projection(box2.get_normals()[0])

        otproj2 = box2.myprojection2
        myproj2 = box1.get_bounds_of_projection(box2.get_normals()[1])

        if myproj1[1] < otproj1[0] or otproj1[1] < myproj1[0]:
            return None
        elif myproj2[1] < otproj2[0] or otproj2[1] < myproj2[0]:
            return None

        else:
            return AABB.find_intersection_point(box1, box2)
