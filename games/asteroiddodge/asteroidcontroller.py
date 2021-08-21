from proton.component import Component
from proton.gametime import GameTime
from proton.protonsingleton import ProtonSingleton 
from proton.motioncomponent import MotionComponent
from math import sin,cos

from proton.protonmath.vector2 import Vector2


class AsteroidController(Component):

    def __init__(self, gameobject_):
        super(AsteroidController, self).__init__(gameobject_)
        self.gravity = Vector2(0, 0.1)
        self.speed = Vector2(0, 4)
        self.rotatespeed = 5.0

    def set_speed(self, speed):
        self.speed = Vector2(0,speed)
        
    def setpos(self, position):
        self.game_object().get_component(MotionComponent) .set_position(position)

    def update(self):
        pos = self.game_object().get_component(MotionComponent).position()
       
        dt = ProtonSingleton(GameTime).dt()
        pos = pos + (self.speed * dt) + 0.5 * self.gravity * dt * dt
        self.game_object().get_component(MotionComponent) .set_position(pos.x, pos.y)
         
        self.speed = self.speed + self.gravity * dt
        self.game_object().motion .rotate_by(self.rotatespeed * dt)
        if pos.y > 800:
            self.game_object() .set_active(False)
            self.game_object().get_component(MotionComponent) .set_position(0,-100)
            self.speed = Vector2(0,10.5)