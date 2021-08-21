from proton.collider import Collider
from proton.physics import rigidbody
from proton.physics.rigidbody import RigidBody
from proton.protonmath.vector2 import Vector2
from proton.protonsingleton import ProtonSingleton, Singleton
from proton.quadmanager import QuadManager

@Singleton
class PhysicsManager(object):
    _instance = None

    def __init__(self):
        self.allgameobjects = []
        self.quadmanager = QuadManager(1 + 2 + 4 + 8 + 16, self.do_layers_collide)
        self.colliders = []
        self.collidelayers = {}

    @staticmethod
    def add_collide_layers(layer1, layer2):
        s = (layer1 ^ layer2) + 31 * (layer1 + layer2) - ((layer1 >> 2) ^ (layer2 >> 2))
        ProtonSingleton(PhysicsManager).collidelayers[s] = True
   

    def do_layers_collide(self, layer1, layer2):
        s = (layer1 ^ layer2) + 31 * (layer1 + layer2) - ((layer1 >> 2) ^ (layer2 >> 2))
        if s in self.collidelayers:
            return True
        else:
            return False

    def runphys(self, gamecolliders): 
        collisions = self.quadmanager.check_collisions(2, Vector2(4000, 4000), gamecolliders)
 
        for k, v in collisions.items():
            v[0].get_component(Collider).lock.acquire()
            v[1].get_component(Collider).lock.acquire()
            if v[0].is_alive() and v[1].is_alive() and v[0].is_active() and v[1].is_active():
                rigidbody.RigidBody.oncollide(v[0].get_component(RigidBody), v[1].get_component(RigidBody))
                v[0].on_collision(v[1]) 
                if v[1].is_alive(): 
                    v[1].on_collision(v[0])
            v[0].get_component(Collider).lock.release()
            v[1].get_component(Collider).lock.release()
