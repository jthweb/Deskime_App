import os
import subprocess
import sys
import time
import ctypes
from pathlib import Path

def install_package(package):
    """Install a package using pip and suppress errors."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    except subprocess.CalledProcessError:
        pass  # Suppress any errors during installation

def enable_ansi_support():
    """Enable ANSI escape sequences on Windows."""
    if os.name == 'nt':
        import colorama
        colorama.init()  # Initialize colorama to enable ANSI support

def print_error(message):
    """Print error messages in red."""
    print("\033[91m" + message + "\033[0m")  # Red text
    time.sleep(2.2)

def print_success(message):
    """Print success messages in green."""
    print("\033[92m" + message + "\033[0m")  # Green text
    time.sleep(1.5)

def check_pythonw():
    """Check if pythonw is available."""
    try:
        subprocess.run(['pythonw', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_success("pythonw is available")
        time.sleep(2.2)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Error: pythonw is not available. Please ensure Python is installed correctly.")
        time.sleep(2.2)
        sys.exit(1)

def install_requirements():
    """Install the packages listed in requirements.txt."""
    if os.path.exists('requirements.txt'):
        print("Installing requirements from requirements.txt...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print_success("Requirements installed successfully.")
        time.sleep(2.2)
    else:
        print_error("Error: requirements.txt not found. Please ensure it is in the same directory as setup.py.")
        time.sleep(2.2)
        sys.exit(1)

def install_fonts():
    """Install all .ttf and .otf fonts in the fonts directory."""
    fonts_dir = Path('fonts')
    if fonts_dir.exists() and fonts_dir.is_dir():
        font_files = list(fonts_dir.glob('*.ttf')) + list(fonts_dir.glob('*.otf'))
        if font_files:
            for font in font_files:
                try:
                    subprocess.run(['copy', str(font), 'C:\\Windows\\Fonts'], check=True, shell=True)
                    print_success(f"Installed font: {font.name}")
                    time.sleep(1.3)
                except subprocess.CalledProcessError:
                    print_error(f"Error installing font: {font.name}")
                    time.sleep(2.2)
        else:
            print_error("Error: No .ttf or .otf fonts found in the /fonts directory.")
            time.sleep(2.2)
    else:
        print_error("Error: /fonts directory not found. Please ensure it exists and contains .ttf or .otf files.")
        time.sleep(2.2)
        sys.exit(1)


def force_admin_mode():
    """Request administrator privileges."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Relaunch the script with admin privileges
        print("Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

def print_waiting(message):
    """Print waiting messages in orangish-yellow."""
    print("\033[38;5;214m" + message + "\033[0m")  # Orangish-yellow text
    time.sleep(2.2)

if __name__ == "__main__":
    force_admin_mode()     # Request administrator privileges
    print_waiting("Please wait...")  # Display waiting message
    install_package('colorama')  # Install the colorama package
    enable_ansi_support()  # Enable ANSI support for Windows terminals
    print_waiting("Checking for pythonw...")  # Display waiting message
    check_pythonw()        # Check if pythonw is available
    print_waiting("Installing requirements...")  # Display waiting message
    install_requirements()  # Install required packages
    print_waiting("Installing fonts...")  # Display waiting message
    install_fonts()        # Install fonts
    print_success("Congrats! Deskime is installed!")  # Display success message
    time.sleep(2)
