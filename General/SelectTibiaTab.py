import Addresses
from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QListWidget, QLabel, QVBoxLayout)
from PyQt5.QtGui import QIcon
from General.MainWindowTab import MainWindowTab
import win32gui
import win32process
import psutil


class SelectTibiaTab(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.process_list = []

        # Set window icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))
        self.setWindowTitle("EasyBot Select Client")
        self.setFixedSize(500, 400)

        # Layout
        self.layout = QVBoxLayout(self)

        # Label
        label = QLabel("Select a process to attach:", self)
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(label)

        # List widget
        self.process_listwidget = QListWidget(self)
        self.layout.addWidget(self.process_listwidget)

        # Connect button
        self.connect_button = QPushButton('Connect to Selected Process', self)
        self.connect_button.clicked.connect(self.load_tibia_button)
        self.layout.addWidget(self.connect_button)

        # Refresh button
        self.refresh_button = QPushButton('Refresh Process List', self)
        self.refresh_button.clicked.connect(self.refresh_processes)
        self.layout.addWidget(self.refresh_button)

        # Load processes on init
        self.refresh_processes()

    def refresh_processes(self):
        """Enumerate all processes with windows and display them."""
        self.process_listwidget.clear()
        self.process_list = []

        def enum_window_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text and "Easy Bot" not in window_text:  # Filter out empty titles and bot itself
                    try:
                        _, proc_id = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(proc_id)
                        process_name = process.name()
                        
                        # Store process info
                        self.process_list.append({
                            'hwnd': hwnd,
                            'window_title': window_text,
                            'proc_id': proc_id,
                            'process_name': process_name
                        })
                        
                        # Display in list
                        display_text = f"{window_text} ({process_name} - PID: {proc_id})"
                        self.process_listwidget.addItem(display_text)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

        win32gui.EnumWindows(enum_window_callback, None)

    def load_tibia_button(self) -> None:
        selected_index = self.process_listwidget.currentRow()
        if selected_index < 0 or selected_index >= len(self.process_list):
            return  # No selection
        
        selected_process = self.process_list[selected_index]
        
        # Pass selected process info to Addresses
        Addresses.load_tibia(
            window_title=selected_process['window_title'],
            proc_id=selected_process['proc_id'],
            hwnd=selected_process['hwnd']
        )
        
        self.close()
        self.main_window = MainWindowTab()
        self.main_window.show()

