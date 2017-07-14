'''
Created on 4 Nov 2015

@author: wnm24546
'''

#TODO QDialog has gone away in PyQt5 - what replaces it???
from PyQt4.QtGui import (QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QRadioButton, QVBoxLayout, QWidget)
from PyQt4 import QtCore

import os

#from Lucky import CalibrationConfigView
from Lucky.MainPresenter import (MainPresenter, CalibPresenter)
from Lucky.LuckyExceptions import IllegalArgumentException

class AllViews(object):
    
    def showFileBrowserDialog(self, initDir=None, caption="Choose a file"):
        if (initDir == None):
            initDir = os.path.expanduser("~")
        return str(QFileDialog.getOpenFileName(self, directory=initDir, caption=caption))
        
    def showDirBrowserDialog(self, initDir=None, caption="Choose a directory"):
        if (initDir == None):
            initDir = os.path.expanduser("~")
        return str(QFileDialog.getExistingDirectory(self, directory=initDir, caption=caption))

####

class MainView(QWidget, AllViews):
    def __init__(self, parent=None):
        super(MainView, self).__init__(parent)
        self.setWindowTitle("Lucky")
        #self.SetWindowIcon(QtGui.QIcon('SomeLocalIcon.png'))
        
        self.alreadyUpdating = False
        
        self.presenter = MainPresenter()
        
        self.setupUI(self.presenter.dataModel)
        self.updateWidgetStates(self.presenter.dataModel)
        
    def setupUI(self, mainData):
        ####
        #Creation of supporting layouts
        baseLayout = QVBoxLayout()
        controlsLayout = QGridLayout() #This is everything except the buttons
        
        ####
        #Mode controls
        modeGrpBox = QGroupBox("Mode:")
        self.modeRadBtns = [QRadioButton("Live"),
                            QRadioButton("Offline")]
        for i in range(len(self.modeRadBtns)):
            self.modeRadBtns[i].setChecked(mainData.mode[i])
            self.modeRadBtns[i].clicked.connect(self.modeRadBtnClick)
        modeLayout = QHBoxLayout()
        self.addWidgetListToLayout(self.modeRadBtns, modeLayout)
        modeGrpBox.setLayout(modeLayout)
        controlsLayout.addWidget(modeGrpBox, 0, 0)
        
        ####
        #Calib controls
        calibLayout = QVBoxLayout()
        calibGrpBox = QGroupBox("Calibration Type:")
        self.calibRadBtns = [QRadioButton("Calibration"),
                             QRadioButton("Calibration F1"),
                             QRadioButton("Calibration F2")]
        for i in range(len(self.calibRadBtns)):
            self.calibRadBtns[i].clicked.connect(self.calibRadBtnClick)
            self.calibRadBtns[i].setChecked(mainData.calibType[i])
        calibGrpLayout = QVBoxLayout()
        self.addWidgetListToLayout(self.calibRadBtns, calibGrpLayout)
        calibGrpBox.setLayout(calibGrpLayout)
        calibLayout.addWidget(calibGrpBox)
        
        calibConfBtn = QPushButton("Configure Calibration...")
        calibConfBtn.clicked.connect(self.calibConfClick)
        calibLayout.addWidget(calibConfBtn)
        
        controlsLayout.addLayout(calibLayout, 1, 0, 3, 1)
        
        ####
        #Data location
        dataDirGrpBox = QGroupBox("Data directory:")
        self.dataDirTextBox = QLineEdit()
        self.dataDirTextBox.setText(str(mainData.dataDir))
        self.dataDirTextBox.textChanged.connect(self.dataDirPathChanged)
        self.browseDataDirBtn = QPushButton("Browse...")
        self.browseDataDirBtn.clicked.connect(self.dataDirBrowseBtnClick)
        
        dataDirLayout = QHBoxLayout()
        dataDirLayout.addWidget(self.dataDirTextBox)
        dataDirLayout.addWidget(self.browseDataDirBtn)
        dataDirGrpBox.setLayout(dataDirLayout)
        controlsLayout.addWidget(dataDirGrpBox, 0, 1, 1, 2)
        
        ####
        #US/DS selector
        fileGrpBox = QGroupBox("Spectrum data files (US/DS) :")
        self.prevUSDSPairBtn = QPushButton("<")
        self.prevUSDSPairBtn.setFixedWidth(40)
        self.prevUSDSPairBtn.clicked.connect(self.changeUSDSPairBtnClick)
        self.nextUSDSPairBtn = QPushButton(">")
        self.nextUSDSPairBtn.clicked.connect(self.changeUSDSPairBtnClick)
        self.nextUSDSPairBtn.setFixedWidth(40)
        self.usdsPairTextBoxes = []
        for i in range(2):
            self.usdsPairTextBoxes.append(QLineEdit())
            #Set initial values of USDS pair boxes.
            if mainData.usdsPair[i] == '':
                self.usdsPairTextBoxes[i].setText(mainData.usdsPair[i])
            else:
                self.usdsPairTextBoxes[i].setText(os.path.basename(mainData.usdsPair[i]))
            self.usdsPairTextBoxes[i].textChanged.connect(self.usdsPairTextChanged)
            self.usdsPairTextBoxes[i].setFixedWidth(100)
        
        fileLayout = QHBoxLayout()
        fileLayout.addWidget(self.prevUSDSPairBtn)
        fileLayout.addWidget(self.usdsPairTextBoxes[0])
        fileLayout.addWidget(self.usdsPairTextBoxes[1])
        fileLayout.addWidget(self.nextUSDSPairBtn)
        fileGrpBox.setLayout(fileLayout)
        controlsLayout.addWidget(fileGrpBox, 1, 1, 1, 2)
        
        ###
        #Integration range
        # - N.B. set text values before setting the textchanged slot
        integRangeGrpBox = QGroupBox("Integration Range:")
        integRangeLayout = QGridLayout()
        integrationTextInputWidth = 40
        integElemNames = ["Beginning:", "End:", "Window Size:"]
        integElemLabels = []
        integNmLabels = []
        self.integElemTextBoxes = []
        colNr, rowNr = 0, 0
        for i in range(len(integElemNames)):
            integElemLabels.append(QLabel(integElemNames[i]))
            self.integElemTextBoxes.append(QLineEdit())
            self.integElemTextBoxes[i].setFixedWidth(integrationTextInputWidth)
            self.integElemTextBoxes[i].setText(str(mainData.integrationConf[i]))
            self.integElemTextBoxes[i].textChanged.connect(self.integConfigChanged)
            integNmLabels.append(QLabel("nm"))
            
            colNr = i%2
            if colNr == 0:
                rowNr += 1
            integRangeLayout.addWidget(integElemLabels[i], rowNr, 3*colNr)
            integRangeLayout.addWidget(self.integElemTextBoxes[i], rowNr, (3*colNr)+1)
            integRangeLayout.addWidget(integNmLabels[i], rowNr, (3*colNr)+2)
        
        integRangeGrpBox.setLayout(integRangeLayout)
        controlsLayout.addWidget(integRangeGrpBox, 2, 1, 2, 2)
        
        ###
        #Calculation results
        planckTempLabel = QLabel("Average T(Planck):")
        self.planckTempValLabel = QLabel()
        self.planckTempValLabel.setFixedWidth(50)
        self.planckTempValLabel.setAlignment(QtCore.Qt.AlignRight)
        planckKLabel = QLabel("K")
        planckKLabel.setAlignment(QtCore.Qt.AlignLeft)
        dPlancKTempLabel = QLabel(u"\u0394 T(Planck):")
        self.dPlanckTempValLabel = QLabel()
        self.dPlanckTempValLabel.setFixedWidth(50)
        self.dPlanckTempValLabel.setAlignment(QtCore.Qt.AlignRight)
        dPlanckKLabel = QLabel("K")
        dPlanckKLabel.setAlignment(QtCore.Qt.AlignLeft)
        wienTempLabel = QLabel("Average T(Wien):")
        self.wienTempValLabel = QLabel()
        self.wienTempValLabel.setFixedWidth(50)
        self.wienTempValLabel.setAlignment(QtCore.Qt.AlignRight)
        wienKLabel = QLabel("K")
        wienKLabel.setAlignment(QtCore.Qt.AlignLeft)
        dWienTempLabel = QLabel(u"\u0394 T(Wien):")
        self.dWienTempValLabel = QLabel()
        self.dWienTempValLabel.setFixedWidth(50)
        self.dWienTempValLabel.setAlignment(QtCore.Qt.AlignRight)
        dWienKLabel = QLabel("K")
        dWienKLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.updateTTextLabels()
        
        resultsLayout = QGridLayout()
        resultsLayout.addWidget(planckTempLabel, 0, 0)
        resultsLayout.addWidget(self.planckTempValLabel, 0, 1, alignment=QtCore.Qt.AlignRight)
        resultsLayout.addWidget(planckKLabel, 0, 2, alignment=QtCore.Qt.AlignLeft)
        resultsLayout.addWidget(dPlancKTempLabel, 1, 0)
        resultsLayout.addWidget(self.dPlanckTempValLabel, 1, 1, alignment=QtCore.Qt.AlignRight)
        resultsLayout.addWidget(dPlanckKLabel, 1, 2, alignment=QtCore.Qt.AlignLeft)
        resultsLayout.addWidget(wienTempLabel, 0, 3)
        resultsLayout.addWidget(self.wienTempValLabel, 0, 4, alignment=QtCore.Qt.AlignRight)
        resultsLayout.addWidget(wienKLabel, 0, 5, alignment=QtCore.Qt.AlignLeft)
        resultsLayout.addWidget(dWienTempLabel, 1, 3)
        resultsLayout.addWidget(self.dWienTempValLabel, 1, 4, alignment=QtCore.Qt.AlignRight)
        resultsLayout.addWidget(dWienKLabel, 1, 5, alignment=QtCore.Qt.AlignLeft)
        
        controlsLayout.addLayout(resultsLayout, 4, 0, 1, 3)
        
        ####
        #Control buttons
        self.runBtn = QPushButton('Run')
        self.runBtn.clicked.connect(self.runBtnClicked)
        self.stopBtn = QPushButton('Stop')
        self.stopBtn.clicked.connect(self.stopBtnClicked)
        quitBtn = QPushButton('Quit')
        quitBtn.clicked.connect(QtCore.QCoreApplication.instance().quit)#TODO Add control to kill plots properly
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.runBtn)
        buttonLayout.addWidget(self.stopBtn)
        buttonLayout.addWidget(quitBtn)
        
        ####
        #Add the 1st tier layouts & set the base layout
        baseLayout.addLayout(controlsLayout)
        baseLayout.addLayout(buttonLayout)
        self.setLayout(baseLayout)

