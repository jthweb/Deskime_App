import datetime, json, keyboard
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtWidgets import QDesktopWidget, QGraphicsDropShadowEffect

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(697, 175)
        self.config=json.load(open("Config/settings.json"))
        print(self.config)

        qtRectangle = MainWindow.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        MainWindow.move(qtRectangle.topLeft().x(),qtRectangle.topLeft().y()-250)
        
        MainWindow.setMouseTracking(False)
        self.shadow = QGraphicsDropShadowEffect(self,
            blurRadius=0.0,
            color=QtGui.QColor("white"),
            offset=QtCore.QPointF(0.0, 0.0)
        )
        self.shadow3 = QGraphicsDropShadowEffect(self,
            blurRadius=0.0,
            color=QtGui.QColor("white"),
            offset=QtCore.QPointF(0.0, 0.0)
        )
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setStyleSheet(f"font: {self.config['time_font_size']}pt \"My Font\";\n"
"color: rgb(255, 255, 255);")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_3.setGraphicsEffect(self.shadow3)
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGraphicsEffect(self.shadow)
        self.label.setStyleSheet("QLabel#label{\n"
f"    font: {self.config['day_font_size']}pt \"Anurati\";\n"
"    color: rgb(255, 255, 255);\n"
"}")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        shadow2 = QGraphicsDropShadowEffect(self,
            blurRadius=0.0,
            color=QtGui.QColor("white"),
            offset=QtCore.QPointF(0.0, 0.0)
        )
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGraphicsEffect(shadow2)
        self.label_2.setStyleSheet(f"font: {self.config['day-month-year_font_size']}pt \"My Font\";\n"
"color: rgb(255, 255, 255);")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def showTime(self):
        current_time = QTime.currentTime()
        label_time = current_time.toString('hh:mm')
        am_pm=datetime.datetime.today().strftime('%p')
        self.label_3.setText(f"- {label_time} {am_pm} -")
        self.label.setText(" ".join(datetime.datetime.now().strftime("%A").upper()))
        self.label_2.setText(datetime.datetime.today().strftime('%d  %B,  %Y.').upper())

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        MainWindow.setAttribute(Qt.WA_TranslucentBackground, True)
        MainWindow.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.label.setText(_translate("MainWindow", " ".join(datetime.datetime.now().strftime("%A").upper())))
        self.label_2.setText(_translate("MainWindow", datetime.datetime.today().strftime('%d  %B , %Y.').upper()))
        self.label_3.setText(_translate("MainWindow", "- 10:50 AM -"))

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.drag=False
        self.dragPos = QtCore.QPoint()
        
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
        
    def mouseMoveEvent(self, event):
        if self.drag:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

if __name__ == "__main__":
    import sys, os
    app = QtWidgets.QApplication(sys.argv)
    for file in os.listdir("Core/Fonts"):
        if file.endswith(".ttf"):
            font = QtGui.QFontDatabase.addApplicationFont(f"Core/Fonts/{file}")
            QtGui.QFontDatabase.applicationFontFamilies(font)
    window=MainWin()
    window.show()
    if sys.platform=='win32':
        from ctypes import windll
        import win32gui,win32con
        win32gui.SetWindowPos(window.winId(),win32con.HWND_BOTTOM, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE  | win32con.SWP_NOACTIVATE )

        hwnd=win32gui.GetWindow(win32gui.GetWindow(windll.user32.GetTopWindow(0),win32con.GW_HWNDLAST),win32con.GW_CHILD);
        win32gui.SetWindowLong(window.winId(),win32con.GWL_HWNDPARENT,hwnd)
    sys.exit(app.exec_())

