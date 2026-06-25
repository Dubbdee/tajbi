import json
import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QLineEdit, QTextEdit, QCheckBox, QComboBox, QVBoxLayout,
    QHBoxLayout, QGroupBox, QPushButton, QListWidgetItem, QLabel, QGridLayout, QSlider,
    QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QIcon

from Functions.GeneralFunctions import delete_item, manage_profile
from Functions.MemoryFunctions import *
from Walker.WalkerThread import WalkerThread, RecordThread


class WalkerTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.record_thread = None
        self.walker_thread = None

        # Other Variables
        self.labels_dictionary = {}

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))
        # Set Title and Size
        self.setWindowTitle("Walker")
        self.setFixedSize(550, 450)  # Increased size for blacklist

        # --- Status label at the bottom (behaves like a "status bar")
        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Widgets
        self.waypointList_listWidget = QListWidget(self)
        self.record_checkBox = QCheckBox("Auto Recording", self)
        
        # Blacklist widgets
        self.blacklist_x_lineEdit = QLineEdit(self)
        self.blacklist_y_lineEdit = QLineEdit(self)
        self.blacklist_z_lineEdit = QLineEdit(self)
        self.tiles_blacklist_listWidget = QListWidget(self)
        self.tiles_blacklist_listWidget.setFixedSize(150, 200)
        self.current_pos_label = QLabel("Current Pos: -, -, -", self)
        self.current_pos_label.setAlignment(Qt.AlignCenter)
        
        # Directions Group
        self.direction_group = QButtonGroup(self)
        self.direction_buttons = {}
        
        # Actions Group
        self.action_group = QButtonGroup(self)
        self.action_buttons = {}

        # Recording interval slider (1-4 squares)
        self.interval_slider = QSlider(Qt.Horizontal, self)
        self.interval_slider.setMinimum(1)
        self.interval_slider.setMaximum(4)
        self.interval_slider.setValue(1)
        self.interval_slider.setTickPosition(QSlider.TicksBelow)
        self.interval_slider.setTickInterval(1)
        
        self.interval_label = QLabel("Record every: 1 square", self)
        self.interval_slider.valueChanged.connect(self.update_interval_label)

        # Main Layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Initialize UI
        self.waypointList()
        self.tilesBlacklist()

        # Finally add the status label (we'll place it at the bottom row)
        self.layout.addWidget(self.status_label, 2, 0, 1, 2)
        
        # Timer to update current position
        self.position_timer = QTimer(self)
        self.position_timer.timeout.connect(self.update_current_position)
        self.position_timer.start(500)  # Update every 500ms


    def waypointList(self) -> None:
        groupbox = QGroupBox("Waypoints")
        main_layout = QHBoxLayout()
        groupbox.setLayout(main_layout)

        # Left side: List and Clear button
        left_layout = QVBoxLayout()
        clearWaypointList_button = QPushButton("Clear List", self)
        clearWaypointList_button.clicked.connect(self.clear_waypointList)
        left_layout.addWidget(self.waypointList_listWidget)
        left_layout.addWidget(clearWaypointList_button)

        # Right side: Controls
        right_layout = QVBoxLayout()

        # Directions GroupBox
        dir_gb = QGroupBox("Direction")
        dir_layout = QGridLayout()
        dir_gb.setLayout(dir_layout)
        
        # Mapping: Text, Index, Row, Col
        dir_config = [
            ("NW", 6, 0, 0), ("N", 1, 0, 1), ("NE", 5, 0, 2),
            ("W", 4, 1, 0), ("C", 0, 1, 1), ("E", 3, 1, 2),
            ("SW", 8, 2, 0), ("S", 2, 2, 1), ("SE", 7, 2, 2)
        ]
        
        for text, idx, r, c in dir_config:
            rb = QRadioButton(text)
            self.direction_group.addButton(rb, idx)
            dir_layout.addWidget(rb, r, c)
            self.direction_buttons[idx] = rb
        
        if 0 in self.direction_buttons:
            self.direction_buttons[0].setChecked(True)

        # Actions GroupBox
        act_gb = QGroupBox("Action")
        act_layout = QGridLayout()
        act_gb.setLayout(act_layout)
        
        act_config = [
            ("Stand", 0), ("Lure", 4), ("Rope", 1), ("Shovel", 2), ("Ladder", 3)
        ]
        
        row, col = 0, 0
        for text, idx in act_config:
            rb = QRadioButton(text)
            self.action_group.addButton(rb, idx)
            act_layout.addWidget(rb, row, col)
            self.action_buttons[idx] = rb
            col += 1
            if col > 1:
                col = 0
                row += 1
            
        if 0 in self.action_buttons:
            self.action_buttons[0].setChecked(True)

        # Add Button
        add_btn = QPushButton("Add Waypoint", self)
        add_btn.clicked.connect(self.add_waypoint)

        # Layout Assembly
        right_layout.addWidget(dir_gb)
        right_layout.addWidget(act_gb)
        right_layout.addWidget(add_btn)
        
        # Recording stuff
        rec_layout = QVBoxLayout()
        rec_layout.addWidget(self.record_checkBox)
        rec_layout.addWidget(self.interval_label)
        rec_layout.addWidget(self.interval_slider)
        self.record_checkBox.stateChanged.connect(self.start_record_thread)
        right_layout.addLayout(rec_layout)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)
        
        self.waypointList_listWidget.itemDoubleClicked.connect(
            lambda item: delete_item(self.waypointList_listWidget, item)
        )

        self.layout.addWidget(groupbox, 0, 0, 1, 2)



    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        waypoint_list = [
            self.waypointList_listWidget.item(i).data(Qt.UserRole)
            for i in range(self.waypointList_listWidget.count())
        ]
        blacklist = [
            self.tiles_blacklist_listWidget.item(i).data(Qt.UserRole)
            for i in range(self.tiles_blacklist_listWidget.count())
        ]
        data_to_save = {
            "waypoints": waypoint_list,
            "blacklist": blacklist
        }
        if manage_profile("save", "Save/Waypoints", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")

    def load_settings(self, profile_name) -> None:
        filename = f"Save/Waypoints/{profile_name}.json"
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)

            self.waypointList_listWidget.clear()
            self.tiles_blacklist_listWidget.clear()
            
            for walk_data in loaded_data.get("waypoints", []):
                action = int(walk_data.get('Action', 0))
                direction = int(walk_data.get('Direction', 0))
                
                # Backward compatibility for old Lure (Direction=9 -> Action=4)
                if direction == 9 and action == 0:
                    action = 4
                    direction = 0 # Default to Center or keep as is? Center seems safer.
                    walk_data['Action'] = 4
                    walk_data['Direction'] = 0

                walk_name = "Unknown"
                dir_text = "Center"
                if direction in self.direction_buttons:
                     dir_text = self.direction_buttons[direction].text()
                     if dir_text == "C": dir_text = "Center"

                if action == 0:  # Stand
                    walk_name = f"Stand: {walk_data['X']} {walk_data['Y']} {walk_data['Z']} {dir_text}"
                elif action == 1:  # Rope
                    walk_name = f"Rope: {walk_data['X']} {walk_data['Y']} {walk_data['Z']} {dir_text}"
                elif action == 2:  # Shovel
                    walk_name = f"Shovel: {walk_data['X']} {walk_data['Y']} {walk_data['Z']} {dir_text}"
                elif action == 3:  # Ladder
                    walk_name = f"Ladder: {walk_data['X']} {walk_data['Y']} {walk_data['Z']} {dir_text}"
                elif action == 4:  # Lure
                    walk_name = f"Lure: {walk_data['X']} {walk_data['Y']} {walk_data['Z']} {dir_text}"

                walk_item = QListWidgetItem(walk_name)
                walk_item.setData(Qt.UserRole, walk_data)
                self.waypointList_listWidget.addItem(walk_item)
            
            # Load blacklist
            for tile_data in loaded_data.get("blacklist", []):
                tile_text = f"{tile_data['X']}, {tile_data['Y']}, {tile_data['Z']}"
                tile_item = QListWidgetItem(tile_text)
                tile_item.setData(Qt.UserRole, tile_data)
                self.tiles_blacklist_listWidget.addItem(tile_item)
            
            # Restore selection to defaults or last used? Defaults for now.
            if 0 in self.action_buttons: self.action_buttons[0].setChecked(True)
            if 0 in self.direction_buttons: self.direction_buttons[0].setChecked(True)

            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")

    def add_waypoint(self):
        x, y, z = read_my_wpt()
        
        action_id = self.action_group.checkedId()
        direction_id = self.direction_group.checkedId()
        
        waypoint_data = {
            "X": x,
            "Y": y,
            "Z": z,
            "Action": action_id,
            "Direction": direction_id
        }

        self.status_label.setText("")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        display_text = "Unknown"
        dir_text = self.direction_group.button(direction_id).text()
        if dir_text == "C": dir_text = "Center"

        if action_id == 0:  # Stand
            display_text = f'Stand: {x} {y} {z} {dir_text}'
        elif action_id == 1:  # Rope
            display_text = f'Rope: {x} {y} {z} {dir_text}'
        elif action_id == 2:  # Shovel
            display_text = f'Shovel: {x} {y} {z} {dir_text}'
        elif action_id == 3:  # Ladder
            display_text = f'Ladder: {x} {y} {z} {dir_text}'
        elif action_id == 4:  # Lure
            display_text = f'Lure: {x} {y} {z} {dir_text}'

        waypoint = QListWidgetItem(display_text)
        waypoint.setData(Qt.UserRole, waypoint_data)
        self.waypointList_listWidget.addItem(waypoint)
        
        if self.waypointList_listWidget.currentRow() == -1:
            self.waypointList_listWidget.setCurrentRow(0)
        else:
            self.waypointList_listWidget.setCurrentRow(self.waypointList_listWidget.currentRow() + 1)
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText("Waypoint added successfully!")

    def clear_waypointList(self) -> None:
        self.waypointList_listWidget.clear()
        self.status_label.setText("")  # Clear status if you want

    def tilesBlacklist(self) -> None:
        """Create Tiles Black List UI"""
        groupbox = QGroupBox("Tiles Black List", self)
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Input fields layout
        input_layout = QHBoxLayout()
        self.blacklist_x_lineEdit.setPlaceholderText("X")
        self.blacklist_x_lineEdit.setFixedWidth(45)
        self.blacklist_y_lineEdit.setPlaceholderText("Y")
        self.blacklist_y_lineEdit.setFixedWidth(45)
        self.blacklist_z_lineEdit.setPlaceholderText("Z")
        self.blacklist_z_lineEdit.setFixedWidth(45)
        
        input_layout.addWidget(self.blacklist_x_lineEdit)
        input_layout.addWidget(self.blacklist_y_lineEdit)
        input_layout.addWidget(self.blacklist_z_lineEdit)

        # Buttons
        addBlacklistTile_button = QPushButton("Add", self)
        clearBlacklist_button = QPushButton("Clear", self)
        
        # Button Functions
        addBlacklistTile_button.clicked.connect(self.add_blacklist_tile)
        clearBlacklist_button.clicked.connect(self.clear_blacklist)
        
        # Double-click to delete
        self.tiles_blacklist_listWidget.itemDoubleClicked.connect(
            lambda item: delete_item(self.tiles_blacklist_listWidget, item)
        )

        # Add to layout
        groupbox_layout.addLayout(input_layout)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(addBlacklistTile_button)
        buttons_layout.addWidget(clearBlacklist_button)
        groupbox_layout.addLayout(buttons_layout)
        groupbox_layout.addWidget(self.tiles_blacklist_listWidget)
        groupbox_layout.addWidget(self.current_pos_label)  # Add current position label
        
        self.layout.addWidget(groupbox, 0, 2, 2, 1)

    def add_blacklist_tile(self) -> None:
        """Add a tile to the blacklist using manual X, Y, Z input"""
        # Clear previous error styling
        self.blacklist_x_lineEdit.setStyleSheet("")
        self.blacklist_y_lineEdit.setStyleSheet("")
        self.blacklist_z_lineEdit.setStyleSheet("")
        
        # Get input values
        x_text = self.blacklist_x_lineEdit.text().strip()
        y_text = self.blacklist_y_lineEdit.text().strip()
        z_text = self.blacklist_z_lineEdit.text().strip()
        
        # Validate inputs
        if not x_text or not y_text or not z_text:
            if not x_text:
                self.blacklist_x_lineEdit.setStyleSheet("border: 2px solid red;")
            if not y_text:
                self.blacklist_y_lineEdit.setStyleSheet("border: 2px solid red;")
            if not z_text:
                self.blacklist_z_lineEdit.setStyleSheet("border: 2px solid red;")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.status_label.setText("Please enter X, Y, Z coordinates.")
            return
        
        try:
            x = int(x_text)
            y = int(y_text)
            z = int(z_text)
        except ValueError:
            self.blacklist_x_lineEdit.setStyleSheet("border: 2px solid red;")
            self.blacklist_y_lineEdit.setStyleSheet("border: 2px solid red;")
            self.blacklist_z_lineEdit.setStyleSheet("border: 2px solid red;")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.status_label.setText("Coordinates must be integers.")
            return
        
        # Check for duplicates
        tile_text = f"{x}, {y}, {z}"
        for index in range(self.tiles_blacklist_listWidget.count()):
            if self.tiles_blacklist_listWidget.item(index).text() == tile_text:
                self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                self.status_label.setText(f"Tile {tile_text} already in blacklist.")
                return
        
        # Create tile data
        tile_data = {"X": x, "Y": y, "Z": z}
        tile_item = QListWidgetItem(tile_text)
        tile_item.setData(Qt.UserRole, tile_data)
        self.tiles_blacklist_listWidget.addItem(tile_item)
        
        # Clear input fields
        self.blacklist_x_lineEdit.clear()
        self.blacklist_y_lineEdit.clear()
        self.blacklist_z_lineEdit.clear()
        
        # Success message
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText(f"Tile {tile_text} added to blacklist!")

    def clear_blacklist(self) -> None:
        """Clear all tiles from the blacklist"""
        self.tiles_blacklist_listWidget.clear()
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText("Blacklist cleared!")

    def get_blacklist(self) -> set:
        """Return blacklist as set of (x, y, z) tuples for use by TargetThread"""
        return {
            (self.tiles_blacklist_listWidget.item(i).data(Qt.UserRole)['X'],
             self.tiles_blacklist_listWidget.item(i).data(Qt.UserRole)['Y'],
             self.tiles_blacklist_listWidget.item(i).data(Qt.UserRole)['Z'])
            for i in range(self.tiles_blacklist_listWidget.count())
        }
    
    def update_current_position(self) -> None:
        """Update the current position label with player's position"""
        try:
            x, y, z = read_my_wpt()
            self.current_pos_label.setText(f"Current Pos: {x}, {y}, {z}")
        except Exception:
            # If we can't read position, keep previous value or show error
            self.current_pos_label.setText("Current Pos: -, -, -")
    
    def update_interval_label(self, value):
        square_text = "square" if value == 1 else "squares"
        self.interval_label.setText(f"Record every: {value} {square_text}")

    def start_record_thread(self, state) -> None:
        if state == Qt.Checked:
            if self.record_thread:
                self.record_thread.stop()
                self.record_thread.wait(2000)
            
            self.record_thread = RecordThread(self.recordInterval_spinBox.value())
            self.record_thread.wpt_recorded_signal.connect(self.on_waypoint_recorded)
            
            # Use a timer to sync UI state to RecordThread
            self.sync_timer = QTimer(self)
            self.sync_timer.timeout.connect(self.sync_record_data)
            self.sync_timer.start(200)

            self.record_thread.start()
        else:
            if self.record_thread:
                self.record_thread.stop()
                self.record_thread.wait(2000)
                self.record_thread = None
            if hasattr(self, 'sync_timer'):
                self.sync_timer.stop()

    def sync_record_data(self):
        if self.record_thread:
            dir_id = self.direction_group.checkedId()
            dir_text = "Center"
            btn = self.direction_group.button(dir_id)
            if btn:
                dir_text = btn.text()
                if dir_text == "C": dir_text = "Center"
            
            act_id = self.action_group.checkedId()
            self.record_thread.update_snapshot(act_id, dir_id, dir_text)

    def on_waypoint_recorded(self, data):
        # Create QListWidgetItem in GUI thread
        display_text = "Unknown"
        act_id = data["Action"]
        dir_text = data["Display"]
        x, y, z = data["X"], data["Y"], data["Z"]

        if act_id == 0: display_text = f'Stand: {x} {y} {z} {dir_text}'
        elif act_id == 4: display_text = f'Lure: {x} {y} {z}'
        elif act_id == 1: display_text = f'Rope: {x} {y} {z}'
        elif act_id == 2: display_text = f'Shovel: {x} {y} {z}'
        elif act_id == 3: display_text = f'Ladder: {x} {y} {z}'

        waypoint = QListWidgetItem(display_text)
        waypoint.setData(Qt.UserRole, data)
        self.waypointList_listWidget.addItem(waypoint)
        self.waypointList_listWidget.scrollToBottom()

    def start_walker_thread(self, state) -> None:
        if state == Qt.Checked:
            if self.walker_thread:
                self.walker_thread.stop()
                self.walker_thread.wait(2000)

            # Extract waypoints
            waypoints = [
                self.waypointList_listWidget.item(i).data(Qt.UserRole)
                for i in range(self.waypointList_listWidget.count())
            ]
            
            if not waypoints:
                return

            self.walker_thread = WalkerThread(waypoints)
            self.walker_thread.index_update.connect(self.update_waypointList)
            self.walker_thread.start()
        else:
            if self.walker_thread:
                self.walker_thread.stop()
                self.walker_thread.wait(2000)
                self.walker_thread = None


    def update_waypointList(self, option, waypoint):
        if option == 0:
            self.waypointList_listWidget.setCurrentRow(int(waypoint))
        elif option == 1:
            self.waypointList_listWidget.addItem(waypoint)
