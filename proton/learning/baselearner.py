from proton.component import Component  
from proton.gametime import GameTime 
import os
import logging
import numpy as np
import random as rnd
import time
import keras
import tensorflow as tf
from tensorflow.keras import datasets, layers, models
from tensorflow import Graph  # , Session
from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.models import load_model


class Memory:
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.next_states = []
        self.isdone = []

    def store(self, state, action, reward, nextstate, done):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.next_states.append(nextstate)
        self.isdone.append(done)

    def clear(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.next_states = []
        self.isdone = []

    def keep(self, num):
        self.states = self.states[-num:]
        self.actions = self.actions[-num:]
        self.rewards = self.rewards[-num:]
        self.next_states = self.next_states[-num:]
        self.isdone = self.isdone[-num:]

    def remove(self, num):
        self.states = self.states[num:]
        self.actions = self.actions[num:]
        self.rewards = self.rewards[num:]
        self.next_states = self.next_states[num:]
        self.isdone = self.isdone[num:]

    def sample(self, batch_size, shape):
        indices = np.random.permutation(len(self.states))[:batch_size]
        batch1 = []
        batch2 = []
        batch3 = []
        batch4 = []
        batch5 = []

        for idx in indices:
            batch1.append(self.states[idx])
            batch2.append(self.actions[idx])
            batch3.append(self.rewards[idx])
            batch4.append(self.next_states[idx])
            batch5.append(self.isdone[idx])

        return (np.array(batch1).reshape(shape),
                tf.cast(np.array(batch2), tf.float32),
                tf.cast(np.array(batch3).reshape(-1, 1), tf.float32),
                tf.cast(np.array(batch4), tf.float32),
                tf.cast(np.array(batch5).reshape(-1, 1), tf.float32))

class CachedState:
    def __init__(self):
        self.state = None
        self.action = None
        self.reward = None
        self.next_state = None
        self.can_continue = None
        
class BaseLearner(Component):
    """
    Base Learner class is used as the base class for learner components.
    Learner components should be attached to a game object, and need
    a reference to the learning environment (self.env).
    """

    def __init__(self, gameobject_):
        super(BaseLearner, self).__init__(gameobject_)

        self.checkpoint_path = ""
        self.verboseOutput = False
        self.env = None

    def set_env(self, env):
        self.env = env

    def restart(self):
        pass

    def stop(self):
        pass
