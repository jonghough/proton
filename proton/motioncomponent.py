from proton.protonmath.matrix3 import *
from proton.protonmath.vector2 import Vector2
from proton.component import Component
import math
from proton.gameobject import *


class MotionComponent(Component):

    def __init__(self, _gameobject):
        super(MotionComponent, self).__init__(_gameobject)
        self.worldtransform = Matrix3.identity()
        self.localtransform = Matrix3.identity()

    def position(self):
        return Vector2(self.worldtransform.at(0, 2), self.worldtransform.at(1, 2))

    def local_position(self):
        return Vector2(self.localtransform.at(0, 2), self.localtransform(1, 2))

    def set_position(self, x, y):
        """
        Sets the position of the game object to the point (x,y). Any child objects
        will also have their world positions update to maintain the same local position with
        this game object.
        :param x: x position
        :param y: y position
        :return: none
        """
        p = self.position()
        movepos = Matrix3.identity()
        movepos.set(0, 2, x - p.x)
        movepos.set(1, 2, y - p.y)

        self.worldtransform = movepos * self.worldtransform
        if self.game_object().parent is not None:
            self.localtransform = self.game_object().parent(
            ).motion.worldtransform.inverse() * self.worldtransform
        else:
            self.localtransform = Matrix3.identity()

        for child in self.game_object().children:
            child.motion.update_world_transform(self)

    def get_rotation(self):
        '''
        Gets the current rotation value, in radians.
        :return: rotation radians.
        '''
        c = self.worldtransform.at(0, 0)
        s = self.worldtransform.at(1, 0)

        return math.atan2(s, c)

    def set_position_on_parent_change(self):
        pass

    def set_local_position(self, x, y):
        p = self.position()
        movepos = Matrix3.identity()
        movepos.set(0, 2, x - p.x)
        movepos.set(1, 2, y - p.y)

        self.localtransform = movepos * self.localtransform

        if self.game_object().parent is not None:
            self.worldtransform = self.game_object().parent().motion.worldtransform * \
                self.localtransform

        else:
            self.worldtransform = Matrix3.identity() * self.localtransform

        for child in self.game_object().children:
            child.motion.update_world_transform(self)

    def forward(self):
        return Vector2(self.worldtransform.at(0, 0), self.worldtransform.at(1, 0))

    def update_world_transform(self, parent):
        self.worldtransform = parent.worldtransform * self.localtransform

        for child in self.game_object().children:
            child.motion.update_world_transform(self)

    def update_local_transform(self, parent):
        self.localtransform = parent.worldtransform.inverse() * self.worldtransform

        for child in self.game_object().children:
            child.motion.update_local_transform(self)

    def rotate_around(self, radians, pivot):

        c = math.cos(radians)
        s = math.sin(radians)

        pos = self.position()

        sub = Matrix3(0, 0, pivot.x, 0, 0, pivot.y, 0, 0, 0)
        rotator = Matrix3(c, -s, 0, s, c, 0, 0, 0, 1)

        self.worldtransform = (rotator * (self.worldtransform - sub)) + sub

        if self.game_object().parent is not None:
            self.localtransform = self.game_object().parent(
            ).motion.worldtransform.inverse() * self.worldtransform

        else:
            self.localtransform = Matrix3.identity()

        for child in self.game_object().children:
            child.motion.update_world_transform(self)

    def set_rotation(self, theta):
        scale = self.get_scale()
        mat = Matrix2(scale.x * math.cos(theta), scale.y * -math.sin(theta), scale.x * math.sin(theta),
                      scale.y * math.cos(theta))

        self.worldtransform.set(0, 0, mat.at(0, 0))
        self.worldtransform.set(0, 1, mat.at(0, 1))
        self.worldtransform.set(1, 0, mat.at(1, 0))
        self.worldtransform.set(1, 1, mat.at(1, 1))

    def rotate_by(self, radians):
        c = math.cos(radians)
        s = math.sin(radians)

        sub = Matrix3(0, 0, self.worldtransform.at(0, 2), 0,
                      0, self.worldtransform.at(1, 2), 0, 0, 0)
        rotator = Matrix3(c, -s, 0, s, c, 0, 0, 0, 1)

        self.worldtransform = (rotator * (self.worldtransform - sub)) + sub

        if self.game_object().parent is not None:
            self.localtransform = self.game_object().parent(
            ).motion.worldtransform.inverse() * self.worldtransform

        else:
            self.localtransform = Matrix3.identity()

        for child in self.game_object().children:
            child.motion.update_world_transform(self)

    def local_rotate_by(self, radians):
        c = math.cos(radians)
        s = math.sin(radians)

        sub = Matrix3(0, 0, self.localtransform.at(0, 2), 0,
                      0, self.localtransform.at(1, 2), 0, 0, 0)
        rotator = Matrix3(c, -s, 0, s, c, 0, 0, 0, 1)

        self.localtransform = (rotator * (self.localtransform - sub)) + sub

        if self.game_object().parent is not None:
            self.worldtransform = self.game_object().parent().motion.worldtransform * \
                self.localtransform

        else:
            self.worldtransform = Matrix3.identity() * self.localtransform

        for child in self.game_object().children:
            child.motion.update_world_transform(self)

    def set_scale(self, x, y):

        scalex = Vector2(self.worldtransform.at(0, 0),
                         self.worldtransform.at(1, 0)).len()
        scaley = Vector2(self.worldtransform.at(0, 1),
                         self.worldtransform.at(1, 1)).len()
        sm = Matrix3(x / scalex, 0, 0, 0, y / scaley, 0, 0, 0, 1)

        self.worldtransform = self.worldtransform * sm

        if self.game_object().parent is not None:
            self.localtransform = self.game_object().parent(
            ).motion.worldtransform.inverse() * self.worldtransform
        else:
            self.localtransform = Matrix3.identity()

        for child in self.game_object().children:
            child.motion.update_world_transform(self)

    def scale_by(self, x, y):

        sm = Matrix3(x, 0, 0, 0, y, 0, 0, 0, 1)

        self.worldtransform = self.worldtransform * sm

        if self.game_object().parent is not None:
            self.localtransform = self.game_object().parent(
            ).motion.worldtransform.inverse() * self.worldtransform
        else:
            self.localtransform = Matrix3.identity()

        for child in self.game_object().children:
            child.motion.update_world_transform(self)

    def get_scale(self):
        xscale = Vector2(self.worldtransform.at(
            0, 0), self.worldtransform.at(1, 0)).len()
        yscale = Vector2(self.worldtransform.at(
            0, 1), self.worldtransform.at(1, 1)).len()
        return Vector2(xscale, yscale)

    def local_scale_by(self, x, y):
        sm = Matrix3(x, 0, 0, 0, y, 0, 0, 0, 1)

        self.localtransform = self.localtransform * sm

        if self.game_object().parent is not None:
            self.worldtransform = self.game_object().parent().motion.worldtransform * \
                self.localtransform
        else:
            self.worldtransform = Matrix3.identity() * self.localtransform

        for child in self.game_object().children:
            child.motion.update_world_transform(self)
