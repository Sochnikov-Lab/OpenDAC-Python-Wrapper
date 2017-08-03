from opendacwrapper import ODAQ

ODAQ1 = ODAQ()
ODAQ1.open('COM4',verbose=0)
ODAQ1.getADC(0)
#ODAQ1.ramp1(0,0,-5,5,20,1000) #prints
ODAQ1.ramp1(0,0,-5,5,20,100000) #doesn't print
#RAR1,0,0,-5,5,20,1000
#ODAQ1.ramp1(0,0,5,-5,20,100000)
ODAQ1.setDAC(0,0)

#ODAQ1.sine(0,5,400,0,0,100000,1)

#SIN,0,5,200,0,2.5,10000,0.1

#print(ODAQ1.adcbuffer)
print(ODAQ1)
ODAQ1.close()
