from pygame import *
from proton.component import *
from proton.gameobject import *
from pygame import *
from math import * 
from proton.resourcemanager import *
from proton.protonsingleton import *
from proton.protonmath.vector2 import Vector2

class GraphicsComponent(Component):
    def __init__(self, _gameobject):
        super(GraphicsComponent, self).__init__(_gameobject)
        self.sprite = None
        self.blit_sprite = None
        self.sprite_rect = None
        self.blit_sprite_rect = None
        self.render_flag = False
        self.sprite_name = None
        self.render_order = 1  # default
        self.width = 0
        self.height = 0
        self.setup_on_load()


    def setup_on_load(self):
        if self.sprite_name is not None:
            self.set_sprite(self.sprite_name)

    def set_sprite(self, spritename):
        self.sprite_name = spritename
        rm = ProtonSingleton(ResourceManager)
        sprite = rm.load_texture(spritename)
        self.sprite = sprite
        self.sprite_rect = self.sprite.get_rect()
        self.blit_sprite = sprite
        self.blit_sprite_rect = self.blit_sprite.get_rect()
        self.render_flag = True
        self.width = self.sprite_rect.width
        self.height = self.sprite_rect.height
 

    def set_sprite_obj(self, spriteobj):
        if spriteobj is None:
            self.sprite = None
            self.blit_sprite = None
            self.width = 0
            self.height = 0
        else:
            self.sprite = spriteobj
            self.sprite_rect = self.sprite.get_rect()
            self.blit_sprite = self.sprite
            self.blit_sprite_rect = self.blit_sprite.get_rect()
            self.render_flag = True
            self.width = self.sprite_rect.width
            self.height = self.sprite_rect.height  

    def set_render_order(self, rendorder):
        self.render_order = rendorder
        from proton.scenemanager import SceneManager
        ProtonSingleton(SceneManager).scene().sort_render_order()

    def update(self):
        pass

    def draw(self, screen):
        if self.render_flag is False:
            return
        if self.sprite is None:
            return

        xpos = self.game_object().motion.worldtransform.at(0, 2)
        ypos = self.game_object().motion.worldtransform.at(1, 2)

        scalex =  Vector2(self.game_object().motion.worldtransform.at(0, 0),
                         self.game_object().motion.worldtransform.at(1, 0)).len()
        scaley =  Vector2(self.game_object().motion.worldtransform.at(0, 1),
                         self.game_object().motion.worldtransform.at(1, 1)).len()

        self.sprite_rect.x = xpos - 0.5 * self.width
        self.sprite_rect.y = ypos - 0.5 * self.height

        cx = self.game_object().motion.worldtransform.at(0, 0)
        sx = self.game_object().motion.worldtransform.at(0, 1)


        rads = atan2(sx, cx)
        self.blit_sprite= pygame.transform.scale(self.sprite, (int(scalex * self.width), int(scaley * self.height)))
        orig_rect = self.sprite_rect
        c = orig_rect.center

        self.blit_sprite = pygame.transform.rotate(self.blit_sprite, rads * 180.0 / 3.14159265)

        self.blit_sprite_rect = self.blit_sprite.get_rect(center=c)
        self.blit_sprite_rect.width = 100
        screen.blit(self.blit_sprite, self.blit_sprite_rect)
