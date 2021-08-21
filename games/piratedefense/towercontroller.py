import os, sys
 
from math import acos
from pygame.constants import *

from proton.collider import Collider
from proton.component import Component
from proton.graphicscomponent import GraphicsComponent
from proton.physics.rigidbody import RigidBody
from proton.protonmath.vector2 import Vector2
from proton.scenemanager import SceneManager
from games.piratedefense.cannonball import CannonBall
from games.piratedefense.cannoncontroller import CannonController
from proton.resourcemanager import ResourceManager
from proton.protonsingleton import ProtonSingleton
from proton.gameinput import GameInput


class TowerController(Component):
    def __init__(self, gameobject_):
        super(TowerController, self).__init__(gameobject_)
        self.target = None
        self.cannonballs = []
        self.cbcount = 20
        self.idx = 0
        self.input = ProtonSingleton(GameInput)
        self._cannon = None

    def start(self):
        cn = ProtonSingleton(SceneManager).scene().add_new_game_object("CANNON")
        cn.add_component(CannonController)
        self._cannon = cn.get_component(CannonController)
        self._cannon.init()
        rm = ProtonSingleton(ResourceManager)
        pl = rm.load_texture("./games/piratedefense/resources/platform.png")
        self.game_object().graphics.set_sprite_obj(pl)
        self.game_object().motion.set_position(15, 350)
        col = self.game_object().add_component(Collider)
        self.game_object().add_component(RigidBody)
        self.game_object().get_component(GraphicsComponent).renderorder = 9
        col.layer = 24


    def update(self):
        pass

    def oncollision(self, other):
        self.game_object().set_active(False)
        ProtonSingleton(SceneManager).currentscene.stop()

    def stop(self):
        pass

    def restart(self):
        self.game_object().set_active(True)
        self._cannon.restart()

    def get_state(self):
        return self._cannon.get_state()


    def force_action(self,action):
        return self._cannon.force_action(action)