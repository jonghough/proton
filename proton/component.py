
class Component(object):

    def __init__(self, _gameobject):
        self.__gameobject = _gameobject


    def start(self):
        pass

    def update(self):
        pass

    def draw(self,screen):
        pass

    def ondestroy(self):
        pass

    def oncollision(self, other):
        pass

    def __nullcheck(func):
        def wf(*args):
            if not args[0].__gameobject.is_alive():
                raise Exception
            else:
                return func(*args)
        return wf

    @__nullcheck
    def game_object(self):
        return self.__gameobject

