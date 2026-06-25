from Addresses import screen_x, screen_y, screen_width, screen_height, coordinates_x, coordinates_y, battle_x, battle_y
import json
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QGroupBox,
    QGridLayout, QPushButton, QListWidget, QComboBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os

from Functions.GeneralFunctions import manage_profile
from Settings.SettingsThread import SettingsThread


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.settings_thread = None

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))

        # Set Title and Size
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 900)

        # --- Status label at the bottom (for messages, instructions, and showing coordinates)
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")


        # Main layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Initialize sections
        self.set_environment()
        self.set_tools()
        self.set_addresses_ui()

        # Finally, add the status label in row=2 (bottom)
        self.layout.addWidget(self.status_label, 2, 0, 1, 2)


    def set_environment(self) -> None:
        """
        Unified GroupBox for all coordinate settings (environment, tools, areas).
        """
        groupbox = QGroupBox("Coordinate Settings", self)
        main_layout = QVBoxLayout()
        groupbox.setLayout(main_layout)

        # --- Environment Section ---
        env_label = QLabel("Environment & Areas:")
        env_label.setStyleSheet("font-weight: bold; text-decoration: underline;")
        main_layout.addWidget(env_label)
        
        env_layout = QHBoxLayout()
        set_character_pos_button = QPushButton("Set Character", self)
        set_loot_screen_button = QPushButton("Set Loot Area", self)
        set_battle_list_button = QPushButton("Set Battle List", self)
        
        set_character_pos_button.clicked.connect(lambda: self.startSet_thread(0))
        set_loot_screen_button.clicked.connect(lambda: self.startSet_thread(-1))
        set_battle_list_button.clicked.connect(lambda: self.startSet_thread(-2))
        
        env_layout.addWidget(set_character_pos_button)
        env_layout.addWidget(set_loot_screen_button)
        env_layout.addWidget(set_battle_list_button)
        main_layout.addLayout(env_layout)

        # --- Tools & Backpacks Section ---
        tools_label = QLabel("Tools & Backpacks:")
        tools_label.setStyleSheet("font-weight: bold; text-decoration: underline; margin-top: 10px;")
        main_layout.addWidget(tools_label)
        
        # Buttons
        item_bp_button = QPushButton("1 Backpack", self)
        item_bp1_button = QPushButton("2 Backpack", self)
        item_bp2_button = QPushButton("3 Backpack", self)
        item_bp3_button = QPushButton("4 Backpack", self)
        health_button = QPushButton("Health", self)
        mana_button = QPushButton("Mana", self)
        rune1_button = QPushButton("First Rune", self)
        rune2_button = QPushButton("Second Rune", self)
        rope_button = QPushButton("Rope", self)
        shovel_button = QPushButton("Shovel", self)

        # Button connections
        item_bp_button.clicked.connect(lambda: self.startSet_thread(1))
        item_bp1_button.clicked.connect(lambda: self.startSet_thread(2))
        item_bp2_button.clicked.connect(lambda: self.startSet_thread(3))
        item_bp3_button.clicked.connect(lambda: self.startSet_thread(4))
        health_button.clicked.connect(lambda: self.startSet_thread(5))
        mana_button.clicked.connect(lambda: self.startSet_thread(11))
        rune1_button.clicked.connect(lambda: self.startSet_thread(6))
        rune2_button.clicked.connect(lambda: self.startSet_thread(8))
        shovel_button.clicked.connect(lambda: self.startSet_thread(9))
        rope_button.clicked.connect(lambda: self.startSet_thread(10))

        # Layout arrangement
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()
        layout5 = QHBoxLayout()

        layout1.addWidget(item_bp_button)
        layout1.addWidget(item_bp1_button)

        layout2.addWidget(item_bp2_button)
        layout2.addWidget(item_bp3_button)

        layout3.addWidget(health_button)
        layout3.addWidget(mana_button)

        layout4.addWidget(rune1_button)
        layout4.addWidget(rune2_button)

        layout5.addWidget(rope_button)
        layout5.addWidget(shovel_button)

        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)
        main_layout.addLayout(layout4)
        main_layout.addLayout(layout5)

        self.layout.addWidget(groupbox, 0, 0)

    def set_tools(self) -> None:
        """
        Deprecated - merged into set_environment()
        """
        pass

    def set_addresses_ui(self):
        """
        GroupBox for configuring memory addresses and game settings.
        """
        # --- Game Configuration ---
        game_group = QGroupBox("Game Configuration", self)
        game_layout = QGridLayout()
        game_group.setLayout(game_layout)
        
        # Architecture
        game_layout.addWidget(QLabel("Architecture:"), 0, 0)
        self.arch_combo = QComboBox()
        self.arch_combo.addItems(["32 Bit", "64 Bit"])
        game_layout.addWidget(self.arch_combo, 0, 1)
        
        # Square Size
        game_layout.addWidget(QLabel("Square Size:"), 1, 0)
        self.square_size_edit = QLineEdit()
        self.square_size_edit.setPlaceholderText("75")
        game_layout.addWidget(self.square_size_edit, 1, 1)
        
        # Collect Threshold
        game_layout.addWidget(QLabel("Collect Threshold:"), 2, 0)
        self.threshold_edit = QLineEdit()
        self.threshold_edit.setPlaceholderText("0.95")
        game_layout.addWidget(self.threshold_edit, 2, 1)
        
        self.layout.addWidget(game_group, 0, 1) # Place it in top right

        # --- Memory Addresses ---
        groupbox = QGroupBox("Memory Addresses (Hex)", self)
        layout = QGridLayout()
        groupbox.setLayout(layout)
        layout.setSpacing(10)

        # Headers
        headers = ["Name", "Type", "Address", "Offset"]
        for col, text in enumerate(headers):
            label = QLabel(text)
            label.setStyleSheet("font-weight: bold; font-size: 14px; text-decoration: underline;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, 0, col)

        self.address_widgets = {}

        # Define addresses to configure
        addresses = [
            ("Player X", "my_x", "Int"),
            ("Player Y", "my_y", "Int"),
            ("Player Z", "my_z", "Short"),
            ("HP", "my_hp", "Short"),
            ("HP Max", "my_hp_max", "Short"),
            ("MP", "my_mp", "Short"),
            ("MP Max", "my_mp_max", "Short"),
            ("Attack", "attack", "Int"),
            ("Target X Offset", "target_x", "Int"),
            ("Target Y Offset", "target_y", "Int"),
            ("Target Z Offset", "target_z", "Int"),
            ("Target HP Offset", "target_hp", "Int"),
            ("Target Name Offset", "target_name", "String")
        ]

        for i, (label, key, default_type) in enumerate(addresses, start=1):
            self.add_address_row(layout, i, label, key, default_type)

        # Save Button for Addresses
        save_addr_btn = QPushButton("Save && Reload Addresses", self)
        save_addr_btn.clicked.connect(self.save_addresses)
        save_addr_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        layout.addWidget(save_addr_btn, len(addresses) + 1, 0, 1, 4)

        self.layout.addWidget(groupbox, 1, 0, 1, 2) # Place below
        
        # Load addresses on init
        self.load_addresses()

    def add_address_row(self, layout, row, label, key, default_type):
        # Label
        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lbl, row, 0)

        # Type ComboBox
        type_combo = QComboBox()
        type_combo.addItems(["Byte", "Short", "Int", "Long", "Double", "String", "Unicode String"])
        type_combo.setCurrentText(default_type)
        layout.addWidget(type_combo, row, 1)

        # Address LineEdit
        addr_edit = QLineEdit()
        addr_edit.setPlaceholderText("0x0")
        layout.addWidget(addr_edit, row, 2)

        # Offset LineEdit
        offset_edit = QLineEdit()
        offset_edit.setPlaceholderText("0x0, 0x4")
        layout.addWidget(offset_edit, row, 3)

        self.address_widgets[key] = {
            "type": type_combo,
            "address": addr_edit,
            "offset": offset_edit
        }

    def save_addresses(self):
        try:
            data = {}
            # Save Game Config
            data["game_config"] = {
                "architecture": self.arch_combo.currentText(),
                "square_size": self.square_size_edit.text().strip(),
                "collect_threshold": self.threshold_edit.text().strip()
            }

            # Save Addresses
            for key, widgets in self.address_widgets.items():
                data[key] = {
                    "type": widgets["type"].currentText(),
                    "address": widgets["address"].text().strip(),
                    "offset": widgets["offset"].text().strip()
                }
            
            # Save Coordinates
            data["coordinates"] = {
                "X": coordinates_x,
                "Y": coordinates_y,
                "screen_x": screen_x,
                "screen_y": screen_y,
                "screen_width": screen_width,
                "screen_height": screen_height,
                "battle_x": battle_x,
                "battle_y": battle_y
            }
            
            if manage_profile("save", "Save/Settings", "addresses", data):
                import Addresses
                Addresses.load_custom_addresses()
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.status_label.setText("Addresses saved and reloaded!")
        except Exception as e:
            self.status_label.setText(f"Error saving: {e}")

    def load_addresses(self):
        filename = "Save/Settings/addresses.json"
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
                
                # Load Game Config
                config = data.get("game_config", {})
                self.arch_combo.setCurrentText(config.get("architecture", "32 Bit"))
                self.square_size_edit.setText(config.get("square_size", "75"))
                self.threshold_edit.setText(config.get("collect_threshold", "0.95"))

                # Load Addresses
                for key, widgets in self.address_widgets.items():
                    if key in data:
                        entry = data[key]
                        widgets["type"].setCurrentText(entry.get("type", "Int"))
                        widgets["address"].setText(entry.get("address", ""))
                        widgets["offset"].setText(entry.get("offset", ""))
                
                # Load Coordinates
                coords_data = data.get("coordinates", {})
                loaded_x = coords_data.get("X", [])
                loaded_y = coords_data.get("Y", [])
                loaded_screen_x = coords_data.get("screen_x", [])
                loaded_screen_y = coords_data.get("screen_y", [])
                loaded_screen_w = coords_data.get("screen_width", [])
                loaded_screen_h = coords_data.get("screen_height", [])
                loaded_battle_x = coords_data.get("battle_x", [])
                loaded_battle_y = coords_data.get("battle_y", [])
                
                # Update global lists in-place if data exists
                if loaded_x and len(loaded_x) == len(coordinates_x):
                    for i in range(len(coordinates_x)): coordinates_x[i] = loaded_x[i]
                        
                if loaded_y and len(loaded_y) == len(coordinates_y):
                    for i in range(len(coordinates_y)): coordinates_y[i] = loaded_y[i]

                if loaded_screen_x and len(loaded_screen_x) == len(screen_x):
                    for i in range(len(screen_x)): screen_x[i] = loaded_screen_x[i]

                if loaded_screen_y and len(loaded_screen_y) == len(screen_y):
                    for i in range(len(screen_y)): screen_y[i] = loaded_screen_y[i]

                if loaded_screen_w and len(loaded_screen_w) == len(screen_width):
                    for i in range(len(screen_width)): screen_width[i] = loaded_screen_w[i]

                if loaded_screen_h and len(loaded_screen_h) == len(screen_height):
                    for i in range(len(screen_height)): screen_height[i] = loaded_screen_h[i]

                if loaded_battle_x and len(loaded_battle_x) == len(battle_x):
                    for i in range(len(battle_x)): battle_x[i] = loaded_battle_x[i]

                if loaded_battle_y and len(loaded_battle_y) == len(battle_y):
                    for i in range(len(battle_y)): battle_y[i] = loaded_battle_y[i]
                        
            except Exception:
                pass

    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        screen_data = {
            "screenX": screen_x[0],
            "screenY": screen_y[0],
            "screenWidth": screen_width[0],
            "screenHeight": screen_height[0],
            "X": coordinates_x,
            "Y": coordinates_y
        }
        data_to_save = {"screen_data": screen_data}

        if manage_profile("save", "Save/Settings", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")

    def load_settings(self, profile_name) -> None:
        filename = f"Save/Settings/{profile_name}.json"
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)

            settings_data = loaded_data.get("screen_data", {})
            screen_x[0] = settings_data.get("screenX", 0)
            screen_y[0] = settings_data.get("screenY", 0)
            screen_width[0] = settings_data.get("screenWidth", 0)
            screen_height[0] = settings_data.get("screenHeight", 0)

            bp_data_x = settings_data.get("X", [0] * len(coordinates_x))
            bp_data_y = settings_data.get("Y", [0] * len(coordinates_y))

            for i in range(len(coordinates_x)):
                coordinates_x[i] = bp_data_x[i]
                coordinates_y[i] = bp_data_y[i]

            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")

    def startSet_thread(self, index) -> None:
        self.settings_thread = SettingsThread(index, self.status_label)
        
        # For drag selection (Loot Area and Battle List), create overlay in main thread
        if index < 0:
            from Settings.SelectionOverlay import SelectionOverlay
            import Addresses
            
            # Pass game window handle for multi-monitor support
            self.selection_overlay = SelectionOverlay(game_hwnd=Addresses.game)
            
            # Connect signals for thread-safe overlay control
            self.settings_thread.show_overlay.connect(self.selection_overlay.show_selection)
            self.settings_thread.update_overlay.connect(self.selection_overlay.set_selection)
            self.settings_thread.hide_overlay.connect(self.selection_overlay.hide_selection)
            
            # Cleanup overlay when thread finishes
            def cleanup_overlay():
                if hasattr(self, 'selection_overlay'):
                    self.selection_overlay.deleteLater()
                    delattr(self, 'selection_overlay')
            
            self.settings_thread.finished.connect(cleanup_overlay)
        
        self.settings_thread.start()
