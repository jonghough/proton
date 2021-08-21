import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from proton.gameinput import GameInput
from proton.gametime import GameTime, ProtonSingleton
from proton.component import Component


class SquareController(Component):
    NONE = 0
    BLACK = -1
    WHITE = 1

    def __init__(self, gameobject_):
        super(SquareController, self).__init__(gameobject_)
        self._currentcolor = SquareController.NONE
        self._squaresprite = None
        self._blacksprite = None
        self._whitesprite = None
        self.input = ProtonSingleton(GameInput)

    def setup(self, squaresprite, black, white, x, y, onclick):
        self._squaresprite = squaresprite
        self._blacksprite = black
        self._whitesprite = white
        self.pX = x
        self.pY = y
        self._onclick = onclick

        self.game_object().graphics.set_sprite_obj(None)

    def set_position(self, i, j):
        spritesize = self._squaresprite.get_rect().size
        scale = self.game_object().transform().get_scale()
        self.game_object().motion.set_position(500 + i * spritesize[0] * scale.x, 200 + j * spritesize[1] * scale.y)

    def set_color(self, color):
        self._currentcolor = color
        if color == SquareController.BLACK:
            self.game_object().graphics.set_sprite_obj(self._blacksprite)
        elif color == SquareController.WHITE:
            self.game_object().graphics.set_sprite_obj(self._whitesprite)
        else:
            self.game_object().graphics.set_sprite_obj(None)

    def get_color(self):
        return self._currentcolor

    def is_clicked(self, x, y):
        pos = self.game_object().transform().position()
        spritesize = self._squaresprite.get_rect().size
        scale = self.game_object().transform().get_scale()
        if pos.x - scale.x * spritesize[0] / 2 < x < pos.x + scale.x * spritesize[0] / 2 and \
                                        pos.y - scale.y * spritesize[1] / 2 < y < pos.y + scale.y * spritesize[1] / 2:
            return True
        else:
            return False

    def update(self):
        for key in self.input.mousevents.keys(): 
            if key == 1:
                click = self.input.mousevents[key]
                if click is not None: 
                    pos = click[1]
                    if self.is_clicked(pos[0], pos[1]):
                        logging.info( "USER CLICKED!!! at " + str(self.pX) + ", " + str(self.pY))
                        self._onclick(self, )
