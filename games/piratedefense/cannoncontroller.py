from math import sin, acos

from pygame.constants import K_UP, K_DOWN, K_SPACE

from games.piratedefense.cannonlearner import CannonLearner
from proton.collider import Collider
from proton.component import Component
from proton.graphicscomponent import GraphicsComponent
from proton.physics.rigidbody import RigidBody
from proton.protonmath.vector2 import Vector2
from games.piratedefense.cannonball import CannonBall
from proton.scenemanager import SceneManager
from proton.resourcemanager import ResourceManager
from proton.protonsingleton import ProtonSingleton
from proton.gameinput import GameInput
from proton.gametime import GameTime


class CannonController(Component):
    GRAVITY = 900

    def __init__(self, gameobject_):

        super(CannonController, self).__init__(gameobject_)
        self.state = 0  # 0 = stationary, 1 = moving
        self.initialspeed = 400
        self.initialangle = -1.4
        self.initialposition = Vector2(0, 0)
        self.time = 0
        self.targetpoint = Vector2(0, 0)
        self.target = None
        self.cannonballs = []
        self.cbcount = 20
        self.idx = 0
        self.input = ProtonSingleton(GameInput)
        self.cannon_fire_timer = 0.0
        self.FIRE_WAIT_TIME = 1.75  # 1.75 seconds between launches.

    def init(self):
        rm = ProtonSingleton(ResourceManager)
        cannonimag = rm.load_texture("./games/piratedefense/resources/cannon.png")
        self.game_object().graphics.set_sprite_obj(cannonimag)
        self.game_object().motion.set_position(30, 100)
        self.game_object().transform().set_scale(0.5, 0.5)
        self.game_object().get_component(GraphicsComponent).renderorder = 100

        for i in range(self.cbcount):
            go = ProtonSingleton(SceneManager).scene().add_new_game_object("cannonball_" + str(i))
            go.add_component(CannonBall)
            self.cannonballs.append(go.get_component(CannonBall))
            go.set_active(False)
            rm = ProtonSingleton(ResourceManager)
            blackcircle = rm.load_texture("./games/piratedefense/resources/cannonball.png")
            go.motion.set_position(-100, 100)
            go.graphics.set_sprite_obj(blackcircle)
            col = go.add_component(Collider)
            go.add_component(RigidBody)
            go.transform().set_scale(0.25, 0.25)
            go.get_component(GraphicsComponent).renderorder = 10
            col.layer = 24
        self.add_learner()

    def launch(self, angle, speed, target):
        cb = self.cannonballs[self.idx]
        self.idx += 1
        self.idx %= self.cbcount 

        cb.launch(self.game_object().motion.position(), angle, speed, target)
        cb.game_object().set_active(True)

    def restart(self):
        self.game_object().motion.set_position(30, 100)
        for cannon in self.cannonballs:
            cannon.game_object().set_active(False)

    def update(self):
        if str(K_UP) in self.input.keydownevents:
            p = self.game_object().transform().position()
            if p.y > 20:
                p -= Vector2(0, 20)
                self.game_object().transform().set_position(p.x, p.y)
        if str(K_DOWN) in self.input.keydownevents:
            p = self.game_object().transform().position()
            if p.y < 680:
                p += Vector2(0, 20)
                self.game_object().transform().set_position(p.x, p.y)

        if str(K_SPACE) in self.input.keydownevents:
            if self.cannon_fire_timer > self.FIRE_WAIT_TIME:
                self.cannon_fire_timer = 0
                p = self.game_object().transform().position()
                self.launch(-0.25, 400, p + Vector2(90000, 0))

        self.cannon_fire_timer += ProtonSingleton(GameTime).delta_time()


    def launchatpoint(self, point):
        pos = self.game_object().motion.position()
        vec = point - pos
        angle = acos(vec.normalize().dot(Vector2(1, 0)))
        self.launch(-angle, 1000, point)

    def input(self, action):
        if action == 0:
            pass
        elif action == 1:
            self.move_up()
        elif action == 2:
            self.move_down()
        elif action == 3:
            self.fire_cannon()

    def fire_cannon(self):
        if self.cannon_fire_timer > self.FIRE_WAIT_TIME:
            self.cannon_fire_timer = 0
            p = self.game_object().transform().position()
            self.launch(-0.25, 400, p + Vector2(90000, 0))

    def move_up(self):
        p = self.game_object().transform().position()
        if p.y > 20:
            p -= Vector2(0, 20)
            self.game_object().transform().set_position(p.x, p.y)

    def move_down(self):
        p = self.game_object().transform().position()
        if p.y < 680:
            p += Vector2(0, 20)
            self.game_object().transform().set_position(p.x, p.y)

    def force_action(self, action):
        if action is None:
            return True
        else:
            if action == 0:
                return True  # do nothing
            elif action == 1:
                self.move_up()
            elif action == 2:
                self.move_down()
            else:
                self.fire_cannon()
        return True

    def get_state(self):
        return self.game_object().transform().position().y * 1.0 / 700  # y pos

    def add_learner(self):
        self.game_object().add_component(CannonLearner)
        self.learner = self.game_object().get_component(CannonLearner)
        self.learner.env = ProtonSingleton(SceneManager).scene()
