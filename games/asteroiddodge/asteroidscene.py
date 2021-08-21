import sys
import os

import logging
from proton.protonengine import ProtonEngine
from proton.gameobject import GameObject
from proton.scene import Scene
from proton.learning.learnerparams import LearnerParams
import tensorflow as tf
from games.asteroiddodge.gamecontroller import GameController
import yaml


class GameParams:

    def __init__(self, asteroid_speed, asteroid_freq_min, asteroid_freq_max, player_speed):
        self.asteroid_speed = asteroid_speed
        self.asteroid_freq_min = asteroid_freq_min
        self.asteroid_freq_max = asteroid_freq_max
        self.player_speed = player_speed


def get_game_params(paramdata):
    if paramdata is not None:

        asteroid_speed = float(paramdata["asteroid_speed"])
        asteroid_freq_min = float(paramdata["asteroid_freq_min"])
        asteroid_freq_max = float(paramdata["asteroid_freq_max"])
        player_speed = float(paramdata["player_speed"])

        return GameParams(asteroid_speed, asteroid_freq_min, asteroid_freq_max, player_speed)

    else:
        raise Exception("Cannot load game parameters from yaml file.")


def generate_learner_params(playerdata):
    if playerdata is not None:
        model_path = str(playerdata["attributes"]["model_path"])
        learning_rate = str(playerdata["attributes"]["learning_rate"])
        is_training = bool(playerdata["attributes"]["is_training"])
        eps_min = float(playerdata["attributes"]["eps_min"])
        eps_max = float(playerdata["attributes"]["eps_max"])
        eps_decay_steps = float(playerdata["attributes"]["eps_decay_steps"])
        n_steps = float(playerdata["attributes"]["n_steps"])
        start_training_steps = int(
            playerdata["attributes"]["start_training_steps"])
        training_interval = int(playerdata["attributes"]["training_interval"])
        save_steps = float(playerdata["attributes"]["save_steps"])
        copy_steps = float(playerdata["attributes"]["copy_steps"])
        discount_rate = float(playerdata["attributes"]["discount_rate"])
        batch_size = int(playerdata["attributes"]["batch_size"])
        learnerparams = LearnerParams(is_training, eps_min, eps_max, eps_decay_steps,
                                      n_steps,
                                      start_training_steps, training_interval, save_steps, copy_steps, discount_rate, learning_rate, model_path,
                                      batch_size)

        return learnerparams
    else:
        raise Exception("Cannot load parameters from yaml file.")


class AsteroidScene(Scene):

    def __init__(self):
        super(AsteroidScene, self).__init__()

        self.fillcolor = (10, 10, 10)

    def initialize(self, config_data):

        self.game = self.add_new_game_object("gamecontroller")
        self.game.add_component(GameController)
        self.gamecontroller = self.game.get_component(GameController)
        self.add_collide_layers(0, 23)
        l, g = self.create_learner_params(config_data)
        self.learner_params = l
        self.game_params = g
        self.gamecontroller.initialize_game_params(self.game_params)
        self.gamecontroller.initialize_learner(self.learner_params)

    def create_learner_params(self, config_data):
        learn = generate_learner_params(config_data["learner"])
        game_params = get_game_params(config_data["game_params"])
        return learn, game_params

    def gamestarted(self):
        return self.started

    def reloadscene(self):

        self.gamecontroller.reset()
        self.started = True

    def reset(self):
        self.started = False

    def get_reward(self, action):
        return self.gamecontroller.calculate_score()

    def get_legal_actions(self):
        return [-1, 0, 1]

    def save_state(self):
        pass

    def load_state(self):
        pass

    def get_observation(self):
        pass

    def is_game_over(self):
        return self.gamecontroller.gameover

    def finish(self):
        pass

    def get_state(self):
        return self.gamecontroller.get_state()

    def perform_action(self, action):
        success = self.gamecontroller.force_action(action)
        return self.gamecontroller.calculate_score(action)

    def step(self, action):
        logging.info("ENV STEP ACTION: "+str(action))
        reward = self.perform_action(action)
        state = self.get_state()
        done = self.gamecontroller.gameover

        return state, reward, done
