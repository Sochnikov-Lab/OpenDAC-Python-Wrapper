#####OpenDAC Graphical Interface#####
#opendac_gui.py
#Written by J. Sheldon for the Sochnikov lab group at UConn Physics Department
#
#This is the code for our OpenDAC controller application. It contains the GUI
#"Glue" code between the UI design file and the wrapper object ODAC. It also
#contains user input validation to attempt to thwart crashing and illegal operations.
#Complete usage of this GUI requires the opendacwrapper.py and opendac_gui.ui file.
#In addition, PyQT5 and PySerial need to be installed and The OpenDAC DAC-ADC also
#needs our custom firmware installed.


import sys
import serial
import io
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from opendacwrapper import ODAC
from time import sleep
from math import pi

class openDAC_UI(QMainWindow):
    def __init__(self,myODAC):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi("opendac_gui.ui")
        self.DAC = myODAC
        #Bindings:
        #Serial Related Widgets
        self.ui.buttsp_conn.clicked.connect(self.serialConnect)
        self.ui.buttsp_disconn.clicked.connect(self.serialDisconnect)
        self.ui.coboxsp_prt.addItems(["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10","/dev/ttyACM0","/dev/ttyACM1","/dev/ttyACM2","/dev/ttyS0","/dev/ttyS1","/dev/ttyS2"])
        #ACQ1 Related Widgets
        self.ui.butta1_start.clicked.connect(self.ACQ1Start)
        self.ui.lea1_samples.setText("20000")
        self.ui.lea1_srate.setText("2000")
        #ACQ2 Related Widgets
        self.ui.butta2_start.clicked.connect(self.ACQ2Start)
        self.ui.lea2_samples.setText("10000")
        self.ui.lea2_srate.setText("2000")
        #ACQ4 Related Widgets
        self.ui.butta4_start.clicked.connect(self.ACQ4Start)
        self.ui.lea4_samples.setText("5000")
        self.ui.lea4_srate.setText("2000")
        #RAR1 Related Widgets
        self.ui.buttrr1_start.clicked.connect(self.RAR1Start)
        self.ui.ler1_steps.setText("20000")
        self.ui.ler1_intrv.setText("0.0005")
        self.ui.ler1vi.setText("0.0")
        self.ui.ler1vi.setText("0.0")
        self.ui.ler1vf.setText("0.0")
        #RAR4 Related Widgets
        self.ui.buttrr4_start.clicked.connect(self.RAR4Start)
        self.ui.ler4_steps.setText("5000")
        self.ui.ler4_intrv.setText("0.0005")
        self.ui.ler4vi_ch0.setText("0.0")
        self.ui.ler4vf_ch0.setText("0.0")
        self.ui.ler4vi_ch1.setText("0.0")
        self.ui.ler4vf_ch1.setText("0.0")
        self.ui.ler4vi_ch2.setText("0.0")
        self.ui.ler4vf_ch2.setText("0.0")
        self.ui.ler4vi_ch3.setText("0.0")
        self.ui.ler4vf_ch3.setText("0.0")
        #RAR4NB Related Widgets
        self.ui.buttrr4_start_2.clicked.connect(self.RAR4NBStart)
        self.ui.ler4_steps_2.setText("10")
        self.ui.ler4_subsamples_2.setText("5")
        self.ui.ler4_intrv_2.setText("6")
        self.ui.ler4_settle_2.setText("2")
        self.ui.ler4_dwell_2.setText("0.25")
        self.ui.ler4vi_ch0_2.setText("0.0")
        self.ui.ler4vf_ch0_2.setText("0.0")
        self.ui.ler4vi_ch1_2.setText("0.0")
        self.ui.ler4vf_ch1_2.setText("0.0")
        self.ui.ler4vi_ch2_2.setText("0.0")
        self.ui.ler4vf_ch2_2.setText("0.0")
        self.ui.ler4vi_ch3_2.setText("0.0")
        self.ui.ler4vf_ch3_2.setText("0.0")
        #DCOut Related Widgets
        self.ui.buttset_ch0.clicked.connect(self.DCSetCH0)
        self.ui.buttset_ch1.clicked.connect(self.DCSetCH1)
        self.ui.buttset_ch2.clicked.connect(self.DCSetCH2)
        self.ui.buttset_ch3.clicked.connect(self.DCSetCH3)
        self.ui.buttset_all.clicked.connect(self.DCSetAll)
        self.ui.buttset_0v.clicked.connect(self.DCReset0V)
        self.ui.leset_ch0.setText("0.0")
        self.ui.leset_ch1.setText("0.0")
        self.ui.leset_ch2.setText("0.0")
        self.ui.leset_ch3.setText("0.0")
        #SineOut Related Widgets
        self.ui.buttsin_start.clicked.connect(self.SineOut)
        #DataOut Related Widgets
        self.ui.leout_fname.setText("data")
        self.ui.butts_csv.clicked.connect(self.DataOut_CSV)
    def serialConnect(self):#Evt Handler for serial connect button
        port = self.ui.coboxsp_prt.currentText()
        baud = self.ui.lesp_baud.text()
        print("Attempting to connect to: " + str(port) + ":" + str(baud))
        self.DAC.open(port,baud)
        if self.DAC.ready == True:
            print("Connected Successfully")
            self.ui.buttsp_disconn.setEnabled(True)
            self.ui.buttsp_conn.setEnabled(False)
            self.DAC.setConvTime(0,82)
            self.DAC.setConvTime(1,82)
            self.DAC.setConvTime(2,82)
            self.DAC.setConvTime(3,82)
    def serialDisconnect(self):#Evt Handler for serial connect button
        self.DAC.close()
        if self.DAC.ready == False:
            print("Disconnected Successfully")
            self.ui.buttsp_disconn.setEnabled(False)
            self.ui.buttsp_conn.setEnabled(True)
    def ACQ1Start(self):
        failed = 0
        try: #check for value error (unexepected datatype)
            samples = int(self.ui.lea1_samples.text())
            stepsize = 1.0/float(self.ui.lea1_srate.text())
        except ValueError:
            print("Error: Issue with values given.")
            failed = 1
        if failed == 0:
            if samples <= 20000 and stepsize >= 1.0/2000.0: #Make sure hardware limits are respected
                if self.DAC.ready == True:
                    if self.ui.rba1_ch0.isChecked(): #Ch0 radiobutton selected
                        print("CH0 Selected.")
                        self.DAC.acquireOne(0,samples,stepsize)
                    if self.ui.rba1_ch1.isChecked():#Ch1 radiobutton selected
                        print("CH1 Selected.")
                        self.DAC.acquireOne(1,samples,stepsize)
                    if self.ui.rba1_ch2.isChecked():#Ch2 radiobutton selected
                        print("CH2 Selected.")
                        self.DAC.acquireOne(2,samples,stepsize)
                    if self.ui.rba1_ch3.isChecked():#Ch3 radiobutton selected
                        print("CH3 Selected.")
                        self.DAC.acquireOne(3,samples,stepsize)
                else:
                    print("Error: Check Serial Connection")
            else:
                print("Acquire Halted: too many samples (max 20000) or sample rate too fast (max 2kHz)")
        else:
            print("Error: User input bad. Check input fields.")
    def ACQ2Start(self):
        failed = 0
        try:
            samples = int(self.ui.lea2_samples.text())
            stepSize = 1.0/float(self.ui.lea2_srate.text())
        except ValueError:
            print("Error: Issue with values given.")
            failed = 1
        if failed == 0:
            if samples <= 10000 and stepSize >= 1.0/2000.0: #Make sure hardware limits are respected
                if self.DAC.ready == True:
                    if not ((self.ui.rba2_ch0A.isChecked() and self.ui.rba2_ch0B.isChecked()) or (self.ui.rba2_ch1A.isChecked() and self.ui.rba2_ch1B.isChecked()) or (self.ui.rba2_ch2A.isChecked() and self.ui.rba2_ch2B.isChecked()) or (self.ui.rba2_ch3A.isChecked() and self.ui.rba2_ch3B.isChecked())):
                        print("Channel Selection Okay")
                        if self.ui.rba2_ch0A.isChecked():
                            adcA = 0
                        if self.ui.rba2_ch1A.isChecked():
                            adcA = 1
                        if self.ui.rba2_ch2A.isChecked():
                            adcA = 2
                        if self.ui.rba2_ch3A.isChecked():
                            adcA = 3
                        if self.ui.rba2_ch0B.isChecked():
                            adcB = 0
                        if self.ui.rba2_ch1B.isChecked():
                            adcB = 1
                        if self.ui.rba2_ch2B.isChecked():
                            adcB = 2
                        if self.ui.rba2_ch3B.isChecked():
                            adcB = 3
                        self.DAC.acquireTwo(adcA,adcB,samples,stepSize)
                    else:
                        print("Error: Incorrect Channel Selection.")
                else:
                    print("Error: Check Serial Connection")
            else:
                print("Acquire Halted: too many samples (max 20000) or sample rate too fast (max 2kHz)")
        else:
            print("Error: User input bad. Check input fields.")
    def ACQ4Start(self):
        if self.DAC.ready == True:
            failed = 0
            try:
                samples = int(self.ui.lea4_samples.text())
                stepsize = 1.0/float(self.ui.lea4_srate.text())
            except ValueError:
                print("Error: Issue with values given.")
                failed = 1
            if failed == 0:
                if samples <= 5000 and stepsize >= 1.0/2000.0:    #Ramp1 Event Handlers
                    self.DAC.acquireAll(samples,stepsize)
                else:
                    print("Acquire Halted: too many samples (max 5000) or sample rate too fast (max 2kHz)")
            else:
                print("Error: User input bad. Check input fields.")
        else:
            print("Error: Check Serial Connection")
    def RAR1Start(self):
        if self.DAC.ready == True:

            #ADC Selection:
            if self.ui.rbrr1_ch0.isChecked():
                adc = 0
            if self.ui.rbrr1_ch1.isChecked():
                adc = 1
            if self.ui.rbrr1_ch2.isChecked():
                adc = 2
            if self.ui.rbrr1_ch3.isChecked():
                adc = 3
            #DAC Selection:
            if self.ui.rbr1_ch0.isChecked():
                dac = 0
            if self.ui.rbr1_ch1.isChecked():
                dac = 1
            if self.ui.rbr1_ch2.isChecked():
                dac = 2
            if self.ui.rbr1_ch3.isChecked():
                dac = 3
            #Do some checks and run:
            failed = 0
            try:
                v1 = float(self.ui.ler1vi.text())
                v2 = float(self.ui.ler1vf.text())
                steps = float(self.ui.ler1_steps.text())
                interval = float(self.ui.ler1_intrv.text())
            except ValueError:
                print("Error: Issue with values given.")
                failed = 1
            if failed == 0:
                if v1 >= -10.0 and v1 <= 10.0 and v2 >= -10.0 and v2 <= 10.0:
                    self.DAC.rampread1(adc,dac,v1,v2,steps,interval)
                else:
                    print("Error: Check Voltage Range")
            else:
                print("Error: User input bad. Check input fields.")

        else:
            print("Error: Check Serial Connection")
    def RAR4Start(self):
        if self.DAC.ready == True:
            #Do some checks and run:
            failed = 0
            try:
                v0 = [float(self.ui.ler4vi_ch0.text()),float(self.ui.ler4vf_ch0.text())]
                v1 = [float(self.ui.ler4vi_ch1.text()),float(self.ui.ler4vf_ch1.text())]
                v2 = [float(self.ui.ler4vi_ch2.text()),float(self.ui.ler4vf_ch2.text())]
                v3 = [float(self.ui.ler4vi_ch3.text()),float(self.ui.ler4vf_ch3.text())]
                steps = float(self.ui.ler4_steps.text())
                interval = float(self.ui.ler4_intrv.text())
                ch0inrange = v0[0] >= -10.0 and v0[0] <= 10.0 and v0[1] >= -10.0 and v0[1]  <= 10.0
                ch1inrange = v1[0] >= -10.0 and v1[0] <= 10.0 and v1[1] >= -10.0 and v1[1] <= 10.0
                ch2inrange = v2[0] >= -10.0 and v2[0] <= 10.0 and v2[1] >= -10.0 and v2[1] <= 10.0
                ch3inrange = v3[0] >= -10.0 and v3[0] <= 10.0 and v3[1] >= -10.0 and v3[1] <= 10.0
            except ValueError:
                print("Error: Issue with values given.")
                failed = 1
            if failed == 0:
                if ch0inrange and ch1inrange and ch2inrange and ch3inrange:
                    print("RAR4 Started.")
                    self.DAC.rampread4(v0,v1,v2,v3,steps,interval)
                else:
                    print("Error: Check Voltage Range")
            else:
                print("Error: User input bad. Check input fields.")

        else:
            print("Error: Check Serial Connection")
    def RAR4NBStart(self):
        if self.DAC.ready == True:
            #Do some checks and run:
            failed = 0
            try:
                v0 = [float(self.ui.ler4vi_ch0_2.text()),float(self.ui.ler4vf_ch0_2.text())]
                v1 = [float(self.ui.ler4vi_ch1_2.text()),float(self.ui.ler4vf_ch1_2.text())]
                v2 = [float(self.ui.ler4vi_ch2_2.text()),float(self.ui.ler4vf_ch2_2.text())]
                v3 = [float(self.ui.ler4vi_ch3_2.text()),float(self.ui.ler4vf_ch3_2.text())]
                steps = float(self.ui.ler4_steps_2.text())
                interval = float(self.ui.ler4_intrv_2.text())
                settle = float(self.ui.ler4_settle_2.text())
                dwell = float(self.ui.ler4_dwell_2.text())
                subsamples = float(self.ui.ler4_subsamples_2.text())
                filename = float(self.ui.ler4_fname_2.text())
                ch0inrange = v0[0] >= -10.0 and v0[0] <= 10.0 and v0[1] >= -10.0 and v0[1]  <= 10.0
                ch1inrange = v1[0] >= -10.0 and v1[0] <= 10.0 and v1[1] >= -10.0 and v1[1] <= 10.0
                ch2inrange = v2[0] >= -10.0 and v2[0] <= 10.0 and v2[1] >= -10.0 and v2[1] <= 10.0
                ch3inrange = v3[0] >= -10.0 and v3[0] <= 10.0 and v3[1] >= -10.0 and v3[1] <= 10.0
            except ValueError:
                print("Error: Issue with values given.")
                failed = 1
            if failed == 0:
                if ch0inrange and ch1inrange and ch2inrange and ch3inrange:
                    print("RAR4 Started.")
                    self.DAC.rampread4NB(v0,v1,v2,v3,steps,subsamples,interval,settle,dwell,filename)
                else:
                    print("Error: Check Voltage Range")
            else:
                print("Error: User input bad. Check input fields.")

        else:
            print("Error: Check Serial Connection")
    def DCSetCH0(self):
        if self.DAC.ready == True:
            try:
                voltage = float(self.ui.leset_ch0.text())
                self.DAC.setDAC(0,voltage)
                if voltage >= -10.0 and voltage <= 10.0:
                    print("Set output CH0 to " + str(voltage) + " Volts")
            except ValueError:
                print("User Error: Invalid DC Voltage Setting")
        else:
            print("Error: Check Serial Connection")
    def DCSetCH1(self):
        if self.DAC.ready == True:
            try:
                voltage = float(self.ui.leset_ch1.text())
                self.DAC.setDAC(1,voltage)
                if voltage >= -10.0 and voltage <= 10.0:
                    print("Set output CH1 to " + str(voltage) + " Volts")
            except ValueError:
                print("User Error: Invalid DC Voltage Setting")
        else:
            print("Error: Check Serial Connection")
    def DCSetCH2(self):
        if self.DAC.ready == True:
            try:
                voltage = float(self.ui.leset_ch2.text())
                self.DAC.setDAC(2,voltage)
                if voltage >= -10.0 and voltage <= 10.0:
                    print("Set output CH2 to " + str(voltage) + " Volts")
            except ValueError:
                print("User Error: Invalid DC Voltage Setting")
        else:
            print("Error: Check Serial Connection")
    def DCSetCH3(self):
        if self.DAC.ready == True:
            try:
                voltage = float(self.ui.leset_ch3.text())
                self.DAC.setDAC(3,voltage)
                if voltage >= -10.0 and voltage <= 10.0:
                    print("Set output CH3 to " + str(voltage) + " Volts")
            except ValueError:
                print("User Error: Invalid DC Voltage Setting")
        else:
            print("Error: Check Serial Connection")
    def DCSetAll(self):
        if self.DAC.ready == True:
            #Ch0
            try:
                voltage = float(self.ui.leset_ch0.text())
                self.DAC.setDAC(0,voltage)
                if voltage >= -10.0 and voltage <= 10.0:
                    print("Set output CH0 to " + str(voltage) + " Volts")
            except ValueError:
                print("User Error: Invalid DC Voltage Setting, CH0")
            #Ch1
            try:
                voltage = float(self.ui.leset_ch1.text())
                self.DAC.setDAC(1,voltage)
                if voltage >= -10.0 and voltage <= 10.0:
                    print("Set output CH1 to " + str(voltage) + " Volts")
            except ValueError:
                print("User Error: Invalid DC Voltage Setting, CH1")
            #Ch2
            try:
                voltage = float(self.ui.leset_ch2.text())
                self.DAC.setDAC(2,voltage)
                if voltage >= -10.0 and voltage <= 10.0:
                    print("Set output CH2 to " + str(voltage) + " Volts")
            except ValueError:
                print("User Error: Invalid DC Voltage Setting, CH2")
            #Ch3
            try:
                voltage = float(self.ui.leset_ch3.text())
                self.DAC.setDAC(3,voltage)
                if voltage >= -10.0 and voltage <= 10.0:
                    print("Set output CH3 to " + str(voltage) + " Volts")
            except ValueError:
                print("User Error: Invalid DC Voltage Setting, CH3")
        else:
            print("Error: Check Serial Connection")
    def DCReset0V(self):
        if self.DAC.ready == True:
            #Ch0
                self.DAC.setDAC(0,0)
                print("Reset output CH0 to " + str(0.0) + " Volts")
                self.DAC.setDAC(1,0)
                print("Reset output CH1 to " + str(0.0) + " Volts")
                self.DAC.setDAC(2,0)
                print("Reset output CH2 to " + str(0.0) + " Volts")
                self.DAC.setDAC(3,0)
                print("Reset output CH3 to " + str(0.0) + " Volts")
        else:
            print("Error: Check Serial Connection")
    def SineOut(self):
        if self.DAC.ready == True:
            try:
                v00 = float(self.ui.lesin_amp_ch0.text())
                v01 = float(self.ui.lesin_amp_ch1.text())
                v02 = float(self.ui.lesin_amp_ch2.text())
                v03 = float(self.ui.lesin_amp_ch3.text())
                angfreq0 = 2.0*pi*float(self.ui.lesin_freq_ch0.text())
                angfreq1 = 2.0*pi*float(self.ui.lesin_freq_ch1.text())
                angfreq2 = 2.0*pi*float(self.ui.lesin_freq_ch2.text())
                angfreq3 = 2.0*pi*float(self.ui.lesin_freq_ch3.text())
                phase0 = float(self.ui.lesin_phi_ch0.text()) * (2 * pi / 360.0)
                phase1 = float(self.ui.lesin_phi_ch1.text())  * (2 * pi / 360.0)
                phase2 = float(self.ui.lesin_phi_ch2.text())  * (2 * pi / 360.0)
                phase3 = float(self.ui.lesin_phi_ch3.text())  * (2 * pi / 360.0)
                offset0 = float(self.ui.lesin_off_ch0.text())
                offset1 = float(self.ui.lesin_off_ch1.text())
                offset2 = float(self.ui.lesin_off_ch2.text())
                offset3 = float(self.ui.lesin_off_ch3.text())
                interval = float(self.ui.lesin_duration.text())
                self.DAC.sine4(v00,v01,v02,v03,angfreq0,angfreq1,angfreq2,angfreq3,phase0,phase1,phase2,phase3,offset0,offset1,offset2,offset3,interval)
                print("Sine Wave output for " + str(interval) + " sec")
            except ValueError:
                print("User Error: Invalid Settings for Sine4 output")
        else:
            print("Error: Check Serial Connection")
    def DataOut_CSV(self):
        filename = self.ui.leout_fname.text() + "_tt.csv"
        self.DAC.saveToFile(filename)
        #print("CSV file saved: " + filename)

#GUI Initialization
myODAC = ODAC()
app = QApplication(sys.argv)
myWindow = openDAC_UI(myODAC)
myWindow.ui.show()
app.exec_()
