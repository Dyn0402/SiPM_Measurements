# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 14:15:46 2017

@author: Dyn04
"""


# Read data from SiPM Breakdown Measurement text file.
def read_data(path):
    data = [[], [], [], [], [], []]  # [[Time],[SetVoltage],[SupplyVoltage],[MultiVoltage],[Current],[(microVoltage)]]
    
    # Read each line into an element of Lines list.
    file = open(path, 'read')
    lines = file.readlines()
    
    # Using the second line of the file, extract run parameters listed below.
    compact = ["SiPMV", "SiPMN", "Bias", "LEDV", "VMin", "VMax", "VStep", "IReads"]
    params = dict(zip(compact, lines[1].split()[1:]))
    
    # For each line of data, split on tabs and append text to Data list as float.
    for line in lines[4:]:
        line = line.split()
        for i in range(len(line)):
            data[i].append(float(line[i]))
    
    return data, params