###        
    def addWidgetListToLayout(self, widgetList, layout):
        for i in range(len(widgetList)):
            layout.addWidget(widgetList[i])
    
    def runBtnClicked(self):
        self.presenter.runTrigger()
        self.updateWidgetStates()
        self.updateTTextLabels()
    
    def stopBtnClicked(self):
        self.presenter.stopTrigger()
        self.updateWidgetStates()
    
    def getRadBtnStates(self, btnList):
        return tuple([int(radBtn.isChecked()) for radBtn in btnList])
            
    def modeRadBtnClick(self):
        self.presenter.setModeTrigger(self.getRadBtnStates(self.modeRadBtns))
        
        self.presenter.dataChangeTrigger()
        self.updateWidgetStates()
              
    def calibRadBtnClick(self):
        self.presenter.setCalibTypeTrigger(self.getRadBtnStates(self.calibRadBtns))
        
        self.presenter.dataChangeTrigger()
        self.updateWidgetStates()
        
    def calibConfClick(self):
        self.calibConfInput = CalibrationConfigView(self, self.presenter.dataModel.calibConfigData)
        self.calibConfInput.exec_()
        
        self.presenter.dataChangeTrigger()
        self.updateWidgetStates()
    
    def dataDirPathChanged(self):
        textBox = self.sender()
        if self.presenter.changeDataDirTrigger(textBox.text()):
            textBox.setStyleSheet("color: rgb(0, 0, 0);")
        else:
            textBox.setStyleSheet("color: rgb(255, 0, 0);")
        
        #If dataDir changes, US/DS files change too:
        for i in range(2):
            updatedPath = os.path.join(str(textBox.text()), os.path.basename(self.presenter.dataModel.usdsPair[i]))
            self.usdsPairTextBoxes[i].textChanged.emit(updatedPath)
        
        self.presenter.dataChangeTrigger()
        self.updateWidgetStates()
    
    def dataDirBrowseBtnClick(self):
        currDir = self.presenter.dataModel.dataDir
        newDir = self.showDirBrowserDialog(initDir=currDir, caption="Select a new data directory")
        if (newDir == None) or (newDir == ''):
            return
        else:
            self.dataDirTextBox.setText(newDir) #No need to fire an update as it happens automatically
    
    def changeUSDSPairBtnClick(self):
        btn = self.sender()
        if btn == self.prevUSDSPairBtn:
            self.presenter.changeUSDSPairTrigger(dec=True)
        elif btn == self.nextUSDSPairBtn:
            self.presenter.changeUSDSPairTrigger(inc=True)
        else:
            raise IllegalArgumentException(str(btn)+" unknown in this context")
        
        #TODO This is such an ugly hack
        dsFileName = os.path.split(self.presenter.dataModel.usdsPair[0])[1]
        usFileName = os.path.split(self.presenter.dataModel.usdsPair[1])[1]
        self.usdsPairTextBoxes[0].setText(usFileName)
        self.usdsPairTextBoxes[1].setText(dsFileName)
        
