from proton.quadtree import *


class QuadManager(object):
    """
    Manages Quadtree collisions. This checks for collisions between game objects
    inside quadtree quads every frame.
    """

    def __init__(self, size, do_layers_collide):
        self.quads = []
        if size < 0:
            raise Exception

        for i in range(0, size):
            bnds = AABB(Vector2(100, 100))
            self.quads.append(QuadTree(bnds, do_layers_collide))

        self.collision_map = {}
        self.index = 0

    def get_next_quad(self):
        quad = self.quads[self.index]
        self.index = (self.index + 1) % len(self.quads)
        return quad

    def check_collisions(self, depth, dims, colliders): 
        quad = self.get_next_quad()
        quad.bounds.worldtransform.set(0, 2, 200)
        quad.bounds.worldtransform.set(1, 2, 200)
        quad.bounds.dims = dims
        quad.filter_colliders(colliders)
        return quad.split(1, self.get_next_quad)
