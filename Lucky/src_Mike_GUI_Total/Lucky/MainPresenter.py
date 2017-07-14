'''
Created on 5 Nov 2015

@author: wnm24546
'''

import copy, os, re

from Lucky.MPStates import State
from Lucky.DataModel import (CalibrationConfigData, MainData)
from Lucky.LuckyExceptions import BadModelStateException, IllegalArgumentException
from Lucky.Calculations import CalculationService

class AllPresenter(object):
    def __init__(self, dM = None):
        super(AllPresenter, self).__init__()
        
    def isValidPath(self, uiText, dirPath=False):
        return (dirPath and os.path.isdir(uiText)) or (not dirPath and os.path.isfile(uiText))
    
    def isValidInt(self, uiNum):
        try:
            int(uiNum)
            return True
        except ValueError:
            return False
    
    def isValidFloat(self, uiNum):
        try:
            float(uiNum)
            return True
        except ValueError:
            return False

class MainPresenter(AllPresenter):
    def __init__(self, dM = None):
        #Create the data model and the state machine
        if dM == None:
            self.dataModel = MainData()
        else:
            self.dataModel = dM
        self.calcServ = CalculationService(self)
        
        self.stateMach = StateMachine(self)
        
    def runTrigger(self):
        #Start a new calculation thread and kick off the calcs
        self.stateMach.changeState(State.EVENTS.RUN)
        self.calcServ.createCalcs(self.dataModel)
    
    def stopTrigger(self):
        #Kill the calculation thread
        self.stateMach.changeState(State.EVENTS.STOP)
        self.calcServ.disposePlots()
    
    def dataChangeTrigger(self, noData=False):
        if noData:
            dataValid = not self.dataModel.allDataPresent
        else:
            dataValid = self.isDataValid()
        
        if dataValid:
            event = State.EVENTS.DATAGOOD
        else:
            event = State.EVENTS.DATABAD
        self.stateMach.changeState(event)
    
    def setModeTrigger(self, uiData):
        self.stateMach.changeState(self.getModeTransition(uiData))
        #No return as this is a radio button option
        
        print str(self.stateMach.getStateName())
    
    def setCalibTypeTrigger(self, uiData):
        if sum(uiData) != 1:
            raise BadModelStateException("Only one calibration option can be selected")
        self.dataModel.calibType = uiData
        #No return as this is a radio button option
    
    def changeDataDirTrigger(self, uiText):
        self.dataModel.dataDir = str(uiText)
        self.dataModel.calibConfigData.calibDir = str(uiText)
        if uiText == '':
            self.dataModel.dataValid['dataDir'] = False
            return True
        elif self.isValidPath(uiText, dirPath=True):
            self.dataModel.dataValid['dataDir'] = True
            return True
        else:
            self.dataModel.dataValid['dataDir'] = False
            return False
    
    def changeIntegrationValueTrigger(self, uiText):
        if uiText == '':
            return False
        elif self.isValidInt(uiText):
            return True
        else:
            return False
    
    def invalidateIntegration(self):
        self.dataModel.dataValid['integrationConf'] = False
    
    def changeIntegrationConfigTrigger(self, uiNumbs):
        intUINumbs = [int(val) for val in uiNumbs]
        
        self.dataModel.integrationConf = intUINumbs
        if ((intUINumbs[0] < intUINumbs[1]) and (intUINumbs[2] < (intUINumbs[1] - intUINumbs[0]))):
            self.dataModel.dataValid['integrationConf'] = True
            return True
        else:
            self.dataModel.dataValid['integrationConf'] = False
            return False
    
    def calibConfigUpdateTrigger(self, calibConfig, validity):
        self.dataModel.calibConfigData = calibConfig
        self.dataModel.dataValid['calibConfig'] = validity
        
    def getUSDSFileParts(self, usdsIndex):
        #Regular expression to match file name of the format:
        #    A_#.txt
        rePatt = re.compile("([a-zA-Z]+)(_+)([0-9]+)(\.txt$)")
        filePath = os.path.basename(self.dataModel.usdsPair[usdsIndex])
        filePathParts = list(rePatt.match(filePath).groups())
        return filePathParts
    
    def changeUSDSPairTrigger(self, inc=False, dec=False, dsFile=None, usFile=None):
        #Catch malformed args
        if (inc and dec) or ((inc or dec) and (dsFile != None or usFile != None)):
            raise IllegalArgumentException("Cannot inc/decrement together and/or change filenames")
        
        if dsFile != None:
            dsFile = str(dsFile)
            try:
                dsNewPath = os.path.join(self.dataModel.dataDir, dsFile)
            except:
                return False
            self.dataModel.usdsPair[0] = dsNewPath
            if dsFile == '':
                self.dataModel.dataValid['dsFile'] = False
                return True
            elif self.isValidPath(dsNewPath, False):
                self.dataModel.dataValid['dsFile'] = True
                return True
            else:
                self.dataModel.dataValid['dsFile'] = False
                return False
        if usFile != None:
            usFile = str(usFile)
            try:
                usNewPath = os.path.join(self.dataModel.dataDir, usFile)
            except:
                return False
            self.dataModel.usdsPair[1] = usNewPath
            if usFile == '':
                self.dataModel.dataValid['usFile'] = False
                return True
            elif self.isValidPath(usNewPath, False):
                self.dataModel.dataValid['usFile'] = True
                return True
            else:
                self.dataModel.dataValid['usFile'] = False
                return False
        
        if inc or dec:
            def shiftFileName(usdsIndex, shiftVal):
                filePathParts = self.getUSDSFileParts(usdsIndex)
                fileNr = int(filePathParts[2])
                newFileNr = fileNr + shiftVal
                if newFileNr < 0: #TODO This too is ugliness in python format
                    return None
                else:
                    filePathParts[2] = '{0:02d}'.format(fileNr + shiftVal)
                return ''.join(filePathParts)
            
            newUSDSPair = ['', '']
            try:
                for i in range(2):
                    if dec:
                        newUSDSPair[i] = shiftFileName(i, -2)
                    if inc:
                        newUSDSPair[i] = shiftFileName(i, 2)
                    if (newUSDSPair[i] == None):
                        return False
                    newUSDSPair[i] = os.path.join(self.dataModel.dataDir, newUSDSPair[i])
                    
            except:
                return False

            self.dataModel.usdsPair = newUSDSPair
            
            #If calculations have been created update the existing ones.
            if "Stoppable" in self.getSMStateName():
                self.calcServ.updateCalcs()
            
            return True #This should just be ignored...
    
    def dsLTEqualusFile(self):
        
        if any('' in usds for usds in self.dataModel.usdsPair):
            return False
        
        try:
            dsFileParts = self.getUSDSFileParts(0)
            usFileParts = self.getUSDSFileParts(1)
        except:
            return False
        if (dsFileParts == usFileParts) or (int(dsFileParts[2]) >= int(usFileParts[2])):
            self.dataModel.usdsPairGTE = True
            self.dataModel.dataValid['dsFile'] = False
            self.dataModel.dataValid['usFile'] = False
            return True
        else:
            if self.dataModel.usdsPairGTE:
                self.dataModel.usdsPairGTE = False
            return False
    
    def isDataValid(self):
        if not (all(val == True for val in self.dataModel.dataValid.values())):
            test = True
            for data, val in self.dataModel.dataValid.items():
                if not data == 'calibConfig':
                    test = val and test
                if not test:
                    return False
            
            if self.dataModel.calibType == (1,0,0):
                if (self.dataModel.calibConfigData.calibValid['(US)'] and self.dataModel.calibConfigData.calibValid['(DS)']):
                    return True
            elif self.dataModel.calibType == (0,1,0):
                if (self.dataModel.calibConfigData.calibValid['F1 (US)'] and self.dataModel.calibConfigData.calibValid['F1 (DS)']):
                    return True
            elif self.dataModel.calibType == (0,0,1):
                if (self.dataModel.calibConfigData.calibValid['F2 (US)'] and self.dataModel.calibConfigData.calibValid['F2 (DS)']):
                    return True
            return False
        return True
    
    def getModeTransition(self, inputMode=None):
        if inputMode == None:
            inputMode = self.dataModel.mode
        
        if inputMode == (1, 0):
            self.dataModel.dataValid['dsFile'] = True
            self.dataModel.dataValid['usFile'] = True #We won't have this to start, must be true
            return State.EVENTS.LIVE
        elif inputMode == (0, 1):
            #Check validity of current US/DS pair
            for i in range(2):
                usdsLabel = 'dsFile' if i == 0 else 'usFile'
                if self.isValidPath(self.dataModel.usdsPair[0], False):
                    self.dataModel.dataValid[usdsLabel] = True
                else:
                    self.dataModel.dataValid[usdsLabel] = False
            return State.EVENTS.OFFLINE
        else:
            raise BadModelStateException("Invalid mode setting detected")
    
    def getSMStateName(self):
        return self.stateMach.getStateName()
    
    def getSMState(self):
        return self.stateMach.currentState
    
    def getTResults(self):
        return (self.calcServ.planckResults, self.calcServ.wienResults)

