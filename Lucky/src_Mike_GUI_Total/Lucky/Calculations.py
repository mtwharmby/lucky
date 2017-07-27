'''
Created on 24 Nov 2015

@author: wnm24546
'''

from scipy.constants import c, h, k, pi
from scipy.optimize import curve_fit
from collections import OrderedDict
import numpy as np
from Lucky.LuckyExceptions import BadModelStateException

#k is kb

class CalculationService(object):
    
    def __init__(self, pp):
        self.parentPresenter = pp
        
        self.planckResults = (0, 0, 0, 0)
        self.wienResults = (0, 0, 0, 0)
        self.twoColResults = (0, 0, 0, 0)
        
        #TODO Spawn calculations and plots in a separate thread
    def createCalcs(self, dM, debug=False):
        self.updateModel(dM)
        self.dsCalcs = LuckyCalculations(self.dsData, self.dsCalib,
                                         self.integConf, self.bulbTemp, "Downstream Measurement")
        self.usCalcs = LuckyCalculations(self.usData, self.usCalib,
                                         self.integConf, self.bulbTemp, "Upstream Measurement")
        self.dsCalcs.runCalculations()
        self.usCalcs.runCalculations()
        self.updateResults()
        
        #Create plot objects once we've got some data to plot
        self.dsPlots = LuckyPlots(self.dsCalcs)
        self.usPlots = LuckyPlots(self.usCalcs)
    
    def updateCalcs(self):
        #Perhaps add updateModel call?
        self.dsCalcs.runCalculations()
        self.usCalcs.runCalculations()
        self.updateResults()
        
        #Update the plots with new values from the calculations
        self.dsPlots.updatePlots()
        self.usPlots.updatePlots()
    
    def updateResults(self):
        def calculateResults(dsVal, usVal):
            avs = (dsVal + usVal)/2
            diff = abs(dsVal - usVal)
            return [dsVal, usVal, avs, diff]
        
        self.planckResults = calculateResults(self.dsCalcs.planckTemp, self.usCalcs.planckTemp)
        self.wienResults = calculateResults(self.dsCalcs.wienTemp, self.usCalcs.wienTemp)
        self.twoColResults = calculateResults(self.dsCalcs.twoColTemp, self.usCalcs.twoColTemp)
        
    def updateModel(self, dM):
        self.dsData, self.usData = self.openData(dM)
        self.dsCalib, self.usCalib = self.openCalib(dM.calibType, dM.calibConfigData)
        
        self.integConf = dM.integrationConf
        self.bulbTemp = dM.calibConfigData.bulbTemp
    
    def updateData(self, usData=None, dsData=None):
        if (usData == None) and (dsData == None):
            raise BadModelStateException("No data given for data update")
        
        if dsData != None:
            newData = np.loadtxt(usData)
            self.dsCalcs.update(data=newData)

        if usData != None:
            newData = np.loadtxt(usData)
            self.usCalcs.update(data=usData)
    
    def updateIntegration(self, integConf):
        self.dsCalcs.update(integConf=integConf)
        self.usCalcs.update(integConf=integConf)
    
    def updateCalibration(self, calibType, calibConf):
        self.dsCalib, self.usCalib = self.openCalib(calibType, calibConf)
        self.bulbTemp = calibConf.bulbTemp
        
        self.dsCalcs.update(calib=self.dsCalib, bulbTemp=self.bulbTemp)
        self.usCalcs.update(calib=self.usCalib, bulbTemp=self.bulbTemp)
    
    def openCalib(self, calibType, calibConfig):
        calibFileLabels = calibConfig.calibFiles.keys()
        dsCalib, usCalib = None, None 
        for i in range(len(calibType)):
            if calibType[i] == 1:
                dsCalib = str(calibConfig.calibFiles[calibFileLabels[2*i]])
                usCalib = str(calibConfig.calibFiles[calibFileLabels[2*i+1]])
            
            if None not in [dsCalib, usCalib]:
                break
        return np.loadtxt(dsCalib, unpack=True), np.loadtxt(usCalib, unpack=True)
    
    def openData(self, dM):
        return np.loadtxt(dM.usdsPair[0], unpack=True), np.loadtxt(dM.usdsPair[1], unpack=True)
    
    def disposePlots(self):
        self.dsPlots.dispose()
        self.usPlots.dispose()
    
