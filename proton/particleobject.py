from proton.protonmath.matrix2 import *
from proton.protonmath.matrix3 import *
from proton.protonmath.vector2 import *

from proton.gametime import *


class ParticleObject(object):
    def __init__(self, sprite):

        self.acceleration = Vector2(0.0, 0.0)
        self.velocity = Vector2(0.0, 0.0)
        self.position = Vector2(0.0, 0.0)
        self.position.x = 1.0
        self.sprite = sprite
        self.lifetime = 0.0
        self.timer = 0.0
        self.moving = False

    def update(self):
        if self.moving is True:
            dt = GameTime.dt()
            self.timer += dt
            x = self.position.x + self.velocity.x * dt + 0.5 * self.acceleration.x * dt * dt
            y = self.position.y + self.velocity.y * dt + 0.5 * self.acceleration.y * dt * dt

            self.position = Vector2(x, y)

            self.velocity.x += self.acceleration.x * dt
            self.velocity.y += self.acceleration.y * dt

            if self.timer > self.lifetime:
                self.moving = False

    def setup(self, lifetime):
        self.moving = True
        self.timer = 0.0
        self.lifetime = lifetime
