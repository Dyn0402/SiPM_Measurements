# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 14:15:46 2017

@author: Dyn04
"""


#Read data from SiPM Breakdown Measurement text file.
def ReadData(File):
    Data = [[],[],[],[],[]] #[[Time],[SetVoltage],[OutputVoltage],[Current],[(microVoltage)]]
    
    #Read each line into an element of Lines list.
    Lines = File.readlines()
    
    #Using the second line of the file, extract run parameters listed below.
    Compact = ["SiPMV", "SiPMN", "LEDV", "VMin", "VMax", "VStep", "IReads"]
    Params = dict(zip(Compact, Lines[1].split()[1:]))
    
    #For each line of data, split on tabs and append text to Data list as float.
    for line in Lines[4:]:
        line = line.split()
        for i in range(len(line)):
            Data[i].append(float(line[i]))
    
    return(Data, Params)