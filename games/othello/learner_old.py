from collections import deque
from proton.component import Component
from proton.gametime import GameTime
from proton.learning.baselearner import BaseLearner
from proton.learning.baselearner import Memory
from proton.learning.baselearner import CachedState
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
'''
The process

1. create Actor model, Critic model
2. actor model gets state, calculates best move.
3. actor model gets result of move, and next state.
4. the result + state are put in memory
5. memory is sampled by critic. learning proceeds. (1 iteration)
6. move critic model to actor.


see: 
https://www.ai.rug.nl/~mwiering/GROUP/ARTICLES/paper-othello.pdf

'''


class ActorCriticModel():
    def __init__(self):
        self.loss_history = []
        self.model = models.Sequential(
            [layers.Conv2D(20, (3, 3), activation='relu', input_shape=(8, 8, 1), bias_initializer='zeros'),
                layers.MaxPooling2D((3, 3)),
                layers.Conv2D(20, (2, 2), activation='relu',
                              bias_initializer='zeros'),
                layers.Flatten(), 
                layers.Dense(70, activation='relu', bias_initializer='zeros'),
                layers.Dense(66, activation='relu', bias_initializer='zeros'),
                layers.Dense(64, activation='softmax', bias_initializer='zeros')])

        self.optimizer = tf.keras.optimizers.Adam()

    def run(self, x, batch_size=1):
        pred = self.model.predict(x, batch_size=batch_size, steps=1) 
        return pred

    def train_step(self, inputs, labels, actions):
        x = tf.cast(inputs, tf.float32)
        with tf.GradientTape() as tape:

            logits = self.model(x, training=True)

            ohactions = tf.one_hot(actions, 64)
            qvs = tf.reduce_sum(logits * ohactions, axis=1, keepdims=True)

            loss_value = tf.reduce_mean(tf.square(labels-qvs))

            self.loss_history.append(loss_value.numpy().mean())
            grads = tape.gradient(
                loss_value, self.model.trainable_variables)

            self.optimizer.apply_gradients(
                zip(grads, self.model.trainable_variables))

    def copy(self, to_model):
        to_model.set_weights(self.model.get_weights())


