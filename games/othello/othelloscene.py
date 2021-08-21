from games.othello.boardcontroller import BoardController
from proton.learning.rl_interface import RLInterface
from proton.protonengine import ProtonEngine
from proton.scene import Scene
import yaml
from games.othello.playerdata import *
import numpy as np


def generate_player(board, color, playerdata):
    player = str(playerdata["playtype"])

    if player == "random":
        return RandomPlayer(board, color)
    elif player == "minimax":
        searchdepth = str(playerdata["attributes"]["searchdepth"])
        log_level = int(playerdata["attributes"]["log_level"])
        randomness = float(playerdata["attributes"]["randomness"])
        return MinimaxPlayer(board, color, int(searchdepth), log_level, randomness)
    elif player == "human":
        return HumanPlayer(board, color)
    elif player == "ml":
        model_path = str(playerdata["attributes"]["model_path"])
        learning_rate = float(playerdata["attributes"]["learning_rate"])
        is_training = bool(playerdata["attributes"]["is_training"])
        eps_min = float(playerdata["attributes"]["eps_min"])
        eps_max = float(playerdata["attributes"]["eps_max"])
        eps_decay_steps = float(playerdata["attributes"]["eps_decay_steps"])
        n_steps = int(playerdata["attributes"]["n_steps"])
        start_training_steps = int(
            playerdata["attributes"]["start_training_steps"])
        training_interval = int(playerdata["attributes"]["training_interval"])
        save_steps = int(playerdata["attributes"]["save_steps"])
        copy_steps = int(playerdata["attributes"]["copy_steps"])
        discount_rate = float(playerdata["attributes"]["discount_rate"])
        batch_size = int(playerdata["attributes"]["batch_size"])
        learnerparams = LearnerParams(is_training, eps_min, eps_max, eps_decay_steps,
                                      n_steps, start_training_steps, training_interval, save_steps, copy_steps, discount_rate, learning_rate, model_path,
                                      batch_size)

        return MLPlayer(board, color, learnerparams)


def create_players(yamldata, board):
    white = yamldata["white"]
    wp = generate_player(board, 1, white)
    black = yamldata["black"]
    bp = generate_player(board, -1, black)
    return (wp, bp)


class OthelloScene(Scene, RLInterface):
    def __init__(self):
        super(OthelloScene, self).__init__()
        self.fillcolor = (175, 110, 200)

    def getplayers(self, file, boardcontroller):
        with open("games/othello/resources/game4.yml", 'r') as stream:
            try:
                data = yaml.load(stream)
                players = create_players(data, boardcontroller)
                return players
            except yaml.YAMLError as exc:
                logging.error(exc)

    def initialize(self, config_data):
        self.board = self.add_new_game_object("boardcontroller")
        self.board.add_component(BoardController)
        self.board.motion.set_position(500, 500)
        self.boardcontroller = self.board.get_component(BoardController)
        players = self.getplayers("", self.boardcontroller)
        self.boardcontroller.initialize(players[0], players[1])

    def gamestarted(self):
        return self.started

    def resetnow(self):
        logging.info("**** DESTROY GAME OBJECT AND REINITIALIZE ****")
        # self.destroyall()

        self.started = True

    def reloadscene(self):
        self.boardcontroller.reset_board()

    def get_reward(self, color):
        """
        gets the reward for the given action.
        :param action:
        :return:
        """
        score = self.boardcontroller.calculate_score(color)
        return score

    def get_legal_actions(self):
        """
        Gets legal action codes.
        :return: list of legal actions.
        """
        return self.boardcontroller.getlegalmoves()

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

    def is_legal_action(self, action, color):
        return self.boardcontroller.can_make_move(action, color)

    def get_observation(self):
        """
        Gets game state observation.
        :return: game state observation.
        """
        return self.boardcontroller.get_board()

    def is_game_over(self):
        """
        True if game over, false otherwise.
        :return:
        """
        return self.boardcontroller.is_gameover()

    def finish(self):
        pass

    def get_state(self):
        return self.boardcontroller.get_state()

    def perform_action(self, action, color):
        """
        Apply action and return reward.
        :param action:
        :return:
        """

        reward = 0
        if action is not None:
            self.boardcontroller.force_action(action, color)
            reward = self.get_reward(color)
        else:
            winner = self.boardcontroller.winner
            if winner == 0:
                reward = 0
            elif self.boardcontroller.winner == color:
                reward = 1
            else:
                reward = -1
        return reward

    def step(self, action, color):
        reward = self.perform_action(action, color)
        state = self.get_state()
        done = self.is_game_over()
        return state, reward, done
