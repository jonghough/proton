import threading

from proton.protonmath.matrix3 import *
from proton.protonmath.vector2 import *
from proton.aabb import AABB
import proton.scenemanager 
from proton.scene import *


class Collider(Component):

    def __init__(self, _gameobject):
        super(Collider, self).__init__(_gameobject)
        self.worldtransform = Matrix3.identity()
        self.localtransform = Matrix3.identity()
        self.aabb = AABB(Vector2(0, 0))
        self.worldtransform = self.game_object().motion.worldtransform * \
            self.localtransform
        self.aabb.worldtransform = self.worldtransform
        self.layer = 0  # default
        ProtonSingleton(
            proton.scenemanager.SceneManager).scene().colliders.append(self)
        self.lock = threading.Lock()

    def start(self): 
        try:
            rect = self.game_object().graphics.sprite_rect
            self.setdims(Vector2(rect.width, rect.height))
        except:
            pass

    def update(self): 
        self.lock.acquire()
        self.worldtransform = self.game_object().motion.worldtransform * \
            self.localtransform
        self.aabb.worldtransform = self.worldtransform
        self.aabb.calcbounds()
        self.aabb.calcnormals()
        self.lock.release()

    def getaabb(self):
        return None

    def setcenter(self, center): 
        self.lock.acquire()
        self.localtransform.set(0, 2, center.x)
        self.localtransform.set(1, 2, center.y)
        self.worldtransform = self.game_object().motion.worldtransform * \
            self.localtransform

        self.lock.release()

    def getcenter(self): 
        self.lock.acquire()
        return Vector2(self.localtransform.at(0, 2), self.localtransform.at(1, 2))
        self.lock.release()

    def setdims(self, dims): 
        self.lock.acquire()
        self.aabb.dims.x = dims.x
        self.aabb.dims.y = dims.y
        self.lock.release()

    def iscolliding(self, other): 

        self.lock.acquire()
        return self.aabb.iscolliding(other.aabb)
        self.lock.release()

    def setlayer(self, layer_):

        self.lock.acquire()
        self.layer = layer_
        self.lock.release()

    def ondestroy(self):
        self.lock.acquire()
        s = ProtonSingleton(scenemanager.SceneManager)
        s.currentscene.colliders.remove(self)
        self.lock.release()