#         for i in range(2):
#             pathParts = os.path.split(self.presenter.dataModel.usdsPair[i])
#             self.usdsPairTextBoxes[i].setText(pathParts[1])
    
    def usdsPairTextChanged(self):
        textBox = self.sender()
        if textBox == self.usdsPairTextBoxes[0]:
            if self.presenter.changeUSDSPairTrigger(usFile=textBox.text()):
                textBox.setStyleSheet("color: rgb(0, 0, 0);")
            else:
                textBox.setStyleSheet("color: rgb(255, 0, 0);")
        elif textBox == self.usdsPairTextBoxes[1]:
            if self.presenter.changeUSDSPairTrigger(dsFile=textBox.text()):
                textBox.setStyleSheet("color: rgb(0, 0, 0);")
            else:
                textBox.setStyleSheet("color: rgb(255, 0, 0);")
        else:
            raise IllegalArgumentException(str(textBox)+" unknown in this context")
        
        prevState = self.presenter.dataModel.usdsPairGTE
        if self.presenter.dsLTEqualusFile():
            for i in range(2):
                self.usdsPairTextBoxes[i].setStyleSheet("color: rgb(255, 0, 0);")
        elif not prevState == self.presenter.dataModel.usdsPairGTE:
            for i in range(2):
                self.usdsPairTextBoxes[i].textChanged.emit(self.presenter.dataModel.usdsPair[i])
        
        self.presenter.dataChangeTrigger()
        self.updateWidgetStates()
    
    def integConfigChanged(self):
        textBox = self.sender()
        changeResult = self.presenter.changeIntegrationValueTrigger(textBox.text())
        
        if changeResult:
            integConfig = [integTextBox.text() for integTextBox in self.integElemTextBoxes]
            if self.presenter.changeIntegrationConfigTrigger(integConfig):
                styleSheetColour = "color: rgb(0, 0, 0);"
            else:
                styleSheetColour = "color: rgb(255, 0, 0);"
            [integTextBox.setStyleSheet(styleSheetColour) for integTextBox in self.integElemTextBoxes]
        else:
            if textBox.text() == '':
                textBox.setStyleSheet("color: rgb(0, 0, 0);")
                self.presenter.invalidateIntegration()
            else:
                textBox.setStyleSheet("color: rgb(255, 0, 0);")
                self.presenter.invalidateIntegration()
        
        self.presenter.dataChangeTrigger()
        self.updateWidgetStates()
        
    def updateTTextLabels(self):
        planckResults, wienResults = self.presenter.getTResults()
        
        if (planckResults[0] <= 0) and (planckResults[1] <=0):
            planckT = "-"
            dPlanckT = "-"
            wienT = "-"
            dWienT = "-"
        else:
            planckT = "{0:10.2f}".format(planckResults[2])
            dPlanckT = "{0:10.2f}".format(planckResults[3])
            wienT = "{0:10.2f}".format(wienResults[2])
            dWienT = "{0:10.2f}".format(wienResults[3])
        
        self.planckTempValLabel.setText(planckT)
        self.dPlanckTempValLabel.setText(dPlanckT)
        self.wienTempValLabel.setText(wienT)
        self.dWienTempValLabel.setText(dWienT)
        
