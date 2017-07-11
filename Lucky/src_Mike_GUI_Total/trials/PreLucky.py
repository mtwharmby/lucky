#Session where I define all the function needed
def Planck(x,e,T):
    a=numpy.expm1(0.0144043/(x*10**(-9))/T)
    P=e/(x*10**(-9))**5*3.74691*10**(-16)*1/(a-1)
    return P
#Defined Wien function
def Wien(Int,x):
    h=6.626*10**(-34)
    c=3*10**8
    Kb=1.38*10**(-23)
    pi=math.pi
    W=Kb/h/c*numpy.log((x*10**(-9))**5*Int/2/pi/h/c**2)
    return W
#Defined two-colour function
def TwoCol(Int,x):
    h=6.626*10**(-34)
    c=3*10**8
    Kb=1.38*10**(-23)
    pi=math.pi
    count=len(x)
    delta=200
    k=count-delta
    TTwo=[]*count
    #while (i<k):
    for i in range (0,k):#(0,count-1):
        
     f1=1/(x[i]*10**(-9))
     f2=1/(x[i+delta]*10**(-9))
     i1=numpy.log(Int[i]/2/pi/h/c**2/f1**5)*Kb/h/c
     i2=numpy.log(Int[i+delta]/2/pi/h/c**2/f2**5)*Kb/h/c
     TTwo.append(abs((f2-f1)/(i2-i1)))
    for i in range (k,count):
     a = float('nan')
     TTwo.append(a)
    return TTwo
#Defined linear fit for Wien function
def FWien(x,e,T):
    h=6.626*10**(-34)
    c=3*10**8
    Kb=1.38*10**(-23)
    a=1/T
    b=Kb/h/c*numpy.log(e)
    W=b-a*x
    return W
#Defined Gauss fit
def gaus(x, a, x0, sigma):
    return numpy.real(a*numpy.exp(-(x-x0)**2/(2*sigma**2)))

    
#Programma che carica un file di temperatura (raw) lo normalizza e me lo 
#grafica in un plot per ottenere la mia funzione di Planck   
from scipy.optimize import leastsq, curve_fit
import numpy 
import matplotlib.pyplot as plt
import math
import pylab 
import sys

start = 315
end= 1146

#Session where I load the file I need from the folder where the software is
x,y=numpy.loadtxt('../../test/Lucky/testData/T_62_1.txt',unpack=True) ##Raw file
xC,yC=numpy.loadtxt('../../test/Lucky/testData/Calib.txt',unpack=True) ##Calib file

#Session with all the normalization for the collected data
P=Planck(x,1,2436) ##Ideal Planck
Norm=y/yC*P #Normalization file
invX=1/x*10**9 #Inverse of wavelength for Wien function
W=Wien(Norm,x)#Define Wien function
#test=W
#for w in W:
 #   test[numpy.isnan(w)]=[]
Two=TwoCol(Norm,x)
#array = np.array(a,dtype='float')
Two2=numpy.array(Two,dtype='float')
bins=range(1000,3000,1)
hist=numpy.histogram(Two2,bins,density=False)
freq=numpy.array(hist[0])
control=len(hist[1])-1
value=numpy.array(numpy.delete(hist[1],control,0))
#del value[-1]
#xhist=numpy.histogram(x,density=False)

#Session where we save in the same folder .txt files with the new data
# numpy.savetxt('../../test/Lucky/testData/TwoCol.txt',Two)
# numpy.savetxt('../../test/Lucky/testData/Norm.txt',Norm)
# numpy.savetxt('../../test/Lucky/testData/Wien.txt',W)
# numpy.savetxt('../../test/Lucky/testData/frequence.txt',hist[0])

#Session dedicated to all the needed fits
#Planck fit
p0=[1,2000]
#Fit Planck in the range [start:end]
bestP,covarP = curve_fit(Planck, x[start:end], Norm[start:end], p0)
TP=round(bestP[1],2)#Save Planck Temperature
eP=bestP[0]#Save planck Emissivity
xp=x[start:end]
FP=Planck(xp,eP,TP)#Create the new Planck with the fit parameters
PRes=abs(Norm[start:end]-FP)
#for i in PRes:
    
#Wien fit 
invX1=invX[start:end]
W1=W[start:end]
bestW,covarW = curve_fit(FWien,invX[(numpy.isfinite(W))],W[(numpy.isfinite(W))],p0=[1,TP])
#Fit Wien and control that there are no inf or nan arguments in the fit
TW=round(bestW[1])#Save Wien temperature
#Gaussian fit to the histogram two-colours
popt,pcov = curve_fit(gaus,value,freq,p0=[1000,TP,100])
Thist=round(popt[1],2)#Save Histogram temperature
errTot=round(popt[2])#Save hiistogram FWHM
print 'Planck:',TP,'K ','+-',errTot,'K ','Wien:',TW,'K','Hist:',Thist,'K'

#Session dedicated to the plots of the new data and analysis
pylab.figure(figsize=(12,9))#Defines dimension of the figure
#Raw and calibration data subgraph
pylab.subplot(3,2,1)
pylab.title("Raw")
pylab.plot(x,y,'black',x,yC,'r')
pylab.ylim([0,50000])
#Planck subgraph
pylab.subplot(3,2,2)
pylab.title("Planck")
pylab.plot(x,Norm,'black',xp,FP,'r')#,x,Tbest)
pylab.xlim([550,950])

def on_button_press(event):
    print dir(event)
    print "Button:", event.button
    print "Figure coordinates:", event.x, event.y
    print "Data coordinates:", event.xdata, event.ydata
    sys.stdout.flush()
# figure.canvas.mpl_connect('button_press_event', on_button_press)   
#Wien subgraph
pylab.subplot(3,2,3)
pylab.title("Wien")
pylab.plot(invX,W,'black',invX,FWien(invX,*bestW),'red')
pylab.xlim([1052632,1818182])
#Two Colours subgraph
pylab.subplot(3,2,4)
pylab.title("TwoColours")
pylab.plot(x,Two2,'black')
pylab.xlim([550,950])
pylab.ylim([1500,4000])
#Histogram subgraph
pylab.subplot(3,2,5)
pylab.title("Histogram")
pylab.plot(value,freq,'black',value,gaus(value,*popt),'red')

pylab.show() #it plots everything

