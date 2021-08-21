import random
import logging
from proton.ui.textcomponent import TextComponent
from proton.ui.uigraphics import Dims
from games.asteroiddodge.playercomponent import PlayerComponent
from games.asteroiddodge.learner import AsteroidLearner
from proton.collider import Collider
from proton.component import Component
from proton.gametime import GameTime
from proton.physics.rigidbody import RigidBody
from proton.protonsingleton import ProtonSingleton
from proton.resourcemanager import ResourceManager
from proton.scenemanager import SceneManager
from games.asteroiddodge.asteroidcontroller import AsteroidController
from proton.protonmath.vector2 import Vector2
import numpy as np
import math
from games.asteroiddodge.asteroidtitletext import AsteroidTitleText

class GameController(Component):

    def __init__(self, gameobject_):
        super(GameController, self).__init__(gameobject_)
        self.launch_timer = 0
        self.time_to_next_launch = 2.0
        self.player = None
        self.index = 0
        self.score = 0
        self.score_timer = 0
        self.score_timer_max = 0.15
        self.gameover = False
        self.mindist = 100000
        self.cachedscore = 0
        # learner
        self.learner_update_timer = 0.0
        self.learner_update_max = 0.2
        self.cached_min_distance = 100000
        #game params (asteroid, player)
        self.game_params = None

    def initialize_game_params(self, game_params):
        self.game_params = game_params

        self.player.set_speed(self.game_params.player_speed)

    def reset(self):
        for asteroid in self.asteroids:
            asteroid.set_active(False)
            asteroid.motion .set_position(0, -10)
        self.launch_timer = 0
        self.time_to_next_launch = 2.0
        self.index = random.randint(0, 19)
        self.score = 0
        self.score_timer = 0
        self.score_timer_max = 0.15
        self.gameover = False
        player_pos_x = random.randint(10, 690)
        self.player.game_object().motion.set_position(player_pos_x, 650)
        self.mindist = 100000
        self.cached_min_distance = 100000

    def cb(self):
        logging.info("gameover")
        self.gameover = True

    def learner_reset_cb(self):
        self.score = 0
        self.reset()

    def start(self):
        logging.info("Starting")
        self.create_asteroids(20)
        self.initialize_text()

        player = ProtonSingleton(
            SceneManager).scene().add_new_game_object("PLAYER")
        self.player = player.add_component(PlayerComponent)
        self.learner = player.add_component(AsteroidLearner)
        self.learner.set_env(ProtonSingleton(SceneManager).scene())
        self.learner.reset_now = self.learner_reset_cb

        player.motion.set_position(350, 650)
        player.motion.set_scale(0.1, 0.1) 

        self.player.setgameovercallback(self.cb)

    def create_asteroids(self, count):
        self.asteroids = []
        rm = ProtonSingleton(ResourceManager)
        sprite = rm.load_texture(
            "./games/asteroiddodge/resources/asteroid.png")
        for i in range(count):
            a = ProtonSingleton(SceneManager).scene(
            ).add_new_game_object("asteroid_"+str(i))
            a.add_component(AsteroidController)
            a.set_active(False)
            self.asteroids.append(a)
            a.graphics.set_sprite_obj(sprite)
            a.motion.set_scale(0.1, 0.1)
            c = a. add_component(Collider)
            a. add_component(RigidBody)
            c.layer = 23
            self.index = random.randint(0, 19)

    def initialize_learner(self, learner_params):
        self.learner.initialize(learner_params)

    def initialize_text(self):
        ttc = ProtonSingleton(SceneManager).scene().add_new_game_object("TEXT")
        ttc.add_component(TextComponent)
        tc = ttc.get_component(TextComponent)
        tc.settext("Time:", Dims(0, 20,200, 400), (20, 20, 255))
        ttc.add_component(AsteroidTitleText)
        self._titletext = ttc.get_component(AsteroidTitleText)

    def update(self):
        dt = ProtonSingleton(GameTime).dt()
        # for learenr, update timer
        self.update_learner()

        self.launch_timer += dt
        if self.launch_timer > self.time_to_next_launch:
            self.time_to_next_launch = 2.0  # random.uniform(2.0, 2.5)
            self.launch_timer = 0
            self.launch_asteroid()

        self.score_timer += dt
        if self.score_timer > self.score_timer_max:
            self.score_timer = 0
            self.score += 1

    def launch_asteroid(self):
        bombpos = Vector2(random.uniform(0, 10) +
                          self.player.game_object().motion.position().x, -10)
        nextbomb = self.asteroids[self.index]
        nextbomb .set_active(True)
        nextbomb.get_component(AsteroidController).speed = Vector2(
            0, self.game_params.asteroid_speed)  # random.uniform(225.4, 236.0))
        nextbomb.get_component(
            AsteroidController).rotatespeed = random.uniform(1.0, 10.0)
        nextbomb.motion .set_scale(0.1, 0.1)
        self.index = (1 + self.index) % len(self.asteroids)
        nextbomb.motion .set_position(bombpos.x, bombpos.y)

    def calculate_score(self, action):
        logging.info(f"score: {self.score}, max: {self.cachedscore}")
        if self.score > self.cachedscore:
            self.cachedscore = self.score

        if self.gameover:
            logging.info("DEAD!")
            return -1

        player_pos = self.player.game_object().motion.position()

        min_reward = 1
        # if player_pos.x <= 2 or player_pos.x >= 698:
        #     min_reward = -0.8
        px = player_pos.x -350
        #dr =  0.6667* ( 0.5 + 1-math.exp(-1 * abs(px/350)))
        dr = ( 1 - abs(px/350))
       # if px > -150 and px < 150: dr = 0
        min_reward = dr
        def dist_score(pl, ast):
            sc = 1-(abs(pl.x - ast.x) / 350)
            return -sc
            
        for asteroid in self.asteroids:
            p = asteroid.motion.position()
            if asteroid.is_active():
                if p.y < player_pos.y + 60 and player_pos.y - p.y < 100:
                    dscore = dist_score(player_pos, p) 
                    if min_reward > dscore:
                        min_reward = dscore
                elif p.y < player_pos.y + 60 and player_pos.y - p.y < 150 :
                    dscore = 0.75 * dist_score(player_pos, p)
                    if min_reward > dscore:
                        min_reward = dscore
                elif p.y < player_pos.y + 60 and player_pos.y - p.y < 250 :
                    dscore = 0.5 * dist_score(player_pos, p)
                    if min_reward > dscore:
                        min_reward = dscore
                elif p.y < player_pos.y + 60 and player_pos.y - p.y < 350 :
                    dscore = 0.25 * dist_score(player_pos, p)
                    if min_reward > dscore:
                        min_reward = dscore
                # elif p.y < player_pos.y + 60 and player_pos.y - p.y < 450 :
                #     dscore = 0.1 * dist_score(player_pos, p)
                #     if min_reward > dscore:
                #         min_reward = dscore
        
        # if  player_pos.x < 100:
        #     min_reward = -0.999 + 0.5 *7* player_pos.x / 700
        # elif player_pos.x > 600:
        #     min_reward = -0.999 + 0.5 * 7*(1 -  player_pos.x / 700)
        #if min_reward < 0: min_reward *= dr
        return min_reward  

    def get_state(self):
        statex = []
        statey = []
        statea = []
        statev = []
        statedx = []
        statedy = []
        allstate = []
        d = 700
        maxd = math.sqrt(700**2 + 720**2)
        player_pos = self.player.game_object().motion.position()

        def calc_distance(i):
            if i.is_active():
                p = i.motion.position()
                if p.y > player_pos.y + 60:
                    return maxd
                dist = Vector2.dist(p, player_pos)
                return dist
            else:
                return maxd

        acopy = self.asteroids.copy()
        acopy.sort(key=calc_distance)

        allstate.append(player_pos.x / 700)

        player_pos = self.player.game_object().motion.position()

        def append(asteroid):
            pos = asteroid.motion.position()
            dx = (pos.x) / 700
            if not asteroid.is_active() or pos.y > player_pos.y + 60:
                dy = 0
            else:
                dy = pos.y / 700

            allstate.append(dx)
            allstate.append(dy)

        append(acopy[0])
        append(acopy[1])
        append(acopy[2])
        # logging.info(np.array(allstate))
        return np.array(allstate)

    def force_action(self, action):
        if action is None:
            return True
        else:
            #logging.info(f"MOVING ACTION {action}")
            if action == -1:
                self.player.moveleft()
            elif action == 1:
                self.player.moveright()
            else:
                self.player.release()
        return True

    def update_learner(self):
        dt = ProtonSingleton(GameTime).dt()
        self.learner_update_timer += dt
        if self.learner_update_timer > self.learner_update_max:
            self.learner.update_learner()
            self.learner_update_timer = 0.0
