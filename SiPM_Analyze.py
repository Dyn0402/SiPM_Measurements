# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:10:12 2017

@author: nulab
"""

import SiPM_Measure_IO as SIO
import DList as DL
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter


def main():
    R = 2.0 #Ohms
    File = DL.ChooseFile()
    File = open(File, "r")
    Data, Params = SIO.ReadData(File)
    File.close()
    ICor = CorrectI(Data[2], Data[3], R)
    Plot5(Data[2], ICor)
    V, ICor = MvAvg(Data[2], ICor, 7)
    V, ICor = CleanData(V, ICor, 1.5e-2)
    Plot5(V, ICor)
#    Plot4(V, Data[3], ICor)
#    Plot3(Data[2], ICor)
    D3, V3 = GetThirdDer(V, ICor)
    Plot5(V3, D3)
    p0 = [3.0e-5, 0.5, 64.5, 0.15]
    VBounds = [63.5, 66.0]
    V3, D3 = SelectRange(V3, D3, VBounds)
    Plot6(V3, D3, np.asarray(p0))
    popt, pcov = curve_fit(ThirdDFun, V3, D3, p0=p0)
    print(popt)
    Plot6(V3, D3, popt)
#    ILD, VAvg = GetILD(V, ICor)
#    VAvg, ILD = SelectRange(VAvg, ILD, [64.5, 65.5])
#    p0 = [64.0, 0.1, 1.0, 20.0]
#    popt, pcov = curve_fit(ILDMinFun, VAvg, ILD, p0=p0)
#    print popt, pcov
#    Plot7(np.asarray(VAvg), ILD, ILDMinFun, popt)
#    Plot5(VAvg, ILD)
    print("donzo")


#Plot voltage and current against time.

def Plot1(Data):
    VCol = 'b'
    ICol = 'r'
    fig, ax1 = plt.subplots()
    ax1.plot(Data[0], Data[1], VCol)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (Volts)', color=VCol)
    ax1.tick_params('y', colors=VCol)
    
    ax2 = ax1.twinx()
    ax2.plot(Data[0], Data[2], ICol)
    ax2.set_ylabel('Current (Amps)', color=ICol)
    ax2.tick_params('y', colors=ICol)
    
    plt.show()


#Plot current vs voltage.

def Plot2(Data):
    plt.plot(Data[2], Data[3], "r.")
    print(sp.polyfit(Data[1], Data[2], 1))
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (A)")
    plt.show()
    

#Plot ln(current) vs voltage.

def Plot3(V, I):
    plt.plot(V, np.log(I))
    plt.show()
    

def Plot4(V, I, ICor):
    plt.plot(V, I, 'b.')
    plt.plot(V, ICor, 'r.')
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (A)")
    plt.show()
    
    

def Plot5(X, Y):
    plt.plot(X, Y, 'b.')
    plt.show()
    
    
def Plot6(V, ICor, popt):
    plt.plot(V, ICor, 'b.')
    plt.plot(V, ThirdDFun(V, *popt), 'r')
    plt.xlabel('Interpolated Voltage (V)')
    plt.ylabel('Third Derivative of Current (I/V^3)')
    plt.title('Breakdown Voltage: {0}'.format(popt[2]))
    plt.show()
    

def Plot7(X, Y, Fun, fitpars):
    plt.plot(X, Y, 'b.')
    Z = Fun(np.asarray(X), *fitpars)
    plt.plot(X, Z, 'r')
    plt.show()
    
    
def Plot8(X, Y, Fun1, fitpars1, Fun2, fitpars2):
    plt.plot(X, Y, 'b.')
    Z1 = Fun1(np.asarray(X), *fitpars1)
    plt.plot(X, Z1, 'r')
    Z2 = Fun2(np.asarray(X), *fitpars2)
    plt.plot(X, Z2, 'g')
    plt.show()



#Correct for Pico Internal Resistance.
def CorrectI(V, I, R):
    ICor = []
    for i in range(len(V)):
        INew = 1.0 / (1.0 / I[i] - R / V[i])
        ICor.append(INew)
    
    return(ICor)


#Get ILD.
def GetILD(V, I):
    ILD = []
    VAvg = []
    for i in range(len(V)-1):
#        dI = I[i+1] - I[i]
        dV = V[i+1] - V[i]
#        IAvg = (I[i+1] + I[i]) / 2.0
#        NewILD = 1.0 / (1.0 / IAvg * dI / dV)
        dlnI = np.log(I[i+1] / I[i])
        NewILD = 1.0 / (dlnI / dV)
        ILD.append(NewILD)
        VAvg.append((V[i+1] + V[i]) / 2)
        
    return(ILD, VAvg)


#Get DL.
def GetDL(V, I):
    DL = []
    VAvg = []
    for i in range(len(V)-1):
        dV = V[i+1] - V[i]
#        IAvg = (I[i+1] + I[i]) / 2.0
#        NewILD = 1.0 / (1.0 / IAvg * dI / dV)
        dlnI = np.log(I[i+1] / I[i])
        NewDL = dlnI / dV
        DL.append(NewDL)
        VAvg.append((V[i+1] + V[i]) / 2)
        
    return(DL, VAvg)


#Get Breakdown Voltage via the third derivative method.
def ThirdDBD(Data, Params, SiPMV):
    Vbd = float(SiPMV) - Params['opVbd']
    VBound = [Vbd - Params['fitL'], Vbd + Params['fitR']]
    p0 = Params['p0']
    p0[2] = Vbd
#    V, I = SelectRange(Data[2], Data[3], VBound)
    V, I = Data[2][1:], Data[3][1:]
    V, I = CleanData(V, I, Params['VTol'])
#    ICor = CorrectI(V, I, Params['R'])
#    V, ICor = MvAvg(V, ICor, Params['MvAvg'])
    D3, V3 = GetThirdDer(V, I, Params['MvAvg'])
    try:
        popt, pcov = curve_fit(ThirdDFun, V3, D3, p0=p0)
    except:
        print('No fit')
        Plot5(V3, D3)
        return('nofit', 'nofit')
    perr = np.sqrt(np.diag(pcov))
    print('VBd: {0}+-{1}V'.format(popt[2], perr[2]))
    Plot6(V3, D3, popt)
    
    return(popt, perr)



def ILDBD(Data, Params, SiPMV):
#    Vbd = float(SiPMV) - Params['opVbd']
#    VBound = [Vbd - Params['fitL'], Vbd + Params['fitR']]
#    V, I = SelectRange(Data[2], Data[3], VBound)
    V, I = Data[2][1:], Data[3][1:]
    V, I = CleanData(V, I, Params['VTol'])
#    ICor = CorrectI(V, I, Params['R'])
#    V, ICor = MvAvg(V, ICor, Params['MvAvg'])
    ILD, VAvg = GetILD(V, I)
#    VAvg, ILD = MvAvg(VAvg, ILD, Params['MvAvg'])
#    Plot5(VAvg, ILD)
    
    ILDMin = ILD.index(min(ILD[35:-35]))
    VLow, ILDLow = SelectRange(VAvg, ILD, [VAvg[ILDMin] - 0.85, VAvg[ILDMin] - 0.4])
    VHigh, ILDHigh = SelectRange(VAvg, ILD, [VAvg[ILDMin] + 0.1, VAvg[ILDMin] + 2.0])
    
    try:
        poptLow, pcovLow = curve_fit(Line, VLow, ILDLow, p0=[-50.0, 3220.0])
#        Plot7(VLow, ILDLow, Line, poptLow)
#        poptLow, pcovLow = curve_fit(Quad, VLow, ILDLow, p0=[0.0, -50.0, 3220.0])
#        print poptLow
#        Plot7(VLow, ILDLow, Quad, poptLow)
#        poptLow, pcovLow = curve_fit(Exp, VLow, ILDLow, p0=[150.0, -8.0, 64.0])
#        print poptLow
#        Plot7(VLow, ILDLow, Exp, poptLow)
    except(KeyError):
        print('No low fit')
#        Plot5(VLow, ILDLow)
        poptLow, pcovLow = ['nolowfit']*2
    
    try:
        poptHigh, pcovHigh = curve_fit(Quad, VHigh, ILDHigh, p0=[0.0, 0.375, -24.0])
#        Plot7(VHigh, ILDHigh, Quad, poptHigh)
    except(KeyError):
        print('No high fit')
#        Plot5(VHigh, ILDHigh)
        poptHigh, pcovHigh = ['nohighfit']*2
        
    z1, z2 = SolveQuad(poptHigh[0], poptHigh[1] - poptLow[0], poptHigh[2] - poptLow[1])
    print(z1, z2)
        
    Plot8(VAvg, ILD, Line, poptLow, Quad, poptHigh)
    
    
    return(z1)
    


def DLBD(Data, Params, SiPMV):
    V, I = Data[2][1:], Data[3][1:]
    V, I = CleanData(V, I, Params['VTol'])
    DL, VAvg = GetDL(V, I)
    
    Vbd = float(SiPMV) - Params['opVbd']
    VBound = [Vbd - Params['DLfitL'], Vbd + Params['DLfitR']]
    VFit, DLFit = SelectRange(VAvg, DL, VBound)
    p0 = [Vbd, 1e-2]    
    
    popt, pcov = curve_fit(DLFun, VFit, DLFit, p0=p0)
    perr = np.sqrt(np.diag(pcov))
    
    return(popt, perr)



def DLPeak(Data, Params, SiPMV):
    V, I = Data[2][1:], Data[3][1:]
    V, I = CleanData(V, I, Params['VTol'])
    DL, VAvg = GetDL(V, I)
    
    Vbd = float(SiPMV) - Params['opVbd']
#    VSearchBound = [Vbd - Params['DLPeakS'], Vbd + Params['DLPeakS']]
#    VSearch, DLSearch = SelectRange(VAvg, DL, VSearchBound)
#    MaxV = VAvg[DL.index(max(DLSearch))]
    MaxV = VAvg[DL.index(max(DL))]
    VBound = [MaxV - Params['DLPeakW'], MaxV + Params['DLPeakW']]
    VFit, DLFit = SelectRange(VAvg, DL, VBound)
    p0 = [7.0, Vbd, 1.0]    
    
    popt, pcov = curve_fit(Gaus, VFit, DLFit, p0=p0)
    perr = np.sqrt(np.diag(pcov))
    
    Plot7(VFit, DLFit, Gaus, popt)
    
    return(popt, perr)
    


#Get third derivative of I wrt V.
def GetThirdDer(V, I, Smoothing = 3):
    D1, V1 = Derivative(V, I)
    D1 = savgol_filter(D1, 11, 5)
#    D1, V1 = MvAvg(D1, V1, Smoothing)
    D2, V2 = Derivative(V1, D1)
    D2 = savgol_filter(D2, 11, 5)
#    D2, V2 = MvAvg(D2, V2, Smoothing)
    D3, V3 = Derivative(V2, D2)
    D3 = savgol_filter(D3, 11, 5)
#    D3, V3 = MvAvg(D3, V3, Smoothing)
    
    return(D3, V3)
    
    
#Take Discreet Derivative.
def Derivative(X, Y):
    AvgX = []
    DY = []
    i = 0
    while(i < len(X) - 1):
        j = 1
        while(Y[i+j] == Y[i]):
            j+=1
        dY = Y[i+j] - Y[i]
        dX = X[i+j] - X[i]
        DY.append(dY/dX)
        avgX = (X[i+j] + X[i]) / (j + 1.0)
        AvgX.append(avgX)
        i += j
        
#    Plot5(AvgX, DY)
    
    return(DY, AvgX)


#Take Discreet Derivative with linear fits.
def Derivative2(X, Y, points = 2):
    AvgX = []
    DY = []
    i = 0
    while(i < len(X) + 1 - points):
        popt, pcov = curve_fit(Line, X[i:i+points], Y[i:i+points])
        DY.append(popt[0])
        avgX = np.mean(X[i:i+points])
        AvgX.append(avgX)
        i += 1
    
    return(AvgX, DY)


def Line(x, a, b):
    return(a*x + b)

def Quad(x, a, b, c):
    return(a*x**2 + b*x + c)

def Exp(x, a, b, c):
    return(a * np.exp(b * (x - c)))

def Gaus(x, a, b, c):
    return(a * np.exp((-(x-b)**2)/(2*c)))

# 0 = a * x ^ 2 + b * x + c
def SolveQuad(a, b, c):
    z1 = (-b + np.sqrt(b**2 - 4*a*c)) / (2*a)
    z2 = (-b - np.sqrt(b**2 - 4*a*c)) / (2*a)
    return(z1, z2)


#Moving average.
def MvAvg(X, Y, Points):
    XAvg = []
    YAvg = []
    i = 0
    while(i < len(X) - Points):
        xAvg = 0
        yAvg = 0
        j = 0
        while(j < Points):
            xAvg += X[i+j]
            yAvg += Y[i+j]
            j+=1
        xAvg /= Points
        yAvg /= Points
        XAvg.append(xAvg)
        YAvg.append(yAvg)
        i+=1
        
    return(XAvg, YAvg)


#Third derivative fitting function.
def ThirdDFun(V, A, h, V01, sigma):
    y = A * (2 - h / sigma**2 * (V - V01)) * np.exp(-(V  - V01)**2 / (2 * sigma**2))
    
    return(y)

#Function to find min of ILD.
def ILDMinFun(x, a, b, c, d):
    y = b*x + d*np.exp(-c*(x-a))
    return(y)

#Function to fit decay curve on DL.
def DLFun(x, VBD, alpha):
    VRel = (x - VBD) / VBD
    y = VRel / alpha
    fy = (y + 1 - np.exp(y)) / (np.exp(y) - 1)
    DL = (2.0 + fy) / (x - VBD)
    
    return(DL)


#Select a range of data.
def SelectRange(X, Y, XRange):
    NewX = []
    NewY = []
    for i in range(len(X)):
        if(X[i] >= XRange[0] and X[i] <= XRange[1]):
            NewX.append(X[i])
            NewY.append(Y[i])
    
    return(NewX, NewY)


#Remove any potential issues from data.
#If two consecutive x points the same within tolerance,
#coalesce into one with avg y.
def CleanData(X, Y, Tolerance):
    NewX = []
    NewY = []
    i = 0
    while i < len(X):
        j = 0
        while(abs(X[i] - X[i+j]) < Tolerance):
            j+=1
            if(i+j >= len(X)):
                break
        NewX.append(np.mean(X[i:i+j]))
        NewY.append(np.mean(Y[i:i+j]))
        i+=j
    
    return(NewX, NewY)


#Reject obvious outliers from Y data set.
def RejectOutliers(X, Y, Points, sigma):
    NewX = []
    NewY = []
    i = 0
    while i < len(X):
        j = 0
        while(abs(X[i] - X[i+j]) < Tolerance):
            j+=1
            if(i+j >= len(X)):
                break
        NewX.append(np.mean(X[i:i+j]))
        NewY.append(np.mean(Y[i:i+j]))
        i+=j
    
    return(NewX, NewY)


if(__name__ == "__main__"):
    main()