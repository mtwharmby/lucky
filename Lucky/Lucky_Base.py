import NormalisationProcs as normProc#import math
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
import sys

#standard integration range(i)  315-->1146
start = 315
end= 800

#Session where I load the file I need from the folder where the software is
x,y=np.loadtxt('../T_62_1.txt',unpack=True) ##Raw file
xC,yC=np.loadtxt('../Calib.txt',unpack=True) ##Calib file

#Session with all the normalization for the collected data
P=normProc.Planck(x,1,2436) ##Ideal Planck
#TPlanck ID24 =2436
#TPlanck I15 = 3200
Norm=y/yC*P #Normalization file
invX=1/x*10**9 #Inverse of wavelength for Wien function
W=normProc.Wien(Norm,x)#Define Wien function
#test=W
#for w in W:
 #   test[numpy.isnan(w)]=[]
Two=normProc.TwoCol(Norm,x)
#array = np.array(a,dtype='float')
Two2=np.array(Two,dtype='float')
TwoInt=Two2[start:end]
bins=range(1000,3000,1)
hist=np.histogram(TwoInt,bins,density=False)
freq=np.array(hist[0])
control=len(hist[1])-1
value=np.array(np.delete(hist[1],control,0))
#del value[-1]
#xhist=numpy.histogram(x,density=False)

#Session where we save in the same folder .txt files with the new data
np.savetxt('TwoCol.txt',Two)
np.savetxt('Norm.txt',Norm)
np.savetxt('Wien.txt',W)
np.savetxt('frequence.txt',hist[0])

#Session dedicated to all the needed fits
#Planck fit
p0=[1,2000]
#Fit Planck in the range [start:end]
bestP,covarP = curve_fit(normProc.Planck, x[start:end], Norm[start:end], p0)
TP=round(bestP[1],2)#Save Planck Temperature
eP=bestP[0]#Save planck Emissivity
xp=x[start:end]
FP=normProc.Planck(xp,eP,TP)#Create the new Planck with the fit parameters
PRes=abs(Norm[start:end]-FP)#Planck Residual
    
#Wien fit 
invX1=invX[start:end]
W1=W[start:end]
#Fit Wien and control that there are no inf or nan arguments in the fit
bestW,covarW = curve_fit(normProc.FWien,invX1[(np.isfinite(W1))],W1[(np.isfinite(W1))],p0=[1,TP])
Residual=W1-normProc.FWien(invX1[(np.isfinite(W1))],*bestW)
#Save Wien temperature
TW=round(bestW[1])

#Gaussian fit to the histogram two-colours
popt,pcov = curve_fit(normProc.gaus,value,freq,p0=[1000,TP,100])
Thist=round(popt[1],2)#Save Histogram temperature
errTot=round(popt[2])#Save hiistogram FWHM
#create a file with all the results needed
Results=(TP,errTot,TW,abs(((TP-TW)/TP*100)),Thist)
np.savetxt('Results.txt',Results,newline='\n',header="Name Planck STD Wien errPerc Hist")
print 'Planck:',TP,'K ','+-',errTot,'K ','Wien:',TW,'K','Hist:',Thist,'K'

#Defines the method for plotting all the graphs
def plots(x,y,yC,Norm,xp,FP,PFrom,PTo,invX,W,invX1,bestW,Two2,value,freq,popt,TwoInt,Residual,TP):
    fig=plt.figure(figsize=(8,11))#Defines dimension of the figure 

    #Adding subplots to show
    ax1 = fig.add_subplot(3, 2, 1)
    ax2 = fig.add_subplot(3, 2, 2)
    ax3 = fig.add_subplot(3, 2, 3)
    ax4 = fig.add_subplot(3, 2, 4)
    ax5 = fig.add_subplot(3, 2, 5)
    plt.subplots_adjust(wspace=0.3,hspace=0.3)
    #Raw and calibration data subgraph 
    ax1.plot(x, y, x, yC,'red')
    ax1.set_title('Raw vs Calib data')
    ax1.set_xlabel('wavelength (nm)')
    ax1.set_ylim(0,50000)
    ax1.grid(True)
    ticklines = ax1.get_xticklines()
    ticklines.extend( ax1.get_yticklines() )
    gridlines = ax1.get_xgridlines()
    gridlines.extend( ax1.get_ygridlines() )
    ticklabels = ax1.get_xticklabels()
    ticklabels.extend( ax1.get_yticklabels() )

    for line in ticklines:
      line.set_linewidth(3)

    for line in gridlines:
      line.set_linestyle('-')

    for label in ticklabels:
       label.set_color('black')
       label.set_fontsize('medium')


    txt=plt.text(4500,33,TP)
    txt1=plt.text(4200,33,'T=')
    txt2=plt.text(2000,17,TW)
    txt3=plt.text(1800,17,'T=')
    txt.set_size(15)
    txt1.set_size(15)
    txt2.set_size(15)
    txt3.set_size(15)
    fig.canvas.draw()
   

    #Planck subgraph
    ax2.plot(x, Norm, xp, FP,'red')
    ax2.set_title('Planck')
    ax2.set_xlabel('wavelength (nm)')
    ax2.set_xlim(PFrom,PTo)
    ax2.set_yticks([])
    #ax2.grid(True)
    def on_button_press(event):
        #print dir(event)
        #print "BADGER"
        #print "Button:", event.button
        #print "Figure coordinates:", event.x, event.y
        print "Data coordinates:", event.xdata, event.ydata
        #start=event.xdata
        sys.stdout.flush()
   
   #Wien subgraph
    ax3.plot(invX,W,invX1,normProc.FWien(invX1,*bestW),'red',invX1,Residual)
    ax3.set_title('Wien')
    ax3.set_xlabel('1/wavelength (1/m)')
    ax3.set_ylabel("Wien function")
    ax3.set_xlim(10**9/PTo,10**9/PFrom)
    ax3.set_yticks([])
    #ax3.grid(True)
   
    
    #Two Colours subgraph
    ax4.plot(x,Two2,x[start:end],TwoInt,'red')
    ax4.set_title('Sliding Two-Colours')
    ax4.set_xlabel('wavelength (nm)')
    ax4.set_ylabel('T (K)')
    ax4.set_xlim(PFrom,PTo)
    ax4.grid(True)
    ticklines4 = ax4.get_xticklines()
    ticklines4.extend( ax4.get_yticklines() )
    gridlines4 = ax4.get_xgridlines()
    gridlines4.extend( ax4.get_ygridlines() )
    ticklabels4 = ax4.get_xticklabels()
    ticklabels4.extend( ax4.get_yticklabels() )

    for line in ticklines4:
      line.set_linewidth(3)

    for line in gridlines4:
      line.set_linestyle('-')

    for label in ticklabels4:
       label.set_color('black')
       label.set_fontsize('medium')
   
    

    #Histogram subgraph
    ax5.plot(value,freq,value,normProc.gaus(value,*popt),'red')
    ax5.set_title('Histogram')
    ax5.set_xlabel('T(K)')
    ax5.set_ylabel('# Counts')
    


    #pylab.show() #it plots everything
    fig.canvas.mpl_connect('button_press_event', on_button_press)
    plt.show()

#Plot range
PFrom=500
PTo=1000
plots(x,y,yC,Norm,xp,FP,PFrom,PTo,invX,W,invX1,bestW,Two2,value,freq,popt,TwoInt,Residual,TP)