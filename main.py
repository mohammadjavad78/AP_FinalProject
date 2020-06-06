import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

Form=uic.loadUiType(os.path.join(os.getcwd(),"gui-intro.ui"))[0]

class IntroWindow(QMainWindow, Form):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyle("Fusion")
    
    w=IntroWindow()
    w.show()
    sys.exit(app.exec_())