class LuckyCalculations(object): #TODO Make calcs use calcserv to get bulbTemp, integConf & calibset
    
    def __init__(self, data, calib, integConf, bulbTemp, label, debug=False):
        self.dataSet = data
        self.calibSet = calib
        self.intConf = integConf
        self.bulbTemp = bulbTemp
        self.label = label
        
        self.planckPlotRange = [550, 900]
        self.wienPlotRange = [1e9 / self.planckPlotRange[1], 1e9/self.planckPlotRange[0]]
        
        #Prepare the data
        self.normaliseData()
    
    def update(self, data=None, integConf=None, calib=None, bulbTemp=None):
        self.dataSet = data if (data != None) else self.dataSet
        self.intConf = integConf if (integConf != None) else self.intConf
        self.calibSet = calib if (calib != None) else self.calibSet
        self.bulbTemp = bulbTemp if (bulbTemp != None) else self.bulbTemp
        
        if (data != None) or (calib != None) or (bulbTemp != None):
            self.normaliseData()
        if integConf != None:
            self.calculateRanges()
    
    def normaliseData(self):
        self.planckIdeal = self.planck(self.dataSet[0], 1, self.bulbTemp)
        self.planckIdeal = np.reshape(self.planckIdeal, (1, len(self.planckIdeal)))
        #This step adds the normalises dataset & concatenates with the original data array
        self.dataSet = np.concatenate((self.dataSet, self.dataSet[1] / self.calibSet[1] * self.planckIdeal), axis=0)
        
        #We've changed the data so we need to recalculate the ranges:
        self.calculateRanges()
    
    def calculateRanges(self):
        #Data sets for fitting or plotting, limited by integration range
        self.invWL = 1e9 / self.dataSet[0]# For Wien function
        self.invWLIntegLim = self.invWL[self.intConf[0]:self.intConf[1]]
        self.wlIntegLim = self.dataSet[0][self.intConf[0]:self.intConf[1]]
        self.RawIntegLim= self.dataSet[1][self.intConf[0]:self.intConf[1]]
        self.normIntegLim = self.dataSet[2][self.intConf[0]:self.intConf[1]]
        
    def runCalculations(self):
        #Calculate functions over the range of data
        self.wienData = self.wien(self.dataSet[0], self.dataSet[2])
        self.wienDataIntegLim = self.wienData[self.intConf[0]:self.intConf[1]]
        self.twoColData = self.twoColour(self.dataSet[0], self.dataSet[2], self.intConf[2])
        self.twoColDataLim = self.twoColData[self.intConf[0]:self.intConf[1]] #twoColData limited between the integration boundaries
        #modifica
       
        self.a = int(round(min(self.twoColDataLim)))
        self.b = int(round(max(self.twoColDataLim)))
        self.binning = range(self.a, self.b, 30)
        #self.twoColHistFreq, self.twoColHistValues = np.histogram(self.twoColDataLim, bins=np.log(len(self.twoColDataLim))/np.log(2)+4], density=False)
        self.twoColHistFreq, self.twoColHistValues = np.histogram(self.twoColDataLim, bins= self.binning, density=False)
        
        #old
        #self.twoColHistFreq, self.twoColHistValues = np.histogram(self.twoColDataLim, bins=range(1500,5000,1), density=False)
        #self.twoColHistValues = np.delete(self.twoColHistValues, len(self.twoColHistFreq), 0)
        
        #Do fits
        self.fitPlanck()
        self.fitWien()
        self.fitHistogram()
        
    def fitPlanck(self):
        #Do some fitting for Planck...
        ###
        self.planckFit, planckCov = curve_fit(self.planck, self.wlIntegLim, self.normIntegLim, [1,2000])
        self.planckTemp = self.planckFit[1]
        self.planckEmiss = self.planckFit[0]
        #Planck with fit params(??)
        self.planckFitData = self.planck(self.wlIntegLim, self.planckEmiss, self.planckTemp)
        
        #new method defined to operate a sliding average. usefull for the fit Histogram
    def moving_average(self, a, n=2) :
        self.ret = np.cumsum(a, dtype=float)
        self.ret[n:] = self.ret[n:] - self.ret[:-n]
        return self.ret[n - 1:] / n

    
    def fitWien(self):
        #Do some fitting for Wien...
        ###
        self.wienFit, wienCov = curve_fit(self.fWien, self.invWLIntegLim[(np.isfinite(self.wienDataIntegLim))], self.wienDataIntegLim[(np.isfinite(self.wienDataIntegLim))], p0=[1, self.planckTemp])
        self.wienResidual = self.wienDataIntegLim - self.fWien(self.invWLIntegLim[(np.isfinite(self.wienDataIntegLim))], *self.wienFit)
        self.wienTemp = self.wienFit[1]
        
    def fitHistogram(self):
        #Gaussian fit of two colour histogram
        ###
        #print('averaged twocolhistvalues:')
        #print self.moving_average(self.twoColHistValues)
        self.histFit, histCov = curve_fit(self.gaus, self.moving_average(self.twoColHistValues), self.twoColHistFreq, p0=[1000,self.planckTemp,100])
        self.twoColTemp = self.histFit[1]
        self.twoColErr = self.histFit[2]
    
    #old
    #def fitHistogram(self):
        #Gaussian fit of two colour histogram
        ###
        #self.histFit, histCov = curve_fit(self.gaus, self.twoColHistValues, self.twoColHistFreq, p0=[1000,self.planckTemp,100])
        #self.twoColTemp = self.histFit[1]
        #self.twoColErr = self.histFit[2]
    
    
    
    #Planck function
    def planck(self, wavelength, emiss, temp):
        wavelength = wavelength * 1e-9
        return emiss / np.power(wavelength, 5) * (2 * pi * h * np.power(c, 2)) / np.expm1((h * c)/(k * wavelength * temp))
    
    #Wien function
    def wien(self, wavelength, intens):
        wavelength = wavelength * 1e-9
        return self.wienBase(np.power(wavelength, 5) * intens / (2 * pi * h * np.power(c, 2)))
        
    #Linear Wien function
    def fWien(self, wavelength, emiss, temp):
