import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from opendacwrapper import ODAQ

class opendaciface(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi("opendac_gui.ui")
        self.ui.show()

#Initialization
app = QApplication(sys.argv)
window = opendaciface()
myODAQ = ODAQ()
myODAQ.open('COM4',verbose=0)


sys.exit(app.exec_())
