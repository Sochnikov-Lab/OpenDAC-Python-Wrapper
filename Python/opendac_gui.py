import sys
import serial
import io
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from opendacwrapper import ODAC
from time import sleep

class openDAC_UI(QMainWindow):
    def __init__(self,myODAC):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi("opendac_gui.ui")
        self.DAC = myODAC
        #Bindings:
        #self.BUTTON.clicked.connect(self.BUTTONCLICKEDFUNC)

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
        #RAR4 Related Widgets
        self.ui.buttrr4_start.clicked.connect(self.RAR4Start)
        #DCOut Related Widgets
        self.ui.buttset_ch0.clicked.connect(self.DCSetCH0)
        self.ui.buttset_ch1.clicked.connect(self.DCSetCH1)
        self.ui.buttset_ch2.clicked.connect(self.DCSetCH2)
        self.ui.buttset_ch3.clicked.connect(self.DCSetCH3)
        self.ui.buttset_all.clicked.connect(self.DCSetAll)
        self.ui.buttset_0v.clicked.connect(self.DCReset0V)
        #SineOut Related Widgets
        self.ui.buttsin_start.clicked.connect(self.SineOut)
        #Ramp1 Out Related Widgets
        self.ui.buttr1_start.clicked.connect(self.Ramp1Start)
        #Ramp4 Out Related Widgets
        self.ui.buttr4_start.clicked.connect(self.Ramp4Start)
        #DataOut Related Widgets
        self.ui.butts_csv.clicked.connect(self.DataOut_CSV)
        self.ui.butts_plot.clicked.connect(self.DataOut_PLT)
        self.ui.butts_pds.clicked.connect(self.DataOut_PDS)
        self.ui.leout_fname.setText("data")

    #def BUTTONCLICKEDFUNC(self):

    #Serial Connection Event Handlers
    def serialConnect(self):#Evt Handler for serial connect button

        port = self.ui.coboxsp_prt.currentText()
        baud = self.ui.lesp_baud.text()
        print("Attempting to connect to: " + str(port) + ":" + str(baud))
        self.DAC.open(port,baud)
        #sleep(1)
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
    #ACQ1 Event Handlers
    def ACQ1Start(self):
        try:
            samples = int(self.ui.lea1_samples.text())
            stepsize = 1.0/float(self.ui.lea1_srate.text())
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
        except ValueError:
            print("Error: Issue with values given.")

    #ACQ2 Event Handlers
    def ACQ2Start(self):
        print("Acquire 2")
        if not ((self.ui.rba2_ch0A.isChecked() and self.ui.rba2_ch0B.isChecked()) or (self.ui.rba2_ch1A.isChecked() and self.ui.rba2_ch1B.isChecked()) or (self.ui.rba2_ch2A.isChecked() and self.ui.rba2_ch2B.isChecked()) or (self.ui.rba2_ch3A.isChecked() and self.ui.rba2_ch3B.isChecked())):
            print("Channel Selection Okay")
        else:
            print("Error: Incorrect Channel Selection.")
    #ACQ4 Event Handlers
    def ACQ4Start(self):
        try:
            samples = int(self.ui.lea4_samples.text())
            stepsize = 1.0/float(self.ui.lea4_srate.text())
            if samples <= 5000 and stepsize >= 1.0/2000.0:
                if self.DAC.ready == True:
                    print("CH0,CH1,CH2,CH3 Selected.")
                    self.DAC.acquireAll(samples,stepsize)
                else:
                    print("Error: Check Serial Connection")
            else:
                print("Acquire Halted: too many samples (max 5000) or sample rate too fast (max 2kHz)")
        except ValueError:
            print("Error: Issue with values given.")
    #RAR1 Event Handlers
    def RAR1Start(self):
        print("Ramp and Read 1 Started")
    #RAR4 Event Handlers
    def RAR4Start(self):
        print("Ramp and Read 4 Started")
    #DCOut Event Handlers
    def DCSetCH0(self):
        print("Set CH0")
    def DCSetCH1(self):
        print("Set CH1")
    def DCSetCH2(self):
        print("Set CH2")
    def DCSetCH3(self):
        print("Set CH3")
    def DCSetAll(self):
        print("Set CH0 - CH3")
    def DCReset0V(self):
        print("Reset CH0 - CH3 to 0.0V")
    #SineOut Event Handlers
    def SineOut(self):
        print("Sine Output Started")
    #Ramp1 Event Handlers
    def Ramp1Start(self):
        print("Ramp 1 Started")
    #Ramp4 Event Handlers
    def Ramp4Start(self):
        print("Ramp 4 Started")
    #DataOut Event Handlers
    def DataOut_CSV(self):
        filename = self.ui.leout_fname.text() + "_tt.csv"
        self.DAC.saveToFile(filename)
        print("CSV file saved: " + filename)
    def DataOut_PLT(self):
        filename = self.ui.leout_fname.text() + "_tt.png"
        print("Plot Plotted")
    def DataOut_PDS(self):
        filename = self.ui.leout_fname.text() + "_pds.png"
        print("Plot Plotted")






#GUI Initialization
myODAC = ODAC()
app = QApplication(sys.argv)
myWindow = openDAC_UI(myODAC)
myWindow.ui.show()
app.exec_()
