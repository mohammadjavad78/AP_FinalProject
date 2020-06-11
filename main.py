import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog# , QHBoxLayout, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent
from PyQt5.QtGui import QIcon, QPalette,QImage
from PyQt5.QtCore import QUrl,Qt
from PyQt5.QtMultimediaWidgets import QVideoWidget


Form=uic.loadUiType(os.path.join(os.getcwd(),"gui-intro.ui"))[0]

class IntroWindow(QMainWindow, Form):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon('logo.png'))
        
        p =self.palette()
        p.setColor(QPalette.Window, Qt.gray)
        self.setPalette(p)
        
        self.setupUi(self)
        
        videowidget = QVideoWidget()
        self.vertical.addWidget(videowidget)
        self.videoplayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoplayer.setVideoOutput(videowidget)
        self.sliderfilm.setRange(0,0)
        self.volume.setRange(0,100)
        self.videoplayer.setVolume(100)
        self.volume.setValue(100)
        
        self.play.setEnabled(False)
        self.stop.setEnabled(False)   
           
        self.sliderfilm.sliderMoved.connect(self.setpos)
        self.videoplayer.positionChanged.connect(self.position)
        self.videoplayer.durationChanged.connect(self.changed)
        self.videoplayer.volumeChanged.connect(self.setvolpos)
        self.volume.sliderMoved.connect(self.setvolpos)
        self.actionOpen.triggered.connect(self.Loadvideo)
        self.play.clicked.connect(self.play_video)
        self.open.clicked.connect(lambda:self.Loadvideo(self.videoplayer))
        self.stop.clicked.connect(self.stopp)
        
    ##setting position of film        
    def setpos(self, position):
        self.videoplayer.setPosition(position)
        
    def position(self, position):
        self.sliderfilm.setValue(position)
        
    def changed(self, duration):
        self.sliderfilm.setRange(0, duration)
        
    ##setting position of volume        
    def setvolpos(self, position):
        self.videoplayer.setVolume(position)    
        
    ##stop button
    def stopp(self):
            self.stop.setEnabled(False)
            self.play.setText("Start")
            self.videoplayer.stop()
            self.videoplayer.setPosition(0)
            
    ##open button or open from menu bar
    def Loadvideo(self,videoplayer):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if(filename!=""):
            self.videoplayer.setPosition(0)
            types=(".mov" in filename )or( ".png" in filename )or( ".mp4" in filename)
            if types:
                if(filename!=""):
                    self.videoplayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
                    self.videoplayer.play()
                    self.stop.setEnabled(True)
                    self.play.setEnabled(True)
                    self.play.setText("Pause")

    ##play button
    def play_video(self):
        self.stop.setEnabled(True)
        if self.videoplayer.state() == QMediaPlayer.PlayingState:
            self.play.setText("Resume")
            self.videoplayer.pause()
        else:
            self.videoplayer.play()
            self.play.setText("Pause")

        
if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyle("Fusion")
    
    w=IntroWindow()
    w.show()
    sys.exit(app.exec_())