###
    def updateWidgetStates(self, extraData=None):
        mainData = self.presenter.dataModel if (extraData == None) else extraData
        
        #Mode radio buttons
        for i in range(len(self.modeRadBtns)):
            self.modeRadBtns[i].setEnabled(mainData.allUIControlsEnabled)
        
        #Calibration type radio buttons
        for i in range(len(self.calibRadBtns)):
            self.calibRadBtns[i].setEnabled(mainData.allUIControlsEnabled)
        
        #Datadir
        self.browseDataDirBtn.setEnabled(mainData.allUIControlsEnabled)
        self.dataDirTextBox.setEnabled(mainData.allUIControlsEnabled)
        
        #US/DS pair
        self.prevUSDSPairBtn.setEnabled((mainData.allUIControlsEnabled) or (mainData.usdsControlsEnabled))
        self.nextUSDSPairBtn.setEnabled((mainData.allUIControlsEnabled) or (mainData.usdsControlsEnabled))
        for i in range(2):
            self.usdsPairTextBoxes[i].setEnabled((mainData.allUIControlsEnabled) and (mainData.usdsControlsEnabled)) 
        
        #Integration controls
        for textBox in self.integElemTextBoxes:
            textBox.setEnabled(mainData.allUIControlsEnabled)
        
        ###
        #Buttons
        self.runBtn.setEnabled(mainData.runEnabled)
        self.stopBtn.setEnabled(mainData.stopEnabled)


