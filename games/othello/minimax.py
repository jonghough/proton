import math
from itertools import chain
import logging
import copy
from games.othello.squarecontroller import SquareController
from games.othello.movecalculator import MoveCalculator

"""
Minimax implementation for Othello (Reversi), with a default heuristic evaluation function,
calculatescore.
"""


def calculatescore2(board, color):
    """

    :param board:
    :param color:
    :return:
    """
    CORNER = 6
    CENTRAL = 1
    EDGE = 2
    #board.print_me()
    white = len([x for x in board._squares if x == SquareController.WHITE])
    black = len([x for x in board._squares if x == SquareController.BLACK])
    sc = 0 
    if black + white > 57:
        return color * (white - black)
    else:

        if board._squares[0] == Minimax.minimax_color:
            sc += CORNER
        elif board._squares[0] == -Minimax.minimax_color:
            sc -= CORNER
        if board._squares[7] == Minimax.minimax_color:
            sc += CORNER
        elif board._squares[7] == -Minimax.minimax_color:
            sc -= CORNER
        if board._squares[56] == Minimax.minimax_color:
            sc += CORNER
        elif board._squares[56] == -Minimax.minimax_color:
            sc -= CORNER
        if board._squares[63] == Minimax.minimax_color:
            sc += CORNER
        elif board._squares[63] == -Minimax.minimax_color:
            sc -= CORNER

        for i in range(1, 8):
            sq = board._squares[i]
            if sq == Minimax.minimax_color:
                sc += CENTRAL
            elif sq == -Minimax.minimax_color:
                sc -= CENTRAL

        for i in [57, 58, 59, 60, 61, 62]:  # range(56, 64):
            sq = board._squares[i]
            if sq == Minimax.minimax_color:
                sc += EDGE
            elif sq == -Minimax.minimax_color:
                sc -= EDGE

        for i in [8, 16, 24, 32, 40, 48]:
            sq = board._squares[i]
            if sq == Minimax.minimax_color:
                sc += EDGE
            elif sq == -Minimax.minimax_color:
                sc -= EDGE

        for i in [15, 23, 31, 39, 47, 55]:
            sq = board._squares[i]
            if sq == Minimax.minimax_color:
                sc += EDGE
            elif sq == -Minimax.minimax_color:
                sc -= EDGE
         
        return sc


def calculatescore(board, color):
    """

    :param board:
    :param color:
    :return:
    """
    white = len([x for x in board._squares if x == SquareController.WHITE])
    black = len([x for x in board._squares if x == SquareController.BLACK])
    sc = 0
    if black + white > 50:
        return color * (white - black)
    else:
        wm = len(MoveCalculator.get_possible_moves(board, SquareController.WHITE))
        bm = len(MoveCalculator.get_possible_moves(board, SquareController.BLACK))
        return color * (wm - bm)


class Minimax:
    current_color = 1
    minimax_color = 0

    def __init__(self, depth, minimax_color_, log_level, eval_callback): 
        self.depth = depth
        self.log_level = log_level
        self.eval_callback = eval_callback
        self.alpha = -100000
        self.beta = 100000
        Minimax.minimax_color = minimax_color_

    def changesquare(self, board, color, i, j):
        white = len([x for x in board._squares if x == SquareController.WHITE])
        black = len([x for x in board._squares if x == SquareController.BLACK])
        MoveCalculator.make_move(board, i, j, 8, color)
        white = len([x for x in board._squares if x == SquareController.WHITE])
        black = len([x for x in board._squares if x == SquareController.BLACK])

    def run_next(self, board, color, depth, ismax, possiblemoves):
        hs = self.alpha
        nextmax = not ismax
        if not ismax:
            hs = self.beta
        if len(possiblemoves) == 0:
            #logging.info("minimax: cannot move")
            # we cannot move, so allow the opponent to move.
            return self.run_minimax(board, color, None, depth, nextmax)
                    

        quit = False
        for i in range(0, len(possiblemoves)):
            if quit is False:
                if ismax:
                    bc = copy.deepcopy(board)
                    score = self.run_minimax(bc, color, possiblemoves[i], depth, nextmax)
                    
                    if score is not None:
                        e = score 
                        if self.alpha <= e:
                            self.alpha = e
                        if self.beta <= self.alpha: 
                            return self.alpha
                else:
                    bc = copy.deepcopy(board)
                    score = self.run_minimax(bc, color, possiblemoves[i], depth, nextmax)
                    if score is not None:
                        e = score 
                        if self.beta >= e:
                            self.beta = e
                        if self.beta <= self.alpha:
                            return self.beta
        if ismax: 
            return self.alpha 
        else: 
            return self.beta

    def run_minimax(self, board, color, position, depth, ismax):
        if position is not None:
            self.changesquare(board, color, position[0], position[1])
        if depth >= self.depth:
            return self.eval_callback(board, Minimax.current_color)
        else:
            possiblemoves = MoveCalculator.get_possible_moves(board, color * -1)
            return self.run_next(copy.deepcopy(board), color * -1, depth + 1, ismax, possiblemoves)

    def evaluate(self, board, color):
        Minimax.minimax_color = color
        possibleinitmoves = MoveCalculator.get_possible_moves(board, color)
        if len(possibleinitmoves) == 0:
            return (board, None, None)
        else:
            optimal = []
            Minimax.current_color = color
            self.alpha = -100000
            self.beta = 100000
            for pos in possibleinitmoves:
                b = copy.deepcopy(board)
                optimal.append((b, self.run_minimax(b, color, pos, 1, True), pos))

            optimal.sort(key=lambda xo: xo[1], reverse=(True))
            if self.log_level > 0:
                logging.info ("minimax: optimal score for " + str(color) + ", " + str(optimal[0][1]))
                logging.info ("minimax: worst score for " + str(color) + ", " + str(optimal[len(optimal)-1][1]))
                logging.info ("minimax: MAX SEARCH DEPTH " + str(self.depth))
            
            if self.log_level > 1:
                optimal[0][0].print_me()
            return optimal[0]
