'''
Created on 3 Feb 2016

@author: wnm24546
'''

from Lucky.DataModel import MainData
from Lucky.MPStates import State

class MockMainPresenter(object):
    def __init__(self):
        self.dataModel = MainData()
        self.calcServ = MockCalcServ()
    
    def getModeTransition(self):
        return State.EVENTS.LIVE

class MockCalcServ(object):
    def createCalcs(self, dM):
        pass