#####################################


class CalibrationConfigView(QDialog, AllViews):

    def __init__(self, parent_widget, calibConfig):
        super(CalibrationConfigView, self).__init__(parent=parent_widget)
        self.setWindowTitle("Configure Calibration")
        #self.SetWindowIcon(QtGui.QIcon('SomeLocalIcon.png'))
        self.presenter = CalibPresenter(calibConfig)
        
        #This needs to run after we've read & set the original calibConfig
        self.setupUI(calibConfig)
        self.updateWidgetStates()
        
    
    def setupUI(self, mainData):
        ####
        #Creation of supporting layouts
        baseLayout = QVBoxLayout()
        
        ####
        #Select the base directory to look for calibration files
        calibDirGrpBox = QGroupBox("Calibration Directory:")
        self.calibDirTextBox = QLineEdit()
        self.calibDirTextBox.setText(mainData.calibDir)
        self.calibDirTextBox.textChanged.connect(self.calibDirPathChanged)
        self.browseCalibDirBtn = QPushButton("Browse...")
        self.browseCalibDirBtn.clicked.connect(self.calibDirBrowseBtnClick)
        calibDirLayout = QHBoxLayout()
        calibDirLayout.addWidget(self.calibDirTextBox)
        calibDirLayout.addWidget(self.browseCalibDirBtn)
        calibDirGrpBox.setLayout(calibDirLayout)
        baseLayout.addWidget(calibDirGrpBox)
        
        ####
        #Select specific calibration file names to use
        calibFileLayout = QGridLayout()
        calibFileGrpBox = QGroupBox("Calibration Files:")
        nrLabels = len(self.presenter.calibModel.calibFiles)
        self.calibFileLabels = {}
        self.calibFileTextBoxes={}
        self.calibFileBrowseBtns = {}
