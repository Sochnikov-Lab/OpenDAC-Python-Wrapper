import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

class ODAQApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
    def initUI(self):


        self.resize(800,600)
        self.setWindowTitle('OpenDAC Command Interface')
        self.show()



sys.exit(ODAQAPP.exec_())