#         wavelength = wavelength * 1e-9
        return self.wienBase(emiss) - (1/temp) * wavelength
    
    #Wien support function (this is just recycling code)
    def wienBase(self, exponent):
        return k / (h * c) * np.log(exponent)
    
    #Two colour function
    def twoColour(self, wavelength, intens, delta):
        #wavelength = wavelength * 1e-9
        nPoints = len(wavelength)
        nWindows = nPoints - delta
        twoCol = []
        
        #def twoColCalc(wavelength, intens):
        #    return np.log(intens * np.power(wavelength, 5) / (2 * pi * h * np.power(c, 2))) * (k / (h *c))
         
        for i in range(nWindows):
            f1 = 1 / (wavelength[i]* 1e-9)
            f2 = 1/ (wavelength[i + delta]* 1e-9)
            i1 = np.log(intens[i]/2/pi/h/c**2/f1**5)*k/h/c #twoColCalc(wavelength[i], intens[i])
            i2 = np.log(intens[i+delta]/2/pi/h/c**2/f2**5)*k/h/c #twoColCalc(wavelength[i + delta], intens[i+delta])
            twoCol.append(abs((f2 - f1) / (i2 - i1)))
        
        for i in range(nWindows, nPoints):
            twoCol.append(float('nan'))
            
        return twoCol
    
    #Gaussian for fit
    def gaus(self, x, a, x0, sigma):
        return a*np.exp(-(x-x0)**2/(2*sigma**2))

###


