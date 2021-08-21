import pygame

from proton.component import *
from pygame import Color

from proton.component import Component
from proton.ui.uigraphics import UIGraphics
from proton.ui.uigraphics import Dims


class TextComponent(UIGraphics):

    def __init__(self, _gameobject):
        """

        :param _gameobject:
        """
        super(TextComponent, self).__init__(_gameobject)

        self.text = None
        self.textSize = 1
        #self.textColor = Color.Red
        self.setup(Dims(100,200,200,100))
        self.font = pygame.font.SysFont('Monospace', 100)

    def settext(self,txt, dims, color):
        self.text=txt
        textsurface = self.font.render(self.text, False, color)
        self.game_object().graphics.set_sprite_obj(textsurface)

        self.setup(dims)






