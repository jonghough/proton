import os, sys

import random

from proton.gametime import GameTime, ProtonSingleton
from proton.component import Component
from proton.protonmath.vector2 import Vector2
from proton.splines import CatmullRomSpline


class PirateShipController(Component):
    def __init__(self, gameobject_):
        super(PirateShipController, self).__init__(gameobject_)
        self.crspline = None
        self.game_object().set_active(False)

    @staticmethod
    def onfinish():
        # self.game_object() .set_active(False)
        logging.info("finished!")

    def start(self):
        pass

    def launch(self):
        self.game_object().set_active(True)
        v0 = Vector2(1000, 400)
        v1 = Vector2(1000, random.randint(20, 470))
        v2 = Vector2(random.randint(800, 990), random.randint(20, 690))
        v3 = Vector2(random.randint(500, 700), random.randint(20, 680))
        v4 = Vector2(random.randint(400, 450), random.randint(20, 680))
        v5 = Vector2(random.randint(200, 300), random.randint(20, 680))
        v6 = Vector2(random.randint(120, 150), random.randint(20, 680))
        v7 = Vector2(50, random.randint(40, 600))
        v8 = Vector2(0, random.randint(40, 600))
        self.crspline = CatmullRomSpline([v0, v1, v2, v3, v4, v5, v6, v7, v8], PirateShipController.onfinish)

    def update(self):
        if not self.game_object().is_active() or self.crspline is None:
            return
        dt = ProtonSingleton(GameTime).dt()
        p = self.crspline.updatecurveatspeed(dt, 100)
        self.game_object().motion.set_position(p.x, p.y)

    def oncollision(self, other):
        self.game_object().set_active(False)
        logging.info("COLLISION")
