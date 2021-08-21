
from proton.component import Component
from proton.gametime import GameTime, ProtonSingleton
from proton.motioncomponent import MotionComponent
from proton.protonmath.vector2 import Vector2


class RigidBody(Component):

    def __init__(self,_gameobject):
        super(RigidBody, self).__init__(_gameobject)
        self.position = self.game_object().get_component(MotionComponent).position()
        self.netforce = Vector2(0,10)
        self.acceleration = Vector2(0,0)
        self.velocity = Vector2(0,0)

        self.rads = 0

        self.mass = 1
        self.inversemass = 1
        self.gravity = 10

        self.rotationvelocity = 10
        self.rotationinertia = 1
        self.iskinematic = True

        self.rotationvelocity = 0
        self.rotationinertia = 1
        self.iskinematic = False


    def updatephysics(self, dt):
        '''
        Update the kinematics physics.
        :param dt: delta time
        :return: nothing
        '''
        if self.iskinematic:
            self.position = self.position + (self.velocity * dt) +(self.acceleration * 0.5 * dt * dt)
            self.acceleration = self.acceleration + self.netforce * self.inversemass
            self.velocity = self.velocity + self.acceleration * dt

            self.rads = self.rotationvelocity * dt


    def update(self):
        if self.iskinematic:
            self.updatephysics(GameTime.dt())
            self.game_object().get_component(MotionComponent).set_position(self.position.x, self.position.y)
            self.game_object().get_component(MotionComponent).rotate_by(self.rads)


    @staticmethod
    def oncollide(rb1, rb2): 
        nextv1 = (rb1.velocity * (rb1.mass - rb2.mass)) + (2.0 * rb2.mass * rb2.velocity)
        nextv2 = (rb2.velocity * (rb2.mass - rb1.mass)) + (2.0 * rb1.mass * rb1.velocity)

        totalmass = rb1.mass + rb2.mass

        nextv1.x = nextv1.x / totalmass
        nextv1.y = nextv1.y / totalmass

        nextv2.x = nextv2.x / totalmass
        nextv2.y = nextv2.y / totalmass

        rb1.velocity = nextv1
        rb2.velocity = nextv2

        dt = ProtonSingleton(GameTime).dt()

        rb1.position = rb1.position + (rb1.velocity * dt) + (rb1.acceleration * 0.5 * dt * dt)
        rb2.position = rb2.position + (rb2.velocity * dt) + (rb2.acceleration * 0.5 * dt * dt)




