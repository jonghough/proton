import random
import math
import tensorflow as tf
from collections import namedtuple
   
from games.othello.boardcontroller import *
from games.othello.minimax import calculatescore2, Minimax
from games.othello.board import Board


class CPUPlayer(object):
    """
    CPU PLayer for the Othello simulation.
    """
    
    def __init__(self, board, myColor):
        self._board = board
        self._color = myColor
        self._memory = []
        self._minimax_depth_limit = 4


    def can_move(self):

        board = Board(self._board)
        return len(MoveCalculator.get_possible_moves(board,self._color)) > 0

    def _set_move_minimax(self):
        logging.info("minimax turn: ")
        board = Board(self._board)
        minimaxx = Minimax(self._minimax_depth_limit, calculatescore2)
        a = minimaxx.evaluate(board, self._color)
        if a[2] is None:
            return False
        else:
            self._board.load(a[0])
            return True

    def _set_move_random(self):
        brd = Board(self._board)
        lm = MoveCalculator.get_possible_moves(brd, self._color)
        if len(lm) == 0:
            return False
        r = random.randint(0, 90000)
        r %= len(lm)
        m = lm[r]
        MoveCalculator.make_move(brd, m[0], m[1], 8, self._color)
        self._board.load(brd)
        return True


    def set_piece(self):
        k = random.randint(0, 100)
        if   self._color == 1:
            brd = Board(self._board)
            lm = MoveCalculator.get_possible_moves(brd,self._color)
            if len(lm) == 0:
                return False
            r = random.randint(0, 90000)
            r %= len(lm) 
            m = lm[r]
            MoveCalculator.make_move(brd, m[0], m[1], 8, self._color)
            self._board.load(brd)
            return True


        board = Board(self._board)
        minimaxx = Minimax(self._minimax_depth_limit, calculatescore2)
        a = minimaxx.evaluate(board, self._color)
        if a[2] is None:
            return False
        else:
            self._board.load(a[0])
            return True