import matplotlib.pyplot as plt
class LuckyPlots(object):
    def __init__(self, calcs, debug=False):
        if debug:
            return
        self.debug = debug
        
        self.luckyCalcs = calcs
        
        self.fig = plt.figure(self.luckyCalcs.label)
        self.fig.suptitle(self.luckyCalcs.label, fontsize="16", weight="bold", color = 'b')
        self.ax1 = self.fig.add_subplot(3, 2, 1)#Raw+Calib
        self.ax2 = self.fig.add_subplot(3, 2, 3)#Planck
        self.ax3 = self.fig.add_subplot(3, 2, 4)#Wien
        self.ax3.xaxis.get_major_formatter().set_powerlimits((0, 1))
        self.ax4 = self.fig.add_subplot(3, 2, 5)#2Colour
        self.ax5 = self.fig.add_subplot(3, 2, 6)#Histogram
        self.ax5.xaxis.get_major_formatter().set_powerlimits((0, 1))
        self.ax6 = self.ax3.twinx()
        
        #Layout settings for the plots
        plt.subplots_adjust(wspace=0.3, hspace=0.7)
        
        #One-time configuration of plots
        self.ax1.set_title('Raw (blue) & Calibration Data (green)', fontsize= 13, style='italic', weight="bold")
        self.ax1.set_xlabel('Wavelength [nm]', fontsize= 13)
        self.ax1.grid(True, linestyle='-')
        
        self.ax2.set_title('Planck Function Data', fontsize='13', style='italic', weight="bold")
        self.ax2.set_xlabel('Wavelength [nm]', fontsize= 13)
        self.ax3.set_ylabel("Planck Function [a.u.]", fontsize= 13)
        #self.ax2.set_yticks([])
        self.ax2.set_yticks([0.1, 0.3, 0.5, 0.7, 0.9])
        
        self.ax3.set_title('Wien Function Data', fontsize='13', style='italic', weight="bold")
        self.ax3.set_xlabel(r'1/Wavelength [m$^{-1}$]', fontsize= 13)
        self.ax3.set_ylabel("Wien Function", fontsize= 13)
        self.ax3.set_yticks([])
        
        self.ax4.set_title('Two-Colour Plot', fontsize='13', style='italic', weight="bold")
        self.ax4.set_xlabel('Wavelength  [nm]', fontsize= 13)
        self.ax4.set_ylabel('Temperature [K]', fontsize= 13)
        self.ax4.grid(True, linestyle='-')
        
        
        
        self.ax5.set_title('Two-colour Histogram', fontsize='13', style='italic', weight="bold")
        self.ax5.set_xlabel('Temperature [K]', fontsize= 13)
        self.ax5.set_ylabel('Counts [a.u.]', fontsize= 13)
     
        self.ax6.set_ylabel('Wien Residual', color='g', fontsize= 13)
        self.updatePlots(redraw=False)
        
        #ax1 = calibration and raw spectrum
        #ax2 = planck spectrum
        #ax3 = wien
        #ax4 = 2-col
        #ax5 =histogram
        #ax6 = residuals in subplot (3,2,4)
         
        if not self.debug:
            #Draw the plots if we're not debugging
            plt.ion()
            plt.show()
            #Needed to make plt appear!
            #   http://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib
            plt.pause(0.001)
            
    def updatePlots(self, redraw=True):
        #Raw and calibration data subgraph 
        self.ax1.plot(self.luckyCalcs.dataSet[0], self.luckyCalcs.dataSet[1], 
                 self.luckyCalcs.dataSet[0], self.luckyCalcs.calibSet[1],'green',self.luckyCalcs.wlIntegLim,self.luckyCalcs.RawIntegLim,'red')
        self.ax1.set_ylim(0, self.getYMax(self.luckyCalcs.dataSet[1], self.luckyCalcs.calibSet[1]))
#        self.ax1.set_ylim(0,50000) #TODO Get max fn.
        
        #Planck data subgraph
        #self.ax2.plot(self.luckyCalcs.dataSet[0], self.luckyCalcs.dataSet[2], 
         #        self.luckyCalcs.wlIntegLim, self.luckyCalcs.planckFitData, 'red')
        #self.ax2.set_xlim(*self.luckyCalcs.planckPlotRange)
             #Planck data subgraph
        self.ax2.plot(self.luckyCalcs.dataSet[0], self.luckyCalcs.dataSet[2] / max(self.luckyCalcs.dataSet[2]), 
                 self.luckyCalcs.wlIntegLim, self.luckyCalcs.planckFitData / max(self.luckyCalcs.dataSet[2]), 'red')
        self.ax2.set_xlim(*self.luckyCalcs.planckPlotRange)
        self.ax2.set_ylim([0, 1])
      
        #Wien data subgraph
        self.ax3.plot(self.luckyCalcs.invWL, self.luckyCalcs.wienData,
                 self.luckyCalcs.invWLIntegLim, self.luckyCalcs.fWien(self.luckyCalcs.invWLIntegLim,*self.luckyCalcs.wienFit), 'red')
        self.ax3.set_xlim(*self.luckyCalcs.wienPlotRange)
        #Two Colour data subgraph
        self.ax4.plot(self.luckyCalcs.dataSet[0], self.luckyCalcs.twoColData, 'b:', 
                 self.luckyCalcs.wlIntegLim, self.luckyCalcs.twoColDataLim, 'r:')
        self.ax4.set_xlim(*self.luckyCalcs.planckPlotRange)
        #self.ax4.set_ylim([np.amin(calcs.TwoColDataLim),np.amax(calcs.TwoColDataLim)])
        #self.ax4.set_ylim(*calcs.twoColDataLim)
        #nuova modifica
        self.ax4.set_ylim(self.luckyCalcs.twoColTemp - 500, self.luckyCalcs.twoColTemp + 500)
        
        #Histogram subgraph
        #old
        #self.ax5.plot(self.luckyCalcs.twoColHistValues, self.luckyCalcs.twoColHistFreq,
        #         self.luckyCalcs.twoColHistValues, self.luckyCalcs.gaus(self.luckyCalcs.twoColHistValues, *self.luckyCalcs.histFit), 'red')
        #modifica
        self.ax5.hist(self.luckyCalcs.twoColDataLim, self.luckyCalcs.binning)
        self.ax5.plot(self.luckyCalcs.twoColHistValues, self.luckyCalcs.gaus(self.luckyCalcs.twoColHistValues, *self.luckyCalcs.histFit), 'red')
        
        #
        self.ax5.set_xlim([self.luckyCalcs.twoColTemp - 400, self.luckyCalcs.twoColTemp + 400])
        #self.ax5.set_xlim(1800,4000)
        #Residual subgraph of the Wien
        ordin = len(self.luckyCalcs.invWL)*[0]
        self.ax6.plot(self.luckyCalcs.invWLIntegLim, self.luckyCalcs.wienResidual,'green',self.luckyCalcs.invWL,ordin,'black')
       
        
        #Create text label for calculated T values  -OLD-
        #textLabel = OrderedDict([("T"+r"$_{Planck}$","{0:10.2f}".format(self.luckyCalcs.planckTemp)),
         #                        ("T"+r"$_{Wien}$","{0:10.2f}".format(self.luckyCalcs.wienTemp)),
          #                       ("T"+r"$_{Two Colour}$","{0:10.2f}".format(self.luckyCalcs.twoColTemp))]) 
    
     #Create text label for calculated T values -modified-
        textLabel = OrderedDict([("T"+r"$_{Planck}$" + "[K]","{0:9d}".format(int(self.luckyCalcs.planckTemp))),
                                 ("T"+r"$_{Wien}$"+ "[K]","{0:9d}".format(int(self.luckyCalcs.wienTemp))),
                                 ("T"+r"$_{2col}$"+ "[K]","{0:9d}".format(int(self.luckyCalcs.twoColTemp)))]) 
    
        self.errWienPlanck = (abs(self.luckyCalcs.planckTemp - self.luckyCalcs.wienTemp)/ (self.luckyCalcs.planckTemp))*100 
        self.std2col = self.luckyCalcs.twoColErr
        textLabel1 = OrderedDict([
                                 ("ERR"+"$_{2col}$"+ "[K]","{0:9d}".format(int(self.std2col))),
                                 ("ERR"+"$_{W-P}$","{0:9.2f}".format(self.errWienPlanck))
                                 ])     
    
