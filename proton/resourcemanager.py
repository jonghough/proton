from pygame import *
import pygame

from proton.protonsingleton import ProtonSingleton, Singleton


@Singleton
class ResourceManager(object):
    _instance = None

    def __init__(self):
        self.__texturemap = {}
        self.__audiomap = {}

    def load_texture(self, filename):
        if filename in self.__texturemap.keys():
            return self.__texturemap[filename]
        else:
            tex = pygame.image.load(filename)
            self.__texturemap[filename] = tex
            return tex

    def get_texture(self, filename):
        bmp = self.__texturemap[filename]
        return bmp

    def load_audio(self, filename):
        if filename in self.__audiomap.keys():
            return self.__audiomap[filename]
        else:
            a = pygame.mixer.Sound(filename)
            self.__audiomap[filename] = a
            return a

    def get_audio(self, filename):
        aud = self.__audiomap[filename]
        return aud

    def clear(self):
        self.__texturemap.clear()
        self.__audiomap.clear()


