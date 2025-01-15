import sys
import ctypes
import winreg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

user32 = ctypes.windll.user32
SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

def get_workerw_window():
    progman = user32.FindWindowW("Progman", None)
    result = ctypes.c_void_p()
    user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, 0, 1000, ctypes.byref(result))

    workerw = None
    def enum_windows_proc(hwnd, lParam):
        p = ctypes.create_unicode_buffer(255)
        user32.GetClassNameW(hwnd, p, 255)
        if p.value == "WorkerW":
            workerw_handle = ctypes.windll.user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", 0)
            if workerw_handle != 0:
                nonlocal workerw
                workerw = ctypes.windll.user32.FindWindowExW(0, hwnd, "WorkerW", 0)
        return True

    enum_windows_proc_t = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(enum_windows_proc_t(enum_windows_proc), 0)

    return workerw

class WebWallpaper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.url = QUrl("!!! YOUR CUSTOM LINK/HTML FILE HERE !!!")
        self.web_view = QWebEngineView(self)
        self.original_wallpaper = self.get_current_wallpaper()
        self.initUI()

    def initUI(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))

        workerw = get_workerw_window()
        if workerw:
            ctypes.windll.user32.SetParent(int(self.winId()), workerw)

        self.web_view.setUrl(self.url)
        self.web_view.setGeometry(0, 0, self.width(), self.height())
        self.web_view.show()
        self.show()

    def get_current_wallpaper(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
                wallpaper_path, _ = winreg.QueryValueEx(key, "WallPaper")
                return wallpaper_path
        except Exception:
            return ""

    def set_wallpaper(self, wallpaper_path):
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)

    def restore_original_wallpaper(self):
        if self.original_wallpaper:
            self.set_wallpaper(self.original_wallpaper)
        else:
            self.set_wallpaper("")

    def closeEvent(self, event):
        self.restore_original_wallpaper()
        event.accept()

class LpvCLI:
    def __init__(self):
        self.web_wallpaper = None

    def start_wallpaper(self):
        app = QApplication(sys.argv)
        self.web_wallpaper = WebWallpaper()
        app.exec_()

def main():
    lpv = LpvCLI()
    lpv.start_wallpaper()

if __name__ == "__main__":
    main()
