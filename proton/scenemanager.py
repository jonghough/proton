import proton.scene
from proton.protonsingleton import *


@Singleton
class SceneManager(object):
    _instance = None

    def __init__(self):
        self.currentscene = None
        self.width = None
        self.height = None

    def load_scene(self, scene, config_data):
        if self.currentscene is not None:
            self.currentscene.destroy_all()
        self.currentscene = scene
        scene.initialize(config_data)

    def scene(self):
        return ProtonSingleton(SceneManager).currentscene
