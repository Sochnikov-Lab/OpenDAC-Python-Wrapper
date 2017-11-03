import serial
import io

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

        #Quad CH acquire buffers:
        self.adcbuffer0 = []
        self.adcbuffer1 = []
        self.adcbuffer2 = []
        self.adcbuffer3 = []

    #Attempts to open serial instance
    def open(self,COMPORT,BAUDRATE=115200,verbose=0):
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

            #Check if Device is Ready:
            self.serIO.write(unicode('*RDY?\r'))
            self.serIO.flush()
            status = str(self.serIO.readline()).rstrip().lstrip()
            if status == "READY":
                self.ready = True
            else:
                self.ready = False

            if self.ser.isOpen == True and verbose == 1:
                print("================Connection==================")
                print("o  Port:            " + self.ser.port)
                print("o  Baudrate:        " + str(self.ser.baudrate))
                print("o  DeviceID:        " + self.ID)
                print("o  Device Status:   " + status)
                print("============================================")
        except serial.SerialException:
            print("**ODAC: Failed to open serial port**")

    def close(self,verbose=0):
        try:
            self.ser.close()
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
        self.serIO.write(unicode('SET,'+ str(channel) +',' + str(voltage) + '\r'))
        self.serIO.flush()
    def ramp1(self,adc,dac,v1,v2,steps,interval):
        self.serIO.write(unicode('RAR1,'+ str(adc) + ',' + str(dac) + ',' + str(v1) + ',' + str(v2) + ',' + str(steps) + ',' + str(interval) + ',' + '\r'))
        self.serIO.flush()
        adcbufferstr = str(self.serIO.readline()).rstrip().lstrip() #read ascii from serial port
        self.serIO.flush()
        print(adcbufferstr)
        self.adcbuffer = adcbufferstr.split(',') #break string into a list
        #for i in range(0,len(self.adcbuffer)):
        #    self.adcbuffer[i] = float(self.adcbuffer[i])
    #output a sine wave on one channel
    def sine(self,dac,v0,angfreq,phase,offset,nsteps,interval):
        commandstr = 'SIN,' + str(dac) + ',' + str(v0) + ',' + str(angfreq) + ',' + str(phase) + ',' + str(offset) + ',' + str(nsteps) + ',' + str(interval) + '\n'
        #print commandstr
        self.serIO.write(unicode(commandstr))
    def acquireOne(self,adc,nSteps,stepSize):
        self.adc1rec = adc
        #Clear buffers:
        self.adctimes[:] = []
        self.adcbuffer[:] = []
        self.adcbuffer0[:] = []
        self.adcbuffer1[:] = []
        self.adcbuffer2[:] = []
        self.adcbuffer3[:] = []
        commandstr = 'ACQ1,' + str(adc) + ',' + str(nSteps) + ',' + str(stepSize) + '\n'
        self.serIO.write(unicode(commandstr)) #Send command
        self.serIO.flush()


        self.ser.timeout = nSteps*stepSize+1.0
        print("Acquire for: " + str(self.ser.timeout) + " sec")

        adcbuffer_full_str = str(self.serIO.read(nSteps*10)) #Full buffer string

        self.ser.timeout = 0.25 #return to default timeout
        #Decompose full list string to rows:
        adcbuffer_row_str = adcbuffer_full_str.split("\n")

        #convert list into list of values:
        for i in range(0,len(adcbuffer_row_str)):
            self.adctimes.append(i*stepSize)
            self.adcbuffer.append(float(adcbuffer_row_str[i]))

        #cleanup:
        del adcbuffer_full_str
        del adcbuffer_row_str


    def acquireAll(self,nSteps,stepSize):

        self.adc1rec = - 2
        #Clear buffers
        self.adcbuffer[:] = []
        self.adcbuffer0[:] = []
        self.adcbuffer1[:] = []
        self.adcbuffer2[:] = []
        self.adcbuffer3[:] = []
        commandstr = 'ACQA,' + str(nSteps) + ',' + str(stepSize) + '\n'
        self.serIO.write(unicode(commandstr))
        self.serIO.flush()

        self.ser.timeout = nSteps*stepSize+1.0
        print("Acquire for: " + str(self.ser.timeout) + " sec")
        adcbuffer_full_str = str(self.serIO.read(nSteps*46)) #Full buffer string
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

        print(self.adcbuffer0)

    def saveToFile(self,filename):
        #datastructure:
        #time,ch0,ch1,ch2,ch3"

        datafile = open(filename,'w')
        datafile.write("time(s),ch0(V),ch1(V),ch2(V),ch3(V)\n")

        #Check sizes of buffers, determine what chs are recorded:
        if self.adc1rec == 0:    #CH0 recorded
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.adcbuffer[i]) +",,,\n")
        if self.adc1rec == 1:#CH1 recorded
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + ",," + str(self.adcbuffer[i]) +",,\n")
        if self.adc1rec == 2:#CH2 recorded
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + ",,," + str(self.adcbuffer[i]) +",\n")
        if self.adc1rec == 3:#CH3 recorded
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + ",,,," + str(self.adcbuffer[i]) +"\n")
        if self.adc1rec == -1:#NOTHING recorded
            print "User Error: No data collected"
        if self.adc1rec == -2:#ALL recorded
            for i in range(0,len(self.adctimes)):
                datafile.write(str(self.adctimes[i]) + "," + str(self.adcbuffer0[i]) + "," + str(self.adcbuffer1[i]) + "," + str(self.adcbuffer2[i]) + "," + str(self.adcbuffer3[i]) + "\n")
        datafile.close()
