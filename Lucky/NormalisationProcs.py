# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 11:12:40 2015

@author: roc54795
"""

import numpy as np
pi = np.pi
#from math import pi

#Constants:
h=6.626*10**(-34)
c=3*10**8
Kb=1.38*10**(-23)

#Session where I define all the function needed
def Planck(x,e,T):
    a=np.expm1(0.0144043/(x*10**(-9))/T)
    P=e/(x*10**(-9))**5*3.74691*10**(-16)*1/(a-1)
    return P

#Defined Wien function
def Wien(Int,x):
    W=Kb/h/c*np.log((x*10**(-9))**5*Int/2/pi/h/c**2)
    return W

#Defined two-colour function
def TwoCol(Int,x):
    count=len(x)
    delta=200
    k=count-delta
    TTwo=[]*count
    #while (i<k):
    for i in range (0,k):#(0,count-1):    
        f1=1/(x[i]*10**(-9))
        f2=1/(x[i+delta]*10**(-9))
        i1=np.log(Int[i]/2/pi/h/c**2/f1**5)*Kb/h/c
        i2=np.log(Int[i+delta]/2/pi/h/c**2/f2**5)*Kb/h/c
        TTwo.append(abs((f2-f1)/(i2-i1)))
    for i in range (k,count):
        a = float('nan')
        TTwo.append(a)
    return TTwo

#Defined linear fit for Wien function
def FWien(x,e,T):
    a=1/T
    b=Kb/h/c*np.log(e)
    W=b-a*x
    return W

#Defined Gauss fit
def gaus(x, a, x0, sigma):
    return np.real(a*np.exp(-(x-x0)**2/(2*sigma**2)))