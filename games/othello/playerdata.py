from games.othello.movecalculator import MoveCalculator
from games.othello import minimax
from games.othello.boardcontroller import *
from games.othello.minimax import calculatescore, calculatescore2
from games.othello.board import Board
import random as rnd
import numpy as np

USER = 0
RANDOM = 1
MINIMAX = 2
ACTORCRITIC = 3
PLAYER_TYPES = {0: 'USER', 1: 'RANDOM', 2: 'MINIMAX', 3: 'ACTORCRITIC'}


class BasePlayer(object):
    def __init__(self, board, myColor):
        self._board = board
        self._color = myColor
        self._memory = []

    def player_type(self):
        return USER

    def is_player_type(self,player_type):
        return PLAYER_TYPES[self.player_type()] == player_type


    def can_move(self):
        board = Board(self._board)
        return len(MoveCalculator.get_possible_moves(board, self._color)) > 0

    def make_move(self):
        return False


    def reset(self):
        pass


    def reset_with_data(self, state, reward):
        pass


class RandomPlayer(BasePlayer):

    def __init__(self, board, myColor):
        super(RandomPlayer, self).__init__(board, myColor)

    def _set_move_random(self):
        brd = Board(self._board)
        lm = MoveCalculator.get_possible_moves(brd, self._color)
        if len(lm) == 0:
            return False
        r = rnd.randint(0, 90000)
        r %= len(lm)
        m = lm[r]
        MoveCalculator.make_move(brd, m[0], m[1], 8, self._color)
        self._board.load(brd)
        return True

    def player_type(self):
        return RANDOM

    def make_move(self):
        return self._set_move_random()


class MinimaxPlayer(BasePlayer):

    def __init__(self, board, my_color, searchdepth, log_level, randomness):
        super(MinimaxPlayer, self).__init__(board, my_color)
        self._minimax_depth_limit = searchdepth 
        self._log_level = log_level
        self._randomness = randomness

    def _set_move_minimax(self):
        board = Board(self._board)
        if rnd.uniform(0.0, 1.0) < self._randomness:
            possible = MoveCalculator.get_possible_moves(board, self._color)
            if len(possible) == 0:
                return False
            indices = np.random.permutation(len(possible)) 
            return possible[indices[0]]
            # action = rnd.randint(0, 63)
            # while not MoveCalculator.get_possible_moves(board, self._color):
            #     action = rnd.randint(0, 63) 
            # return action
        else:    
            minimaxx = minimax.Minimax(self._minimax_depth_limit, self._color, self._log_level, calculatescore2)
         
            a = minimaxx.evaluate(board, self._color)
            if a[2] is None:
                return False
            else:
                self._board.load(a[0])
                return True

    def make_move(self):
        return self._set_move_minimax()

    def player_type(self):
        return MINIMAX


class HumanPlayer(BasePlayer):
    def __init__(self, board, myColor):
        super(HumanPlayer, self).__init__(board, myColor)
        pass

    def player_type(self):
        return USER


class MLPlayer(BasePlayer):
    def __init__(self, board, myColor,  learner_params):
        super(MLPlayer, self).__init__(board, myColor)
        self._learner = None 
        self.learner_params = learner_params



    def get_model_path(self):
        return self._model_path

    def set_learner(self, learner):
        self._learner = learner 
        learner.initialize(self.learner_params)

    def player_type(self):
        return ACTORCRITIC

    def make_move(self):
        if len(self._board.getlegalmoves(self._color)) == 0:
            return False  # cannot move
        else:
            self._learner.your_turn()
            return True


    def reset(self):
        self._learner.reset()

    
    def reset_with_data(self, state, reward):
        self._learner.reset_with_reward(state,reward)