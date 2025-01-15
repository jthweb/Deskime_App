import sys
import json
import logging
import ctypes
import time
from PyQt6.QtWidgets import QApplication, QFrame, QStyleOption, QStyle, QHBoxLayout, QLabel, QToolTip, QGraphicsOpacityEffect
from PyQt6.QtGui import QDesktopServices, QIcon, QPixmap, QPainter, QCursor, QFontMetrics
from PyQt6.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QUrl, QObject, QEvent, QPoint
from ctypes import windll
from win32api import GetSystemMetrics

############### SETTINGS ####################
DOCK_ICON_SIZE = 36
ANIMATION_SPEED = 200
PADDING = 6
BORDER_RADIUS = 16
HIDE_TASKBAR = False  # Hide Windows taskbar when Dock is running. Taskbar must have enabled Auto Hide option. Only primary taskbar will be hidden.
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
                x = global_pos.x() + ((DOCK_ICON_SIZE - PADDING) - tooltip_width) // 2
                y = global_pos.y() - DOCK_ICON_SIZE - PADDING
                QToolTip.showText(QPoint(x, y), self.tooltip_text, obj)
        elif event.type() == QEvent.Type.Leave:
            QToolTip.hideText()
        return False

class FloatingDock(QFrame):
    def __init__(self, config):
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
        for label_name, label_info in config.items():
            icon_label = QLabel(self)
            icon_path = label_info["icon"]
            icon = QIcon(icon_path)
            pixmap = icon.pixmap(DOCK_ICON_SIZE, DOCK_ICON_SIZE)
            icon_label.setPixmap(pixmap)
            action_type = label_info["type"]
            if action_type == "open_app":
                action = lambda exec=label_info["exec"]: self.open_app(exec)
            elif action_type == "open_url":
                action = lambda url=label_info["url"]: self.open_website(url)
            else:
                action = lambda: None
            icon_label.mousePressEvent = lambda event, action=action: self.on_icon_click(event, action)
            tooltip_filter = TooltipEventFilter(icon_label, label_name, self)
            icon_label.installEventFilter(tooltip_filter)
            layout.addWidget(icon_label)

        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_visibility)
        self.timer.start(400)
        self.is_visible = False

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(ANIMATION_SPEED)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        option = QStyleOption()
        option.initFrom(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, option, painter, self)

    def toggle_visibility(self):
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        if self.rect().contains(cursor_pos):
            if not self.is_visible:
                self.slide_up_animation.start()
                self.opacity_animation.setStartValue(0)
                self.opacity_animation.setEndValue(1)
                self.opacity_animation.start()
                self.show()
                self.is_visible = True
        else:
            if self.is_visible:
                self.slide_down_animation.start()
                self.opacity_animation.setStartValue(1)
                self.opacity_animation.setEndValue(0)
                self.opacity_animation.start()
                self.is_visible = False

    def on_icon_click(self, event, action):
        if event.button() == Qt.MouseButton.LeftButton:
            action()

    def open_app(self, exec):
        try:
            import subprocess
            subprocess.Popen(exec)
        except Exception as e:
            logging.error(f"Error executing: {e}")

    def open_website(self, url):
        try:
            QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            logging.error(f"Error opening website: {e}")

def hide_taskbar():
    taskbar = ctypes.windll.user32.FindWindowA(b'Shell_TrayWnd', None)
    ctypes.windll.user32.ShowWindow(taskbar, 0)

def show_taskbar():
    taskbar = ctypes.windll.user32.FindWindowA(b'Shell_TrayWnd', None)
    ctypes.windll.user32.ShowWindow(taskbar, 9)

def app_config():
    with open("Taskbar_items.json", "r") as config_file:
        return json.load(config_file)

def main():
    if HIDE_TASKBAR:
        hide_taskbar()
    else:
        show_taskbar()

    config = app_config()
    app = QApplication(sys.argv)
    # Set the global stylesheet for QToolTip
    app.setStyleSheet("""
        QToolTip {
            font-size: 13px;
            padding:1px 2px;
            border-radius: 2px;
            border: 1px solid #41434c;
            background-color: rgb(30, 33, 49);
            color: white;
        }
    """)
    widget = FloatingDock(config)
    # Ensure the widget calculates its layout immediately
    widget.show()
    widget.raise_()
    widget.activateWindow()
    
    screen = ctypes.windll.user32
    dpi = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    SCREEN_HEIGHT = int (screen.GetSystemMetrics(1) // dpi)
    SCREEN_WIDTH  = int (screen.GetSystemMetrics(0) // dpi)
    widget.move((SCREEN_WIDTH - widget.width()) // 2, SCREEN_HEIGHT - 1)
    
    TOTAL_HEIGHT = DOCK_ICON_SIZE + (PADDING * 4) + 2 # Padding bottom + border
    widget.hidden_pos = QPoint((SCREEN_WIDTH - widget.width()) // 2, SCREEN_HEIGHT - 1)
    widget.visible_pos = QPoint((SCREEN_WIDTH - widget.width()) // 2, SCREEN_HEIGHT - TOTAL_HEIGHT)
    widget.hide()
    widget.slide_up_animation = QPropertyAnimation(widget, b"pos")
    widget.slide_up_animation.setDuration(ANIMATION_SPEED)
    widget.slide_up_animation.setStartValue(widget.hidden_pos)
    widget.slide_up_animation.setEndValue(widget.visible_pos)

    widget.slide_down_animation = QPropertyAnimation(widget, b"pos")
    widget.slide_down_animation.setDuration(ANIMATION_SPEED)
    widget.slide_down_animation.setStartValue(widget.visible_pos)
    widget.slide_down_animation.setEndValue(widget.hidden_pos)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
