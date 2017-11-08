#python tt_to_pds.py [channel to analyze] [csv file 0 name] [csv file 1 name] []...]

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#Load in the data:
nTraces = len(sys.argv) - 1 #Number of time traces to average
argchannel = str(sys.argv[1]) #Channel to do DFT on
#Collect list of files from CLI arguments
argfilenames = [] #List of filenames for each timetrace
for i in range(0,nTraces):
    argfilename.append(str(sys.argv[1+i]))
nSamples = [] #List of lengths of each timetrace
timeSteps = [] #List of timesteps of each timetrace
timesML = [] #Masterlist of time stamps [[,tt0,],[,tt1,],[,tt2,],...,[,ttN,]]
voltsML = [] #Masterlist of voltages [[,tt0,],[,tt1,],[,tt2,],...,[,ttN,]]
for i in range(0,nTraces):
    dataframe = pd.read_csv(argfilenames[i])
    #Get list of time stamps and voltages from the desired channel
    times.append(dataframe["time(s)"]) #list of times
    if int(argchannel) == 0:
        voltsML.append(dataframe["ch0(V)"])
    if int(argchannel) == 1:
        voltsML.append(dataframe["ch1(V)"])
    if int(argchannel) == 2:
        voltsML.append(dataframe["ch2(V)"])
    if int(argchannel) == 3:
        voltsML.append(dataframe["ch3(V)"])
    nSamples.append(len(times))
    timestep.append(times[1] - times[0])

#Data should presumbably be loaded in, now.
print voltsML