#         {"T"+r"$_{Planck}$" : "{0:10.2f}".format(self.luckyCalcs.planckTemp),
#                      "T"+r"$_{Wien}$" : "{0:10.2f}".format(self.luckyCalcs.wienTemp),
#                      "T"+r"$_{Two Colour}$":"{0:10.2f}".format(self.luckyCalcs.twoColTemp)}
        labelPosition = (0.54, 0.85)
        rowNr = 0
        for label,tVal in textLabel.iteritems( ):
            plt.figtext(labelPosition[0], labelPosition[1]-(0.05*rowNr), label, fontdict = None, size = 'large')
            plt.figtext(labelPosition[0]+0.080, labelPosition[1]-(0.05*rowNr), tVal, fontdict = None, size = 'large')
            rowNr += 1
        
        labelPosition1 = (0.78, 0.85)
        rowNr = 0
    
        for label,tVal in textLabel1.iteritems( ):
            if self.errWienPlanck < 1 or rowNr == 0 :
                plt.figtext(labelPosition1[0], labelPosition1[1]-(0.05*rowNr), label, fontdict = None, size = 'large')
                plt.figtext(labelPosition1[0]+0.080, labelPosition1[1]-(0.05*rowNr), tVal, fontdict = None, size = 'large')
            else:
                plt.figtext(labelPosition1[0], labelPosition1[1]-(0.05*rowNr), label, fontdict = None, size = 'large')
                plt.figtext(labelPosition1[0]+0.080, labelPosition1[1]-(0.05*rowNr), tVal, fontdict = None, size = 'large', color = 'r')
            
            rowNr += 1
            
        
        
        
        if redraw and not self.debug:
            plt.draw()
            #Needed to make plt appear!
            #   http://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib
            plt.pause(0.001)
            
        #Draws text label on plot
#         txt=plt.text(4500,33,TP)
#         txt1=plt.text(4200,33,'T=')
#         txt2=plt.text(2000,17,TW)
#         txt3=plt.text(1800,17,'T=')
#         txt.set_size(15)
#         txt1.set_size(15)
#         txt2.set_size(15)
#         txt3.set_size(15)
#         fig.canvas.draw()
        
    def getYMax(self, *data):
        maxes = []
        for dat in data:
            maxes.append(np.amax(dat))
        
        return max(maxes)*1.1
    
    def dispose(self):
        plt.close(self.luckyCalcs.label)