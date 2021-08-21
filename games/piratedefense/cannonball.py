from proton.component import Component
from math import sin, cos
from proton.protonmath.vector2 import Vector2
from proton.gametime import GameTime, ProtonSingleton

class CannonBall(Component):
    GRAVITY = 90

    def __init__(self, gameobject_):

        super(CannonBall, self).__init__(gameobject_)
        self.state = 0  # 0 = stationary, 1 = moving
        self.initialspeed = 400
        self.initialangle = -1.4
        self.initialposition = Vector2(0, 0)
        self.time = 0
        self.targetpoint = Vector2(0,0)

    def launch(self, initialpos, initialangle, initialspeed, targetpoint):
        self.initialspeed = initialspeed
        self.initialangle = initialangle
        self.initialposition = initialpos
        self.time = 0
        self.game_object().motion.set_position(self.initialposition.x, self.initialposition.y)
        self.targetpoint = targetpoint

    def update(self):

        if self.state is not -1:
            dt = ProtonSingleton(GameTime).dt()
            self.time += dt
            vpos = self.time * sin(
                self.initialangle) * self.initialspeed + 0.5 * CannonBall.GRAVITY * self.time * self.time
            nexty = self.initialposition.y + vpos

            hpos = self.time * cos(self.initialangle) * self.initialspeed
            nextx = self.initialposition.x + hpos
            self.game_object().motion.set_position(nextx, nexty)

            if Vector2.dist(Vector2(nextx,nexty), self.targetpoint) < 0.01:
                self.game_object().set_active(False)

            elif nexty > self.targetpoint.y + 1:
                self.game_object().set_active(False)
