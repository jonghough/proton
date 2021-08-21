from pygame.constants import *
import logging
from proton.collider import Collider
from proton.component import Component
from proton.gameinput import GameInput
from proton.gametime import GameTime
from proton.protonsingleton import ProtonSingleton 
from proton.physics.rigidbody import RigidBody
from proton.resourcemanager import ResourceManager
from proton.scenemanager import SceneManager
from proton.protonmath.vector2 import Vector2


class PlayerComponent(Component):
    def __init__(self, gameobject_):
        super(PlayerComponent, self).__init__(gameobject_)
        self.speed = Vector2(200, 0)
        self.accel = Vector2(0, 0)
        self.score = 0
        self.vdirection = 0
        self.hdirection = 0
        self.input = ProtonSingleton(GameInput)
        self.missiles = []
        self.movetimer = 0
        self.maxmovetime=0.1
        self.ismoving=False
        
        self.RIGHTDOWN=0
        self.LEFTDOWN=1
        self.UP=2
        self.buttonstate = self.UP

    def setgameovercallback(self, ongameover):
        self.ongameover = ongameover

    def set_speed (self, speed):
        self.speed = Vector2(speed,0)

    def start(self): 
        rm = ProtonSingleton(ResourceManager)
        sprite = rm.load_texture("./games/asteroiddodge/resources/fighter_spaceship.png")
        self.game_object().graphics.set_sprite_obj(sprite)
        self.game_object().motion.set_position(350, 650)
        c = self.game_object().add_component(Collider)
        self.game_object().add_component(RigidBody)
        c.layer = 0

     
         
    def update(self):
        dt = ProtonSingleton(GameTime).dt()
        pos = self.game_object().motion.position()

        if self.ismoving:
            self.movetimer += dt
            if self.movetimer > self.maxmovetime:
                self.ismoving = False
                self.movetimer = 0
                
        if str(K_LEFT) in self.input.keydownevents:
            if self.ismoving and self.hdirection == -1: 
                pass
            else:
                self.hdirection = -1
                self.ismoving = True
                self.movetimer = 0 

        if str(K_RIGHT) in self.input.keydownevents:
            if self.ismoving and self.hdirection == 1: 
                pass
            else:
                self.hdirection = 1
                self.ismoving = True
                self.movetimer = 0 

        if self.ismoving: 
            pos = self.game_object().motion.position()
            newx = pos.x + self.hdirection * self.speed.x * dt
            if self.hdirection == -1 and newx < 0: newx = 0
            if self.hdirection == 1 and newx >700: newx = 700
               
            self.game_object().motion .set_position(newx, \
                                             pos.y + self.vdirection * self.speed.y * dt)


    def oncollision(self, other):
        self.ongameover()

    def moveleft(self):
        self.buttonstate = self.LEFTDOWN
        self.hdirection = -1
        self.ismoving = True
        self.movetimer = 0
        time = ProtonSingleton(GameTime).time() 
        pos = self.game_object().motion.position() 

    def release(self):
        if  self.buttonstate == self.LEFTDOWN or self.buttonstate == self.RIGHTDOWN:
            self.hdirection = 0

    def moveright(self):
        self.buttonstate = self.RIGHTDOWN
        self.hdirection = 1
        self.ismoving = True
        self.movetimer = 0
        time = ProtonSingleton(GameTime).time() 
        pos = self.game_object().motion.position() 
