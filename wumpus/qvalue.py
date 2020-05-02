from logic import *
from wumpus_environment import *
from wumpus_kb import *
from wumpus_planners import *
import glo
import minisat as msat
from time import clock
import sys
import pickle
from os import path

# more worlds build policy base, assuming:
#
# 4x4 gridworld, no internal walls
# grid is winnable
#
####

class QValueAgent(Explorer):
    def __init__(self, heading='east', environment=None, verbose=True):
        super(QValueAgent, self).__init__(program=self.agent_program, heading=heading, environment=environment, verbose=verbose)
        self.possible_actions = ["Forward", "TurnLeft", "TurnRight", "Shoot"]
        self.states = []
        self.actions = []
        self.scores = []
        self.wumpus_alive = 100
        self.has_gold = 0
        self.stench_array = [0] * 16
        self.breeze_array = [0] * 16
        self.qvd = QValueDictionary()

    def agent_program(self, percept):
        if percept[2]:
            self.has_gold == 100
            return "Grab"

        if self.has_gold and (self.location == self.initial_location):
            return "Climb"

        self.scores.append(self.performance_measure) # record score of previous action
        self.updateBeliefs(percept)

        state = self.makeState(percept)
        self.states.append(state) # record current state

        action_index = self.qvd.queryDictionary(state) # get best action if state already exists

        if(glo.noise and random.random() < .2): # impl action noise
            #print "uzai"
            action_index -= random.randint(1, 3)

        self.actions.append(action_index) # record chosen action
        action = self.possible_actions[action_index]
        return action

    def makeState(self, percept):
        state = [self.location[0], self.location[1], self.heading, self.has_gold, self.wumpus_alive, self.bump]
        state.extend(self.stench_array)
        state.extend(self.breeze_array)
        return tuple(state)

    def updateBeliefs(self, percept):
        if percept[4]:
            self.wumpus_alive = 0

        if percept[3]:
            self.bump = 100
        else:
            self.bump = 0

        ones = self.location[0] - 1
        fours = (self.location[1] - 1) * 4
        index = ones + fours

        if percept[0]:
            self.stench_array[index] = 1
        else:
            self.stench_array[index] = -1

        if percept[1]:
            self.breeze_array[index] = 1
        else:
            self.breeze_array[index] = -1

    def close(self):
        #print self.states
        del self.scores[0]
        self.qvd.saveDictionary(self.states, self.actions, self.scores)


# dic values correspond to [forward, turnright, turnleft, shoot]
class QValueDictionary():
    def __init__(self):
        self.filename = "qvaluedictionary.pickle"
        try:
            with open(self.filename, "rb") as file:
                self.dic = pickle.load(file)
        except:
            self.dic = {(1, 1, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0):[0, 0, 0, 0]}

    def queryDictionary(self, state):
        if state in self.dic:
            return self.dic[state].index(max(self.dic[state]))
        else:
            return random.randint(0, 3)

    def saveDictionary(self, states, actions, scores):
        previous_score = scores[-1]
        win = False
        if previous_score > 0:
            win = True

        while states != []:
            # make new entry if does not exist yet
            state = states.pop()
            action = actions.pop()
            if state not in self.dic:
                self.dic[state] = [0, 0, 0, 0]

            values = self.dic[state]
            
            #reward/punishment
            if win and previous_score > values[action]:
                values[action] = previous_score
                previous_score -= 1
            else:
                values[action] -= 1

            self.dic[state] = values

        # save to file
        with open(self.filename, "wb") as file:
            pickle.dump(self.dic, file)

def manhat(a, b):
    distance = 0
    for x, y in zip(a, b):
        distance += abs(x - y)

    return distance

def selectWithNoise(a):
    a = [x + random.uniform(-100, 100) for x in a]
    return a.index(max(a))