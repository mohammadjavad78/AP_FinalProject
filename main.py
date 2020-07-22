import os
import sys
from dateutil.parser import parse
import pandas as pd
from datetime import datetime
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QDialog,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QStyle,
    QHBoxLayout,
    QVBoxLayout,
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIcon, QPalette, QImage
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.uic import loadUi
import win32api


qss = """
    QMenuBar {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 lightgray, stop:1 darkgray);
    }
    QMenuBar::item {
        spacing: 3px;           
        padding: 2px 10px;
        background-color: rgb(210,105,30);
        color: rgb(255,255,255);  
        border-radius: 5px;
    }
    QMenuBar::item:selected {    
        background-color: rgb(244,164,96);
    }
    QMenuBar::item:pressed {
        background: rgb(128,0,0);
    }

    /* +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ */  

    QMenu {
        background-color: #ABABAB;   
        border: 1px solid black;
        margin: 2px;
    }
    QMenu::item {
        color: white;
        background-color: tranparent;

    }
    QMenu::item:selected { 
        background-color: #654321;
        color: rgb(255,255,255);
    }

    QVideoWidget {
        background-color: #A0A0A0;
    }
    """


Form = uic.loadUiType(os.path.join(os.getcwd(), "gui-intro.ui"))[0]


class PlotThread(QtCore.QThread):
    def __init__(self, window, x, y):
        QtCore.QThread.__init__(self, parent=window)
        self.window = window
        self.window.preview = Preview(x, y)
        # self.preview = preview
        frame = QFrame(self.window)
        self.window.preview.main.addWidget(frame)
        self.window.preview.setWindowFlags(Qt.FramelessWindowHint)
        frame.move(x, y)
        # frame.resize(112, 112)
        # frame.setLineWidth(0.6)
        qv = QVBoxLayout(frame)
        self.window.preview.videowidget2 = QVideoWidget()
        qv.addWidget(self.window.preview.videowidget2)
        self.window.preview.videoplayer2 = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.window.preview.videoplayer2.setVideoOutput(
            self.window.preview.videowidget2
        )
        self.window.preview.videoplayer2.setMedia(
            QMediaContent(QUrl.fromLocalFile(self.window.filename))
        )
        self.window.preview.videoplayer2.play()
        self.window.preview.videoplayer2.pause()
        self.window.preview.show()

    def run(self, x, y):
        self.window.preview.videoplayer2.setPosition(100000)
        self.window.x = 1
        while (
            x - 10 < win32api.GetCursorPos()[0]
            and win32api.GetCursorPos()[0] < x + 10
            and y - 10 < win32api.GetCursorPos()[1]
            and win32api.GetCursorPos()[1] < y + 10
        ):
            # print("ssss")
            pass
        else:
            print("close")
            self.window.preview.close()


class Preview(QMainWindow):
    def __init__(self, x, y):
        super(Preview, self).__init__()

        loadUi("untitled2.ui", self)
        self.move(x, y - 120)
        # self.hide()

    def mouseMoveEvent(self, event):
        self.onHoveredleave()
        print("move")

    # def eventFilter(self, source, event):
    #     if event.type() == QtCore.QEvent.MouseMove:
    #         if event.buttons() == QtCore.Qt.NoButton:
    #             print("sssss")
    #             self.close()
    #     return super(Window, self).eventFilter(source, event)


class LoginPage(QDialog):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi("searchtag.ui", self)

    def shows(self, layout):
        data = pd.read_excel("tags.xlsx")
        firstline = pd.DataFrame(data, index=[0])
        if self.tableWidget.currentRow() == 0:
            dt = parse(str(list(firstline)[1]))
            t = str(list(firstline)[1])
        else:
            dt = parse(str(data.iat[self.tableWidget.currentRow(), 1]))
            t = str(data.iat[self.tableWidget.currentRow() - 1, 1])
        pt = datetime.strptime(t, "%H:%M:%S")
        total_seconds = pt.second + pt.minute * 60 + pt.hour * 3600
        layout.videoplayer.setPosition(total_seconds * 1000)


