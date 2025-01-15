import sys
import json
import logging
import ctypes
import time
from PyQt6.QtWidgets import QApplication, QFrame, QStyleOption, QStyle, QHBoxLayout, QLabel, QToolTip, QGraphicsOpacityEffect
from PyQt6.QtGui import QDesktopServices, QIcon, QPixmap, QPainter, QCursor, QFontMetrics
from PyQt6.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QUrl, QObject, QEvent, QPoint
from ctypes import windll
import subprocess

############### SETTINGS ####################
DOCK_ICON_SIZE = 24
ANIMATION_SPEED = 200
PADDING = 6
BORDER_RADIUS = 16
HIDE_TASKBAR = False
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#############################################

class TooltipEventFilter(QObject):
    def __init__(self, parent, tooltip_text, dock_widget):
        super().__init__(parent)
        self.tooltip_text = tooltip_text
        self.dock_widget = dock_widget

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Enter:
            if not self.dock_widget.opacity_animation.state() == QPropertyAnimation.State.Running and \
               not self.dock_widget.slide_up_animation.state() == QPropertyAnimation.State.Running and \
               not self.dock_widget.slide_down_animation.state() == QPropertyAnimation.State.Running:
                global_pos = obj.mapToGlobal(QPoint(0, 0))
                font_metrics = QFontMetrics(obj.font())
                tooltip_width = font_metrics.horizontalAdvance(self.tooltip_text)
                icon_height = obj.height()
                x = global_pos.x() + ((DOCK_ICON_SIZE - PADDING) - tooltip_width) * 2
                y = global_pos.y() - DOCK_ICON_SIZE - PADDING
                QToolTip.showText(QPoint(x, y), self.tooltip_text, obj)
        elif event.type() == QEvent.Type.Leave:
            QToolTip.hideText()
        return False

class FloatingDock(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(f"""
            QFrame {{
               background-color: rgba(30, 33, 49, 0.85);
               border: 1px solid #41434c;
               border-radius: {BORDER_RADIUS}px;
               padding: {PADDING}px;
            }}
            QLabel {{
                background-color: transparent;
                color: white;
                border: none;
                margin:0 4px;
                padding: {PADDING}px;
                border-radius: {BORDER_RADIUS / 1.4}px;
            }}
            QLabel:hover {{
                background-color: rgba(255, 255, 255, 0.2);
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Time and Date Label
        self.time_label = QLabel(self)
        self.update_time()
        layout.addWidget(self.time_label)

        # Volume Icon
        volume_label = QLabel(self)
        volume_icon = QIcon("./icons/iconio/Prohibited_Light_580b9be8cabcf67c353ba00cf70cbb13.png")  # Replace with your volume icon path
        volume_label.setPixmap(volume_icon.pixmap(DOCK_ICON_SIZE, DOCK_ICON_SIZE))
        volume_label.mousePressEvent = lambda event: self.open_volume_mixer()
        tooltip_filter = TooltipEventFilter(volume_label, "Volume", self)
        volume_label.installEventFilter(tooltip_filter)
        layout.addWidget(volume_label)

        # Wi-Fi Icon
        wifi_label = QLabel(self)
        wifi_icon = QIcon("./icons/iconio/cardview-linkedentity-dark@4x.png")  # Replace with your Wi-Fi icon path
        wifi_label.setPixmap(wifi_icon.pixmap(DOCK_ICON_SIZE, DOCK_ICON_SIZE))
        wifi_label.mousePressEvent = lambda event: self.toggle_wifi()
        tooltip_filter = TooltipEventFilter(wifi_label, "Wi-Fi", self)
        wifi_label.installEventFilter(tooltip_filter)
        layout.addWidget(wifi_label)

        # Security Icon
        sec_label = QLabel(self)
        sec_icon = QIcon("./icons/iconio/Completed_c5d83783f271634d6a5810e602052ce5e5793d701286fec1c3ea07f45eb18442.png")  
        sec_label.setPixmap(sec_icon.pixmap(DOCK_ICON_SIZE, DOCK_ICON_SIZE))
        sec_label.mousePressEvent = lambda event: self.security()
        tooltip_filter = TooltipEventFilter(sec_label, "Protected", self)
        sec_label.installEventFilter(tooltip_filter)
        layout.addWidget(sec_label)

        # office
        off_label = QLabel(self)
        off_icon = QIcon("./icons/iconio/icon.png")  
        off_label.setPixmap(off_icon.pixmap(DOCK_ICON_SIZE, DOCK_ICON_SIZE))
        off_label.mousePressEvent = lambda event: self.off()
        tooltip_filter = TooltipEventFilter(off_label, "Office 2024", self)
        off_label.installEventFilter(tooltip_filter)
        layout.addWidget(off_label)

        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(ANIMATION_SPEED)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)

        # Set up slide animations
        self.slide_up_animation = QPropertyAnimation(self, b"pos")
        self.slide_up_animation.setDuration(ANIMATION_SPEED)
        self.slide_down_animation = QPropertyAnimation(self, b"pos")
        self.slide_down_animation.setDuration(ANIMATION_SPEED)

        # Set initial positions
        self.hidden_pos = QPoint(0, 0)  # Adjust as needed for your screen
        self.visible_pos = QPoint(0, 0)  # Adjust as needed for your screen
        self.move(self.hidden_pos)

        self.is_visible = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        option = QStyleOption()
        option.initFrom(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, option, painter, self)

    def update_time(self):
        current_time = time.strftime("%H:%M:%S\n%d-%m-%Y")
        self.time_label.setText(current_time)

    def open_volume_mixer(self):
        try:
            subprocess.Popen("sndvol.exe")
        except Exception as e:
            logging.error(f"Error opening volume mixer: {e}")

    def security(self):
        try:
            subprocess.Popen("C://Program Files//Norton//Suite//NortonUI.exe")
        except Exception as e:
            logging.error(f"Error opening Norton Security: {e}")

    def off(self):
        try:
            subprocess.Popen("pythonw C:\\Users\\97466\\Documents\\PythonDockmain\\office.pyw")
        except Exception as e:
            logging.error(f"Error opening MsOffice 2024: {e}")

    def toggle_wifi(self):
        logging.info("Toggling Wi-Fi/Flight Mode (functionality not implemented)")

def hide_taskbar():
    taskbar = ctypes.windll.user32.FindWindowA(b'Shell_TrayWnd', None)
    ctypes.windll.user32.ShowWindow(taskbar, 0)

def show_taskbar():
    taskbar = ctypes.windll.user32.FindWindowA(b'Shell_TrayWnd', None)
    ctypes.windll.user32.ShowWindow(taskbar, 9)

def main():
    if HIDE_TASKBAR:
        hide_taskbar()

    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QToolTip {
            font-size: 13px;
            padding:1px 2px;
            border-radius: 5px;
            border: 1px solid #41434c;
            background-color: rgb(30, 33, 49);
            color: white;
        }
    """)

    widget = FloatingDock()
    widget.show()
    widget.raise_()
    widget.activateWindow()

    # Position the dock at the bottom left corner
    screen = ctypes.windll.user32
    SCREEN_HEIGHT = screen.GetSystemMetrics(1)
    SCREEN_WIDTH = screen.GetSystemMetrics(0)
    widget.move(0, SCREEN_HEIGHT - widget.height())

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
