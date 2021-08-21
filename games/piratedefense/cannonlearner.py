import os
import random as rnd

import numpy as np
import tensorflow as tf
#from tensorflow.contrib.layers import fully_connected

from collections import deque
from proton.gametime import GameTime
from proton.protonsingleton import ProtonSingleton
from proton.learning.baselearner import BaseLearner


class CannonLearner(BaseLearner):
    def __init__(self, gameobject_):
        super(CannonLearner, self).__init__(gameobject_)
        self.learner_params = None
        self.iteration = 0
        self.batch_size = 50
        self.hidden_activation = tf.nn.relu
        self.output_size = 4

        self.eps_min = 0.05
        self.eps_max = 1.0
        self.eps_decay_steps = 5000
        self.n_steps = 1000000
        self.training_start = 50
        self.training_interval = 3
        self.save_steps = 5
        self.copy_steps = 5
        self.discount_rate = 0.95
        self.training_start = 50
        self.training_interval = 3
        self.checkpoint_path = "./games/piratedefense/resources/tf/pirate_model0001"
        self.initializer = tf.contrib.layers.variance_scaling_initializer()
        self.color = 0

        # learning init
        self.session = tf.Session()
        self.done = False
        self.success = True
        self.episodetime = []
        self.starttime = 0
        self.timer = 0

    def generate_network(self, X_state, scope):
        """
        Input to outputs:
        3 -> 9 -> 8 -> 3
        :param X_state: the state to input
        :param scope:
        :return:
        """
        prev_layer = X_state
        with tf.variable_scope(scope) as scope:
            layer1 = fully_connected(prev_layer, num_outputs=20,
                                     activation_fn=tf.nn.sigmoid, weights_initializer=self.initializer)
            prev_layer = layer1
            layer2 = fully_connected(prev_layer, num_outputs=18,
                                     activation_fn=tf.nn.sigmoid, weights_initializer=self.initializer)
            prev_layer = layer2
            outputs = fully_connected(prev_layer, self.output_size, activation_fn=tf.nn.softmax,
                                      weights_initializer=self.initializer)

            trainable_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=scope.name)
            trainable_vars_by_name = {var.name[len(scope.name):]: var for var in trainable_vars}
            return outputs, trainable_vars_by_name

    def start(self):
        # crete a network
        self.X_state = tf.placeholder(tf.float32, shape=[None, 11])
        self.actor_q_values, self.actor_vars = self.generate_network(self.X_state, scope="q_networks/actor")
        self.critic_q_values, self.critic_vars = self.generate_network(self.X_state, scope="q_networks/critic")
        self.copy_ops = [actor_var.assign(self.critic_vars[var_name]) for var_name, actor_var in
                         self.actor_vars.items()]
        self.copy_critic_to_actor = tf.group(*self.copy_ops)
        self.X_action = tf.placeholder(tf.int32, shape=[None])
        self.q_value = tf.reduce_sum(self.critic_q_values * tf.one_hot(self.X_action, self.output_size), axis=1,
                                     keep_dims=True)
        self.replay_memory_size = 1000
        self.replay_memory = deque([], maxlen=self.replay_memory_size)

        self.learning_rate = 0.01
        self.y = tf.placeholder(tf.float32, shape=[None, 1])
        self.cost = tf.reduce_mean(tf.square(self.y - self.q_value))
        self.global_step = tf.Variable(0, trainable=False, name='global_step')
        self.optimizer = tf.train.AdamOptimizer(self.learning_rate)
        self.training_op = self.optimizer.minimize(self.cost, global_step=self.global_step)
        self.init = tf.global_variables_initializer()
        self.saver = tf.train.Saver()
        self.sess = None
        self.sess = tf.Session() 
        if os.path.isfile(self.checkpoint_path + ".meta"): 
            self.saver.restore(self.sess, self.checkpoint_path)
        else:
            self.init.run(session=self.sess)

    def restart(self):
        self.iteration = 0
        self.done = False
        self.copy_critic_to_actor.run(session=self.sess)
        self.saver.save(self.sess, self.checkpoint_path)

        self.env.reload_scene()

        self.episodetime.append(ProtonSingleton(GameTime).time() - self.starttime) 
        s = sum(self.episodetime[-10:])
        c = len(self.episodetime[-10:]) 

    def update(self):
        self.done = False
        self.timer += ProtonSingleton(GameTime).dt()
        if self.timer < 0.1:
            return
        self.timer = 0.0
        step = self.global_step.eval(session=self.sess)
        self.iteration += 1

        obs, reward, self.done, self.success = self.env.step(None)  # step one
        state = self.convert_state(obs)  # get state
        if self.done:
            self.restart()
            return

        q_values = self.actor_q_values.eval(session=self.sess, feed_dict={self.X_state: state})  # evaluate state
        action = self.epsilon_greedy(q_values, step)  # get best action
        obs, reward, self.done, self.success = self.env.step(action - 1)  # perform chosen action
        if self.done:
            self.restart()
            return
        if step >= self.n_steps:
            return

        next_state = self.convert_state(obs)  # evaluate state
        self.replay_memory.append((state, action, reward, next_state, 1.0 - self.done))  # append to memory
        if self.iteration < self.training_start or self.iteration % self.training_interval != 0:
            return

        # =================================== CRITIC LEARNING ================================
        X_state_val, X_action_val, rewards, X_next_state_val, continues = (
            self.sample_memories(self.batch_size)
        )

        next_q_values = self.actor_q_values.eval(session=self.sess,
                                                 feed_dict={self.X_state: X_next_state_val.reshape(self.batch_size, 11)})
        max_next_q_values = np.max(next_q_values, axis=1, keepdims=True)
        y_val = rewards + continues * self.discount_rate * max_next_q_values

        self.training_op.run(session=self.sess,
                             feed_dict={self.X_state: X_state_val.reshape(self.batch_size, 11), self.X_action: X_action_val,
                                        self.y: y_val})

        if step % self.copy_steps == 0:
            self.copy_critic_to_actor.run(session=self.sess)

        if step % self.save_steps == 0:
            self.saver.save(self.sess, self.checkpoint_path)

    def sample_memories(self, batch_size):
        indices = np.random.permutation(len(self.replay_memory))[:batch_size]
        cols = [[], [], [], [], []]
        for idx in indices:
            memory = self.replay_memory[idx]
            for col, value in zip(cols, memory):
                col.append(value)
        cols = [np.array(col) for col in cols] 
        return cols[0], cols[1], cols[2].reshape(-1, 1), cols[3], cols[4].reshape(-1, 1)

    def epsilon_greedy(self, q_values, step):
        epsilon = max(self.eps_min, self.eps_max - (self.eps_max - self.eps_min) * step / self.eps_decay_steps)
        self.epsilon = epsilon
        if rnd.uniform(0.0, 1.0) < epsilon:
            return rnd.randint(0, self.output_size - 1)
        else: 
            return np.argmax(q_values)

    def convert_state(self, obs):
        """
        Reshape the Observed state (array of length 3) to an array of 1x3.
        inputs:
        :param obs: observation (state)
        :return: reshaped observation
        """
        s = obs.flatten().reshape(1, 11) 
        return s


