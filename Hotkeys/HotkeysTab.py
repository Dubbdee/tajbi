from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QTableWidget, QPushButton,
    QLabel, QCheckBox, QLineEdit, QComboBox, QHeaderView, QTableWidgetItem
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import json
from Functions.GeneralFunctions import manage_profile
from Hotkeys.HotkeysThread import HotkeysThread

class HotkeysTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.hotkeys_thread = None

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))

        # Set Title and Size
        self.setWindowTitle("Hotkeys")
        self.setFixedSize(550, 350)

        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: Red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Main layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Table Widget with 4 columns: Hotkey, Time (s), Random (s), Active
        self.hotkeys_tableWidget = QTableWidget(self)
        self.hotkeys_tableWidget.setColumnCount(4)
        self.hotkeys_tableWidget.setHorizontalHeaderLabels(["Hotkey", "Time (s)", "Random (s)", "Active"])
        
        # Configure table
        header = self.hotkeys_tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Buttons
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_hotkey)
        
        self.remove_button = QPushButton("Remove", self)
        self.remove_button.clicked.connect(self.remove_hotkey)
        
        # Data sync timer
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.sync_data_to_thread)
        self.sync_timer.start(1000) # Sync every second

        # Start thread
        self.hotkeys_thread = HotkeysThread()
        self.hotkeys_thread.start()

        # Layout Arrangement
        self.layout.addWidget(self.hotkeys_tableWidget, 0, 0, 1, 2)
        self.layout.addWidget(self.add_button, 1, 0)
        self.layout.addWidget(self.remove_button, 1, 1)
        self.layout.addWidget(self.status_label, 2, 0, 1, 2)


    def add_hotkey(self):
        """Add a new editable row to the table"""
        row_position = self.hotkeys_tableWidget.rowCount()
        self.hotkeys_tableWidget.insertRow(row_position)
        
        # Column 0: Hotkey ComboBox
        hotkey_combo = QComboBox()
        for i in range(1, 13):
            hotkey_combo.addItem(f"F{i}")
        self.hotkeys_tableWidget.setCellWidget(row_position, 0, hotkey_combo)
        
        # Column 1: Time LineEdit
        time_edit = QLineEdit()
        time_edit.setPlaceholderText("2.0")
        time_edit.setText("2.0")
        self.hotkeys_tableWidget.setCellWidget(row_position, 1, time_edit)
        
        # Column 2: Random LineEdit
        random_edit = QLineEdit()
        random_edit.setPlaceholderText("0.5")
        random_edit.setText("0.5")
        self.hotkeys_tableWidget.setCellWidget(row_position, 2, random_edit)
        
        # Column 3: Active CheckBox (centered)
        active_checkbox = QCheckBox()
        active_checkbox.setChecked(False)
        # Center the checkbox
        checkbox_widget = QWidget()
        checkbox_layout = QGridLayout(checkbox_widget)
        checkbox_layout.addWidget(active_checkbox, 0, 0, Qt.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        self.hotkeys_tableWidget.setCellWidget(row_position, 3, checkbox_widget)
        
        self.status_label.setText("")

    def remove_hotkey(self):
        """Remove selected row(s) from the table"""
        selected_rows = set()
        for item in self.hotkeys_tableWidget.selectedItems():
            selected_rows.add(item.row())
        
        # Also check for selected cells with widgets
        for index in self.hotkeys_tableWidget.selectedIndexes():
            selected_rows.add(index.row())
        
        if not selected_rows:
            current_row = self.hotkeys_tableWidget.currentRow()
            if current_row >= 0:
                selected_rows.add(current_row)
        
        # Remove rows in reverse order to avoid index shifting issues
        for row in sorted(selected_rows, reverse=True):
            self.hotkeys_tableWidget.removeRow(row)



    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        
        hotkey_list = []
        for row in range(self.hotkeys_tableWidget.rowCount()):
            # Get hotkey from ComboBox
            hotkey_combo = self.hotkeys_tableWidget.cellWidget(row, 0)
            hotkey = hotkey_combo.currentText() if hotkey_combo else "F1"
            
            # Get time from LineEdit
            time_edit = self.hotkeys_tableWidget.cellWidget(row, 1)
            try:
                time_value = float(time_edit.text()) if time_edit and time_edit.text() else 2.0
            except ValueError:
                time_value = 2.0
            
            # Get random from LineEdit
            random_edit = self.hotkeys_tableWidget.cellWidget(row, 2)
            try:
                random_value = float(random_edit.text()) if random_edit and random_edit.text() else 0.5
            except ValueError:
                random_value = 0.5
            
            # Get active from CheckBox
            checkbox_widget = self.hotkeys_tableWidget.cellWidget(row, 3)
            active = False
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                active = checkbox.isChecked() if checkbox else False
            
            hotkey_data = {
                "Hotkey": hotkey,
                "Interval": time_value,
                "Randomize": random_value,
                "Active": active
            }
            hotkey_list.append(hotkey_data)
            
        data_to_save = {"hotkeys": hotkey_list}

        if manage_profile("save", "Save/Hotkeys", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' saved!")

    def load_settings(self, profile_name) -> None:
        filename = f"Save/Hotkeys/{profile_name}.json"
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)

            # Clear existing rows
            self.hotkeys_tableWidget.setRowCount(0)
            
            for entry in loaded_data.get("hotkeys", []):
                row_position = self.hotkeys_tableWidget.rowCount()
                self.hotkeys_tableWidget.insertRow(row_position)
                
                # Hotkey ComboBox
                hotkey_combo = QComboBox()
                for i in range(1, 13):
                    hotkey_combo.addItem(f"F{i}")
                hotkey_combo.setCurrentText(entry.get("Hotkey", "F1"))
                self.hotkeys_tableWidget.setCellWidget(row_position, 0, hotkey_combo)
                
                # Time LineEdit
                time_edit = QLineEdit()
                time_edit.setText(str(entry.get("Interval", 2.0)))
                self.hotkeys_tableWidget.setCellWidget(row_position, 1, time_edit)
                
                # Random LineEdit
                random_edit = QLineEdit()
                random_edit.setText(str(entry.get("Randomize", 0.5)))
                self.hotkeys_tableWidget.setCellWidget(row_position, 2, random_edit)
                
                # Active CheckBox
                active_checkbox = QCheckBox()
                active_checkbox.setChecked(entry.get("Active", False))
                checkbox_widget = QWidget()
                checkbox_layout = QGridLayout(checkbox_widget)
                checkbox_layout.addWidget(active_checkbox, 0, 0, Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.hotkeys_tableWidget.setCellWidget(row_position, 3, checkbox_widget)

            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")
    def get_hotkeys_data(self):
        hotkey_list = []
        for row in range(self.hotkeys_tableWidget.rowCount()):
            # Get hotkey from ComboBox
            hotkey_combo = self.hotkeys_tableWidget.cellWidget(row, 0)
            hotkey = hotkey_combo.currentText() if hotkey_combo else "F1"
            
            # Get time from LineEdit
            time_edit = self.hotkeys_tableWidget.cellWidget(row, 1)
            try:
                time_value = float(time_edit.text()) if time_edit and time_edit.text() else 2.0
            except ValueError:
                time_value = 2.0
            
            # Get random from LineEdit
            random_edit = self.hotkeys_tableWidget.cellWidget(row, 2)
            try:
                random_value = float(random_edit.text()) if random_edit and random_edit.text() else 0.5
            except ValueError:
                random_value = 0.5
            
            # Get active from CheckBox
            checkbox_widget = self.hotkeys_tableWidget.cellWidget(row, 3)
            active = False
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                active = checkbox.isChecked() if checkbox else False
            
            hotkey_list.append({
                "Hotkey": hotkey,
                "Interval": time_value,
                "Randomize": random_value,
                "Active": active
            })
        return hotkey_list

    def sync_data_to_thread(self):
        if self.hotkeys_thread:
            data = self.get_hotkeys_data()
            self.hotkeys_thread.update_hotkey_data(data)

    def closeEvent(self, event):
        if self.hotkeys_thread:
            self.hotkeys_thread.stop()
            self.hotkeys_thread.wait(2000)
        event.accept()
