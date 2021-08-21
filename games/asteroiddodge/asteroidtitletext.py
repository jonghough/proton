from proton.component import Component
from proton.gametime import GameTime, ProtonSingleton
from proton.ui.textcomponent import TextComponent
from proton.ui.uigraphics import Dims


class AsteroidTitleText(Component):
    def __init__(self, gameobject_):
        super(AsteroidTitleText, self).__init__(gameobject_)
        self._tc = None
        self._run = True
        self._finishtime = 0
        self._current_time = 0
        self._start_time = 0

        self._dims = Dims(20, 20, 190, 80)
        self._color = (255, 255, 255)

    def start(self):
        self._tc = self.game_object().get_component(TextComponent)

    def update(self):
        if not self._run:
            self._start_time = ProtonSingleton(GameTime).time()
            self._tc.settext("Game Over. Finish time: " + "{:10.3f}".format(self._finishtime / 1000.0),
                             self._dims, self._color)
        else:
            self._current_time=ProtonSingleton(GameTime).time()
            self._tc.settext("Time: "+"{:10.3f}".format((self._current_time - self._start_time)/1000.0), self._dims, self._color)

    def stop(self):
        self._run = False
        self._finishtime = ProtonSingleton(GameTime).time()

    def restart(self):
        self._run = True
