'''
This file is essentially unused
'''


class RLInterface(object):

    def __init__(self):
        pass


    def launch(self):
        pass

    def get_reward(self, action):
        """
        gets the reward for the given action.
        :param action:
        :return:
        """
        pass

    def get_legal_actions(self):
        """
        Gets legal action codes.
        :return: list of legal actions.
        """
        pass

    def save_state(self):
        """
        saves the state
        :return:
        """
        pass

    def load_state(self):
        """
        loads the state
        :return:
        """
        pass

    def get_observation(self):
        """
        Gets game state observation.
        :return: game state observation.
        """
        return None

    def is_game_over(self):
        """
        True if game over, false otherwise.
        :return:
        """
        return False

    def step(self):
        """
        Game step
        :return:
        """
        return None
    
    def finish(self):
        pass

    def get_state(self):
        """
        Gets the current game state.
        :return:
        """
        pass


    def perform_action(self, action):
        """
        Apply action and return reward.
        :param action:
        :return:
        """
        pass

