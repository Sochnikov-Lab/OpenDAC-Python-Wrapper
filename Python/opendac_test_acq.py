from opendacwrapper import ODAC
import pandas as pd
import matplotlib.pyplot as plt
#import numpy as np #for future DFT

ODAQ1 = ODAC()
ODAQ1.open('/dev/ttyACM0',verbose=0)
ODAQ1.setConvTime(0,82)
ODAQ1.setConvTime(1,82)
ODAQ1.setConvTime(2,82)
ODAQ1.setConvTime(3,82)

ODAQ1.acquireOne(0,2000,0.0001)
#ODAQ1.acquireAll(1000,0.00100)
ODAQ1.saveToFile("data.csv")

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
