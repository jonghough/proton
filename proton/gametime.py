from proton.protonsingleton import *
from pygame import *
import pygame

@Singleton
class GameTime(object):
    _instance = None

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.TICKS = 60
        self.lasttime = 0.0
        self.__dt = 0.0

    def update(self):
        t = pygame.time.get_ticks()
        self.__dt = (t - self.lasttime) / 1000.0
        self.lasttime = t 

    def delta_time(self):
        return self.__dt

    def time_since_start(self):
        return pygame.time.get_ticks()

    def dt(self):
        return self.delta_time()

    def time(self):
        return self.time_since_start()
