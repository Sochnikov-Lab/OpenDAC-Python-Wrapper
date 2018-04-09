from opendacwrapper import ODAC
import pandas as pd
import matplotlib.pyplot as plt
#import numpy as np #for future DFT

ODAQ1 = ODAC()
ODAQ1.open('/dev/ttyACM0',verbose=0)
#     sine(dac,v0,angfreq,phase,offset,interval):
#ODAQ1.sine(0,5,2*3.14159*200,0,0,20000)
v0 = 5
v1 = 5
v2 = 5
v3 = 5
w0 = 2*3.14159*60
w1 = 2*3.14159*60
w2 = 2*3.14159*60
w3 = 2*3.14159*60
phi0 = 0
phi1 = 0
phi2 = 0
phi3 = 0
dc0 = 0
dc1 = 0
dc2 = 0
dc3 = 0
ODAQ1.sine4(v0,v1,v2,v3,w0,w1,w2,w3,phi0,phi1,phi2,phi3,dc0,dc1,dc2,dc3,20000)

#ODAQ1.setDAC(0,0)
#ODAQ1.setDAC(1,0)
#ODAQ1.setDAC(2,0)
#ODAQ1.setDAC(3,0)


#mockup of how DFT averaging should work:
#Collect nRun traces:
#for run in range(0,nRuns):
#    ODAQ1.acquireOne(0,500,0.0125)
#    ODAQ1.saveToFile("mytest" + str(run) + ".csv") #pad "run" with 0s to make machine readable
#    #somehow do DFT
#    #
#    #
#Now average DFTs:
#for run in range(0,nRuns)
#    #do math on DFTs
#Plot
