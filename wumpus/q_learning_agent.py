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
import copy
#from time import clock
#import sys
#import utils

class QLearningAgent(Explorer):
    def __init__(self, heading='east', environment=None, verbose=True):
        super(QLearningAgent, self).__init__(self.agent_program, heading, environment, verbose)
        self.heading = heading
        self.QValues = {}
        self.score = 0
        self.step = 0
        self.alpha = 0.2
        self.discount = 0.9
        self.flag = True
#        self.action_list = ['TurnRight', 'TurnLeft', 'Forward', 'Climb', 'Shoot', 'Stop', 'Grab']
        self.action_list = ['TurnRight', 'TurnLeft', 'Forward', 'Grab', 'Climb']
        self.prev_action = None
        self.prev_state = None
        
    
#    def reset(self):
#        super(QLearningAgent, self).reset()
#        self.step = 0
#        self.values = []
#        self.QValues = {}
#        self.flag = True
#        self.write_q_values(self.QValues)
#        
        
    def agent_program(self, percept):
#        self.values.append(self.performance_measure)
        if percept[2] and self.location == self.initial_location:
            return 'Climb'
        state = (tuple(percept), self.location)
        self.load_q_values()
        for action in self.action_list:
            self.add_state(state, action)
        self.write_q_values(self.QValues)
        self.update_q_values(state)
        return_act = self.choose_action(state)
        
        if self.verbose:
            print("Q-Value iteration : step no. = {0}".format(self.step))
        print("Choosing action : {0}".format(return_act))
        self.prev_action = return_act
        self.prev_state = state
        self.score = self.performance_measure
        self.step+=1
        return return_act
        
    def add_state(self, state, action):
        if (state, action) not in self.QValues.keys():
            self.QValues[(state, action)] = 0
            
    def load_q_values(self):
        file_name = 'q_value_dict.pickle'
        try:
            with open(file_name, "rb") as file:
                self.QValues = pickle.load(file)
        except:
            print("Dictionary cannot be opened")
            self.write_q_values(self.QValues)
        if self.QValues == None:
            self.QValues = {}
            
    def update_q_values(self, state):
        if self.prev_state == None and self.prev_action == None:
            return
        updated_val = 0
#        legal_actions = self.get_legal_actions(state)
        q_max = max([ self.QValues[(state, action)] for action in self.action_list])
        updated_val = self.get_reward() + self.discount * q_max
        self.QValues[(self.prev_state, self.prev_action)] = self.QValues[(self.prev_state, self.prev_action)] + self.alpha * (updated_val - self.QValues[(self.prev_state, self.prev_action)])
        self.write_q_values(self.QValues)
            
        
    def get_legal_actions(self, state):
        res = self.action_list.copy()
        if self.location != self.initial_location:
            res.remove('Climb')
        return res
        
    def choose_action(self, state):
        choice = random.randint(1,10)
        key_list = [s for s, a in self.QValues.items() if s[0] == state]
        max_val_list = [(self.QValues[key], key) for key in key_list]
        max_val_list = sorted(max_val_list, key = lambda x:x[0])
        if choice > 2:
            return max_val_list[-1][1][1]
        else:
            list_copy = ['TurnRight', 'TurnLeft', 'Forward', 'Grab', 'Climb']
            list_copy.remove(max_val_list[-1][1][1])
            return random.choice(list_copy)
        
    def write_q_values(self,q_val):
        file_name = 'q_value_dict.pickle'
        try:
            with open(file_name, "wb") as file:
                pickle.dump(q_val, file)
        except:
            print("Uanble to write to Dictionary")
            sys.exit(-1)
        
    def get_reward(self):
        return self.performance_measure - self.score
        