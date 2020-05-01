#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 21:34:34 2020

@author: omkar
"""

from wumpus_environment import Explorer
import pickle
import sys
import random
#from time import clock
#import sys
#import utils

class QLearningAgent(Explorer):
    def __init__(self, heading='east', environment=None, verbose=True):
        super(QLearningAgent, self).__init__(self.agent_program, heading, environment, verbose)
        self.heading = heading
        self.QValues = {}
        self.values = []
        self.step = 0
        self.epsilon = 0.05
        self.gamma = 0.8
        self.alpha = 0.2
        self.discount = 0.9
        self.flag = True
        self.action_list = ['TurnRight', 'TurnLeft', 'Forward', 'Climb', 'Shoot', 'Stop', 'Grab']
        self.prev_action = None
        
    
    def reset(self):
        super(QLearningAgent, self).reset()
        self.step = 0
        self.values = []
        self.QValues = {}
        self.flag = True
        
        
    def agent_program(self, percept):
        action_list = ['TurnRight', 'TurnLeft', 'Forward', 'Climb', 'Shoot', 'Stop', 'Grab']
        self.values.append(self.performance_measure)
#        if self.flag:
#            self.run_iterations(percept, self.initial_location, action_list)
        state = (tuple(percept), self.location)
        for action in action_list:
            self.add_state(state, action)
        self.update_q_values(state)
        return_act = self.choose_action(state)
        
        if self.verbose:
            print("Q-Value iteration : step no. = {0}".format(self.step))
        print("Choosing action : {0}".format(self.QValues.keys()[1][1]))
        self.prev_action = return_act
        return return_act
        
    def add_state(self, state, action):
        file_name = 'q_value_dict.pickle'
        self.QValues = self.load_q_values()
        if (state, action) not in self.QValues.keys():
            self.QValues[(state, action)] = 0
        try:
            with open(file_name, "wb") as file:
                pickle.dump(self.QValues, file)
        except:
            print("Uanble to write to Dictionary")
            sys.exit(-1)
        
            
    def load_q_values(self):
        file_name = 'q_value_dict.pickle'
        try:
            with open(file_name, "rb") as file:
                self.QValues = pickle.load(file)
        except:
            print("Dictionary cannot be opened")
            sys.exit(-1)
            
    def update_q_values(self, state):
        updated_val = 0
        legal_actions = self.get_legal_actions(state)
        q_max = max([ self.QValue(state, action) for action in legal_actions])
        updated_val = self.values[-1] + self.discount * q_max
        self.QValues[(state, self.prev_action)] = self.QValues[(state, self.prev_action)] + self.alpha * (updated_val - self.QValues[(state, self.prev_action)])
        self.write_q_values(self.QValue)
            
        
    def get_legal_actions(self, state):
        res = self.action_list.copy()
        if self.location != self.initial_location:
            res.remove('Climb')
        return res
        
    def choose_action(self):
        choice = random.randint(1,10)
        if choice > 2:
            return self.QValues.keys()[0][1]
        else:
            return random.choice(self.action_list.copy().remove(self.QValues.keys()[0][1]))
        
    def write_q_values(q_val):
        file_name = 'q_value_dict.pickle'
        try:
            with open(file_name, "wb") as file:
                pickle.dump(q_val, file)
        except:
            print("Uanble to write to Dictionary")
            sys.exit(-1)
        
        