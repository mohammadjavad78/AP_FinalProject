import os
import sys
from datetime import datetime
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QFileDialog,
    QStyle,
    QTableWidgetItem,
    QDialogButtonBox,
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import QUrl, Qt, QFileInfo
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.uic import loadUi
import win32api
import csv


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


class Preview(QMainWindow):
    def __init__(self, x, y):
        super(Preview, self).__init__()

        loadUi("untitled2.ui", self)
        self.move(x, y - 120)
        # self.hide()

    def mouseMoveEvent(self, event):
        self.onHoveredleave()


class LoginPage(QDialog):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi("searchtag.ui", self)

    def shows(self, layout):
        x = self.tableWidget.currentRow()
        t = layout.dataL[x][1]
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
        self.volume.installEventFilter(self)
        self.frames.installEventFilter(self)
        self.frame_2.installEventFilter(self)
        self.frames.installEventFilter(self)

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
        self.tolfilm = 0
        self.listviewstatus = 0
        self.listbtn.clicked.connect(lambda: self.list())
        self.listView.itemClicked.connect(self.listwidgetclicked)
        self.theme1.triggered.connect(lambda: self.theme01())
        self.theme2.triggered.connect(lambda: self.theme02())
        self.theme3.triggered.connect(lambda: self.theme03())
        self.theme4.triggered.connect(lambda: self.theme04())
        self.actionFarsi.triggered.connect(lambda: self.farsi())
        self.actionEnglish.triggered.connect(lambda: self.english())
        self.filename = ""
        self.x = 0
        self.videowidget3 = QVideoWidget()
        self.verticalLayout_8.addWidget(self.videowidget3)
        self.videoplayer3 = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoplayer3.setVideoOutput(self.videowidget3)
        self.widget.hide()
        self.stop.setEnabled(False)
        self.m = 0
        self.dataL = []
        with open("config.txt") as f:
            self.config = f.read()
        if int(self.config) == 11:
            self.theme01()
            self.farsi()
        if int(self.config) == 12:
            self.theme01()
            self.english()
        elif int(self.config) == 21:
            self.farsi()
            self.theme02()
        elif int(self.config) == 22:
            self.english()
            self.theme02()
        elif int(self.config) == 31:
            self.farsi()
            self.theme03()
        elif int(self.config) == 32:
            self.english()
            self.theme03()
        elif int(self.config) == 41:
            self.farsi()
            self.theme04()
        elif int(self.config) == 42:
            self.english()
            self.theme04()

    def farsi(self):
        self.menuLanguage.setTitle("زبان")
        self.menuView.setTitle("نمایش")
        self.theme1.setText("تم ۱")
        self.theme2.setText("تم ۲")
        self.theme3.setText("تم ۳")
        self.theme4.setText("تم ۴")
        self.menuFile.setTitle("فایل")
        self.actionOpen.setText("باز کردن ویدیو")
        self.actionSearch_By_Tag.setText("پنل تگ ها")
        self.actionFullscreen.setText("تمام صفحه")
        self.actionEnglish.setText("انگلیسی")
        self.actionFarsi.setText("فارسی")
        self.decreaseRate.setStatusTip("کاهش سرعت")
        self.decreaseRate.setToolTip("کاهش سرعت")
        self.increaseRate.setStatusTip("افزایش سرعت")
        self.increaseRate.setToolTip("افزایش سرعت")
        self.open.setStatusTip("باز کردن ویدیو")
        self.open.setToolTip("باز کردن ویدیو")
        self.stop.setStatusTip("توقف")
        self.stop.setToolTip("توقف")
        self.skipback.setStatusTip("عقب رفتن")
        self.skipback.setToolTip("عقب رفتن")
        self.play.setStatusTip("شروع/ایست")
        self.play.setToolTip("شروع/ایست")
        self.skipforward.setStatusTip("جلو رفتن")
        self.skipforward.setToolTip("جلو رفتن")
        self.volume.setStatusTip("صدا")
        self.volume.setToolTip("صدا")
        self.listbtn.setStatusTip("دسترسی آسان")
        self.listbtn.setToolTip(
            "پنلی شامل تگ ها و پنجره ای برای پیش نمایش را نمایان/پنهان میکند که با کلیک کردن بر روی هر کدام ویدیو به آن لحظه میرود"
        )
        with open("config.txt") as f:
            self.config = f.read()
        if int(self.config) // 10 == 1:
            with open("config.txt", "w") as f2:
                f2.write("11")
        if int(self.config) // 10 == 2:
            with open("config.txt", "w") as f2:
                f2.write("21")
        if int(self.config) // 10 == 3:
            with open("config.txt", "w") as f2:
                f2.write("31")
        if int(self.config) // 10 == 4:
            with open("config.txt", "w") as f2:
                f2.write("41")

    def english(self):
        self.menuLanguage.setTitle("Language")
        self.menuView.setTitle("View")
        self.theme1.setText("Theme1")
        self.theme2.setText("Theme2")
        self.theme3.setText("Theme3")
        self.theme4.setText("Theme4")
        self.menuFile.setTitle("File")
        self.actionOpen.setText("Open Video")
        self.actionSearch_By_Tag.setText("Tags Panel")
        self.actionFullscreen.setText("Fullscreen")
        self.actionEnglish.setText("English")
        self.actionFarsi.setText("Persian")
        self.decreaseRate.setStatusTip("Decrease Play Speed")
        self.decreaseRate.setToolTip("Decrease Play Speed")
        self.increaseRate.setStatusTip("Increase Play Speed")
        self.increaseRate.setToolTip("Increase Play Speed")
        self.open.setStatusTip("Open Video")
        self.open.setToolTip("Open Video")
        self.stop.setStatusTip("Stop")
        self.stop.setToolTip("Stop")
        self.skipback.setStatusTip("Previous")
        self.skipback.setToolTip("Previous")
        self.play.setStatusTip("Play/Pause")
        self.play.setToolTip("Play/Pause")
        self.skipforward.setStatusTip("Next")
        self.skipforward.setToolTip("Next")
        self.volume.setStatusTip("Volume")
        self.volume.setToolTip("Volume")
        self.listbtn.setStatusTip("Easy Access")
        self.listbtn.setToolTip(
            "Shows/Hides a panel for the tags that can be clicked on to take the video to its moment and also a preview window"
        )
        with open("config.txt") as f:
            self.config = f.read()
            if self.config == "":
                with open("config.txt", w) as f2:
                    f2.write("11")
                    self.config = "11"
        if int(self.config) // 10 == 1:
            with open("config.txt", "w") as f2:
                f2.write("12")
        if int(self.config) // 10 == 2:
            with open("config.txt", "w") as f2:
                f2.write("22")
        if int(self.config) // 10 == 3:
            with open("config.txt", "w") as f2:
                f2.write("32")
        if int(self.config) // 10 == 4:
            with open("config.txt", "w") as f2:
                f2.write("42")

    def moviess(self):
        x = self.filename.split("/")
        file_name = self.filename[: self.filename.find(x[len(x) - 1])]
        png = ""
        png2 = ""
        folders = os.listdir(file_name + r"/")
        for file in folders:
            if file.find(".mp4") > 0:
                png = png + ";" + file_name + file
                png2 = ";" + file_name + file + png2
        png = png + ";"
        self.png = png
        png2 = png2 + ";"
        self.png2 = png2

    def hoverleave(self):
        self.widget.hide()

    def gotovolume(self):
        x, _ = win32api.GetCursorPos()
        self.videoplayer.setVolume(
            int(
                (x - self.mapToGlobal(self.volume.pos()).x())
                / self.volume.width()
                * 100
            )
        )
        self.volume.setValue(
            int(
                (x - self.mapToGlobal(self.volume.pos()).x())
                / self.volume.width()
                * 100
            )
        )
        if self.m % 2 == 1:
            self.m += 1
            self.videoplayer.setMuted(False)

    def goto(self):
        x, _ = win32api.GetCursorPos()
        if self.filename != "":
            self.videoplayer.setPosition(
                (x - self.mapToGlobal(self.sliderfilm.pos()).x())
                / self.sliderfilm.width()
                * self.dur
                * 1000
            )

    def onHovered(self):
        x, _ = win32api.GetCursorPos()
        if self.filename != "":
            if self.listviewstatus % 2 == 1:
                self.videoplayer3.setPosition(
                    (x - self.mapToGlobal(self.sliderfilm.pos()).x())
                    / self.sliderfilm.width()
                    * self.dur
                    * 1000
                )
                self.widget.show()

    def eventFilter(self, obj, event):
        if obj == self.sliderfilm and event.type() == QtCore.QEvent.HoverMove:
            self.onHovered()
        elif (
            obj == self.frames or obj == self.frame_2
        ) and event.type() == QtCore.QEvent.Enter:
            self.hoverleave()
        elif obj == self.sliderfilm and event.type() == QtCore.QEvent.MouseButtonPress:
            self.goto()
        elif obj == self.volume and event.type() == QtCore.QEvent.MouseButtonPress:
            self.gotovolume()
        elif obj == self.frames and event.type() == QtCore.QEvent.MouseButtonDblClick:
            if not self.isFullScreen():
                self.fulls()
            else:
                self.unfull()

        return super(QMainWindow, self).eventFilter(obj, event)

    def stopp(self):
        self.stop.setEnabled(False)
        self.videoplayer.stop()
        self.videoplayer.setPosition(0)
        self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def listwidgetclicked(self, item):
        t = item.text()
        t = t[t.find(">") + 1 :]
        pt = datetime.strptime(t, "%H:%M:%S")
        total_seconds = pt.second + pt.minute * 60 + pt.hour * 3600
        if self.a == 0:
            self.videoplayer.setPosition(total_seconds * 1000)

    def list(self):
        if self.listviewstatus % 2 == 1:
            self.listView.hide()
            self.widget.hide()
            self.listbtn.setText("^")
            self.listviewstatus += 1
        else:
            self.listbtn.setText("v")
            self.listviewstatus += 1
            self.listView.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.unfull()
        elif e.key() == Qt.Key_6:
            if self.filename != "":
                self.videoplayer.setPosition(self.videoplayer.position() + 5000)
        elif e.key() == Qt.Key_4:
            if self.filename != "":
                self.videoplayer.setPosition(self.videoplayer.position() - 5000)
        elif e.key() == Qt.Key_Space:
            if self.filename != "":
                self.play_video()
        elif e.key() == Qt.Key_M:
            if self.m % 2 == 0:
                self.m += 1
                self.videoplayer.setMuted(True)
                self.volume.setEnabled(False)
                self.vvv = self.volume.value()
                self.volume.setValue(0)
            else:
                self.m += 1
                self.volume.setValue(self.vvv)
                self.volume.setEnabled(True)
                self.videoplayer.setMuted(False)

    def screen(self):
        if not self.isFullScreen():
            self.fulls()
        else:
            self.unfull()

    # forward media 5s
    def skipforw(self):
        a = self.png.find(self.filename)
        aa = self.png.find(";", a + 1)
        filename = self.png[aa + 1 : self.png.find(";", aa + 1)]
        if filename != "":
            self.filename = filename
            self.videoplayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.videoplayer3.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            title = filename.split("/")
            title = title[len(title) - 1]
            self.setWindowTitle(f"Taz Player openning{title}")
            self.videoplayer3.play()
            self.videoplayer3.pause()
            self.widget.hide()
            self.videoplayer.setPosition(0)
            self.videoplayer.play()
            self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            clip = VideoFileClip(filename)
            self.dur = clip.duration

    def skipbac(self):
        a = self.png2.find(self.filename)
        aa = self.png2.find(";", a + 1)
        filename = self.png2[aa + 1 : self.png2.find(";", aa + 1)]
        if filename != "":
            self.filename = filename
            self.videoplayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.videoplayer3.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            title = filename.split("/")
            title = title[len(title) - 1]
            self.setWindowTitle(f"Taz Player openning{title}")
            self.videoplayer3.play()
            self.videoplayer3.pause()
            self.widget.hide()
            self.videoplayer.setPosition(0)
            self.videoplayer.play()
            self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            clip = VideoFileClip(filename)
            self.dur = clip.duration

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

    # Handling Tags
    def fillListView(self):
        for i in range(len(self.dataL)):
            self.listView.addItem(self.dataL[i][0] + "->" + self.dataL[i][1])

    def updateTagFile(self):
        fname = self.fileName.split(".")
        fname = fname[0]
        with open(fname + ".csv", mode="w") as f:
            writer = csv.writer(
                f,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )
            for line in self.dataL:
                writer.writerow(line)

    def giveTime(self):
        vidPos = self.videoplayer.position()
        h = int(vidPos / 1000 // 3600)
        m = int((vidPos / 1000 - h * 3600) // 60)
        s = int(((vidPos / 1000 - h * 3600 - m * 60) % 60) % 60) * 100 // 100
        if h < 10:
            h = "0" + str(h)
        if m < 10:
            m = "0" + str(m)
        if s < 10:
            s = "0" + str(s)
        return f"{h}:{m}:{s}"

    def insertTag(self, tableWidget):
        t = tableWidget
        tag = "New Tag"
        tagTime = self.giveTime()
        l = len(self.dataL)
        i = 0
        flag = False

        while tagTime > self.dataL[i][1]:
            i += 1
            if i >= l:
                break

        if i < l:
            if tagTime == self.dataL[i][1]:
                flag = True

        if not flag:
            self.dataL.insert(i, [tag, tagTime])

            t.insertRow(i)
            t.setItem(
                i, 0, QTableWidgetItem(tag),
            )
            t.setItem(
                i, 1, QTableWidgetItem(tagTime),
            )
            t.editItem(t.item(i, 0))

    def removeRow(self, tableWidget):
        if len(self.dataL) > 0:
            self.dataL.remove(self.dataL[tableWidget.currentRow()])
        tableWidget.removeRow(tableWidget.currentRow())

    def updateList(self, tableWidget):
        for i in range(tableWidget.rowCount()):
            self.dataL[i] = [
                tableWidget.item(i, 0).text(),
                tableWidget.item(i, 1).text(),
            ]

    def undoChanges(self):
        fname = self.fileName.split(".")
        fname = fname[0]
        with open(fname + ".csv", mode="r+") as f:
            data = csv.reader(f)
            self.dataL = list(data)

    def fillTable(self, tableWidget):
        tableWidget.setRowCount(len(self.dataL))
        for i in range(len(self.dataL)):
            tableWidget.setItem(i, 0, QTableWidgetItem(self.dataL[i][0]))
            tableWidget.setItem(i, 1, QTableWidgetItem(self.dataL[i][1]))

    def openTagFile(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Tag File", filter="*.csv",
        )
        if filename != "":
            self.fileName = filename
            with open(filename, mode="r+") as f:
                data = csv.reader(f)
                self.dataL = list(data)

    def opensecond(self):
        login_page = LoginPage()
        login_page.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        if int(self.config) % 10 == 1:
            login_page.Save.setText("برو به")
            login_page.apply.setText("اعمال تغییرات")
            login_page.buttonBox.button(QDialogButtonBox.Ok).setText("تایید")
            login_page.buttonBox.button(QDialogButtonBox.Cancel).setText("انصراف")
            login_page.AddRow.setText("افزودن تگ")
            login_page.DeleteRow.setText("حذف تگ")
            login_page.OpenTagButton.setText("باز کردن فایل تگ")
            login_page.tableWidget.setHorizontalHeaderLabels(["تگ", "زمان"])
        else:
            login_page.tableWidget.setHorizontalHeaderLabels(["Tag", "Time"])

        self.fillTable(login_page.tableWidget)

        login_page.buttonBox.accepted.connect(
            lambda: [
                self.updateList(login_page.tableWidget),
                self.listbtn.setFocus(),
                self.listView.clear(),
                self.fillListView(),
                self.updateTagFile(),
            ]
        )

        login_page.buttonBox.rejected.connect(
            lambda: [self.listbtn.setFocus(), self.undoChanges(),]
        )

        login_page.apply.clicked.connect(
            lambda: [
                self.updateList(login_page.tableWidget),
                self.listView.clear(),
                self.fillListView(),
            ]
        )

        login_page.AddRow.clicked.connect(
            lambda: [self.insertTag(login_page.tableWidget),]
        )

        login_page.Save.clicked.connect(
            lambda: [
                login_page.shows(self),
                self.updateList(login_page.tableWidget),
                self.listbtn.setFocus(),
                self.listView.clear(),
                self.fillListView(),
            ]
        )

        login_page.DeleteRow.clicked.connect(
            lambda: [self.removeRow(login_page.tableWidget),]
        )

        login_page.OpenTagButton.clicked.connect(
            lambda: [
                self.openTagFile(),
                self.fillTable(login_page.tableWidget),
                self.listView.clear(),
                self.fillListView(),
            ]
        )

        login_page.tableWidget.sortByColumn(1, Qt.AscendingOrder)
        # if int(self.config) % 10 == 2:
        #     login_page.tableWidget.setHorizontalHeaderLabels(["Tag", "Time"])
        # else:
        #     login_page.tableWidget.setHorizontalHeaderLabels(["تگ", "زمان"])

        login_page.exec_()

    # End of Handling Tags

    def fulls(self):
        self.decreaseRate.hide()
        self.increaseRate.hide()
        self.centralwidget.setContentsMargins(0, 0, 0, 0)
        self.play.hide()
        self.open.hide()
        self.skipforward.hide()
        self.skipback.hide()
        self.label.hide()
        self.label_2.hide()
        self.volume.hide()
        self.menubar.hide()
        self.sliderfilm.hide()
        self.statusBar.hide()
        self.showFullScreen()
        self.listbtn.hide()
        self.widget.hide()
        self.listView.hide()
        self.frame_2.hide()
        self.stop.hide()
        self.listviewstatus = 1

    def unfull(self):
        self.frame_2.show()
        self.stop.show()
        self.list()
        self.centralwidget.setContentsMargins(10, 10, 10, 10)
        self.decreaseRate.show()
        self.increaseRate.show()
        self.play.show()
        self.open.show()
        self.skipforward.show()
        self.skipback.show()
        self.label.show()
        self.label_2.show()
        self.volume.show()
        self.menubar.show()
        self.sliderfilm.show()
        self.statusBar.show()
        self.showNormal()
        self.listbtn.show()

    ##setting position of film
    def setpos(self, position):
        self.videoplayer.setPosition(position)

    def position(self, position):
        position2 = self.tolfilm * 1000 - position + 1000
        hour = int((position / 3600000) % 24)
        hour2 = int((position2 / 3600000) % 24)
        if hour < 10:
            hour = "0" + str(hour)
        if hour2 < 10:
            hour2 = "0" + str(hour2)
        minute = int((position / 60000) % 60)
        minute2 = int((position2 / 60000) % 60)
        if minute < 10:
            minute = "0" + str(minute)
        if minute2 < 10:
            minute2 = "0" + str(minute2)
        second = int((position / 1000) % 60)
        second2 = int((position2 / 1000) % 60)
        if second < 10:
            second = "0" + str(second)
        if second2 < 10:
            second2 = "0" + str(second2)
        self.label.setText(f"{hour}:{minute}:{second}")
        self.label_2.setText(f"{hour2}:{minute2}:{second2}")
        self.sliderfilm.setValue(position)
        if position2 < 1000:
            self.videoplayer.stop()
            self.sliderfilm.setValue(0)
            self.stop.setEnabled(False)
            self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def changed(self, duration):
        self.sliderfilm.setRange(0, duration)

    ##setting position of volume
    def setvolpos(self, position):
        self.videoplayer.setVolume(position)

    ##open button or open from menu bar
    def Loadvideo(self, videoplayer):
        self.a = 0
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            filter="*.mp4;*.mov;*.wmv;*.webm;*.wmv;*.m4v;*.m4a;*.flv",
        )
        if filename != "":
            self.videoplayer.setPosition(0)
            self.filename = filename
            if filename != "":
                self.fileName = filename.split(".")[0]
                fname = filename.split(".")
                fnmae = fname[0]
                if os.path.isfile(fnmae + ".csv"):
                    with open(fnmae + ".csv", mode="r+") as f:
                        data = csv.reader(f)
                        self.dataL = list(data)
                        self.listView.clear(),
                        self.fillListView()
                clip = VideoFileClip(filename)
                self.dur = clip.duration
                self.videoplayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
                self.videoplayer3.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
                self.moviess()
                clip = VideoFileClip(filename)
                self.tolfilm = int(clip.duration)
                title = filename.split("/")
                title = title[len(title) - 1]
                self.setWindowTitle(f"Taz Player openning : {title}")
                self.videoplayer3.play()
                self.videoplayer3.pause()
                self.widget.hide()
                self.stop.setEnabled(True)
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
            self.stop.setEnabled(True)
            self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def theme01(self):
        self.videowidget.setStyleSheet("background-color: #404040")
        self.setStyleSheet("background-color: #A0A0A0")
        if self.theme1.text() == "Theme1":
            with open("config.txt", "w") as f:
                f.write("12")
        else:
            with open("config.txt", "w") as f:
                f.write("11")

    def theme02(self):
        self.videowidget.setStyleSheet("background-color: #330019")
        self.setStyleSheet("background-color: #990000")
        if self.theme1.text() == "Theme1":
            with open("config.txt", "w") as f:
                f.write("22")
        else:
            with open("config.txt", "w") as f:
                f.write("21")

    def theme03(self):
        self.videowidget.setStyleSheet("background-color: #35557F")
        self.setStyleSheet("background-color: #003366")
        if self.theme1.text() == "Theme1":
            with open("config.txt", "w") as f:
                f.write("32")
        else:
            with open("config.txt", "w") as f:
                f.write("31")

    def theme04(self):
        self.videowidget.setStyleSheet("background-color: #00FF00")
        self.setStyleSheet("background-color: #4C9900")
        if self.theme1.text() == "Theme1":
            with open("config.txt", "w") as f:
                f.write("42")
        else:
            with open("config.txt", "w") as f:
                f.write("41")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(qss)
    w = IntroWindow()
    w.show()
    sys.exit(app.exec_())
