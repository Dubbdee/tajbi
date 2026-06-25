from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QListWidget, QComboBox, QPushButton,
    QLabel, QCheckBox, QListWidgetItem
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import json
from Functions.GeneralFunctions import delete_item, manage_profile
from SmartHotkeys.SmartHotkeysThread import SmartHotkeysThread, SetSmartHotkeyThread


class SmartHotkeysTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.smart_hotkeys_thread = None
        self.set_smart_hotkey_thread = None

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))

        # Set Title and Size
        self.setWindowTitle("Smart Hotkeys")
        self.setFixedSize(300, 200)  # Increased to fit the status label and checkbox

        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: Red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Main layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # List Widgets
        self.smart_hotkeys_listWidget = QListWidget(self)
        self.smart_hotkeys_listWidget.setFixedHeight(60)
        self.smart_hotkeys_listWidget.itemDoubleClicked.connect(
            lambda item: delete_item(self.smart_hotkeys_listWidget, item)
        )

        # Combo Boxes
        self.rune_option_combobox = QComboBox(self)
        self.rune_option_combobox.addItems(["With Crosshair", "On Target", "On Yourself"])

        self.hotkey_option_combobox = QComboBox(self)
        for i in range(1, 13):
            self.hotkey_option_combobox.addItem(f"F{i}")

        # Buttons
        self.coordinates_button = QPushButton("Coordinates", self)

        # Button functions
        self.coordinates_button.clicked.connect(self.start_set_hotkey_thread)

        # Add Widgets to Layout
        self.layout.addWidget(self.smart_hotkeys_listWidget, 0, 0, 1, 3)
        self.layout.addWidget(self.rune_option_combobox, 1, 0)
        self.layout.addWidget(self.hotkey_option_combobox, 1, 1)
        self.layout.addWidget(self.coordinates_button, 1, 2)

        # Finally, add the status label in row 2 (spanning all columns)
        self.layout.addWidget(self.status_label, 2, 0, 1, 3)

    def start_set_hotkey_thread(self) -> None:
        if self.set_hotkey_thread and self.set_hotkey_thread.isRunning():
            self.set_hotkey_thread.stop()
            self.set_hotkey_thread.wait(2000)

        hotkey_name = self.hotkey_option_combobox.currentText()
        rune_option = self.rune_option_combobox.currentText()
        
        self.set_hotkey_thread = SetSmartHotkeyThread(hotkey_name, rune_option)
        self.set_hotkey_thread.status_signal.connect(self.update_status_label)
        self.set_hotkey_thread.hotkey_set_signal.connect(self.add_smart_hotkey_item)
        self.set_hotkey_thread.start()

    def update_status_label(self, text, style):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(style)

    def add_smart_hotkey_item(self, data):
        hotkey_item = QListWidgetItem(data["Hotkey"])
        hotkey_item.setData(Qt.UserRole, data)
        self.smart_hotkeys_listWidget.addItem(hotkey_item)
        # If smart hotkeys thread is running, we might need to update its data
        if self.smart_hotkeys_thread and self.smart_hotkeys_thread.isRunning():
            self.start_smart_hotkeys_thread(Qt.Checked)

    def start_smart_hotkeys_thread(self, state) -> None:
        if state == Qt.Checked:
            if self.smart_hotkeys_thread:
                self.smart_hotkeys_thread.stop()
                self.smart_hotkeys_thread.wait(2000)

            # Extract data
            hotkeys_data = [
                self.smart_hotkeys_listWidget.item(i).data(Qt.UserRole)
                for i in range(self.smart_hotkeys_listWidget.count())
            ]
            
            self.smart_hotkeys_thread = SmartHotkeysThread(hotkeys_data)
            self.smart_hotkeys_thread.start()
        else:
            if self.smart_hotkeys_thread:
                self.smart_hotkeys_thread.stop()
                self.smart_hotkeys_thread.wait(2000)
                self.smart_hotkeys_thread = None

    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        hotkey_list = []
        for i in range(self.smart_hotkeys_listWidget.count()):
            item = self.smart_hotkeys_listWidget.item(i)
            hotkey_list.append({
                "Name": item.text(),
                "Data": item.data(Qt.UserRole)
            })
            
        data_to_save = {"smart_hotkeys": hotkey_list}

        if manage_profile("save", "Save/SmartHotkeys", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")

    def load_settings(self, profile_name) -> None:
        filename = f"Save/SmartHotkeys/{profile_name}.json"
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)

            self.smart_hotkeys_listWidget.clear()
            for hotkey_entry in loaded_data.get("smart_hotkeys", []):
                item = QListWidgetItem(hotkey_entry["Name"])
                item.setData(Qt.UserRole, hotkey_entry["Data"])
                self.smart_hotkeys_listWidget.addItem(item)

            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")