####

class CalibPresenter(AllPresenter):
    def __init__(self, cM = None):
        #Create the data model and the state machine
        if cM == None:
            self.calibModel = CalibrationConfigData()
        else:
            self.calibModel = cM
            
    def changeCalibDirTrigger(self, uiText):
        self.calibModel.calibDir = uiText
        if self.isValidPath(uiText, dirPath=True) or uiText == '':
            return True
        else:
            return False
    
    def changeCalibFileTrigger(self, uiText, calibId):
        self.calibModel.calibFiles[calibId] = uiText
        if uiText == '':
            self.calibModel.calibValid[calibId] = False
            return True
        elif self.isValidPath(uiText, dirPath=False):
            self.calibModel.calibValid[calibId] = True
            return True
        else:
            self.calibModel.calibValid[calibId] = False
            return False
    
    def changeBulbTempTrigger(self, uiText):
        self.calibModel.bulbTemp = float(uiText)
        if uiText == '':
            self.calibModel.calibValid['bulbTemp'] = False
            return True
        elif (self.isValidInt(uiText) or self.isValidFloat(uiText)) and (float(uiText) >= 0):
            self.calibModel.calibValid['bulbTemp'] = True
            return True
        else:
            self.calibModel.calibValid['bulbTemp'] = False
            return False
    
    def isValidConfig(self):
        return all(val == True for val in self.calibModel.calibValid.values())

####

class StateMachine(object):
    def __init__(self, mp):
        self.mainPres = mp
        
        #This is a slightly convoluted way to avoid importing StartState
        self.currentState = State().next(State.EVENTS.START)()
        self.currentState.run(self.mainPres)
        
        #Set the StateMachine based on the dataModel of the mainPres
        self.changeState(self.mainPres.getModeTransition())
        
    def changeState(self, event):
        while True:
            nextState = self.currentState.next(event)
            if nextState == type(self.currentState):
                break
            self.currentState = nextState()
            self.currentState.run(self.mainPres)
    
    def getStateName(self):
        return self.currentState.name


