from logic import *
from wumpus_environment import *
from wumpus_kb import *
from wumpus_planners import *
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

class MonteCarloAgent(Explorer):
    def __init__(self, heading='east', environment=None, verbose=True):
        super(MonteCarloAgent, self).__init__(program=self.agent_program, heading=heading, environment=environment, verbose=verbose)
        self.possible_actions = ["Forward", "TurnLeft", "TurnRight", "Shoot"]
        self.states = []
        self.actions = []
        self.scores = []
        self.wumpus_alive = 100
        self.has_gold = 0
        self.stench_array = [0] * 16
        self.breeze_array = [0] * 16
        self.mcd = MonteCarloDictionary()

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

        action_index = self.mcd.queryDictionary(state) # get best action from nearest state
        self.actions.append(action_index) # record chosen action
        action = self.possible_actions[action_index]
        return action

    def makeState(self, percept):
        state = [self.location[0], self.location[1], self.heading, self.has_gold, self.wumpus_alive]
        state.extend(self.stench_array)
        state.extend(self.breeze_array)
        return tuple(state)

    def updateBeliefs(self, percept):
        if percept[4]:
            self.wumpus_alive = 0

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
        self.mcd.saveDictionary(self.states, self.actions, self.scores)


# dic values correspond to [forward, turnright, turnleft, shoot]
class MonteCarloDictionary():
    def __init__(self):
        self.filename = "montecarlodictionary.pickle"
        try:
            with open(self.filename, "rb") as file:
                self.dic = pickle.load(file)
        except:
            self.dic = {(1, 1, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0):[0, 0, 0, 0]}

    def queryDictionary(self, state):
        distance, key = min([(manhat(state, key), key) for key in self.dic.keys()])
        return selectWithNoise(self.dic[key])
        #return self.dic[key].index(max(addNoise(self.dic[key])))

    def saveDictionary(self, states, actions, scores):
        final_score = scores[-1]
        previous_score = 0

        for state, action, score in zip(states, actions, scores):
            # make new entry if does not exist yet
            if state not in self.dic:
                self.dic[state] = [0, 0, 0, 0]

            delta = score - previous_score
            previous_score = score

            # update entry
            values = self.dic[state]
            values[action] += delta + final_score/75

            # cap preference
            if (action == 1 or action == 2) and values[action] > 100:
               values[action] = 100

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