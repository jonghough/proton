import sys
import os

import numpy as np

from games.piratedefense.titletext import TitleText
from proton.physics.rigidbody import RigidBody
from proton.ui.textcomponent import TextComponent
from proton.ui.uigraphics import Dims
from games.piratedefense.towercontroller import TowerController

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
# sys.path.insert(0,"../../")
from proton.resourcemanager import ResourceManager
from proton.protonsingleton import ProtonSingleton
from proton.protonengine import ProtonEngine, Vector2, GameTime
from proton.gameobject import GameObject
from proton.scene import Scene
from games.piratedefense.cannonball import CannonBall
from proton.collider import Collider
from games.piratedefense.pirateshipcontroller import PirateShipController
from games.piratedefense.piratescontroller import PiratesController

from proton.learning.rl_interface import RLInterface


class PirateDefenseScene(Scene, RLInterface):
    def __init__(self):
        super(PirateDefenseScene, self).__init__()
        self.fillcolor = (2, 110, 225)
        self.mindist = 10000
        self.score = 0
        self.cache_score = 0
        self.game_over = False

    def initialize(self, config_data):
        c = self.add_new_game_object("TOWER")
        rm = ProtonSingleton(ResourceManager)
        self._blackcircle = rm.load_texture("./games/piratedefense/resources/blackcircle.png")
        self._pirateship = rm.load_texture("./games/piratedefense/resources/pirateship.png")
        c.add_component(TowerController)
        self._tower = c.get_component(TowerController)

        pc = self.add_new_game_object("PIRATES")
        pc.add_component(PiratesController)
        self._pc = pc.get_component(PiratesController)
        self._pc.setup(20, self._pirateship)
        self.add_collide_layers(24, 22)

        ttc = self.add_new_game_object("TEXT")
        ttc.add_component(TextComponent)
        tc = ttc.get_component(TextComponent)
        tc.settext("Time:", Dims(500, 20, 600, 70), (255, 255, 255))
        ttc.add_component(TitleText)
        self._titletext = ttc.get_component(TitleText)

        self.gameoverobj = self.add_new_game_object("GAMEOVER")
        gotex = rm.load_texture("./games/piratedefense/resources/gameover.png")
        self.gameoverobj.graphics.set_sprite_obj(gotex)
        self.gameoverobj.set_active(False)

    def reload_scene(self):
        self.restart()

    def restart(self):
        self.gameoverobj.set_active(False)
        self._titletext.restart()
        self._tower.restart()
        self._pc.restart()
        self.game_over = False

    def stop(self):
        self.game_over = True
        self._titletext.stop()
        self._tower.stop()
        self._pc.stop()
        self.gameoverobj.set_active(True)
        self.gameoverobj.transform().set_position(500, 350)

    def launch(self):
        pass

    def get_reward(self, action):
        if action == None:
            if self.game_over:
                return -1
            else:
                return 1
        self.score = ProtonSingleton(GameTime).time() / 1000.0

        def normalize(v):
            return Vector2(v.x / 1200, v.y / 700)

        ships = [normalize(x.game_object().transform().position()) for x in self._pc.pirateships if
                 x.game_object().is_active()]
        a = 0
        length = len(ships)
        for i in range(0, len(ships)):
            a += ships[i].y

        if a > 0:
            a /= length

        return a - 0.5
        # r = self.score - self.cache_score
        # self.cache_score = self.score
        # return 1 if r > 0 else 0

    def get_legal_actions(self):
        return [0, 1, 2, 3]  # nothing, up, down, fire

    def save_state(self):
        """
        saves the state
        :return:
        """
        pass

    def load_state(self):
        """
        loads the state
        :return:
        """
        pass

    def get_observation(self):
        """
        Gets game state observation.
        :return: game state observation.
        """
        return None

    def is_game_over(self):
        """
        True if game over, false otherwise.
        :return:
        """
        return self.game_over

    def step(self, action):

        reward = self.perform_action(action)
        s = self.get_state()
        done = self.game_over

        return s, reward, done, True

    def finish(self):
        pass

    def get_state(self):

        # y position of cannon, closest 2 ships.
        pos = self._tower.get_state()
      

        def normalize(v):
            return Vector2(v.x / 1200, v.y / 700)

        ships = [normalize(x.game_object().transform().position()) for x in self._pc.pirateships if
                 x.game_object().is_active()]
        sorted_ships = sorted(ships, key=lambda f: f.magnitude(), reverse=False)
        
        while len(sorted_ships) < 5:
            sorted_ships.append(Vector2(1, 1))
 
        game_state = [pos]
        for i in range(0, 5):
            game_state.append(sorted_ships[i].x)
            game_state.append(sorted_ships[i].y)
       
        return np.array(game_state)

    def perform_action(self, action):
        success = self._tower.force_action(action)
        rew = self.get_reward(action) 
        return rew


if __name__ == "__main__":
    engine = ProtonEngine("Pirate Defense", 1200, 700, True)
    asteroidscene = PirateDefenseScene()
    engine.load_scene(asteroidscene)
    engine.run()
