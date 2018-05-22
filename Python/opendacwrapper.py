#####OpenDAC Wrapper#####
#opendacwrapper.py
#Written by J. Sheldon for the Sochnikov lab group at UConn Physics Department
#
#This file contains the class for communicating with the OpenDAC project's DAC-ADC
#with our modified firmware containging several new functions outlined in our
#documentation file.

import serial
import io
from math import floor
import time
import os
#Below: Attempt at a fix for Windows being weird
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#DAC-ADC Controller Class
class ODAC(object):
    #Initialization: create necessary variables and configurable serial instance
    def __init__(self):
        self.ID = ''         #ID of instrument
        self.ready = False   #If device is ready for command
        self.ser = serial.Serial() #Serial Instance
        self.ser.timeout = 0.25 #read timeout --Should fix this to get rid of latency
        self.serIO = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser),encoding = "ascii",newline="\r\n") #Linux
        #self.serIO = io.TextIOWrapper(io.BufferedRandom(self.ser),newline="\r\n")
        self.adctimes = [] #Timestamp list
        #Single CH acquire buffer:
        self.adcbuffer = []
        self.adc1rec = -1 #What channel was read. -1 means not read yet. -2 means all were read.
        self.adcrecA = -1 #2ch Acquisition - first channel. -1 means not read yet.
        self.adcrecB = -1 #2ch Acquisition - second channel. -1 means not read yet.
        #Quad CH acquire buffers:
        self.adcbuffer0 = []
        self.adcbuffer1 = []
        self.adcbuffer2 = []
        self.adcbuffer3 = []
        #Computed DAC values for RAR:
        self.dacbuffer0 = []
        self.dacbuffer1 = []
        self.dacbuffer2 = []
        self.dacbuffer3 = []
    def open(self,COMPORT,BAUDRATE=115200):
        try:
            self.ser.port = COMPORT
            self.ser.baudrate = BAUDRATE
            self.ser.open()

            #--Hack -- BufferedRWPair does not sync. This forces it to.
            #To fix control commands not working
            self.serIO.write(unicode('\r'))
            self.serIO.flush()
            self.serIO.readline()
            #--Hack--

            #Read ID from Serial Port:
            self.serIO.write(unicode('*IDN?\r'))
            self.serIO.flush()
            self.ID = str(self.serIO.readline()).rstrip().lstrip()
            self.serIO.flush()

            #Check if Device is Ready:
            self.serIO.write(unicode('*RDY?\r'))
            self.serIO.flush()
            status = str(self.serIO.readline()).rstrip().lstrip()
            if status == "READY":
                self.ready = True
            else:
                self.ready = False
        except serial.SerialException:
            print("**ODAC: Failed to open serial port**")
        except UnicodeDecodeError:
            print("**ODAC: Failed to read serial port. Try again")
    def close(self,verbose=0):
        try:
            self.ser.close()
            self.ready = False
            if self.ser.is_open == False and verbose == 1:
                print("**Successfully closed serial port**")
        except serial.SerialException:
            print("o  Failed to close serial port.")
    def isReady(self):
        self.serIO.write(unicode('*RDY?\r'))
        self.serIO.flush()
        if str(self.serIO.readline()).rstrip().lstrip() == "READY":
            return True
        else:
            return False
    def clearBuffers(self):
        self.adctimes[:] = []
        self.adcbuffer[:] = []
        self.adcbuffer0[:] = []
        self.adcbuffer1[:] = []
        self.adcbuffer2[:] = []
        self.adcbuffer3[:] = []
        self.dacbuffer0[:] = []
        self.dacbuffer1[:] = []
        self.dacbuffer2[:] = []
        self.dacbuffer3[:] = []
        self.adcrecA = -1
        self.adcrecB = -1
    def getADC(self,channel):
        self.serIO.flush()
        self.serIO.write(unicode('GET_ADC,'+ str(channel) + '\r'))
        self.serIO.flush()
        return str(self.serIO.readline()).rstrip()
    def setDAC(self,channel,voltage):
        if voltage >= -10 and voltage <= 10:
            self.serIO.write(unicode('SET,'+ str(channel) +',' + str(voltage) + '\r'))
        else:
            print("Warning: DAC Voltage range setting for ch" + str(channel) + " exceeds specification (-10V to +10V)")
            print("         *No Change*")
        self.serIO.flush()
    def setConvTime(self,channel,convTime): #microseconds. Default is something like 900us
        self.serIO.write(unicode('CONVERT_TIME,'+ str(channel) + "," + str(convTime) + '\r'))
        self.serIO.flush()
    def ramp1(self,dac,v1,v2,steps,interval):
        self.serIO.write(unicode('RAMP1,'+ str(dac) + ',' + str(v1) + ',' + str(v2) + ',' + str(steps) + ',' + str(interval) + ',' + '\r'))
        self.serIO.flush()
    def ramp2(self,dac1,dac2,v1i,v2i,v1f,v2f,steps,interval):
        self.serIO.write(unicode('RAMP2,'+ str(dac) + ',' + str(v1i) + ',' + str(v2i) + ',' + str(v1f) + ',' + str(v2f) + ',' + str(steps) + ',' + str(interval) + ',' + '\r'))
        self.serIO.flush()
    def rampread1(self,adc,dac,v1,v2,steps,interval,filename):
        #Setup and flags:
        self.clearBuffers()
        self.adc1rec = -4 #-4 = rampread1 or rampread4
        voltagestep = (v2 - v1)/(steps-1)
        #Send command:
        self.serIO.flush()
        #self.serIO.write(unicode('RAR1,'+ str(adc) + ',' + str(dac) + ',' + str(v1) + ',' + str(v2) + ',' + str(steps) + ',' + str(interval) + ',' + '\r'))
        self.serIO.write(unicode('RAR1,'+ str(adc)))
        self.serIO.flush()
        self.serIO.write(unicode(',' + str(dac) + ',' + str(v1) + ',' + str(v2)))
        self.serIO.flush()
        self.serIO.write(unicode(',' + str(steps)))
        self.serIO.flush()
        self.serIO.write(unicode(','+ str(interval) + ',' + '\r'))
        self.serIO.flush()
        #Read serial data:
        self.ser.timeout = steps*interval+5.0
        adcbufferstr = str(self.serIO.read(int(steps)*13)).encode("utf-8") #Full buffer string
        self.ser.timeout = 0.25 #return to default timeout
        self.serIO.flush()
        #Decompose full list string to rows:
        adcbufferrowstr = adcbufferstr.split(",")
        print adcbufferrowstr
        #Put data into correct buffer:
        if adc == 0:
            for i in range(0,len(adcbufferrowstr)):
                print adcbufferrowstr[i]
                self.adcbuffer0.append(float(adcbufferrowstr[i]))
        if adc == 1:
            for i in range(0,len(adcbufferrowstr)):
                self.adcbuffer1.append(float(adcbufferrowstr[i]))
        if adc == 2:
            for i in range(0,len(adcbufferrowstr)):
                self.adcbuffer2.append(float(adcbufferrowstr[i]))
        if adc == 3:
            for i in range(0,len(adcbufferrowstr)):
                self.adcbuffer3.append(float(adcbufferrowstr[i]))

        #Fill unused lists to avoid printout error. Also fill time list and DAC voltage inferences:
        for step in range(0,int(steps)):
            self.adctimes.append(step*interval)
            if adc == 0:
                self.adcbuffer1.append('')
                self.adcbuffer2.append('')
                self.adcbuffer3.append('')
            if adc == 1:
                self.adcbuffer0.append('')
                self.adcbuffer2.append('')
                self.adcbuffer3.append('')
            if adc == 2:
                self.adcbuffer0.append('')
                self.adcbuffer1.append('')
                self.adcbuffer3.append('')
            if adc == 3:
                self.adcbuffer0.append('')
                self.adcbuffer1.append('')
                self.adcbuffer2.append('')
            if dac == 0:
                self.dacbuffer0.append(v1 + voltagestep*step)
                self.dacbuffer1.append('')
                self.dacbuffer2.append('')
                self.dacbuffer3.append('')
            if dac == 1:
                self.dacbuffer0.append('')
                self.dacbuffer1.append(v1 + voltagestep*step)
                self.dacbuffer2.append('')
                self.dacbuffer3.append('')
            if dac == 2:
                self.dacbuffer0.append('')
                self.dacbuffer1.append('')
                self.dacbuffer2.append(v1 + voltagestep*step)
                self.dacbuffer3.append('')
            if dac == 3:
                self.dacbuffer0.append('')
                self.dacbuffer1.append('')
                self.dacbuffer2.append('')
                self.dacbuffer3.append(v1 + voltagestep*step)
        #cleanup:
        del adcbufferstr
        del adcbufferrowstr
        print("Finished!")
        #save:
        try:
            #datastructure:
            #time,DAC0,DAC1,DAC2,DAC3,ADC0,ADC1,ADC2,ADC3"
            fullfname = "data/" + filename + ".csv"
            datafile = open(fullfname,'w')
            datafile.write("time(s),DAC ch0(V),DAC ch1(V),DAC ch2(V),DAC ch3(V),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.dacbuffer0[i]) + "," + str(self.dacbuffer1[i]) + "," + str(self.dacbuffer2[i]) + "," + str(self.dacbuffer3[i]) + "," + str(self.adcbuffer0[i]) + "," + str(self.adcbuffer1[i]) + "," + str(self.adcbuffer2[i]) + "," + str(self.adcbuffer3[i]) + "\n")
            datafile.close()
            print("Data Saved")
        except IndexError:
            print("Index Error: Data not saved")
        #--Hack-- to clear buffer. BufferedRWPair does not sync.
        self.serIO.write(unicode('\r'))
        self.serIO.flush()
        self.serIO.readline()
        self.serIO.flush()
        time.sleep(0.25)
        #--Hack--
    def rampread4(self,v0,v1,v2,v3,steps,interval,filename):
        #setup and flags:
        self.clearBuffers()
        self.adc1rec = -4 #-4 = rampread1 or rampread4
        voltagestep = [(v0[1]-v0[0])/(steps-1),(v1[1]-v1[0])/(steps-1),(v2[1]-v2[0])/(steps-1),(v3[1]-v3[0])/(steps-1)]
        #Send command over serial port:
        #self.serIO.write(unicode('RARA,'+ str(v0[0]) + ',' + str(v0[1]) + ',' + str(v1[0]) + ',' + str(v1[1]) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v3[0]) + ',' + str(v3[1]) + ',' + str(steps) + ',' + str(interval) + ',' + '\r'))
        #self.serIO.flush()
        self.serIO.flush()
        self.serIO.write(unicode('RARA,'+ str(v0[0]) + ',' + str(v0[1])))
        self.serIO.flush()
        self.serIO.write(unicode(',' + str(v1[0]) + ',' + str(v1[1])))
        self.serIO.flush()
        self.serIO.write(unicode( ',' + str(v2[0]) + ',' + str(v2[1])))
        self.serIO.flush()
        self.serIO.write(unicode(',' + str(v3[0]) + ',' + str(v3[1])))
        self.serIO.flush()
        self.serIO.write(unicode(',' + str(steps) + ',' + str(interval) + ',' + '\r'))
        self.serIO.flush()
        #Read serial data:
        self.ser.timeout = steps*interval+10
        adcbuffer_full_str = str(self.serIO.read(int(steps)*52)) #Full buffer string
        self.ser.timeout = 0.25
        self.serIO.flush()

        #Decompose full list string to rows:
        adcbuffer_row_str = adcbuffer_full_str.split("\n")
        print adcbuffer_row_str
        #adcbuffer_row_str[0].split(',')[1]: voltage for row 0 ch 1
        #convert each line into list of values, append values to buffers:
        for step in range(0,len(adcbuffer_row_str)-1):
            #Convert each element into a float, save to buffer:
            self.adcbuffer0.append(float(adcbuffer_row_str[step].split(',')[0]))
            self.adcbuffer1.append(float(adcbuffer_row_str[step].split(',')[1]))
            self.adcbuffer2.append(float(adcbuffer_row_str[step].split(',')[2]))
            self.adcbuffer3.append(float(adcbuffer_row_str[step].split(',')[3]))
            #Record DAC values:
            self.dacbuffer0.append(v0[0] + step*voltagestep[0])
            self.dacbuffer1.append(v1[0] + step*voltagestep[1])
            self.dacbuffer2.append(v2[0] + step*voltagestep[2])
            self.dacbuffer3.append(v3[0] + step*voltagestep[3])
            #Append times:
            self.adctimes.append(step*interval)
        #cleanup:
        del adcbuffer_full_str
        del adcbuffer_row_str
        print("Finished!")

        #save:
        try:
            #datastructure:
            #time,DAC0,DAC1,DAC2,DAC3,ADC0,ADC1,ADC2,ADC3"
            fullfname = "data/" + filename + ".csv"
            datafile = open(fullfname,'w')
            datafile.write("time(s),DAC ch0(V),DAC ch1(V),DAC ch2(V),DAC ch3(V),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.dacbuffer0[i]) + "," + str(self.dacbuffer1[i]) + "," + str(self.dacbuffer2[i]) + "," + str(self.dacbuffer3[i]) + "," + str(self.adcbuffer0[i]) + "," + str(self.adcbuffer1[i]) + "," + str(self.adcbuffer2[i]) + "," + str(self.adcbuffer3[i]) + "\n")
            datafile.close()
            print("Data Saved")
        except IndexError:
            print("Index Error: Data not saved")
        #--Hack-- to clear buffer. BufferedRWPair does not sync.
        self.serIO.write(unicode('\r'))
        self.serIO.flush()
        self.serIO.readline()
        self.serIO.flush()
        time.sleep(0.25)
        #--Hack--
    def rampread4NB(self,v0,v1,v2,v3,steps,subsamples,interval,settle,dwell,filename):
        #setup and flags:
        self.clearBuffers()

        if interval-subsamples*dwell-settle >= 0:
            self.adc1rec = -1 #-1 = nothing in hardware buffer to read out. This is read out into sep file!
            voltagestep = [(v0[1]-v0[0])/(steps-1),(v1[1]-v1[0])/(steps-1),(v2[1]-v2[0])/(steps-1),(v3[1]-v3[0])/(steps-1)]
            datafile = open("data/" + filename,'a')
            datafile.write("time,DAC ch0(V),DAC ch1(V),DAC ch2(V),DAC ch3(V),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            datafile.close()
            for step in range(0,steps):
                print("Step " + str(step + 1) + " of " + str(steps) + ".")
                #Set DAC voltages for this step:
                self.setDAC(0,v0[0]+step*voltagestep[0])
                self.setDAC(1,v1[0]+step*voltagestep[1])
                self.setDAC(2,v2[0]+step*voltagestep[2])
                self.setDAC(3,v3[0]+step*voltagestep[3])
                #Record inferred DAC values:
                dacv0 = v0[0] + step*voltagestep[0]
                dacv1 = v1[0] + step*voltagestep[1]
                dacv2 = v2[0] + step*voltagestep[2]
                dacv3 = v3[0] + step*voltagestep[3]
                #Wait for DAC levels to settle:
                time.sleep(settle)
                #sub sample loop:
                for subsample in range(0,subsamples):
                    #Record timestamp
                    timestamp = time.strftime('"%d-%m-%y,%H:%M:%S"') #Find a way to get milliseconds too
                    #Read ADC and save values:
                    adcv0 = self.getADC(0)
                    adcv1 = self.getADC(1)
                    adcv2 = self.getADC(2)
                    adcv3 = self.getADC(3)
                    #save to file:
                    with open("data/" + filename,'a') as datafile:
                        datafile.write(str(timestamp) + "," + str(dacv0) + "," + str(dacv1) + "," + str(dacv2) + "," + str(dacv3) + "," + str(adcv0) + "," + str(adcv1) + "," + str(adcv2) + "," + str(adcv3) + "\n\r")
                    time.sleep(dwell)
                time.sleep(interval-subsamples*dwell-settle) #Unknown contribution from saving left out
            print("Finished!")
        else:
            print("Check to make sure q=interval-settle-subsamples*dwell >= 0.")
            print("Why? This is how measurements are timed:")
            print("S = Set DAC; | = subsample measurement; : = end of measurement interval")
            print("s = settle time; d = dwell time; i = interval")
            print("")
            print("S---s---->|-d-|-d-|-d-|-d-:----q---S----s----|-d-|-d-|-d-|-d-:")
            print("i = q + settle + subsamples*dwell, where q = time between DAC change and end of interval >= 0")
    def sine(self,dac,v0,angfreq,phase,offset,interval):
        commandstr = 'SIN,' + str(dac) + ',' + str(v0) + ',' + str(angfreq) + ',' + str(phase) + ',' + str(offset) + ',' + str(interval) + '\n'
        self.serIO.write(unicode(commandstr))
    def sine4(self,v00,v01,v02,v03,angfreq0,angfreq1,angfreq2,angfreq3,phase0,phase1,phase2,phase3,offset0,offset1,offset2,offset3,interval):
        #commandstr = 'SIN4,' + str(v00) + ',' + str(v01) + ',' + str(v02) + ',' + str(v03) + ',' + str(angfreq0)  + ',' + str(angfreq1)  + ',' + str(angfreq2)  + ',' + str(angfreq3) + ',' + str(phase0) + ',' + str(phase1) + ',' + str(phase2) + ',' + str(phase3) + ',' + str(offset0) + ',' + str(offset1) + ',' + str(offset2) + ',' + str(offset3) + ',' + str(interval) + '\r'
        #self.serIO.write(unicode(commandstr))
        #self.serIO.flush()

        commandstr0 = 'SIN4,' + str(v00) + ',' + str(v01) + ','
        commandstr1 = str(v02) + ',' + str(v03) + ','
        commandstr2 = str(angfreq0)  + ',' + str(angfreq1)  + ','
        commandstr3 = str(angfreq2)  + ',' + str(angfreq3) + ','
        commandstr4 = str(phase0) + ',' + str(phase1) + ','
        commandstr5 = str(phase2) + ',' + str(phase3) + ','
        commandstr6 = str(offset0) + ',' + str(offset1) + ','
        commandstr7 = str(offset2) + ',' + str(offset3) + ','
        commandstr8 = str(interval) + '\r'

        self.serIO.write(unicode(commandstr0))
        self.serIO.flush()
        self.serIO.write(unicode(commandstr1))
        self.serIO.flush()
        self.serIO.write(unicode(commandstr2))
        self.serIO.flush()
        self.serIO.write(unicode(commandstr3))
        self.serIO.flush()
        self.serIO.write(unicode(commandstr4))
        self.serIO.flush()
        self.serIO.write(unicode(commandstr5))
        self.serIO.flush()
        self.serIO.write(unicode(commandstr6))
        self.serIO.flush()
        self.serIO.write(unicode(commandstr7))
        self.serIO.flush()
        self.serIO.write(unicode(commandstr8))
        self.serIO.flush()


    def acquireOne(self,adc,nSteps,stepSize,runs,filename_base):
        for run in range(0,runs):
            #setup and flags:
            self.clearBuffers()
            self.adc1rec = adc
            print("Acquire " + str(nSteps) + " samples for " + str(nSteps*stepSize) + " sec at " + str(1.0/stepSize) + " Hz")
            #Send command over serial port:
            self.serIO.flush()
            #time.sleep(0.25)
            #self.serIO.write(unicode('\r'))
            #self.serIO.flush()
            time.sleep(0.25)
            #self.serIO.write(unicode('ACQ1,' + str(adc) + ',' + str(nSteps) + ',' + str(stepSize) + '\r')) #Send command
            #self.serIO.flush()
            self.serIO.write(unicode('ACQ1,' + str(adc))) #Send command
            self.serIO.flush()
            self.serIO.write(unicode(',' + str(nSteps) + ',')) #Send command
            self.serIO.flush()
            self.serIO.write(unicode(str(stepSize) + '\r')) #Send command
            self.serIO.flush()
            #Read acquisition data:
            self.ser.timeout = nSteps*stepSize+10.0
            adcbuffer_full_str = str(self.serIO.read(2+nSteps*13)).encode("utf-8") #Full buffer string
            self.ser.timeout = 0.25 #return to default timeout
            self.serIO.flush()
            #Decompose full list string to rows:
            adcbuffer_row_str = adcbuffer_full_str.split(",")
            #convert list into list of values:
            for i in range(0,nSteps):
                #print(adcbuffer_row_str[i])
                self.adctimes.append(i*stepSize)
                try:
                    self.adcbuffer.append(float(adcbuffer_row_str[i]))
                except ValueError:
                    print("Error converting point #%04d" %i)
                    print adcbuffer_full_str
            #cleanup:
            del adcbuffer_full_str
            del adcbuffer_row_str
            print("Finished!")

            #Save to File:
            try:
                filename = "data/" + filename_base + "_%03d.csv" % run
                #Check sizes of buffers, determine what chs are recorded:
                if self.adc1rec == 0:    #CH0 recorded
                    #datastructure:
                    #time,ch0,ch1,ch2,ch3"
                    datafile = open(filename,'w')
                    datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
                    for i in range(0,len(self.adctimes)):
                        datafile.write(str(self.adctimes[i]) + "," + str(self.adcbuffer[i]) +",,,\n")
                    datafile.close()
                if self.adc1rec == 1:#CH1 recorded
                    #datastructure:
                    #time,ch0,ch1,ch2,ch3"
                    datafile = open(filename,'w')
                    datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
                    for i in range(0,len(self.adctimes)):
                        datafile.write(str(self.adctimes[i]) + ",," + str(self.adcbuffer[i]) +",,\n")
                    datafile.close()
                if self.adc1rec == 2:#CH2 recorded
                    #datastructure:
                    #time,ch0,ch1,ch2,ch3"
                    datafile = open(filename,'w')
                    datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
                    for i in range(0,len(self.adctimes)):
                        datafile.write(str(self.adctimes[i]) + ",,," + str(self.adcbuffer[i]) +",\n")
                    datafile.close()
                if self.adc1rec == 3:#CH3 recorded
                    #datastructure:
                    #time,ch0,ch1,ch2,ch3"
                    datafile = open(filename,'w')
                    datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
                    for i in range(0,len(self.adctimes)):
                        datafile.write(str(self.adctimes[i]) + ",,,," + str(self.adcbuffer[i]) +"\n")
                    datafile.close()
                print("Data Saved")
            except IndexError:
                print("Index error. Data not saved.")

            #--Hack-- to clear buffer. BufferedRWPair does not sync.
            self.serIO.write(unicode('\r'))
            self.serIO.flush()
            self.serIO.readline()
            time.sleep(0.25)
            #--Hack--



    def acquireTwo(self,adcA,adcB,nSteps,stepSize,filename):
        #setup and flags:
        self.clearBuffers()
        self.adc1rec = - 3
        self.adcrecA = adcA
        self.adcrecB = adcB
        bufferv_xdim = 4
        bufferv_ydim = 5000

        #Check that adcA and adcB are indeed different channels.
        if adcA != adcB:
            #write command:
            print("Acquire " + str(nSteps) + " samples for " + str(nSteps*stepSize) + " sec at " + str(1.0/stepSize) + " Hz")
            self.serIO.flush()
            self.serIO.write(unicode('ACQ2,' + str(adcA) + ',' + str(adcB) + ',' + str(nSteps) + ',' + str(stepSize) + '\r'))
            self.serIO.flush()
            #read data from serial port:
            self.ser.timeout = nSteps*stepSize+1.0
            adcbuffer_full_str = str(self.serIO.read(nSteps*52)) #Full buffer string
            self.ser.timeout = 0.25 #return to default timeout
            #Decompose full list string to rows:
            adcbuffer_row_str = adcbuffer_full_str.split("\n")
            #convert each line into list of values, append values to buffers:
            for step in range(0,nSteps-1):
                xidx = int(floor((2*step) / bufferv_ydim))
                yidxA = int(((2*step) % bufferv_ydim))
                yidxB = int(yidxA + 1)
                rowarrstr = adcbuffer_row_str[yidxA].split(',')
                #Convert each element into a float, save to buffer only if data collected for that channel:
                try:
                    if adcA == 0:
                        self.adcbuffer0.append(float(rowarrstr[xidx]))
                    if adcA == 1:
                        self.adcbuffer1.append(float(rowarrstr[xidx]))
                    if adcA == 2:
                        self.adcbuffer2.append(float(rowarrstr[xidx]))
                    if adcA == 3:
                        self.adcbuffer3.append(float(rowarrstr[xidx]))
                    if adcB == 0:
                        self.adcbuffer0.append(float(rowarrstr[xidx]))
                    if adcB == 1:
                        self.adcbuffer1.append(float(rowarrstr[xidx]))
                    if adcB == 2:
                        self.adcbuffer2.append(float(rowarrstr[xidx]))
                    if adcB == 3:
                        self.adcbuffer3.append(float(rowarrstr[xidx]))
                except ValueError:
                    print("Failure at xidx: " + str(xidx))
                    print("          yidxA: " + str(yidxA))
                    print("          yidxB: " + str(yidxB))
                    print("           step: " + str(step))
                #Append times:
                self.adctimes.append(step*stepSize)
            #Fill arrays not used (to maintain array lengths for save-to-file function)
            if len(self.adcbuffer0) == 0:
                for step in range(0,nSteps-2):
                    self.adcbuffer0.append('')
            if len(self.adcbuffer1) == 0:
                for step in range(0,nSteps-2):
                    self.adcbuffer1.append('')
            if len(self.adcbuffer2) == 0:
                for step in range(0,nSteps-2):
                    self.adcbuffer2.append('')
            if len(self.adcbuffer3) == 0:
                for step in range(0,nSteps-2):
                    self.adcbuffer3.append('')
            print("Finished!")

            #Save:
            try:
                #datastructure:
                #time,ch0,ch1,ch2,ch3"
                fullfname = "data/" + filename + ".csv"
                datafile = open(fullfname,'w')
                datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
                for i in range(0,len(self.adctimes)):
                    datafile.write(str(self.adctimes[i]) + "," + str(self.adcbuffer0[i]) + "," + str(self.adcbuffer1[i]) + "," + str(self.adcbuffer2[i]) + "," + str(self.adcbuffer3[i]) + "\n")
                datafile.close()
                print("Data saved.")
            except IndexError:
                print("Index Error: Data not saved.")
            self.serIO.flush()
            #--Hack-- to clear buffer. BufferedRWPair does not sync.
            self.serIO.write(unicode('\r'))
            self.serIO.flush()
            self.serIO.readline()
            time.sleep(0.25)
            #--Hack--
        else:
            print("ODAC Error: Duplicate adc channel selected. Canceled acquisition.")
    def acquireAll(self,nSteps,stepSize,filename):
        self.clearBuffers()
        self.adc1rec = - 2
        self.serIO.flush()
        #self.serIO.write(unicode('ACQA,' + str(nSteps) + ',' + str(stepSize) + '\r'))
        self.serIO.write(unicode('ACQA,' + str(nSteps)))
        self.serIO.flush()
        self.serIO.write(unicode(',' + str(stepSize) + '\r'))
        self.serIO.flush()
        self.ser.timeout = nSteps*stepSize+10
        print("Acquire " + str(nSteps) + " samples for " + str(nSteps*stepSize) + " sec at " + str(1.0/stepSize) + " Hz")
        adcbuffer_full_str = str(self.serIO.read(nSteps*52)) #Full buffer string
        self.ser.timeout = 0.25 #return to default timeout
        #Decompose full list string to rows:
        adcbuffer_row_str = adcbuffer_full_str.split("\n")
        #convert each line into list of values, append values to buffers:
        for step in range(0,len(adcbuffer_row_str)-1):
            #print rowstr2
            #Convert each element into a float, save to buffer:
            self.adcbuffer0.append(float(adcbuffer_row_str[step].split(',')[0]))
            self.adcbuffer1.append(float(adcbuffer_row_str[step].split(',')[1]))
            self.adcbuffer2.append(float(adcbuffer_row_str[step].split(',')[2]))
            self.adcbuffer3.append(float(adcbuffer_row_str[step].split(',')[3]))
            #Append times:
            self.adctimes.append(step*stepSize)
        print("Finished!")
        #Save:
        try:
            #datastructure:
            #time,ch0,ch1,ch2,ch3"
            fullfname = "data/" + filename + ".csv"
            datafile = open(fullfname,'w')
            datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.adcbuffer0[i]) + "," + str(self.adcbuffer1[i]) + "," + str(self.adcbuffer2[i]) + "," + str(self.adcbuffer3[i]) + "\n")
            datafile.close()
            print("Data Saved")
        except IndexError:
            print("Index Error: Data not saved")
        self.serIO.flush()
        #--Hack-- to clear buffer. BufferedRWPair does not sync.
        self.serIO.write(unicode('\r'))
        self.serIO.flush()
        self.serIO.readline()
        time.sleep(0.25)
        #--Hack--
    def viewPDS(self,channel,gain,runs,filename_base):
        print("Loading PDS. Please be patient!")
        #Construct execution string:
        commandstr =  "python tt_to_pds.py " + str(channel) + " " + str(gain) + " "
        #print commandstr
        for run in range(0,runs):
            commandstr = commandstr + "data/" + filename_base + "_%03d.csv" % run + " "

        #run tt_to_pds.py:
        os.system(commandstr)
