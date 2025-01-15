import sys
import webbrowser
import os
import re
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QHBoxLayout, QWidget
from plyer import notification
from asteval import Interpreter  # Importing the Interpreter for safe evaluation

class SearchBar(QMainWindow):
    def __init__(self):
        super().__init__()


        # Set up the main window properties
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 400, 100)

        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Set up layout
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create the search bar
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search / Command...")
        self.search_input.setFont(QFont("Jetbrains Mono", 14))
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 50);
                border: none;
                border-radius: 15px;
                padding: 10px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        self.search_input.returnPressed.connect(self.perform_search)  # Connect the return key to the search function

        # Add the search bar to the layout
        layout.addWidget(self.search_input)

        # Set the window to the bottom right of the screen
        self.set_position()


    def set_position(self):
        """Position the window in the bottom right corner of the screen."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        x = screen_rect.width() - self.width() - 5  # 5 pixels from the right edge
        y = screen_rect.height() - self.height() - 5  # 5 pixels from the bottom edge
        self.move(x, y)

    def perform_search(self):
        """Perform the search or command based on user input."""
        query = self.search_input.text().strip().lower()  # Normalize the query
        if query:
            try:
                if query == "shutdown":
                    os.system("SlideToShutdown")  # Use SlideToShutdown
                elif self.is_math_operation(query):
                    # Handle implicit multiplication
                    query = self.handle_implicit_multiplication(query)
                    result = self.calculate(query)  # Calculate the result
                    self.show_notification("Calculation Result", f"The result of '{query}' is: {result}")
                else:
                    self.perform_web_search(query)  # Default to web search
            except Exception as e:
                self.show_notification("Error", f"An error occurred: {e}")

            self.search_input.clear()  # Clear the input after processing

    def handle_implicit_multiplication(self, query):
        """Replace implicit multiplication (e.g., 3(9-10) with 3 * (9 - 10))."""
        return re.sub(r'(\d+(\.\d+)?)(\()', r'\1 * \3', query)

    def perform_web_search(self, query):
        url = f"https://duckduckgo.com/?q={query}"

        try:
            webbrowser.open(url)  # Open the URL in the default web browser
        except Exception as e:
            self.show_notification("Error", f"Error performing web search: {e}")

    def is_math_operation(self, query):
        """Check if the query is a valid math operation, including decimals and parentheses."""
        return bool(re.match(r'^[\d\s\+\-\*\/\.\$%]+$', query))

    def calculate(self, query):
        """Evaluate the mathematical expression safely using asteval."""
        interpreter = Interpreter()  # Create an interpreter instance
        try:
            result = interpreter.eval(query)  # Evaluate the expression
            return result
        except Exception as e:
            self.show_notification("Error", f"Error in calculation: {e}")
            return "Error"

    def show_notification(self, title, message):
        """Show a Windows notification."""
        notification.notify(
            title=title,
            message=message,
            app_name='SearchBar',
            timeout=12  # Notification will be visible for 12 seconds
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the background color to be transparent
    app.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0); }")

    window = SearchBar()
    window.show()
    sys.exit(app.exec())