from proton.protonmath.vector2 import *


class CatmullRomSpline(object):
    def __init__(self, control_points, on_finish):
        self.control_points = control_points
        self.on_finish = on_finish

        if self.control_points is None or len(self.control_points) == 0:
            raise Exception

        self.p0 = self.control_points[0]
        self.p1 = self.control_points[1]
        self.p2 = self.control_points[2]
        self.p3 = self.control_points[3]

        self.did_reach_end = False
        self.normalized_timer = 0

    def addvector(self, vec):
        self.control_points.append(vec)

    def updatecurve(self, dt):
        if self.did_reach_end is True:
            return self.control_points[1]

        self.normalized_timer += dt

        if self.normalized_timer > 1.0:
            self.normalized_timer = 0.0
            self.control_points.pop(0)

            if len(self.control_points) < 4:
                self.did_reach_end = True
                if self.on_finish is not None:
                    self.on_finish()
                return self.control_points[1]
            else:
                self.p0 = self.control_points[0]
                self.p1 = self.control_points[1]
                self.p2 = self.control_points[2]
                self.p3 = self.control_points[3]

        t = self.normalized_timer
        return 0.5 * (2 * self.p1 + (self.p2 - self.p0) * t +
                      (2 * self.p0 - 5 * self.p1 + 4 * self.p2 - self.p3) * t * t +
                      (3 * self.p1 - self.p0 - 3 * self.p2 + self.p3) * t * t * t)

    def updatecurveatspeed(self, dt, speed):
        speed *= 2
        spd = self.gettangentatcurrenttime().len()

        if spd < 0.000001:
            spd = 0.000001
        realdt = dt * (speed / spd)
        return self.updatecurve(realdt)

    def gettangentatcurrenttime(self):
        if len(self.control_points) < 4:
            return Vector2(0, 0)

        else:
            p0 = self.control_points[0]
            p1 = self.control_points[1]
            p2 = self.control_points[2]
            p3 = self.control_points[3]

            t = self.normalized_timer
            return (p2 - p0) + 2 * (2 * p0 - 5 * p1 + 4 * p2 - p3) * t + \
                   3 * (3 * p1 - p0 - 3 * p2 + p3) * t * t

    def get2ndderivative(self):
        if len(self.control_points) < 4:
            return Vector2(0, 0)
        else:
            p0 = self.control_points[0]
            p1 = self.control_points[1]
            p2 = self.control_points[2]
            p3 = self.control_points[3]

            t = self.normalized_timer
            return 2 * (2 * p0 - 5 * p1 + 4 * p2 - p3) + \
                   6.0 * (3 * p1 - p0 - 3 * p2 + p3) * t
