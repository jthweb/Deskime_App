import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsBlurEffect
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QPoint, QUrl
from PySide6.QtGui import QPalette, QColor

class AcrylicWidget(QMainWindow):
    def __init__(self, html_file):
        super().__init__()

        # Set window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Set layout
        layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(layout)
        self.central_widget.setStyleSheet("""
            QWidget {
                border: 2px solid rgba(255, 255, 255, 0);
                border-radius: 100px;
                background-color: rgba(255, 255, 255, 0);
            }
        """)

        # Create a QWebEngineView to display HTML content
        self.web_view = QWebEngineView(self.central_widget)
        self.web_view.setUrl(QUrl.fromLocalFile(html_file))  # Load the HTML file as QUrl

        # Set rounded corners and background color
        self.web_view.setStyleSheet("""
            QWebEngineView {
                border: 2px solid rgba(255, 255, 255, 0);
                border-radius: 100px;
                background-color: rgba(255, 255, 255, 0);
            }
        """)

        layout.addWidget(self.web_view)

        # Set the size of the window
        self.resize(400, 300)

        # Move the window to the top right corner with a 10px gap
        self.move(QApplication.primaryScreen().availableGeometry().topRight() - self.rect().topRight() - QPoint(30, -30))

        # Set the background color of the central widget to transparent
        self.central_widget.setStyleSheet("background-color: rgba(255, 255, 255, 0.0);")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application palette for acrylic effect
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255, 0))  # Transparent background
    app.setPalette(palette)

    # Path to your HTML file
    html_file_path = "\widget_site.html"

    window = AcrylicWidget(html_file_path)
    window.show()
    if sys.platform=='win32':
        from ctypes import windll
        import win32gui,win32con
        win32gui.SetWindowPos(window.winId(),win32con.HWND_BOTTOM, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE  | win32con.SWP_NOACTIVATE )

        hwnd=win32gui.GetWindow(win32gui.GetWindow(windll.user32.GetTopWindow(0),win32con.GW_HWNDLAST),win32con.GW_CHILD);
        win32gui.SetWindowLong(window.winId(),win32con.GWL_HWNDPARENT,hwnd)

    sys.exit(app.exec_())