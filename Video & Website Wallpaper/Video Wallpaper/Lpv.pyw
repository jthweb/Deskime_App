import sys
import ctypes
import traceback
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QPixmap, QImage
from ffpyplayer.player import MediaPlayer
from PIL import Image
import winreg  # Windows registry module

user32 = ctypes.windll.user32
SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

def get_workerw_window():
    """Find the WorkerW window that Windows uses to display the desktop background."""
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

class VideoWallpaper(QMainWindow):
    command_signal = pyqtSignal(str)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.player = None
        self.label = QLabel(self)
        self.is_playing = True
        self.stop_requested = threading.Event()
        self.original_wallpaper = self.get_current_wallpaper()
        self.current_volume = 0.0  # Store the current volume (100%)
        self.timer = QTimer(self)
        self.initUI()
        self.init_video_player(self.video_path)

        # Connect signal to slot
        self.command_signal.connect(self.process_command)

    def initUI(self):
        """Initialize the video window."""
        try:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setWindowFlag(Qt.Tool)
            self.setWindowFlag(Qt.WindowStaysOnBottomHint)

            workerw = get_workerw_window()
            if workerw:
                ctypes.windll.user32.SetParent(int(self.winId()), workerw)

            self.setGeometry(0, 0, ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
            self.show()
        except Exception as e:
            print("Error initializing the UI:")
            traceback.print_exc()

    def init_video_player(self, video_path):
        """Initialize the video player and start playing."""
        try:
            self.player = MediaPlayer(video_path)
            self.set_volume(self.current_volume)  # Default volume level (100%)
            self.timer.timeout.connect(self.play_frame)
            self.timer.start(33)  # Set initial interval to approximately 30 fps
        except Exception as e:
            print("Error initializing video player:")
            traceback.print_exc()

    def set_volume(self, volume_level):
        """Set the volume of the video player."""
        if self.player:
            self.player.set_volume(volume_level)

    def play_frame(self):
        """Play each frame of the video."""
        if self.stop_requested.is_set():
            return  # Stop processing frames if a stop has been requested

        try:
            if self.is_playing:
                frame, val = self.player.get_frame()
                if val == 'eof':
                    self.player.seek(0, relative=False)  # Loop the video
                if frame is not None:
                    img, _ = frame
                    img_size = img.get_size()
                    raw_image = Image.frombytes('RGB', img_size, img.to_bytearray()[0])
                    qimage = QImage(raw_image.tobytes(), raw_image.width, raw_image.height, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimage)
                    self.label.setPixmap(pixmap)
                    self.label.setGeometry(0, 0, self.width(), self.height())
        except Exception as e:
            print("Error playing video frame:")
            traceback.print_exc()

    def get_current_wallpaper(self):
        """Get the path of the current wallpaper from the Windows Registry."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
                wallpaper_path, _ = winreg.QueryValueEx(key, "WallPaper")
                return wallpaper_path
        except Exception as e:
            print("Error retrieving current wallpaper path:")
            traceback.print_exc()
            return ""

    def set_wallpaper(self, wallpaper_path):
        """Set the desktop wallpaper."""
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)

    def restore_original_wallpaper(self):
        """Restore the original wallpaper."""
        if self.original_wallpaper:
            print(f"Restoring original wallpaper: {self.original_wallpaper}")
            self.set_wallpaper(self.original_wallpaper)
        else:
            print("No original wallpaper found. Setting default blank wallpaper.")
            self.set_wallpaper("")  # Set default wallpaper or a blank wallpaper

    def process_command(self, command):
        """Process commands received from stdin."""
        if command == 'play':
            self.is_playing = True
            self.set_volume(self.current_volume)  # Restore the volume
            print("Playing video and audio.")
        elif command == 'pause':
            self.is_playing = False
            self.current_volume = self.player.get_volume()  # Save the current volume level
            self.set_volume(0.0)  # Mute the audio
            print("Pausing video and muting audio.")
        elif command.startswith('volume'):
            try:
                _, volume_level = command.split()
                volume_level = float(volume_level)
                self.current_volume = volume_level  # Update current volume
                self.set_volume(volume_level)
                print(f"Setting volume to {volume_level}.")
            except ValueError:
                print("Invalid volume command. Usage: volume <level>")
        elif command.startswith('frames'):
            try:
                _, frame_rate = command.split()
                frame_rate = int(frame_rate)
                self.set_frame_rate(frame_rate)
                print(f"Setting frame rate to {frame_rate} fps.")
            except ValueError:
                print("Invalid frame rate command. Usage: frames <rate>")
        elif command == 'remove':
            self.remove_wallpaper()
            print("Removing video wallpaper.")
        elif command == 'exit':
            self.exit_application()
            print("Exiting application.")
        else:
            print("Unknown command.")

    def set_frame_rate(self, frame_rate):
        """Adjust the frame rate of the video playback."""
        if frame_rate > 0:
            interval = int(1000 / frame_rate)  # Convert frame rate to interval in milliseconds
            self.timer.setInterval(interval)
            print(f"Frame rate set to {frame_rate} fps (Interval: {interval} ms).")
        else:
            print("Frame rate must be greater than 0.")

    @pyqtSlot()
    def remove_wallpaper(self):
        """Stop the video player and close the window, restore the original wallpaper."""
        self.stop_requested.set()  # Stop playing frames
        self.timer.stop()          # Stop the timer
        if self.player:
            self.player.close_player()  # Stop the MediaPlayer
        self.restore_original_wallpaper()  # Restore original wallpaper
        self.close()                # Close the window

    def exit_application(self):
        """Exit the application gracefully."""
        self.stop_requested.set()  # Stop playing frames
        self.timer.stop()          # Stop the timer
        if self.player:
            self.player.close_player()  # Stop the MediaPlayer
        self.restore_original_wallpaper()  # Restore original wallpaper
        self.close()                # Close the window
        QApplication.quit()        # Quit the QApplication event loop

class CommandThread(QThread):
    def __init__(self, video_wallpaper, parent=None):
        super().__init__(parent)
        self.video_wallpaper = video_wallpaper
        self.running = True

    def run(self):
        """Listen for commands from stdin."""
        print("You can now send commands (play, pause, volume <level>, frames <rate>, remove, exit):")
        while self.running:
            command = sys.stdin.readline().strip()  # Non-blocking command input
            if command:
                self.video_wallpaper.command_signal.emit(command)
                if command == 'exit':
                    self.running = False

class LpvCLI:
    def __init__(self):
        self.video_wallpaper = None

    def start_wallpaper(self, video_path):
        """Start the video wallpaper."""
        app = QApplication(sys.argv)
        self.video_wallpaper = VideoWallpaper(video_path)

        # Start a thread to listen for commands from stdin
        command_thread = CommandThread(self.video_wallpaper)
        command_thread.start()

        app.exec_()

def main():
    if len(sys.argv) > 1:
        video_path = sys.argv[1]  # Get the video path from the command line
        lpv = LpvCLI()
        lpv.start_wallpaper(video_path)
    else:
        print("Please provide a video file as an argument.")

if __name__ == "__main__":
    main()
