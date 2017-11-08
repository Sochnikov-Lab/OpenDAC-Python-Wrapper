#python tt_to_pds.py [channel to analyze] [amplifier gain] [csv file 0 name] [csv file 1 name] []...]

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt


#Load in the data:
nTraces = len(sys.argv) - 2 #Number of time traces to average
ampGain = sys.argv[2]
argchannel = str(sys.argv[1]) #Channel to do DFT on
#Collect list of files from CLI arguments
argfilenames = [] #List of filenames for each timetrace
for i in range(0,nTraces):
    argfilenames.append(str(sys.argv[2+i]))
nSamples = [] #List of lengths of each timetrace
timeSteps = [] #List of timesteps of each timetrace
timesML = [] #Masterlist of time stamps [[,tt0,],[,tt1,],[,tt2,],...,[,ttN,]]
voltsML = [] #Masterlist of voltages [[,tt0,],[,tt1,],[,tt2,],...,[,ttN,]]
for i in range(1,nTraces):
    dataframe = pd.read_csv(argfilenames[i])
    #Get list of time stamps and voltages from the desired channel
    timesML.append(dataframe["time(s)"]) #list of times
    nSamples.append(len(dataframe["time(s)"]))
    if int(argchannel) == 0:
        voltsML.append(dataframe["ch0(V)"])
    if int(argchannel) == 1:
        voltsML.append(dataframe["ch1(V)"])
    if int(argchannel) == 2:
        voltsML.append(dataframe["ch2(V)"])
    if int(argchannel) == 3:
        voltsML.append(dataframe["ch3(V)"])
    timeSteps.append(timesML[i-1][1] - timesML[i-1][0])

#Data should presumbably be loaded in, now. Create window functions:
WindowFuncs = [] #List of window functions for each time trace
for i in range(0,nTraces-1):
    WindowFuncs.append(np.hanning(nSamples[i]))
#print WindowFuncs

fftML = []
#Compute DFT/PDS
for i in range(0,nTraces-1):
    #convert voltage list to np array
    npvolts = np.asarray(voltsML[i])/ampGain
    voltsDC = np.mean(npvolts)
    #Subtract off DC level:
    npvolts = npvolts - voltsDC
    #compute FFT:
    fftML.append((np.absolute(np.fft.fft(npvolts*WindowFuncs[i],nSamples[i])))/sqrt(nSamples[i]))

print fftML
