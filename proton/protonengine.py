import sys
import importlib
import threading
import yaml
import pygame
from pygame import *
from pygame.locals import *
from proton.physics.physicsmanager import PhysicsManager
from proton.gameinput import *
from proton.soundmanager import SoundManager
from proton.scene import *
from proton.scenemanager import * 
import logging

class Config:

    def __init__(self, config_path):
        super().__init__()
        with open(config_path, 'r') as stream:
            try:
                self.config  = yaml.load(stream)
            except yaml.YAMLError as exc:
                logging.error(exc)

class ProtonEngine(object):

    def __init__(self, config_path): 
        pygame.init()
        pygame.mixer.init()
        # init resource manager
        self.resourcemanager = ProtonSingleton(ResourceManager)
        self.scenemanager = ProtonSingleton(SceneManager)
        self.gameinput = ProtonSingleton(GameInput)
        self.gametime = ProtonSingleton(GameTime)
        self.physmanager = ProtonSingleton(PhysicsManager)
        self.soundmanager = ProtonSingleton(SoundManager)
        self._config = Config(config_path)
        self.title = self._config.config["title"]
        self.width = int(self._config.config["dims"]["width"])
        self.height = int(self._config.config["dims"]["height"])
        self.graphics = bool(self._config.config["has_graphics"])
        if self.graphics:
            pygame.display.set_caption(str(self.title))
            pygame.font.init()
            flags = FULLSCREEN | DOUBLEBUF
            self.screen = pygame.display.set_mode((self.width, self.height))  # , flags)
        self.clock = pygame.time.Clock()
        self.scenemanager.width = self.width
        self.scenemanager.height = self.height

        ## ========== load scene ================
        self.load_scene()

    def load_scene(self):
        game_name = self._config.config["module"]
        scene = self._config.config["scene"]
        module = importlib.import_module(f"{game_name}")
        cls = getattr(module, scene)
        self.scenemanager.load_scene(cls(), self._config.config)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

                self.gameinput.keydownevents[str(event.key)] = event

            elif event.type == pygame.KEYUP:
                self.gameinput.keyupevents[str(event.key)] = event
            elif event.type == pygame.MOUSEBUTTONDOWN:
                btn = event.button
                pos = pygame.mouse.get_pos()
                self.gameinput.mousevents[btn] = (btn, pos)

    def run(self):
        self.scenemanager.currentscene.started = True
        while True:
            self.gameinput.keydownevents.clear()
            self.gameinput.keyupevents.clear()
            self.gameinput.mousevents.clear()
            self.gametime.update()
            self.handle_events()

            pt = threading.Thread(target=self.physmanager.runphys(
                self.scenemanager.currentscene.colliders))
            ut = threading.Thread(
                target=self.scenemanager.currentscene.update_scene)
            pt.start()
            ut.start()
            ut.join()
            pt.join()

            if self.graphics:
                self.screen.fill(self.scenemanager.currentscene.fillcolor)
                self.scenemanager.currentscene.render_scene(self.screen)
                pygame.display.flip()
