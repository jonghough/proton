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
    def __init__(self, model_params):
        self._model_params = model_params
        self.loss_history = []
        self.model = models.Sequential(
            [
                layers.Dense(75, input_dim=64, activation='relu',
                             use_bias=True, bias_initializer='zeros'),
                layers.Dense(80, activation='relu', use_bias=True,
                             bias_initializer='zeros'),
                # layers.Dense(68, activation='relu', use_bias=True,
                #              bias_initializer='zeros'),
                layers.Dense(64, activation='softmax', use_bias=True, bias_initializer='zeros')])
        logging.info("LEARNING RATE "+str(model_params.learning_rate))
        lr = tf.cast(float(model_params.learning_rate), dtype=tf.float32)
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=lr)

    def run(self, x, batch_size=1):
        pred = self.model.predict_proba(x, batch_size=batch_size)
        #logging.info(f"predicted values : {pred}")
        return pred

    def train_step(self, inputs, labels, actions):
        '''
https://keras.io/api/losses/probabilistic_losses/#categoricalcrossentropy-class
        '''
        x = tf.cast(inputs, tf.float32)
        with tf.GradientTape() as tape:

            logits = self.model(x, training=True)
            ohactions = tf.one_hot(actions, 64)  
            #logging.info(f"ohactions {ohactions[0]}")

            #cce = tf.keras.losses.CategoricalCrossentropy()
            #loss = cce(ohlabels, logits *ohactions)
            #logging.info(f"logits {logits[0]}")
            #logging.info(f"logits[0] {logits[0]}")
             
            qvs = tf.reduce_sum(logits * ohactions, axis=1, keepdims=True)
            #logging.info(f"qvs: {(logits * ohactions)[0]}")
            #logging.info(f"labels: {labels}")
            loss_value = tf.reduce_mean(tf.square(labels-qvs), axis=1)
            #logging.info(f"LOSS VALUE {loss_value}")
            self.loss_history.append(loss_value.numpy().mean())
            #logging.info(f"loss h {self.loss_history[-10:]}")
            grads = tape.gradient(
                loss_value, self.model.trainable_variables)

            self.optimizer.apply_gradients(
                zip(grads, self.model.trainable_variables))

    def copy(self, to_model): 
        #logging.info(f"Weights {self.model.get_weights()[0]}")
        to_model.set_weights(self.model.get_weights())


class OthelloLearner(BaseLearner):
    def __init__(self, gameobject_):
        super(OthelloLearner, self).__init__(gameobject_)
        self.learner_params = None
        self.iteration = 0
        self.replay_memory_size = 10000
        self.replay_memory = Memory()
        self.is_training = True
        self.checkpoint_path = None
        self.initializer = None
        self.color = 0

        # cache state
        self.cached_state = None

    def train_critic(self, input, labels):
        predictions = self.critic(input, training=True)

    def generate_network(self, params):
        self.actor = ActorCriticModel(params)
        self.critic = ActorCriticModel(params)

    def copy_critic_to_actor(self):
        self.critic.copy(self.actor.model)

    def save_state(self):
        pass

    def initialize(self, learner_params):
        self.learner_params = learner_params
        self.generate_network(self.learner_params)
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
        obs, reward, done = self.env.step(None, self.color)

        state = self.convert_state(obs)
        # add the next state to previous state, action pair, and append to memory
        if self.cached_state is not None:
            self.replay_memory.store(self.cached_state.state,
                                     self.cached_state.action, reward, state, 1.0 - done)

            self.cached_state = None

        self.done = done
        if self.done:
            return
            
        q_values = self.actor.run(state, batch_size=1)

        # logging.info(q_values)

        def on_forbidden(move): 
            pass 
        action = self.epsilon_greedy(
            q_values, self.iteration, on_forbidden)   
        obs, reward, done = self.env.step(action, self.color) 

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
        if self.iteration > self.learner_params.start_training_steps and self.iteration % self.learner_params.training_interval == 0:
            self._train_network()

        # copy from critic to actor if necessary
        if self.iteration % self.learner_params.copy_steps == 0:
            logging.info("copy weights ")
            self.copy_critic_to_actor()

        # save if necessary
        if self.iteration % self.learner_params.save_steps == 0:
            logging.info("save model ")
            self.critic.model.save_weights(self.checkpoint_path)

    def _train_network(self):  
        sample_states, sample_action, rewards, sample_next_states, continues \
            = self.replay_memory.sample(self.learner_params.batch_size, (self.learner_params.batch_size, 64))
   
        sn = tf.reshape(sample_next_states, (self.learner_params.batch_size, 64))
        next_q_values = self.actor.run(
            sn, batch_size=self.learner_params.batch_size) 
        max_next_q_values = np.max(next_q_values, axis=1, keepdims=True) 

        # run training on samples
        y_val = rewards + self.learner_params.discount_rate * max_next_q_values 
        self.critic.train_step(sample_states.reshape(
            self.learner_params.batch_size, 64), y_val,  tf.cast(sample_action, dtype=tf.int32))

    def convert_state(self, obs):
        s = obs.flatten().reshape(1, 64)
        return s

    def epsilon_greedy(self, q_values, step, on_forbidden=None):
        epsilon = max(self.learner_params.eps_min, self.learner_params.eps_max - (
            self.learner_params.eps_max - self.learner_params.eps_min) * step / self.learner_params.eps_decay_steps)

        logging.info(f"EPSILON: {epsilon}")
        logging.info(f"STEP: {step}")
        do_random = False
        if not self.learner_params.is_training:
            if rnd.uniform(0.0, 1.0) < 0.01:
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
