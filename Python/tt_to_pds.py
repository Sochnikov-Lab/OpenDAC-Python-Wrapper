#python tt_to_pds.py [channel to analyze] [amplifier gain] [csv file 0 name] [csv file 1 name] []...]
#Note: Time traces must have same number of points and use the same timestep for this script to work!

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

if min(nSamples) != max(nSamples):
    print "ERROR: Datasets do not have same length!"

timeStep = (timesML[0][1] - timesML[0][0]) #Timestep for data sets. Assuming all have same timestep!

#Data should presumbably be loaded in, now. Create window functions:
WindowFuncs = [] #List of window functions for each time trace
wENBW = 2.5
wCohG = 0.5
for i in range(0,nTraces-1):
    WindowFuncs.append(np.hanning(nSamples[i]))
#print WindowFuncs

fftTempML = []
fdata = []
#Compute DFT/PDS
for i in range(0,nTraces-1):

    #convert voltage list to np array
    npvolts = np.divide(np.asarray(voltsML[i]),float(ampGain))
    voltsDC = np.mean(npvolts)
    #Subtract off DC level:
    npvolts = npvolts - voltsDC
    #compute FFT:
    fftTempML.append((np.absolute(np.fft.fft(npvolts*WindowFuncs[i],nSamples[i])))/sqrt(nSamples[i]))
    fdata.append(np.multiply(fftTempML[i],fftTempML[i])/wENBW)

    #Add DC back in:
    fdata[i][0] = voltsDC

#Double duplicated elements:
for i in range(0,nSamples[0]-1):
    for j in range(0,nTraces-1):
        fdata[j][i] = fdata[j][i]*2
    #fdata[i][1:nSamples-1] = fdata[i][1:nSamples-1]*2

#Create sum
spect = np.zeros(nSamples[0])
for j in range(0,nTraces-1):
    for i in range(1,nSamples[0]-1):
        spect[i] = spect[i] + fdata[j][i]

#Average:
spect = (spect/nTraces) * (timeStep)


#Assuming same sample step and number of samples, new X axis of frequencies:
#frequenciestemp = np.linspace(0,nSamples[0],nSamples[0])
#frequencies = []
#for i in range(0,nSamples[0]):
#    frequencies.append(frequenciestemp[i]*(1.0/timeStep) / nSamples[0])

#frequenciestemp = np.linspace(0,nSamples[0],nSamples[0])
frequencies = np.fft.fftfreq(nSamples[0],d=timeStep)

#print fdata


print("Number of Time Traces to Average: " + str(len(fftTempML)))
print("Length of x: " + str(len(frequencies)))
print("Length of y: " + str(len(spect)))


pltfig = plt.figure()
ax = plt.gca()
#ax.scatter(times,ch0V, c='r', label="50 $\Omega$ Termination")
ax.plot(frequencies,spect, c='b', label="Sine Wave",linewidth=1.0)
ax.set_xlim([0.1,100000])
ax.set_ylim([0.0000000000000001,10])
ax.set_title("PDS Test")
ax.set_xlabel("frequencies (Hz)")
ax.set_ylabel("Spectral Power (A.U.)")
ax.set_xscale("log")
ax.set_yscale("log")

ax.legend()
print frequencies
plt.show()
pltfig.savefig('figdata_pds.png')
