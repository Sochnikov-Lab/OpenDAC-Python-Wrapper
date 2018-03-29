import serial
import io
from math import floor

#Open DAC-ADC Class
class ODAC(object):
    #Initialization: create necessary variables and configurable serial instance
    def __init__(self):
        self.ID = ''         #ID of instrument
        self.ready = False   #If device is ready for command
        self.ser = serial.Serial() #Serial Instance
        self.ser.timeout = 0.25 #read timeout --Should fix this to get rid of latency
        self.serIO = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser),newline='\r\n')
        self.adctimes = []
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

            #--Hack --
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
    def getADC(self,channel):
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
    #RR1 Needs work
    def rampread1(self,adc,dac,v1,v2,steps,interval):
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
        self.adc1rec = -4 #-4 = rampread1 or rampread4
        voltagestep = (v2 - v1)/steps

        self.serIO.write(unicode('RAR1,'+ str(adc) + ',' + str(dac) + ',' + str(v1) + ',' + str(v2) + ',' + str(steps) + ',' + str(interval) + ',' + '\r'))
        self.serIO.flush()

        #adcbufferstr = str(self.serIO.readline()).rstrip().lstrip() #read ascii from serial port
        self.ser.timeout = steps*interval+5.0
        adcbufferstr = str(self.serIO.read(int(steps)*13)) #Full buffer string
        self.ser.timeout = 0.25 #return to default timeout
        #Decompose full list string to rows:
        adcbufferrowstr = adcbufferstr.split("\n")

        self.serIO.flush()
        if adc == 0:
            for i in range(0,len(adcbufferrowstr)):
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

        for step in range(0,int(steps)):
            self.adctimes.append(step*interval)
            #Fill in unused arrays (fixes save-to-file function error for empty lists)
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
                self.dacbuffer0.append(voltagestep*step)
                self.dacbuffer1.append('')
                self.dacbuffer2.append('')
                self.dacbuffer3.append('')
            if dac == 1:
                self.dacbuffer0.append('')
                self.dacbuffer1.append(voltagestep*step)
                self.dacbuffer2.append('')
                self.dacbuffer3.append('')
            if dac == 2:
                self.dacbuffer0.append('')
                self.dacbuffer1.append('')
                self.dacbuffer2.append(voltagestep*step)
                self.dacbuffer3.append('')
            if dac == 3:
                self.dacbuffer0.append('')
                self.dacbuffer1.append('')
                self.dacbuffer2.append('')
                self.dacbuffer3.append(voltagestep*step)

    def rampread4(self,v0,v1,v2,v3,steps,interval):
        self.adctimes[:] = []
        self.adcbuffer[:] = []
        self.adcbuffer0[:] = []
        self.adcbuffer1[:] = []
        self.adcbuffer2[:] = []
        self.adcbuffer3[:] = []
        self.serIO.write(unicode('RARA,'+ str(v0[0]) + ',' + str(v0[1]) + ',' + str(v1[0]) + ',' + str(v1[1]) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v3[0]) + ',' + str(v3[1]) + ',' + str(steps) + ',' + str(interval) + ',' + '\r'))
        self.serIO.flush2()
        adcbuffer_full_str = str(self.serIO.read(nSteps*13)) #Full buffer string
        self.serIO.flush()
        #Decompose full list string to rows:
        adcbuffer_row_str = adcbuffer_full_str.split("\n")
        #adcbuffer_row_str[0].split(',')[1] EXAMPLE OF: voltage for row 0 ch 1
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
        #cleanup:
        del adcbuffer_full_str
        del adcbuffer_row_str
    def sine(self,dac,v0,angfreq,phase,offset,interval):
        commandstr = 'SIN,' + str(dac) + ',' + str(v0) + ',' + str(angfreq) + ',' + str(phase) + ',' + str(offset) + ',' + str(interval) + '\n'
        self.serIO.write(unicode(commandstr))
    def sine4(self,v00,v01,v02,v03,angfreq0,angfreq1,angfreq2,angfreq3,phase0,phase1,phase2,phase3,offset0,offset1,offset2,offset3,interval):
        commandstr = 'SIN4,' + str(v00) + ',' + str(v01) + ',' + str(v02) + ',' + str(v03) + ',' + str(angfreq0)  + ',' + str(angfreq1)  + ',' + str(angfreq2)  + ',' + str(angfreq3) + ',' + str(phase0) + ',' + str(phase1) + ',' + str(phase2) + ',' + str(phase3) + ',' + str(offset0) + ',' + str(offset1) + ',' + str(offset2) + ',' + str(offset3) + ',' + str(interval) + '\n'
        self.serIO.write(unicode(commandstr))
    def acquireOne(self,adc,nSteps,stepSize):
        self.adc1rec = adc
        self.adcrecA = -1
        self.adcrecB = -1
        #Clear buffers:
        self.adctimes[:] = []
        self.adcbuffer[:] = []
        self.adcbuffer0[:] = []
        self.adcbuffer1[:] = []
        self.adcbuffer2[:] = []
        self.adcbuffer3[:] = []
        commandstr = 'ACQ1,' + str(adc) + ',' + str(nSteps) + ',' + str(stepSize) + '\n'
        print("Acquire " + str(nSteps) + " samples for " + str(nSteps*stepSize) + " sec at " + str(1.0/stepSize) + " Hz")
        self.serIO.flush()
        self.serIO.write(unicode(commandstr)) #Send command
        self.serIO.flush()
        self.ser.timeout = nSteps*stepSize+5.0
        adcbuffer_full_str = str(self.serIO.read(nSteps*13)) #Full buffer string
        self.ser.timeout = 0.25 #return to default timeout
        #Decompose full list string to rows:
        adcbuffer_row_str = adcbuffer_full_str.split("\n")
        #convert list into list of values:
        #for i in range(0,len(adcbuffer_row_str)):
        for i in range(0,nSteps):
            self.adctimes.append(i*stepSize)
            self.adcbuffer.append(float(adcbuffer_row_str[i]))
        #self.adctimes = np.linspace(0,stepSize*nSteps,num=nSteps)
        #cleanup:
        del adcbuffer_full_str
        del adcbuffer_row_str
    #acq2 needs work
    def acquireTwo(self,adcA,adcB,nSteps,stepSize):
        self.adc1rec = - 3
        self.adcrecA = adcA
        self.adcrecB = adcB
        #Clear buffers
        self.adctimes[:] = []
        self.adcbuffer[:] = []
        self.adcbuffer0[:] = []
        self.adcbuffer1[:] = []
        self.adcbuffer2[:] = []
        self.adcbuffer3[:] = []
        bufferv_xdim = 4
        bufferv_ydim = 5000
        commandstr = 'ACQ2,' + str(adcA) + ',' + str(adcB) + ',' + str(nSteps) + ',' + str(stepSize) + '\n'
        if adcA != adcB:
            self.serIO.write(unicode(commandstr))
            self.serIO.flush()
            self.ser.timeout = nSteps*stepSize+1.0
            print("Acquire " + str(nSteps) + " samples for " + str(nSteps*stepSize) + " sec at " + str(1.0/stepSize) + " Hz")
            adcbuffer_full_str = str(self.serIO.read(nSteps*52)) #Full buffer string
            self.ser.timeout = 0.25 #return to default timeout
            #Decompose full list string to rows:
            adcbuffer_row_str = adcbuffer_full_str.split("\n")
            #convert each line into list of values, append values to buffers:
            for step in range(0,nSteps-2):
                xidx = int(floor((2*step) / bufferv_ydim))
                yidxA = int(((2*step) % bufferv_ydim))
                yidxB = int(yidxA + 1)
                rowarrstr = adcbuffer_row_str[yidxA].split(',')
                print rowarrstr
                #Convert each element into a float, save to buffer only if data collected for that channel:
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


        else:
            print("ODAC Error: Duplicate adc channel selected. Canceled acquisition.")
    def acquireAll(self,nSteps,stepSize):

        self.adc1rec = - 2
        self.adcrecA = -1
        self.adcrecB = -1
        #Clear buffers
        self.adctimes[:] = []
        self.adcbuffer[:] = []
        self.adcbuffer0[:] = []
        self.adcbuffer1[:] = []
        self.adcbuffer2[:] = []
        self.adcbuffer3[:] = []
        commandstr = 'ACQA,' + str(nSteps) + ',' + str(stepSize) + '\n'
        self.serIO.write(unicode(commandstr))
        self.serIO.flush()

        self.ser.timeout = nSteps*stepSize+1.0
        print("Acquire " + str(nSteps) + " samples for " + str(nSteps*stepSize) + " sec at " + str(1.0/stepSize) + " Hz")
        adcbuffer_full_str = str(self.serIO.read(nSteps*52)) #Full buffer string
        self.ser.timeout = 0.25 #return to default timeout

        #Decompose full list string to rows:
        adcbuffer_row_str = adcbuffer_full_str.split("\n")
        #adcbuffer_row_str[0].split(',')[1] EXAMPLE OF: voltage for row 0 ch 1

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
    def saveToFile(self,filename):
        #datastructure:
        #time,ch0,ch1,ch2,ch3"
        #Check sizes of buffers, determine what chs are recorded:
        if self.adc1rec == 0:    #CH0 recorded
            print("Saved CH0 to file")
            datafile = open(filename,'w')
            datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.adcbuffer[i]) +",,,\n")
            datafile.close()
        if self.adc1rec == 1:#CH1 recorded
            print("Saved CH1 to file")
            datafile = open(filename,'w')
            datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + ",," + str(self.adcbuffer[i]) +",,\n")
            datafile.close()
        if self.adc1rec == 2:#CH2 recorded
            print("Saved CH2 to file")
            datafile = open(filename,'w')
            datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + ",,," + str(self.adcbuffer[i]) +",\n")
            datafile.close()
        if self.adc1rec == 3:#CH3 recorded
            print("Saved CH3 to file")
            datafile = open(filename,'w')
            datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + ",,,," + str(self.adcbuffer[i]) +"\n")
            datafile.close()
        if self.adc1rec == -1:#NOTHING recorded
            print "User Error: No data collected"
        if self.adc1rec == -2:#ALL recorded
            print("Saved CH0-CH3 to file")
            datafile = open(filename,'w')
            datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.adcbuffer0[i]) + "," + str(self.adcbuffer1[i]) + "," + str(self.adcbuffer2[i]) + "," + str(self.adcbuffer3[i]) + "\n")
            datafile.close()
        if self.adc1rec == -3:#Two recorded
            print("Saved two channels to file")
            datafile = open(filename,'w')
            datafile.write("time(s),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.adcbuffer0[i]) + "," + str(self.adcbuffer1[i]) + "," + str(self.adcbuffer2[i]) + "," + str(self.adcbuffer3[i]) + "\n")
            datafile.close()
        if self.adc1rec == -4:#Ramp and Read 1 or 4
            print("Saved Ramp and Read CH0 to file")
            datafile = open(filename,'w')
            datafile.write("time(s),DAC ch0(V),DAC ch1(V),DAC ch2(V),DAC ch3(V),ADC ch0(V),ADC ch1(V),ADC ch2(V),ADC ch3(V)\n")
            print len(self.dacbuffer0)
            print len(self.dacbuffer1)
            print len(self.dacbuffer2)
            print len(self.dacbuffer3)
            print len(self.adcbuffer0)
            print len(self.adcbuffer1)
            print len(self.adcbuffer2)
            print len(self.adcbuffer3)
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.dacbuffer0[i]) + "," + str(self.dacbuffer1[i]) + "," + str(self.dacbuffer2[i]) + "," + str(self.dacbuffer3[i]) + "," + str(self.adcbuffer0[i]) + "," + str(self.adcbuffer1[i]) + "," + str(self.adcbuffer2[i]) + "," + str(self.adcbuffer3[i]) + "\n")
            datafile.close()