class IntroWindow(QMainWindow, Form):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon("logo.png"))

        p = self.palette()
        p.setColor(QPalette.Window, Qt.gray)
        self.setPalette(p)

        self.setupUi(self)

        self.preview = Preview(0, 0)
        self.preview.show()
        self.preview.close()

        self.a = 1
        self.videowidget = QVideoWidget()
        self.vertical.addWidget(self.videowidget)
        self.videoplayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoplayer.setVideoOutput(self.videowidget)
        self.sliderfilm.setRange(0, 0)
        self.volume.setRange(0, 100)
        self.videoplayer.setVolume(100)
        self.volume.setValue(100)

        self.play.setEnabled(False)
        self.increaseRate.setEnabled(False)
        self.decreaseRate.setEnabled(False)

        self.sliderfilm.installEventFilter(self)

        # putting Icons on buttons

        self.increaseRate.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.decreaseRate.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSeekBackward)
        )
        self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.open.setIcon(self.style().standardIcon(QStyle.SP_DirHomeIcon))
        self.skipforward.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.skipback.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.stop.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))

        self.sliderfilm.sliderMoved.connect(self.setpos)
        self.videoplayer.positionChanged.connect(self.position)
        self.videoplayer.durationChanged.connect(self.changed)
        self.videoplayer.volumeChanged.connect(self.setvolpos)
        self.volume.sliderMoved.connect(self.setvolpos)
        self.actionOpen.triggered.connect(self.Loadvideo)
        self.actionSearch_By_Tag.triggered.connect(self.opensecond)
        self.actionFullscreen.triggered.connect(self.screen)
        self.skipforward.clicked.connect(self.skipforw)
        self.skipback.clicked.connect(self.skipbac)
        self.increaseRate.clicked.connect(self.incRate)
        self.decreaseRate.clicked.connect(self.decRate)
        self.play.clicked.connect(self.play_video)
        self.open.clicked.connect(lambda: self.Loadvideo(self.videoplayer))
        self.stop.clicked.connect(self.stopp)
        self.listView.hide()
        self.addtolist()
        self.listviewstatus = 0
        self.listbtn.clicked.connect(lambda: self.list())
        self.listView.itemClicked.connect(self.listwidgetclicked)
        self.theme1.triggered.connect(lambda: self.theme01())
        self.theme2.triggered.connect(lambda: self.theme02())
        self.theme3.triggered.connect(lambda: self.theme03())
        self.theme4.triggered.connect(lambda: self.theme04())
        self.filename = ""
        self.x = 0

        # def itemClicked(item):
        #     print("sassss")

        # self.button = QPushButton("button", self)
        ####how to hid window flag
        # self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        # self.hide()
        # self.show()

    def eventFilter(self, obj, event):
        if (
            obj == self.sliderfilm
            and event.type() == QtCore.QEvent.HoverEnter
            and event.type() != QtCore.QEvent.HoverMove
            # and event.type() != QtCore.QEvent.MouseButtonPress
            # and event.type() != QtCore.QEvent.MouseMove
        ):
            self.onHovered()
        return super(QMainWindow, self).eventFilter(obj, event)

        # qv.resize(100, 100)
        # # frame.
        # qv.move(x, y)

    def mouseMoveEvent(self, event):
        self.onHoveredleave()
        print("move")

    def onHoveredleave(self):
        print("close")
        self.preview.close()
        self.x = 0

    def onHovered(self):
        # print("hovered")
        x, y = win32api.GetCursorPos()
        print(f"x,y mouse is {x},{y}")
        print(self.sliderfilm.width(), self.sliderfilm.height())
        print(
            self.mapToGlobal(self.sliderfilm.pos()).x(),
            self.mapToGlobal(self.sliderfilm.pos()).y(),
        )
        if self.filename != "":
            self.thread = PlotThread(self, x, y)
            self.thread.run(x, y)

    def stopp(self):
        self.stop.setEnabled(False)
        self.videoplayer.stop()
        self.videoplayer.setPosition(0)

    def listwidgetclicked(self, item):
        t = item.text()
        pt = datetime.strptime(t, "%H:%M:%S")
        total_seconds = pt.second + pt.minute * 60 + pt.hour * 3600
        if self.a == 0:
            self.videoplayer.setPosition(total_seconds * 1000)

    def list(self):
        if self.listviewstatus % 2 == 1:
            self.listView.hide()
            self.listbtn.setText("^")
            self.listviewstatus += 1
        else:
            self.listbtn.setText("v")
            self.listviewstatus += 1
            self.listView.show()

    # def resizeEvent(self, cls):
    #     print(self.geometry())
    #     width = self.frameGeometry().width()
    #     height = self.frameGeometry().height()
    #     self.button.move(width - 200, height - 200)

    def mouseDoubleClickEvent(self, cls):
        if not self.isFullScreen():
            # self.showFullScreen()
            self.fulls()
        else:
            self.unfull()
            # self.showNormal()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.unfull()
                # self.showNormal()

    def screen(self):
        if not self.isFullScreen():
            # self.showFullScreen()
            self.fulls()
        else:
            self.unfull()
            # self.showNormal()

    # forward media 5s
    def skipforw(self):
        self.videoplayer.setPosition(self.videoplayer.position() + 5000)

    def skipbac(self):
        self.videoplayer.setPosition(self.videoplayer.position() - 5000)

        # set increase rate

    def incRate(self):
        if self.videoplayer.playbackRate() == 0:
            x = self.videoplayer.playbackRate() + 1
        else:
            x = self.videoplayer.playbackRate()
        self.videoplayer.setPlaybackRate(x + 0.25)

    # set decrease rate
    def decRate(self):
        if self.videoplayer.playbackRate() == 0:
            x = self.videoplayer.playbackRate() + 1
        else:
            x = self.videoplayer.playbackRate()
        self.videoplayer.setPlaybackRate(x - 0.25)

    def addtolist(self):
        data = pd.read_excel("tags.xlsx")
        firstline = pd.DataFrame(data, index=[0])
        x = pd.DataFrame(data, columns=[list(firstline)[0]])
        self.listView.addItem(str(list(firstline)[1]))
        for i in range(x.size):
            self.listView.addItem(str(data.iat[i, 1]))

    def opensecond(self):
        login_page = LoginPage()
        login_page.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        data = pd.read_excel("tags.xlsx")
        firstline = pd.DataFrame(data, index=[0])
        x = pd.DataFrame(data, columns=[list(firstline)[0]])
        login_page.tableWidget.setRowCount(x.size)
        login_page.tableWidget.insertRow(1)
        login_page.tableWidget.setItem(
            0, 0, QtWidgets.QTableWidgetItem(list(firstline)[0])
        )
        login_page.tableWidget.setItem(
            0, 1, QtWidgets.QTableWidgetItem(str(list(firstline)[1]))
        )
        for i in range(x.size):
            for j in range(2):
                login_page.tableWidget.setItem(
                    i + 1, j, QtWidgets.QTableWidgetItem(str(data.iat[i, j]))
                )
            # self.listView.addItem(str(data.iat[i, j]))
        login_page.buttonBox.accepted.connect(lambda: login_page.shows(self))
        login_page.tableWidget.setHorizontalHeaderLabels(["Tag", "Time"])
        login_page.exec_()

    def fulls(self):
        self.decreaseRate.hide()
        self.increaseRate.hide()
        self.centralwidget.setContentsMargins(0, 0, 0, 0)
        self.play.hide()  ################################################
        # self.stop.hide()  ################################################
        self.open.hide()  ################################################
        self.skipforward.hide()  ################################################
        self.skipback.hide()  ################################################
        # self.horizontalSpacer_2.hide()
        # self.horizontalSpacer.hide()
        self.label.hide()  ################################################
        self.volume.hide()  ################################################
        self.menubar.hide()  ################################################################
        self.sliderfilm.hide()  ################################################
        self.statusBar.hide()
        self.showFullScreen()  ################################################
        self.listbtn.hide()
        self.listView.hide()
        self.stop.hide()

    def unfull(self):
        self.stop.show()
        self.centralwidget.setContentsMargins(10, 10, 10, 10)
        self.decreaseRate.show()
        self.increaseRate.show()
        self.play.show()  ################################################
        # self.stop.show()  ################################################
        self.open.show()  ################################################
        self.skipforward.show()  ################################################
        self.skipback.show()  ################################################
        # self.horizontalSpacer_2.hide()
        # self.horizontalSpacer.hide()
        self.label.show()  ################################################
        self.volume.show()  ################################################
        self.menubar.show()  ################################################################
        self.sliderfilm.show()  ################################################
        self.statusBar.show()
        self.showNormal()  ################################################
        self.listbtn.show()
        # self.listView.show()

    ##setting position of film
    def setpos(self, position):
        self.videoplayer.setPosition(position)

    def position(self, position):
        hour = int((position / 3600000) % 24)
        if hour < 10:
            hour = "0" + str(hour)
        minute = int((position / 60000) % 60)
        if minute < 10:
            minute = "0" + str(minute)
        second = int((position / 1000) % 60)
        if second < 10:
            second = "0" + str(second)
        self.label.setText(f"{hour}:{minute}:{second}")
        self.sliderfilm.setValue(position)

    def changed(self, duration):
        self.sliderfilm.setRange(0, duration)

    ##setting position of volume
    def setvolpos(self, position):
        self.videoplayer.setVolume(position)

    ##stop button
    # def stopp(self):
    #     self.stop.setEnabled(False)
    #     self.play.setText("Start")
    #     self.videoplayer.stop()
    #     self.videoplayer.setPosition(0)

    ##open button or open from menu bar
    def Loadvideo(self, videoplayer):
        self.a = 0
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filename != "":
            self.videoplayer.setPosition(0)
            self.filename = filename
            types = (".mov" in filename) or (".png" in filename) or (".mp4" in filename)
            if types:
                if filename != "":
                    self.videoplayer.setMedia(
                        QMediaContent(QUrl.fromLocalFile(filename))
                    )
                    self.videoplayer.play()
                    self.play.setEnabled(True)
                    self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                    self.increaseRate.setEnabled(True)
                    self.decreaseRate.setEnabled(True)

    ##play button
    def play_video(self):
        if self.videoplayer.state() == QMediaPlayer.PlayingState:
            self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.videoplayer.pause()
        else:
            self.videoplayer.play()
            self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def theme01(self):
        self.videowidget.setStyleSheet("background-color: #404040")
        self.setStyleSheet("background-color: #A0A0A0")

    def theme02(self):
        self.videowidget.setStyleSheet("background-color: #330019")
        self.setStyleSheet("background-color: #990000")

    def theme03(self):
        self.videowidget.setStyleSheet("background-color: #35557F")
        self.setStyleSheet("background-color: #003366")

    def theme04(self):
        self.videowidget.setStyleSheet("background-color: #00FF00")
        self.setStyleSheet("background-color: #4C9900")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(qss)
    w = IntroWindow()
    w.show()
    sys.exit(app.exec_())
