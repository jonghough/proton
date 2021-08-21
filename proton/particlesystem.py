import random
from proton.protonmath import *

from proton.component import *
from proton.particleobject import *
from proton.protonmath.vector2 import *
from proton.resourcemanager import *


class ParticleSystem(Component):

    def __init__(self, _gameobject):
        super(ParticleSystem, self).__init__(_gameobject)
        self.particles = []
        self.index = 0
        self.active = False
        self.psritename = None

    def setup(self, particlecount, lifetime, direction, maxradians, rate, loop, spritename):
        self.spritename = spritename
        self.particlecount = particlecount
        self.lifetime = lifetime
        self.direction = direction
        self.maxradians = maxradians
        self.rate = rate
        self.loop = loop
        self.timer = 0.0
        self.active = True

        rm = ProtonSingleton(ResourceManager)
        sprite = rm.load_texture(spritename)
        self.sprite = sprite
        self.spriterect = self.sprite.get_rect()
        self.blitsprite = sprite
        self.blitspriterect = self.blitsprite.get_rect()

        for i in range(0, self.particlecount):
            pobj = ParticleObject(sprite)
            pobj.lifetime = lifetime
            self.particles.append(pobj)

    def setup_on_load(self):
        rm = ProtonSingleton(ResourceManager)
        sprite = rm.load_texture(self.spritename)
        self.sprite = sprite
        self.spriterect = self.sprite.get_rect()
        self.blitsprite = sprite
        self.blitspriterect = self.blitsprite.get_rect()

        for pobj in self.particles:
            pobj.sprite = sprite

    def stop(self):
        pass

    def update(self):
        if self.active is True:
            self.timer += 1.0 / 60.0
            if self.timer > 1.0 / self.rate:
                length = self.direction.len()
                theta = atan2(self.direction.y, self.direction.x)
                j = self.index
                self.particles[j].setup(self.lifetime)
                randomangle = random.uniform(0, 1)
                angle = (randomangle - 0.5) * 2 * self.maxradians

                xdir = cos(theta + angle) * length
                ydir = sin(theta + angle) * length
                self.particles[j].velocity = Vector2(xdir, ydir)
                self.particles[j].position = Vector2(self.game_object().motion.position().x,
                                                     self.game_object().motion.position().y)
                self.timer = 0
                self.index = (self.index + 1) % len(self.particles)

            for p in self.particles:
                p.update()

    def draw(self, screen):
        for p in self.particles:
            if p.moving is True:
                xpos = p.position.x - 0.5 * p.sprite.get_rect().width
                ypos = p.position.y - 0.5 * p.sprite.get_rect().height
                self.spriterect.x = xpos
                self.spriterect.y = ypos
                screen.blit(self.sprite, self.spriterect)
