from opendacwrapper import ODAC
#import numpy as np #for future DFT

ODAQ1 = ODAC()
ODAQ1.open('/dev/ttyACM0',verbose=0)
ODAQ1.acquireOne(0,500,0.0125)
#ODAQ1.acquireAll(500,0.0125)
ODAQ1.saveToFile("mytest2.csv")
ODAQ1.close()
