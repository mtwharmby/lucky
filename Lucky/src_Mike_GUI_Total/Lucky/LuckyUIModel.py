'''
Created on 3 Nov 2015

@author: wnm24546
'''

class MainWindowModel():

    def __init__(self):
        self.runEnabled = True
        self.stopEnabled = False
        self.mode = (1, 0) #Current mode
        self._mode = self.mode #Old mode
    
    def runLuckyCalcs(self):
        self.runEnabled = False
        self.stopEnabled = True
    
    def stopLuckyCalcs(self):
        self.runEnabled = True
        self.stopEnabled = False
    
    def checkMode(self):
        if (sum(self.mode) == 1):
            self._mode = self.mode
        else:
            raise AttributeError("Invalid mode setting")
        
