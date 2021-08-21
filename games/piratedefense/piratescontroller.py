from pkg_resources import ResourceManager

from games.piratedefense.pirateshipcontroller import PirateShipController
from proton.collider import Collider
from proton.component import Component
from proton.gametime import GameTime
from proton.graphicscomponent import GraphicsComponent
from proton.physics.rigidbody import RigidBody
from proton.scenemanager import SceneManager, ProtonSingleton
import numpy

class PiratesController(Component):
    def __init__(self, gameobject_):
        super(PiratesController, self).__init__(gameobject_)
        self.shipcount = 1
        self.pirateships = []
        self.index = 0
        self.timer = 0
        self.MAXTIME = 2
        self._is_running = True

    def setup(self, shipcount, shiptex):
        self.shipcount = shipcount
        for i in range(self.shipcount):
            go = ProtonSingleton(SceneManager).scene().add_new_game_object("pirate_" + str(i))
            go.add_component(PirateShipController)
            self.pirateships.append(go.get_component(PirateShipController))
            go.set_active(False)

            go.motion.set_position(-100, 100000)
            go.graphics.set_sprite_obj(shiptex)
            col = go.add_component(Collider)
          
            go.add_component(RigidBody)
            go.transform().set_scale(0.25, 0.25)
            go.get_component(GraphicsComponent).renderorder = 2
            col.layer = 22

    def releaseship(self):
        ship = self.pirateships[self.index]
        if not ship.game_object().is_active():
            ship.launch()
        self.index += 1
        self.index %= self.shipcount

    def update(self):
        if not self._is_running: return
        if self.timer > self.MAXTIME:
            self.releaseship()
            self.timer = 0

        self.timer += ProtonSingleton(GameTime).delta_time()

    def restart(self):
        self._is_running = True
        for ship in self.pirateships:
            ship.game_object().motion.set_position(-100, 100000)
            ship.game_object().set_active(False)

    def stop(self):
        [a.game_object().set_active(False) for a in self.pirateships]
        self._is_running = False

    def get_state(self):
        arr = []
        # TODO this is not a good idea to have 3 loops.
        # use a dictionary.
        for i in range(0, 700, 50):
            subarr = []
            for j in range(0, 700, 50):
                ctr = 0
                for ship in self.pirateships:
                    p = ship.game_object().transform().position()
                    if ship.game_object().isActive() and \
                                    p.x > i and p.x < i + 50 and \
                                    p.y > j and p.y < j + 50:
                        ctr += 1
                subarr.append(ctr)
            arr.append(subarr)
        return numpy.array([numpy.array(sub) for sub in arr])
