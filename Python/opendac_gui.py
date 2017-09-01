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
        self.ui.coboxsp_prt.addItems(["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10"])
        #ACQ1 Related Widgets
        #ACQ1 Related Widgets
        #RAR1 Related Widgets
        #RAR4 Related Widgets
        #DCOut Related Widgets
        #SineOut Related Widgets
        #Ramp1 Out Related Widgets
        #Ramp4 Out Related Widgets
        #DataOut Related Widgets


    #def BUTTONCLICKEDFUNC(self):

    #Serial Connection Event Handlers
    def serialConnect(self):#Evt Handler for serial connect button

        port = self.ui.coboxsp_prt.currentText()
        baud = self.ui.lesp_baud.text()
        print("Attempting to connect to: " + str(port) + ":" + str(baud))
        self.DAC.open(port,baud)
        sleep(1)
        if self.DAC.ser.isOpen == True:
            print("Connected Successfully")
            self.ui.buttsp_disconn.setEnabled(True)
            self.ui.buttsp_conn.setEnabled(False)
    def serialDisconnect(self):#Evt Handler for serial connect button
        self.DAC.close()
        if self.DAC.ser.isOpen == False:
            print("Disconnected Successfully")
            self.ui.buttsp_disconn.setEnabled(False)
            self.ui.buttsp_conn.setEnabled(True)
    #ACQ1 Event Handlers
    def ACQ1Start(self):
        print("Acquire 1 Started")
    #ACQ4 Event Handlers
    def ACQ4Start(self):
        print("Acquire 4 Started")
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
        print("CSV file output")
    def DataOut_PLT(self):
        print("Plot Plotted")






#GUI Initialization
myODAC = ODAC()
app = QApplication(sys.argv)
myWindow = openDAC_UI(myODAC)
myWindow.ui.show()
app.exec_()