#        self.browseBtnRegister = {}
        
        colNr = 0
        rowNr = -1
        for i in range(nrLabels):
            uiElemName = self.presenter.calibModel.calibFiles.keys()[i]
            
            self.calibFileLabels[uiElemName] = QLabel("Calibration "+uiElemName+":")
            self.calibFileTextBoxes[uiElemName] = QLineEdit(self.presenter.calibModel.calibFiles[uiElemName])
            self.calibFileTextBoxes[uiElemName].textChanged.connect(self.calibFilePathChanged)
            
            self.calibFileBrowseBtns[uiElemName] = QPushButton("Browse...")
            self.calibFileBrowseBtns[uiElemName].clicked.connect(self.calibFileBrowseBtnClick)
            
            #Lay out UI elements in a 2 column format, with the label occupying 2x columns  
            colNr = i%2
            if (colNr == 0):
                rowNr += 1
            calibFileLayout.addWidget(self.calibFileLabels[uiElemName], (2*rowNr), (2*colNr), 1, 2)
            calibFileLayout.addWidget(self.calibFileTextBoxes[uiElemName], ((2*rowNr)+1), (2*colNr))
            calibFileLayout.addWidget(self.calibFileBrowseBtns[uiElemName], ((2*rowNr)+1), (2*colNr+1))
        calibFileGrpBox.setLayout(calibFileLayout)
        baseLayout.addWidget(calibFileGrpBox)
        
        ####
        #Define temperature of bulb used for calibration
        bulbTLabel = QLabel("Bulb Temperature:")
        self.calibTempTextBox = QLineEdit()#Populate from model
        self.calibTempTextBox.setFixedWidth(40)#Same as integrationTextInputWidth in MainView
        self.calibTempTextBox.setText(str(mainData.bulbTemp))
        self.calibTempTextBox.textChanged.connect(self.bulbTempChanged)
        kTempLabel = QLabel("K")
        calibTempLayout = QHBoxLayout()
        calibTempLayout.addWidget(bulbTLabel)
        calibTempLayout.addWidget(self.calibTempTextBox)
        calibTempLayout.addWidget(kTempLabel)
        calibTempLayout.addStretch(1)
        baseLayout.addLayout(calibTempLayout)
        
        ####
        #Buttons to accept/reject dialog
        okCancelBtnBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        okCancelBtnBox.accepted.connect(self.okClick)
        okCancelBtnBox.rejected.connect(self.cancelClick)
        baseLayout.addWidget(okCancelBtnBox)
        
        ####
        #Set the base layout
        self.setLayout(baseLayout)
        
    ####
    def calibDirPathChanged(self):
        textBox = self.sender()
        if self.presenter.changeCalibDirTrigger(textBox.text()):
            textBox.setStyleSheet("color: rgb(0, 0, 0);")
        else:
            textBox.setStyleSheet("color: rgb(255, 0, 0);")
        
    
    def calibDirBrowseBtnClick(self):
        currDir = self.presenter.calibModel.calibDir
        newDir = self.showDirBrowserDialog(initDir=currDir, caption="Select a new calibration directory")
        if (newDir == None) or (newDir == ''):
            return
        else:
            self.calibDirTextBox.setText(newDir) #No need to fire an update as it happens automatically
    
    def calibFilePathChanged(self):
        textBox = self.sender()
        calibId = [uiElemName for uiElemName, btn in self.calibFileTextBoxes.iteritems() if (btn == textBox)][0]
        if self.presenter.changeCalibFileTrigger(textBox.text(), calibId):
            textBox.setStyleSheet("color: rgb(0, 0, 0);")
        else:
            textBox.setStyleSheet("color: rgb(255, 0, 0);")
    
    def calibFileBrowseBtnClick(self):
        calibId = [uiElemName for uiElemName, btn in self.calibFileBrowseBtns.iteritems() if (btn == self.sender())][0]
        
        calibFile = self.showFileBrowserDialog(initDir=self.presenter.calibModel.calibDir)
        if (calibFile == None) or (calibFile == ''):
            return
        else:
            self.calibFileTextBoxes[calibId].setText(calibFile)
            
    def bulbTempChanged(self):
        textBox = self.sender()
        if self.presenter.changeBulbTempTrigger(textBox.text()):
            self.calibTempTextBox.setStyleSheet("color: rgb(0, 0, 0);")
        else:
            self.calibTempTextBox.setStyleSheet("color: rgb(255, 0, 0);")
    
    def updateWidgetStates(self, extraData=None):
        mainData = self.presenter.calibModel if (extraData == None) else extraData
        
        for name in mainData.calibFiles.keys():
            self.calibFileTextBoxes[name].setText(mainData.calibFiles[name])
        
    def okClick(self):
        validity = self.presenter.isValidConfig()
        self.parent().presenter.calibConfigUpdateTrigger(self.presenter.calibModel, validity)
        self.accept()
         
     
    def cancelClick(self):
        self.reject()