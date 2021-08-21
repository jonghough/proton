from proton.protonsingleton import Singleton


@Singleton
class GameInput(object):
    _instance = None

    def __init__(self):
        self.keydownevents = {}
        self.keyupevents = {}
        self.mousevents = {}
