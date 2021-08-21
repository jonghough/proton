import mmh3
from proton.aabb import *


class QuadTree(object):
    def __init__(self, aabb, do_layers_collide):
        self.bounds = aabb
        self.colliderlist = []
        self.do_layers_collide = do_layers_collide

    def filter_colliders(self, colliders):
        self.colliderlist = []
        if len(colliders) > 1:

            for c in colliders:
                if c.game_object().is_active() is False:
                    continue
                if AABB. is_collide(self.bounds, c.aabb):
                    self.colliderlist.append(c)

    def split(self, depth, getnext):
        self.bounds.calcbounds()
        self.bounds.calcnormals()
        collisions = {}
        if depth < 1:
            return collisions
        elif depth == 1:
            if len(self.colliderlist) < 2:
                pass

            else:
                for c1 in range(0, len(self.colliderlist) - 1):
                    for c2 in range(c1 + 1, len(self.colliderlist)):

                        collider1 = self.colliderlist[c1]
                        collider2 = self.colliderlist[c2]

                        collider1.lock.acquire()
                        collider2.lock.acquire()

                        if self.do_layers_collide(collider1.layer, collider2.layer):
                            collisionpoint = AABB. is_collide(
                                collider1.aabb, collider2.aabb)

                            if collisionpoint is not None:
                                id1 = id(collider1.game_object())
                                id2 = id(collider2.game_object())
                                m = (id1 + id2) + (id1 ^ id2)
                                hashed = mmh3.hash(str(m))
                                collisions[hashed] = (collider1.game_object(
                                ), collider2.game_object(), collisionpoint)

                        collider1.lock.release()
                        collider2.lock.release()
            return collisions

        else:
            # go deeper...
            tlq = getnext()  # -,-
            tlq.bounds.worldtransform = self.bounds.worldtransform - \
                Matrix3(0, 0, self.bounds.dims.x * 0.25, 0, 0, self.bounds.dims.y * 0.25, 0, 0,
                        0)
            tlq.bounds.dims = Vector2(
                self.bounds.dims.x * 0.5, self.bounds.dims.y * 0.5)

            trq = getnext()  # +,-
            trq.bounds.worldtransform = self.bounds.worldtransform - \
                Matrix3(0, 0, self.bounds.dims.x * -0.25, 0, 0, self.bounds.dims.y * 0.25, 0, 0,
                        0)
            trq.bounds.dims = Vector2(
                self.bounds.dims.x * 0.5, self.bounds.dims.y * 0.5)

            brq = getnext()  # +,+
            brq.bounds.worldtransform = self.bounds.worldtransform - \
                Matrix3(0, 0, self.bounds.dims.x * -0.25, 0, 0, self.bounds.dims.y * -0.25, 0,
                        0, 0)
            brq.bounds.dims = Vector2(
                self.bounds.dims.x * 0.5, self.bounds.dims.y * 0.5)

            blq = getnext()  # -,+
            blq.bounds.worldtransform = self.bounds.worldtransform - \
                Matrix3(0, 0, self.bounds.dims.x * 0.25, 0, 0, self.bounds.dims.y * -0.25, 0, 0,
                        0)
            blq.bounds.dims = Vector2(
                self.bounds.dims.x * 0.5, self.bounds.dims.y * 0.5)

            tlq.filter_colliders(self.colliderlist)
            collisions.update(tlq.split(depth - 1, getnext))

            trq.filter_colliders(self.colliderlist)
            collisions.update(trq.split(depth - 1, getnext))

            brq.filter_colliders(self.colliderlist)
            collisions.update(brq.split(depth - 1, getnext))

            blq.filter_colliders(self.colliderlist)
            collisions.update(blq.split(depth - 1, getnext))

            return collisions
