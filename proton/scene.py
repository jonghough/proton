import proton.graphicscomponent
from proton.particlesystem import *
from proton.quadmanager import *
from proton.gameobject import GameObject
from proton.scenemanager import SceneManager
from proton.graphicscomponent import GraphicsComponent
from proton.physics.physicsmanager import PhysicsManager

class Scene(object):
    def __init__(self): 
        self.root = proton.gameobject.GameObject("Root")
        self.allgameobjects = []
        self.quadmanager = QuadManager(32, self.do_layers_collide)
        self.colliders = []
        self.collidelayers = {}
        self.started = False
        self.fillcolor = (255, 255, 255)

    def initialize(self, config_data=None):
        """
        override this and put initialization code here, e.g.
        create initial game objects etc.
        :return:
        """
        pass

    def setup_on_load(self):
        for obj in self.allgameobjects:
            obj.get_component(GraphicsComponent).setup_on_load()
            ps = obj.get_component(ParticleSystem)
            if ps is not None:
                ps.setup_on_load()

    def add_collide_layers(self, layer1, layer2):
        
        ProtonSingleton(proton.physics.physicsmanager.PhysicsManager).add_collide_layers(layer1, layer2)

    def do_layers_collide(self, layer1, layer2):
        s = (layer1 ^ layer2) + 31 * (layer1 + layer2) - ((layer1 >> 2) ^ (layer2 >> 2))
        if s in self.collidelayers:
            return True
        else:
            return False

    def update_scene(self):
        for child in self.allgameobjects:
            child.update()

    def render_scene(self, screen):
        for child in self.allgameobjects:
            if child.is_active() and self.is_on_screen(child):
                child.draw(screen)

    def find_object_by_name(self, name):
        for obj in self.allgameobjects:
            if obj.name == name:
                return obj
        return None

    def is_on_screen(self, gameobj):
        p = gameobj.motion.position()
        sm = ProtonSingleton(SceneManager)
        if p.x < 0 or p.x > sm.width or p.y < 0 or p.y > sm.height:
            return False
        else:
            return True

    def sort_render_order(self):
        self.allgameobjects = sorted(self.allgameobjects,
                                     key=lambda go: go.get_component(proton.graphicscomponent.GraphicsComponent).render_order)

    def add_new_game_object(self, name):
        go = proton.gameobject.GameObject(name) 
        go.set_parent(self.root)
        self.allgameobjects.append(go)
        self.sort_render_order()
        return go

    def destroy_game_object(self, obj):
        if obj in self.allgameobjects:
            self.allgameobjects.remove(obj)
            GameObject.destroy(obj)

    def destroy_all(self):
        for obj in self.allgameobjects:
            GameObject.destroy(obj)
        del self.allgameobjects[:]
