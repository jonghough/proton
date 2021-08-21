from proton.component import Component
from proton.gameinput import GameInput
from proton.gametime import GameTime, ProtonSingleton
from proton.graphicscomponent import GraphicsComponent
from proton.motioncomponent import MotionComponent
from proton.protonmath.vector2 import Vector2


class Dims:

    def __init__(self, l, t, r, b):
        """
        Dimensions
        :param l: left
        :param t: top
        :param r: right
        :param b: bottom
        """
        self.left = l
        self.right = r
        self.top = t
        self.bottom = b


class UIGraphics(Component):
    IDLE = 1
    CLICKED = 2

    def __int__(self, _gameobject):
        super(UIGraphics, self).__init__(_gameobject)
        self.layer = -1
        self.mystate = UIGraphics.IDLE

        self.clicktimer = 0.0
        self.clickmaxtime = 0.3
        self.graphics = self.game_object().get_component(GraphicsComponent)
        self.input = ProtonSingleton(GameInput)

    def ispointinside(self, x, y):
        """

        :param x:
        :param y:
        :return:
        """
        if self.dims.left <= x and x <= self.dims.right and \
                        self.dims.top <= y and y <= self.dims.bottom:
            return True

        else:
            return False

    def onclick(self):
        """

        :return:
        """
        for k, v in self.input.mousevents.items():
            if self.ispointinside(v[1][0], v[1][1]):
                self.clicktimer = 0.0
                self.graphics.renderflag = False
                self.mystate = UIGraphics.CLICKED
                break

    def update(self):
        if self.mystate == UIGraphics.IDLE:
            self.onclick()
        elif self.mystate == UIGraphics.CLICKED:
            self.clicktimer += GameTime.dt()
            if self.clicktimer > self.clickmaxtime:
                self.mystate = UIGraphics.IDLE
                self.clicktimer = 0.0
                self.graphics.renderflag = True

    def setup(self, dims):
        """

        :param dims:
        :return:
        """
        self.dims = dims
        self.mystate = UIGraphics.IDLE
        self.input = ProtonSingleton(GameInput)
        self.clicktimer = 0.0
        self.clickmaxtime = 0.3
        self.graphics = self.game_object().get_component(GraphicsComponent)

        graphics = self.game_object().get_component(GraphicsComponent)

        w = graphics.width
        h = graphics.height

        if w > 0 and h > 0:
            xratio = float(self.dims.right - self.dims.left) * 1.0 / float(w)
            yratio = float(self.dims.bottom - self.dims.top) * 1.0 / float(h)

            motion = self.game_object().get_component(MotionComponent)
            motion.set_scale(xratio, yratio)

            pos = Vector2((self.dims.right + self.dims.left) * 0.5, (self.dims.bottom + self.dims.top) * 0.5)
            motion.set_position(pos.x, pos.y)
