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
'''


class ActorCriticModel():
    def __init__(self, model_params):
        self._model_params = model_params
        self.loss_history = []
        self.model = models.Sequential(
            [
                layers.Dense(12, input_dim=7, activation='relu',
                             bias_initializer='zeros'),
                layers.Dense(16, activation='relu', bias_initializer='zeros'),
                layers.Dense(12, activation='relu', bias_initializer='zeros'),
                layers.Dense(3, activation='softmax', bias_initializer='zeros')])

        logging.info("LEARNING RATE "+str(model_params.learning_rate))
        lr = tf.cast(float(model_params.learning_rate), dtype=tf.float32)
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=lr)

        import keras.backend as K
        logging.info(K.eval(self.optimizer.lr))

    def run(self, x, batch_size=1):
        pred = self.model.predict_proba(x, batch_size=batch_size)
        # if batch_size > 1:
        #logging.info(f"predicted values : {pred[:5]}")
        return pred

    def train_step(self, inputs, labels, actions):
        x = tf.cast(inputs, tf.float32)
        with tf.GradientTape() as tape:

            logits = self.model(x, training=True)

            ohactions = tf.one_hot(actions, 3)
            qvs = tf.reduce_sum(logits * ohactions, axis=1, keepdims=True)

            loss_value = tf.reduce_mean(tf.square(labels-qvs))

            self.loss_history.append(loss_value.numpy().mean())
            grads = tape.gradient(
                loss_value, self.model.trainable_variables)

            self.optimizer.apply_gradients(
                zip(grads, self.model.trainable_variables))

    def copy(self, to_model):
        to_model.set_weights(self.model.get_weights())


class AsteroidLearner(BaseLearner):
    def __init__(self, gameobject_):
        super(AsteroidLearner, self).__init__(gameobject_)
        self.learner_params = None
        self.iteration = 0
        self.INPUT_DIMS = 7

        self.training_start = 60
        self.training_interval = 3
        self.replay_memory_size = 10000
        self.replay_memory = Memory()
        self.is_training = True
        self.checkpoint_path = None
        self.initializer = None
        self.color = 0

        # callback for gamecontroller
        self.reset_now = None

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
            logging.info("checkpoint path is " + str(self.checkpoint_path))
            # if os.path.isfile(self.checkpoint_path):
            logging.info("loading saved checkpoint")
            self.critic.model.load_weights(self.checkpoint_path)
            self.actor.model.load_weights(self.checkpoint_path)
        except:
            logging.warning("No checkout found")
            pass

    def your_turn(self):
        self.tf_update()

    def update_learner(self):
        self.iteration += 1
        # Observe and get state.
        obs, reward, done = self.env.step(None)

        logging.info("REWARD IS: "+str(reward))
        state = self.convert_state(obs)

        # add the next state to previous state, action pair, and append to memory
        if self.cached_state is not None:
            self.replay_memory.store(self.cached_state.state,
                                     self.cached_state.action, reward, state, 1.0 - done)

            # add the mirror reflection
            mirror_cs = self.convert_state(np.array([1-self.cached_state.state.flatten()[0],
                                  1-self.cached_state.state.flatten()[1],
                                  self.cached_state.state.flatten()[2],
                                  1-self.cached_state.state.flatten()[3],
                                  self.cached_state.state.flatten()[4],
                                  1-self.cached_state.state.flatten()[5],
                                  self.cached_state.state.flatten()[6]]
                                 ))
           
            mirror_action = -1 * self.cached_state.action
            mirror_s = self.convert_state(np.array([1 - state.flatten()[0],
                                 1 - state.flatten()[1],  state.flatten()[2], 1-state.flatten()[3], 
                                 state.flatten()[4], 1 - state.flatten()[5], state.flatten()[6]]
                                ))
            #logging.info(f"> {mirror_action} , {self.cached_state.action}")
            # self.replay_memory.store(mirror_cs,
            #                          mirror_action, reward, mirror_s, 1.0 - done)

            self.cached_state = None

        # finally, if done reset
        if done:
            logging.info("RESET NOW")
            self.reset_now()
            return

        q_values = self.actor.run(state)

        # get optimal action
        action = self.epsilon_greedy(
            q_values, self.iteration)  # get best action
        # evaluate best action... get the reward .
        obs, reward, done = self.env.step(action)
        # if in inference mode, don't do anything after
        # this point.
        if not self.learner_params.is_training:
            return

        next_state = self.convert_state(obs)
        self.cached_state = CachedState()
        self.cached_state.state = state
        self.cached_state.action = action

        # if before training begins or not in training interval then finish iteration here.
        if self.iteration >= self.training_start and self.iteration % self.training_interval == 0:
            self._train_network()

        # finally, if done reset
        elif done:
            #logging.info("RESET NOW")
            self.reset_now()
            return

        # copy from ciritc to actor if necessary
        if self.iteration % self.learner_params.copy_steps == 0:
            #logging.info("COPY iterations ")
            self.copy_critic_to_actor()

        # save if necessary
        if self.iteration % self.learner_params.save_steps == 0:
            self.critic.model.save_weights(self.checkpoint_path)

        if self.iteration % 1000 == 0:
            self.replay_memory.keep(1000)
        # finally, if done reset
        if done:
            logging.info("RESET NOW")
            self.reset_now()

    def _train_network(self): 
        # Critic learns -- samples memories
        sample_states, sample_action, rewards, sample_next_states, continues \
            = self.replay_memory.sample(self.learner_params.batch_size, (self.learner_params.batch_size, 7))
 
        sn = tf.reshape(sample_next_states,
                        (self.learner_params.batch_size, 7))
        next_q_values = self.actor.run(
            sn, batch_size=self.learner_params.batch_size) 
        max_next_q_values = np.max(next_q_values, axis=1, keepdims=True)
        
        # run training on samples
        y_val = rewards + self.learner_params.discount_rate * max_next_q_values
        
        self.critic.train_step(sample_states.reshape(
            self.learner_params.batch_size, 7), y_val,  tf.cast(sample_action, dtype=tf.int32))

    def _train_network2(self):
        # Critic learns -- samples memories
        sample_states, sample_actions, rewards, sample_next_states, continues = self.replay_memory.sample(
            self.learner_params.batch_size, (self.learner_params.batch_size, 7, 1))
        xv = tf.cast(sample_states.reshape(
            self.learner_params.batch_size, self.INPUT_DIMS), dtype=tf.float32)
        next_q_values = self.actor.run(xv,  self.learner_params.batch_size)
        max_next_q_values = np.max(next_q_values, axis=1, keepdims=True)

        # run training on samples
        y_val = rewards + continues * self.learner_params.discount_rate * max_next_q_values
       
        xv = tf.cast(sample_states.reshape(
            self.learner_params.batch_size, self.INPUT_DIMS), dtype=tf.float32)
      
        self.critic.train_step(sample_states.reshape(
            self.learner_params.batch_size, self.INPUT_DIMS), y_val,  tf.cast(sample_actions, dtype=tf.int32))

    def convert_state(self, obs):
        s = obs.flatten().reshape(1, self.INPUT_DIMS)
        return s

    def epsilon_greedy(self, q_values, step):
        epsilon = max(self.learner_params.eps_min, self.learner_params.eps_max - (
            self.learner_params.eps_max - self.learner_params.eps_min) * step / self.learner_params.eps_decay_steps)

        logging.info("EPSILON IS "+str(epsilon))
        logging.info("STEP IS "+str(step))
        #logging.info("TRAINING? "+str(self.learner_params.is_training))
        # logging.info(self.checkpoint_path)
        do_random = False
        if not self.learner_params.is_training:
            do_random = False
        elif rnd.uniform(0.0, 1.0) < epsilon / 1.0:
            do_random = True
        # random
        if do_random:
            action = rnd.randint(0, 2)
            return action - 1
        else: 
            args = np.argsort(q_values.flatten())
 
            i = len(args) - 1
            return args[i] - 1
