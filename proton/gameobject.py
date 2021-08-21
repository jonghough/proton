
import proton.graphicscomponent
from proton.scenemanager import SceneManager
from proton.scene import *
from proton.protonsingleton import *
import proton.motioncomponent as mc

class GameObject(object):

    def __init__(self, name):
        """
        Initializes the gameobject.
        :param name: gameobject name.
        """
        self.components = {}
        self.name = name
        self.__parent = None
        self.children = []
        self.motion = mc.MotionComponent(self)
        self.graphics = proton.graphicscomponent.GraphicsComponent(self)
        self.components[mc.MotionComponent.__name__] = self.motion
        self.components[proton.graphicscomponent.GraphicsComponent.__name__] = self.graphics
        self.__alive = True
        self.__active = True

    def is_alive(self):
        return self.__alive

    def __nullcheck(func):
        def wf(*args):
            try:
                if not args[0].__alive:
                    raise Exception
                else:
                    return func(*args)
            except RuntimeError as e:
                pass
        return wf


    @__nullcheck
    def set_active(self, b):
        self.__active = b
        for child in self.children:
            child.set_active(b)

    @__nullcheck
    def is_active(self):
        return self.__active

    @__nullcheck
    def set_parent(self, parent):
        if parent is None:
            s = ProtonSingleton(scenemanager.SceneManager)
            self.set_parent(s.currentscene.root)
        elif GameObject.is_acyclic(parent, self):
            if self.parent() is not None:
                self.parent().children.remove(self)
            self.__parent = parent
            p = self.motion.position()
            self.motion.set_position(p.x, p.y)
            parent.children.append(self)

    @__nullcheck
    def parent(self):
        return self.__parent

    @__nullcheck
    def add_component(self, typez):
        comp = typez(self)
        if typez.__name__ in self.components:
            return self.components[type(comp).__name__]
        else:
            self.components[type(comp).__name__] = comp
            comp.start()
            return comp

    @__nullcheck
    def get_component(self, typez):
        comp = typez(self)
        if typez.__name__ in self.components:
            return self.components[type(comp).__name__]
        else:
            return None

    @__nullcheck
    def transform(self):
        return self.get_component(mc.MotionComponent)

    @__nullcheck
    def start(self):
        pass

    @__nullcheck
    def update(self):
        for k,v in self.components.items():
            v.update()

    @__nullcheck
    def draw(self, screen):
        if self.__active:
            for k,v in self.components.items():
                v.draw(screen)

    @__nullcheck
    def on_destroy(self):
        for k,v in self.components.items():
            v.ondestroy()

    @__nullcheck
    def on_collision(self, other):
        for k,v in self.components.items():
            v.oncollision(other)

    @staticmethod
    def is_acyclic(parent, nextchild):
        for child in nextchild.children:
            if child == parent:
                return False
            else:
                nextok = GameObject.is_acyclic(parent, child)
                if nextok is False:
                    return False
        return True

    @staticmethod
    def destroy(gameobj):
        if not gameobj.is_alive():
            raise Exception # dont try to destroy dead object, please
        else:
            s = ProtonSingleton(SceneManager)
            s.currentscene.allgameobjects.remove(gameobj)
            if gameobj.parent is not None:
                gameobj.parent().children.remove(gameobj)
            for child in gameobj.children:
                GameObject.destroy(child)
            gameobj.__alive = False
