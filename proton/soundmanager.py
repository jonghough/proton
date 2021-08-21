import threading

from proton.protonsingleton import ProtonSingleton, Singleton
from proton.resourcemanager import ResourceManager, pygame


@Singleton
class SoundManager(object):
    _instance = None

    def __init__(self):
        self.currentscene = None
        self.__channels = []



    def playsound(self, filename, volume,loop):
        audio = ProtonSingleton(ResourceManager).load_audio(filename)
        self.__channels.append((filename, audio))
        def runit(a):
            a.set_volume(0.04)

        runit(audio)

    def playmusic(self, filename, volume):
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(volume)


    def stopmusic(self):
        pygame.mixer.music.stop()


    def stopall(self):
        self.stopmusic()

