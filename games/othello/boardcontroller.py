import os
import sys

import math

from games.othello.othellolearner import OthelloLearner
from games.othello.movecalculator import MoveCalculator
from proton.learning.learnerparams import LearnerParams

import numpy as np

from games.othello.squarecontroller import SquareController
from proton.component import Component
from proton.gametime import ProtonSingleton
from proton.resourcemanager import ResourceManager
from proton.scenemanager import SceneManager
from proton.protonmath.vector2 import Vector2
from games.othello.board import Board
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER = 0
RANDOM = 1
MINIMAX = 2
ACTORCRITIC = 3

STATUS_READY = 0
STATUS_CANNOT_MOVE = 1


class BoardController(Component):
    def __init__(self, gameobject_):
        super(BoardController, self).__init__(gameobject_)
        self.direction = Vector2(1, 0)
        self.WIDTH = 8
        self.HEIGHT = 8
        self._squares = []
        self._player1 = None
        self._player2 = None
        self._greenSq = None
        self._whitecircle = None
        self._blackcircle = None
        self._cachescore = 0
        self.turn = SquareController.WHITE
        self.timer = 0
        self.could_move = True
        self.game_running = True
        self.winner = SquareController.NONE
        self.whitestatus = STATUS_READY
        self.blackstatus = STATUS_READY
        self._update_funcs = {0: self.update_human_player(), 1: self.update_random_player(),
                              2: self.update_minimax_player(), 3: self.update_ml_player()}
        self.whitewincount = 0
        self.blackwincount = 0
        self.drawcount = 0

    def load(self, board):
        '''
        Load the board squares form a Board object.
        :param board: 
        :return: 
        '''
        for i in range(0, 64):
            x = int(i / 8.0)
            y = i % 8
            self._squares[x][y]._currentcolor = board._squares[i]
            self._squares[x][y].set_color(board._squares[i])

    def start(self):
        rm = ProtonSingleton(ResourceManager)
        self._whitecircle = rm.load_texture("./games/othello/resources/whitecircle.png")
        self._blackcircle = rm.load_texture("./games/othello/resources/blackcircle.png")
        self._greenSq = rm.load_texture("./games/othello/resources/greensquare.png")

    def update_ml_player(self):
        pass

    def update_random_player(self):
        pass

    def update_human_player(self):
        pass

    def update_minimax_player(self):
        pass

    def set_board(self):
        # load sprites
        counter = 0
        for i in range(0, self.WIDTH):
            l = []
            for j in range(0, self.HEIGHT):
                go = ProtonSingleton(SceneManager).scene().add_new_game_object("square_" + str(i) + "_" + str(j))
                go.set_parent(self.game_object())
                subgo = ProtonSingleton(SceneManager).scene().add_new_game_object("square_sub_" + str(i) + "_" + str(j))
                subgo.set_parent(go)

                subgo.graphics.set_sprite_obj(self._greenSq)
                sc = go.add_component(SquareController)
                sc.setup(self._greenSq, self._blackcircle, self._whitecircle, i, j, self._get_on_click_callback())
                l.append(sc)
                go.motion.set_scale(0.25, 0.25)
                sc.set_position(i, j)

                subgo.graphics.set_render_order(0)

                mid = int(0.5 * self.WIDTH)
                mid2 = mid - 1

                if i == mid:
                    if j == mid:
                        sc.set_color(SquareController.BLACK)
                    elif j == mid2:
                        sc.set_color(SquareController.WHITE)

                elif i == mid2:
                    if j == mid:
                        sc.set_color(SquareController.WHITE)
                    elif j == mid2:
                        sc.set_color(SquareController.BLACK)
                counter += 1
            counter += 1
            self._squares.append(l)
        self.game_running = True
        self.turn = 1

    def reset_board(self):
        # load sprites
        mid = int(0.5 * self.WIDTH)
        mid2 = mid - 1
        for scl in self._squares:
            for sc in scl:
                i = sc.pX
                j = sc.pY
                sc.set_color(SquareController.NONE)
                if i == mid:
                    if j == mid:
                        sc.set_color(SquareController.BLACK)
                    elif j == mid2:
                        sc.set_color(SquareController.WHITE)

                elif i == mid2:
                    if j == mid:
                        sc.set_color(SquareController.WHITE)
                    elif j == mid2:
                        sc.set_color(SquareController.BLACK)

        self.game_running = True
        self.turn = 1
        self.winner = 0
        self._cachescore = 0

    def initialize(self, whiteplayer, blackplayer):
        if whiteplayer is None: raise ValueError('The white player must be selected')
        if blackplayer is None: raise ValueError('The black player must be selected')

        self._player1 = whiteplayer
        self._player2 = blackplayer
        # choose the player types
        # 0 human user
        # 1 random CPU player
        # 2 minimax CPU player
        # 3 actor critic CPU player
        # self.whiteplayer = whiteplayer
        # self.blackplayer = blackplayer

        if self._player1.player_type() == 3:
            # Learner is a component, so needs to be attached to some gameobject. Cant
            # attach to board controller's gameobject, because might need 2 learners.
            # so create a dummy object
            p1obj = ProtonSingleton(SceneManager).scene().add_new_game_object("player1learner")
            self._player1learner = p1obj.add_component(OthelloLearner)
            self._player1.set_learner(self._player1learner)
            #self._player1learner.initialize(LearnerParams(0.05, 1.0, 100000, 1000000, 40, 40, 0.95))
 
            self._player1learner.env = ProtonSingleton(SceneManager).scene()
            self._player1learner.color = 1
        if self._player2.player_type() == 3:
            p2obj = ProtonSingleton(SceneManager).scene().add_new_game_object("player2learner")
            self._player2learner = p2obj.add_component(OthelloLearner)
            self._player2.set_learner(self._player2learner)
 
            self._player2learner.env = ProtonSingleton(SceneManager).scene()
            self._player2learner.color = -1
        # load sprites
        self.set_board()

    def update(self):
        if self.game_running:
            self.timer += 0.01
            if self.turn == -1:
                current_player_type = self._player2.player_type()
            else:
                current_player_type = self._player1.player_type()

            if self.timer > 0.5 and current_player_type > 0:

                self.timer = 0
                did_move = self.player_move(self.turn)

                if self.could_move is False and did_move is False:
                    self.game_running = False
                else:
                    self.could_move = did_move
                    self.turn *= -1

            elif current_player_type == 0:
                board = Board(self)
                moves = MoveCalculator.get_possible_moves(board, self.turn)
                if len(moves) == 0:
                    self.could_move = False
                    self.turn *= -1
                else:
                    self.could_move = True
        
        else:
            self.winner = self.calculate_winner()
            logging.info("WINNER IS " + str(self.winner))
          
              
            if self.whitewincount > 0:
                 logging.info("black win ration >> "+str(self.blackwincount * 1.0 / (self.whitewincount + self.blackwincount)))
            else:
                 logging.info ("100% black win or draw.")
            p1_reward = 1 if self.winner == 1 else -1
            p2_reward = 1 if self.winner == -1 else -1
            st = self.get_state()
            self._player1.reset_with_data(st, p1_reward)
            self._player2.reset_with_data(st, p2_reward)
            ProtonSingleton(SceneManager).scene().reloadscene()

    def is_gameover(self):
        if len(self.getlegalmoves(SquareController.WHITE)) == 0 and len(
                self.getlegalmoves(SquareController.BLACK)) == 0:
            return True
        else:
            return False

    def get_state(self):
        board = Board(self)
        return np.array(board._squares)

    def get_board(self):
        board = {}
        for s in self._squares:
            for sq in s:
                board[(sq.pX, sq.pY)] = sq.getColor()
        return board

    def force_action(self, action, color):
        x = int(action / 8.0)
        y = action % 8
        brd = Board(self)
        MoveCalculator.make_move(brd, x, y, 8, color)
        self.load(brd)

    def player_move(self, color):
        if color == SquareController.WHITE:
            did_move = self._player1.make_move()
        else:
            did_move = self._player2.make_move()
        return did_move

    def getlegalmoves(self, color):
        brd = Board(self)
        return MoveCalculator.get_possible_moves(brd, color)

    def calculate_score(self, color):

        brd = Board(self)
        total_wins = self.whitewincount + self.blackwincount + self.drawcount
        if total_wins == 0:
            return 0
        white = len([x for x in brd.squares if x == SquareController.WHITE])
        black = len([x for x in brd.squares if x == SquareController.BLACK])
        white_ratio = self.whitewincount / total_wins  
        black_ratio = self.blackwincount / total_wins 
        logging.info (f"white {white}, black {black} :: is game over ? {self.is_gameover()}")
      
        logging.info ("win count comparison: " + str(self.whitewincount) + ", " + str(   self.blackwincount) + ", " + str(self.drawcount))
        
        sc = 0
        if self.is_gameover():
            sc = color * (white - black)
            if sc > 0:
                return 1
            elif sc < 0:
                return -1
            else:
                return 0
   

        CORNER = 6
        CORNER_NEG = 6
        CENTRAL = 1
        EDGE = 2
        max_score = (CORNER * 4) + (EDGE * 6) + (CENTRAL * 54)
        sc = 0
        if False:  # black + white > 30:
            return color * (white - black)
        else:

            if brd.squares[0] == color:
                sc += CORNER
            elif brd.squares[0] == -color:
                sc -= CORNER_NEG
            if brd.squares[7] == color:
                sc += CORNER
            elif brd.squares[7] == -color:
                sc -= CORNER_NEG
            if brd.squares[56] == color:
                sc += CORNER
            elif brd.squares[56] == -color:
                sc -= CORNER_NEG
            if brd.squares[63] == color:
                sc += CORNER
            elif brd.squares[63] == -color:
                sc -= CORNER_NEG

            for i in range(1, 8):
                sq = brd.squares[i]
                if sq == color:
                    sc += CENTRAL
                elif sq == -color:
                    sc -= CENTRAL

            for i in [57, 58, 59, 60, 61, 62]:  # range(56, 64):
                sq = brd.squares[i]
                if sq == color:
                    sc += EDGE
                elif sq == -color:
                    sc -= EDGE

            for i in [8, 16, 24, 32, 40, 48]:
                sq = brd.squares[i]
                if sq == color:
                    sc += EDGE
                elif sq == -color:
                    sc -= EDGE

            for i in [15, 23, 31, 39, 47, 55]:
                sq = brd.squares[i]
                if sq == color:
                    sc += EDGE
                elif sq == -color:
                    sc -= EDGE

            multiplier = 1.5
     
            sc =  color * (white - black) / 64
            fs =  (sc - self._cachescore)
            if fs < -1: fs = -1
            if fs > 1: fs = 1
            self._cachescore = sc 
            return sc

    def calculate_winner(self):
        white = len([x for x in [l for sub in self._squares for l in sub] if x._currentcolor == SquareController.WHITE])
        black = len([x for x in [l for sub in self._squares for l in sub] if x._currentcolor == SquareController.BLACK])
 
        if white > black:
            self.whitewincount += 1
            return SquareController.WHITE
        elif black > white:
            self.blackwincount += 1
            return SquareController.BLACK
        else:
            self.drawcount += 1
            return SquareController.NONE

    def _get_on_click_callback(self):

        def onclick(square):
            if self.turn == -1:
                currentplayertype = self._player2.player_type()
            else:
                currentplayertype = self._player1.player_type()
            if currentplayertype is not 0:
                return
            board = Board(self)
            if MoveCalculator.can_make_move(board, square.pX, square.pY, 8, self.turn):
                MoveCalculator.make_move(board, square.pX, square.pY, 8, self.turn)
                self.turn *= -1
                self.could_move = True
                self.load(board)

        return onclick

    

    def can_make_move(self, sq, color):
        x = int(sq / 8.0)
        y = sq % 8
        brd = Board(self)
        return MoveCalculator.can_make_move(brd, x, y, 8, color)
