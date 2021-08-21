from proton.component import Component
from proton.gametime import GameTime, ProtonSingleton
from proton.ui.textcomponent import TextComponent
from proton.ui.uigraphics import Dims


class TitleText(Component):
    def __init__(self, gameobject_):
        super(TitleText, self).__init__(gameobject_)
        self._tc = None
        self._run = True
        self._finishtime = 0
        self._current_time = 0
        self._start_time = 0

    def start(self):
        self._tc = self.game_object().get_component(TextComponent)

    def update(self):
        if not self._run:
            self._start_time = ProtonSingleton(GameTime).time()
            self._tc.settext("Game Over. Finish time: " + "{:10.3f}".format(self._finishtime / 1000.0),
                             Dims(500, 20, 1000, 120), (255, 255, 255))
        else:
            self._current_time=ProtonSingleton(GameTime).time()
            self._tc.settext("Time: "+"{:10.3f}".format((self._current_time - self._start_time)/1000.0), Dims(700, 20, 1000, 90), (255, 255, 255))

    def stop(self):
        self._run = False
        self._finishtime = ProtonSingleton(GameTime).time()

    def restart(self):
        self._run = True
