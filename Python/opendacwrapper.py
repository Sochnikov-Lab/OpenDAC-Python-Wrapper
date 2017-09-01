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
        self.adcbuffer = {}
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

    #acquire readings with sample rate 'SampleRate' (samples per microsecond) over time 'CollectPeriod' (microseconds):
    #with Integration time IntTime
    #def acq1(self,adc1,CollectPeriod,SampleRate,IntTime):