class OthelloLearner(BaseLearner):
    def __init__(self, gameobject_):
        super(OthelloLearner, self).__init__(gameobject_)
        self.learner_params = None
        self.iteration = 0

        self.training_start = 60
        self.training_interval = 3
        self.replay_memory_size = 10000
        self.replay_memory = Memory()
        self.is_training = True
        self.checkpoint_path = None
        self.initializer = None
        self.color = 0
        self.generate_network()

        # cache state
        self.cached_state = None

    def train_critic(self, input, labels):
        predictions = self.critic(input, training=True)

    def generate_network(self ): 
        self.actor = ActorCriticModel()
        self.critic = ActorCriticModel()

    def copy_critic_to_actor(self):
        self.critic.copy(self.actor.model)

    def save_state(self):
        pass

    def initialize(self, learner_params):
        self.learner_params = learner_params
        self.checkpoint_path = learner_params.model_path
        try:
            logging.info(f"checkpoint path is {self.checkpoint_path}")
            logging.info("loading saved checkpoint")
            self.critic.model.load_weights(self.checkpoint_path)
            self.actor.model.load_weights(self.checkpoint_path)
        except:
            logging.warning("No checkpoint found.")

    def reset(self): 
        self.done = False 
    
    def reset_with_reward(self, obs, reward): 
        if True or self.done:
            self.done = False 
            state = self.convert_state(obs)
            logging.info(f">>> reward after end game: {reward}")
            if self.cached_state is not None:
                self.replay_memory.store(self.cached_state.state,
                                     self.cached_state.action, reward, state, True)
            
                self.cached_state = None
        else:
            logging.info("game not done.")

    def your_turn(self):
        self.tf_update()

    def tf_update(self):
        self.iteration += 1
        # Observe and get state.
        obs, reward, done, success = self.env.step(None, self.color)

        state = self.convert_state(obs)
        # add the next state to previous state, action pair, and append to memory
        if self.cached_state is not None:
            self.replay_memory.store(self.cached_state.state,
                                     self.cached_state.action, reward, state, 1.0 - done)
            
            self.cached_state = None

        self.done = done
        if self.done:
            return 
        q_values = self.actor.run(state)
       
        

        def on_forbidden(move):
           # logging.info(f"forbidden {move}")
            #self.replay_memory.store(state, move, -1, state, 1.0 - done)
            pass 
        # get optimal action
        action = self.epsilon_greedy(
            q_values, self.iteration, on_forbidden)  # get best action
        # evaluate best action... get the reward .
        obs, reward, done, success = self.env.step(action, self.color)
        logging.info(f">>> reward after action: {reward}")
        

        next_state = self.convert_state(obs)
        self.cached_state = CachedState()
        self.cached_state.state = state
        self.cached_state.action = action

        # get rid of old samples
        if self.iteration % 1000 == 0:
            self.replay_memory.keep(1000)

        # if in inference mode, don't do anything after
        # this point.
        if not self.learner_params.is_training:
            return
 
        self.replay_memory.store(state, action, reward, next_state, 1.0 - done)

        # if before training begins or not in training interval then finish iteration here.
        if self.iteration > self.training_start and self.iteration % self.training_interval == 0:
            self._train_network()

        # copy from ciritc to actor if necessary
        if self.iteration % self.learner_params.copy_steps == 0:
            logging.info("copy weights ")
            self.copy_critic_to_actor()

        # save if necessary
        if self.iteration % self.learner_params.save_steps == 0:
            logging.info("save model ")
            self.critic.model.save_weights(self.checkpoint_path)

    def _train_network(self):
        '''
            Train the critic network
        '''

        # Critic learns -- samples memories
        sample_states, sample_action, rewards, sample_next_states, continues = self.replay_memory.sample(
            self.learner_params.batch_size, (self.learner_params.batch_size, 8, 8, 1))
    
        next_q_values = self.actor.run(sample_states)
        max_next_q_values = np.max(next_q_values, axis=1, keepdims=True)

        # run training on samples
        y_val = rewards + self.learner_params.discount_rate * max_next_q_values
       
        xv = tf.cast(sample_states.reshape(
            self.learner_params.batch_size, 8, 8, 1), dtype=tf.float32) 
        self.critic.train_step(sample_states.reshape(
            self.learner_params.batch_size, 8, 8, 1), y_val,  tf.cast(sample_action, dtype=tf.int32))


    def convert_state(self, obs):
        s = obs.flatten().reshape(1, 8, 8, 1)
        return s

    def epsilon_greedy(self, q_values, step, on_forbidden=None):
        epsilon = max(self.learner_params.eps_min, self.learner_params.eps_max - (
            self.learner_params.eps_max - self.learner_params.eps_min) * step / self.learner_params.eps_decay_steps)

        logging.info(f"EPSILON: {epsilon}")
        logging.info(f"STEP: {step}") 
        do_random = False
        if not self.learner_params.is_training:
            if rnd.uniform(0.0, 1.0) < 0.15:
                do_random = True
        elif rnd.uniform(0.0, 1.0) < epsilon / 1.0:
            do_random = True
        # random
        if do_random:
            action = rnd.randint(0, 63)
            while not self.env.is_legal_action(action, self.color):
                action = rnd.randint(0, 63)
            logging.info(f"get the legal action(RAND) {action}")
            return action
        else:
            args = np.argsort(q_values.flatten())
            i = len(args) - 1
            while True:
                if self.env.is_legal_action(args[i], self.color):
                    logging.info(f"get the legal action(SORTED) {args[i]}")
                    return args[i]
                else:
                    if on_forbidden is not None:
                        on_forbidden(args[i])
                    i -= 1
                if i < 0:
                    break
            return None  # should never be reached
