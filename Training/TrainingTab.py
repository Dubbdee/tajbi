from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QComboBox, QLineEdit, QListWidget, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox, QListWidgetItem, QLabel
)
from PyQt5.QtGui import QIcon
import json
from Functions.GeneralFunctions import manage_profile
from Training.TrainingThread import TrainingThread, ClickThread, SetThread, FishingThread, AddWaterSpotThread, RuneMakerThread, RuneSetThread, SetFoodThread, FoodEaterThread, BatchAddWaterThread


class TrainingTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.click_thread = None
        self.training_thread = None
        self.set_thread = None
        self.fishing_thread = None
        self.rune_maker_thread = None
        self.food_eater_thread = None

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))

        # Set Title and Size
        self.setWindowTitle("Training")
        self.setFixedSize(320, 650)

        # --- Status label at the bottom (for messages, instructions, and showing coordinates)
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        # Check Boxes
        self.burn_mana_checkbox = QCheckBox("Burn Mana", self)
        self.start_click_checkbox = QCheckBox("Start", self)
        self.start_fishing_checkbox = QCheckBox("Start", self)
        self.start_rune_maker_checkbox = QCheckBox("Start", self)
        self.start_food_eater_checkbox = QCheckBox("Start", self)
        self.rune_timer_checkbox = QCheckBox("Timer Mode", self)

        # Combo Boxes
        self.hotkey_list_combobox = QComboBox(self)
        self.key_list_combobox = QComboBox(self)
        self.rune_hotkey_combobox = QComboBox(self)
        for i in range(1, 11):
            self.rune_hotkey_combobox.addItem(f"F{i}")

        # Line Edits
        self.mp_line_edit = QLineEdit(self)
        self.timer_line_edit = QLineEdit(self)
        self.rune_mana_line_edit = QLineEdit(self)
        self.rune_mana_line_edit.setPlaceholderText("Mana")
        self.rune_timer_line_edit = QLineEdit(self)
        self.rune_timer_line_edit.setPlaceholderText("Sec")
        self.rune_timer_line_edit.setMaximumWidth(40)
        self.fishing_tries_line_edit = QLineEdit(self)
        self.fishing_tries_line_edit.setPlaceholderText("5")
        self.fishing_tries_line_edit.setMaximumWidth(40)
        self.food_interval_line_edit = QLineEdit(self)
        self.food_interval_line_edit.setPlaceholderText("60")
        self.food_interval_line_edit.setMaximumWidth(40)
        self.batch_distance_line_edit = QLineEdit(self)
        self.batch_distance_line_edit.setPlaceholderText("30")
        self.batch_distance_line_edit.setMaximumWidth(40)
        self.batch_distance_line_edit.setToolTip("Pixel distance to consider clicks as 'same square' (default 30)")

        # List Widgets
        self.burn_mana_list_widget = QListWidget(self)

        # Layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Finally, add the status label at the bottom
        self.layout.addWidget(self.status_label, 5, 0, 1, 2)

        # Initialize
        self.burn_mana_list()
        self.add_hotkeys()
        self.click_key()
        self.fishing()
        self.food_eater()
        self.rune_maker()


    def fishing(self) -> None:
        groupbox = QGroupBox("Fishing")
        groupbox_layout = QVBoxLayout(self)
        groupbox.setLayout(groupbox_layout)

        fishing_button = QPushButton("Fishing Rod", self)
        add_water_button = QPushButton("Add Water", self)
        batch_add_button = QPushButton("Batch Add", self)
        clear_water_button = QPushButton("Clear Water", self)
        bait_button = QPushButton("Bait", self)
        food_button = QPushButton("Food", self)

        self.start_fishing_checkbox.stateChanged.connect(self.start_fishing_thread)

        fishing_button.clicked.connect(lambda: self.startSet_thread(0))
        add_water_button.clicked.connect(self.add_water_spot)
        batch_add_button.clicked.connect(self.batch_add_water_spots)
        clear_water_button.clicked.connect(self.clear_water_spots)
        bait_button.clicked.connect(lambda: self.startSet_thread(2))
        food_button.clicked.connect(lambda: self.startSet_thread(3))

        # Water spots list
        self.water_spots_list = QListWidget(self)
        self.water_spots_list.setMaximumHeight(60)

        # Layouts
        layout1 = QHBoxLayout(self)
        layout1.addWidget(fishing_button)
        layout1.addWidget(add_water_button)
        layout1.addWidget(batch_add_button)
        layout1.addWidget(clear_water_button)
        layout1.addWidget(bait_button)
        layout1.addWidget(food_button)
        layout1.addWidget(self.start_fishing_checkbox)
        groupbox_layout.addLayout(layout1)

        layout_tries = QHBoxLayout(self)
        layout_tries.addWidget(QLabel("Tries per spot:"))
        layout_tries.addWidget(self.fishing_tries_line_edit)
        layout_tries.addWidget(QLabel("Batch dist (px):"))
        layout_tries.addWidget(self.batch_distance_line_edit)
        layout_tries.addStretch()
        groupbox_layout.addLayout(layout_tries)

        groupbox_layout.addWidget(QLabel("Water Spots (bot cycles through them):"))
        groupbox_layout.addWidget(self.water_spots_list)
        self.layout.addWidget(groupbox, 2, 0, 1, 2)

    def add_water_spot(self) -> None:
        if self.set_thread and self.set_thread.isRunning():
            self.set_thread.stop()
            self.set_thread.wait()
        if self.set_thread:
            try:
                self.set_thread.finished.disconnect(self.refresh_water_spots_list)
            except TypeError:
                pass  # Was not connected
        self.set_thread = AddWaterSpotThread(self.status_label)
        self.set_thread.finished.connect(self.refresh_water_spots_list)
        self.set_thread.status_signal.connect(self.update_status_label)
        self.set_thread.start()

    def batch_add_water_spots(self) -> None:
        import Addresses
        # Toggle batch mode on/off
        if self.set_thread and isinstance(self.set_thread, BatchAddWaterThread) and self.set_thread.isRunning():
            self.set_thread.stop()
            self.set_thread.wait()
            self.refresh_water_spots_list()
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Batch Add finished! {len(Addresses.fishing_water_spots)} spots total.")
            return
        
        # Stop any other active set thread first
        if self.set_thread and self.set_thread.isRunning():
            self.set_thread.stop()
            self.set_thread.wait()
        if self.set_thread:
            try:
                self.set_thread.finished.disconnect(self.refresh_water_spots_list)
            except TypeError:
                pass
        
        # Read batch distance threshold
        dist_text = self.batch_distance_line_edit.text().strip()
        min_distance = 30
        if dist_text:
            try:
                min_distance = int(dist_text)
                if min_distance < 1:
                    min_distance = 1
            except ValueError:
                min_distance = 30
        
        self.set_thread = BatchAddWaterThread(self.status_label, min_distance=min_distance)
        self.set_thread.finished.connect(self.refresh_water_spots_list)
        self.set_thread.status_signal.connect(self.update_status_label)
        self.set_thread.start()

    def clear_water_spots(self) -> None:
        import Addresses
        Addresses.fishing_water_spots.clear()
        self.refresh_water_spots_list()
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText("Water spots cleared!")

    def refresh_water_spots_list(self) -> None:
        self.water_spots_list.clear()
        import Addresses
        for i, (x, y) in enumerate(Addresses.fishing_water_spots):
            self.water_spots_list.addItem(f"Spot {i+1}: X={x}, Y={y}")

    def rune_maker(self) -> None:
        groupbox = QGroupBox("Rune Maker")
        groupbox_layout = QVBoxLayout(self)
        groupbox.setLayout(groupbox_layout)

        hand_button = QPushButton("Set Hand", self)
        charged_button = QPushButton("Set Charged", self)
        blank_button = QPushButton("Set Blank", self)

        self.start_rune_maker_checkbox.stateChanged.connect(self.start_rune_maker_thread)

        hand_button.clicked.connect(lambda: self.set_rune_coord("Hand"))
        charged_button.clicked.connect(lambda: self.set_rune_coord("Charged Dest"))
        blank_button.clicked.connect(lambda: self.set_rune_coord("Blank Rune"))

        layout1 = QHBoxLayout(self)
        layout1.addWidget(hand_button)
        layout1.addWidget(charged_button)
        layout1.addWidget(blank_button)
        layout1.addWidget(self.start_rune_maker_checkbox)
        groupbox_layout.addLayout(layout1)

        layout2 = QHBoxLayout(self)
        layout2.addWidget(QLabel("Mana Cost:"))
        layout2.addWidget(self.rune_mana_line_edit)
        layout2.addWidget(QLabel("Hotkey:"))
        layout2.addWidget(self.rune_hotkey_combobox)
        groupbox_layout.addLayout(layout2)

        layout3 = QHBoxLayout(self)
        layout3.addWidget(self.rune_timer_checkbox)
        layout3.addWidget(QLabel("Timer (sec):"))
        layout3.addWidget(self.rune_timer_line_edit)
        layout3.addStretch()
        groupbox_layout.addLayout(layout3)

        self.layout.addWidget(groupbox, 4, 0, 1, 2)

    def food_eater(self) -> None:
        groupbox = QGroupBox("Food Eater")
        groupbox_layout = QVBoxLayout(self)
        groupbox.setLayout(groupbox_layout)

        food_button = QPushButton("Set Food", self)
        self.start_food_eater_checkbox.stateChanged.connect(self.start_food_eater_thread)

        food_button.clicked.connect(self.set_food_coord)

        layout1 = QHBoxLayout(self)
        layout1.addWidget(food_button)
        layout1.addWidget(QLabel("Interval (sec):"))
        layout1.addWidget(self.food_interval_line_edit)
        layout1.addWidget(self.start_food_eater_checkbox)
        groupbox_layout.addLayout(layout1)

        self.layout.addWidget(groupbox, 3, 0, 1, 2)

    def set_food_coord(self) -> None:
        if self.set_thread and self.set_thread.isRunning():
            self.set_thread.stop()
            self.set_thread.wait()
        self.set_thread = SetFoodThread(self.status_label)
        self.set_thread.status_signal.connect(self.update_status_label)
        self.set_thread.start()

    def start_food_eater_thread(self, state) -> None:
        if state == Qt.Checked:
            interval_text = self.food_interval_line_edit.text().strip()
            interval = 60
            if interval_text:
                try:
                    interval = int(interval_text)
                    if interval < 1:
                        interval = 1
                except ValueError:
                    interval = 60
            if not self.food_eater_thread:
                self.food_eater_thread = FoodEaterThread(interval)
                self.food_eater_thread.status_signal.connect(self.update_status_label)
                self.food_eater_thread.start()
        else:
            if self.food_eater_thread:
                self.food_eater_thread.stop()
                self.food_eater_thread = None

    def set_rune_coord(self, coord_name) -> None:
        if self.set_thread and self.set_thread.isRunning():
            self.set_thread.stop()
            self.set_thread.wait()
        if self.set_thread:
            try:
                self.set_thread.finished.disconnect(self.refresh_water_spots_list)
            except TypeError:
                pass
        self.set_thread = RuneSetThread(coord_name, self.status_label)
        self.set_thread.status_signal.connect(self.update_status_label)
        self.set_thread.start()

    def start_rune_maker_thread(self, state) -> None:
        if state == Qt.Checked:
            mana_text = self.rune_mana_line_edit.text().strip()
            if not mana_text and not self.rune_timer_checkbox.isChecked():
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                self.status_label.setText("Enter Mana Cost for rune!")
                self.start_rune_maker_checkbox.setChecked(False)
                return
            try:
                mana_cost = int(mana_text) if mana_text else 0
            except ValueError:
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                self.status_label.setText("Mana Cost must be a number!")
                self.start_rune_maker_checkbox.setChecked(False)
                return
            timer_text = self.rune_timer_line_edit.text().strip()
            timer_interval = 10
            if timer_text:
                try:
                    timer_interval = int(timer_text)
                    if timer_interval < 1:
                        timer_interval = 1
                except ValueError:
                    timer_interval = 10
            if not self.rune_maker_thread:
                hotkey = self.rune_hotkey_combobox.currentText()
                timer_mode = self.rune_timer_checkbox.isChecked()
                self.rune_maker_thread = RuneMakerThread(mana_cost, hotkey, timer_mode, timer_interval)
                self.rune_maker_thread.status_signal.connect(self.update_status_label)
                self.rune_maker_thread.start()
        else:
            if self.rune_maker_thread:
                self.rune_maker_thread.stop()
                self.rune_maker_thread = None


    def click_key(self) -> None:
        groupbox = QGroupBox("Click Key")
        groupbox_layout = QVBoxLayout(self)
        groupbox.setLayout(groupbox_layout)

        # Combo Box
        for i in range(1, 11):
            self.key_list_combobox.addItem(f"F{i}")

        # Checkbox
        self.start_click_checkbox.stateChanged.connect(self.start_click_thread)

        # Layouts
        layout1 = QHBoxLayout(self)

        layout1.addWidget(QLabel("Time: "))
        layout1.addWidget(self.timer_line_edit)
        layout1.addWidget(QLabel("Key: "))
        layout1.addWidget(self.key_list_combobox)
        layout1.addWidget(self.start_click_checkbox)

        # Add Layouts
        groupbox_layout.addLayout(layout1)
        self.layout.addWidget(groupbox, 1, 0, 1, 2)

    def burn_mana_list(self) -> None:
        groupbox = QGroupBox("Burn Mana")
        groupbox_layout = QVBoxLayout(self)
        groupbox.setLayout(groupbox_layout)

        # Add Layouts
        groupbox_layout.addWidget(self.burn_mana_list_widget)
        self.layout.addWidget(groupbox, 0, 0, 1, 1)

    def add_hotkeys(self) -> None:
        groupbox = QGroupBox("Hotkeys")
        groupbox_layout = QVBoxLayout(self)
        groupbox.setLayout(groupbox_layout)

        # Buttons
        add_hotkey_button = QPushButton("Add", self)

        # Button functions
        add_hotkey_button.clicked.connect(self.add_hotkey)

        # Check Boxes
        self.burn_mana_checkbox.stateChanged.connect(self.start_training_thread)

        # Combo Boxes
        for i in range(1, 11):
            self.hotkey_list_combobox.addItem(f"F{i}")

        # Layouts
        layout1 = QHBoxLayout(self)
        layout2 = QHBoxLayout(self)

        # Add Widgets
        layout1.addWidget(self.mp_line_edit)
        layout1.addWidget(self.hotkey_list_combobox)
        layout1.addWidget(add_hotkey_button)
        layout2.addWidget(self.burn_mana_checkbox)

        # Add Layouts
        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        self.layout.addWidget(groupbox, 0, 1)

    def add_hotkey(self) -> None:
        hotkey_name = self.hotkey_list_combobox.currentText()
        hotkey_data = {"Mana": int(self.mp_line_edit.text())}
        hotkey = QListWidgetItem(hotkey_name)
        hotkey.setData(Qt.UserRole, hotkey_data)
        self.burn_mana_list_widget.addItem(hotkey)
        self.mp_line_edit.clear()


    def start_click_thread(self, state) -> None:
        if state == Qt.Checked:
            if not self.click_thread:
                self.click_thread = ClickThread(int(self.timer_line_edit.text()), self.key_list_combobox.currentText())
                self.click_thread.start()
        else:
            if self.click_thread:
                self.click_thread.stop()
                self.click_thread = None

    def start_training_thread(self, state) -> None:
        if state == Qt.Checked:
            self.timer_line_edit.setDisabled(True)
            if not self.training_thread:
                self.training_thread = TrainingThread(self.burn_mana_list_widget)
                self.training_thread.start()
        else:
            self.timer_line_edit.setEnabled(True)
            if self.training_thread:
                self.training_thread.stop()
                self.training_thread = None

    def start_fishing_thread(self, state) -> None:
        if state == Qt.Checked:
            if not self.fishing_thread:
                tries_text = self.fishing_tries_line_edit.text().strip()
                tries = 5
                if tries_text:
                    try:
                        tries = int(tries_text)
                        if tries < 1:
                            tries = 1
                    except ValueError:
                        tries = 5
                self.fishing_thread = FishingThread(self.status_label, tries)
                self.fishing_thread.status_signal.connect(self.update_status_label)
                self.fishing_thread.start()
        else:
            if self.fishing_thread:
                self.fishing_thread.stop()
                self.fishing_thread = None


    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        
        burn_mana_list = []
        for i in range(self.burn_mana_list_widget.count()):
            item = self.burn_mana_list_widget.item(i)
            burn_mana_list.append({
                "Name": item.text(),
                "Data": item.data(Qt.UserRole)
            })
            
        click_key_settings = {
            "Timer": self.timer_line_edit.text(),
            "Key": self.key_list_combobox.currentText()
        }

        # Save rune maker settings
        import Addresses
        rune_settings = {
            "mana_cost": self.rune_mana_line_edit.text(),
            "hotkey": self.rune_hotkey_combobox.currentText(),
            "timer_mode": self.rune_timer_checkbox.isChecked(),
            "timer_interval": self.rune_timer_line_edit.text(),
            "hand_x": Addresses.hand_x,
            "hand_y": Addresses.hand_y,
            "charged_dest_x": Addresses.charged_dest_x,
            "charged_dest_y": Addresses.charged_dest_y,
            "blank_rune_x": Addresses.blank_rune_x,
            "blank_rune_y": Addresses.blank_rune_y
        }

        food_settings = {
            "food_x": Addresses.food_x,
            "food_y": Addresses.food_y,
            "interval": self.food_interval_line_edit.text()
        }

        data_to_save = {
            "burn_mana": burn_mana_list,
            "click_key": click_key_settings,
            "water_spots": water_spots,
            "fishing_tries": self.fishing_tries_line_edit.text(),
            "batch_distance": self.batch_distance_line_edit.text(),
            "rune_maker": rune_settings,
            "food_eater": food_settings
        }

        if manage_profile("save", "Save/Training", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")

    def load_settings(self, profile_name) -> None:
        filename = f"Save/Training/{profile_name}.json"
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)

            # Load Burn Mana List
            self.burn_mana_list_widget.clear()
            for burn_data in loaded_data.get("burn_mana", []):
                item = QListWidgetItem(burn_data["Name"])
                item.setData(Qt.UserRole, burn_data["Data"])
                self.burn_mana_list_widget.addItem(item)

            # Load Click Key Settings
            click_settings = loaded_data.get("click_key", {})
            self.timer_line_edit.setText(click_settings.get("Timer", ""))
            key = click_settings.get("Key", "")
            index = self.key_list_combobox.findText(key)
            if index != -1:
                self.key_list_combobox.setCurrentIndex(index)

            # Load Water Spots
            import Addresses
            Addresses.fishing_water_spots.clear()
            for spot in loaded_data.get("water_spots", []):
                Addresses.fishing_water_spots.append((spot["x"], spot["y"]))
            self.refresh_water_spots_list()

            # Load Fishing Tries
            self.fishing_tries_line_edit.setText(loaded_data.get("fishing_tries", ""))

            # Load Batch Distance
            self.batch_distance_line_edit.setText(loaded_data.get("batch_distance", ""))

            # Load Rune Maker Settings
            rune_settings = loaded_data.get("rune_maker", {})
            self.rune_mana_line_edit.setText(rune_settings.get("mana_cost", ""))
            self.rune_timer_checkbox.setChecked(rune_settings.get("timer_mode", False))
            self.rune_timer_line_edit.setText(rune_settings.get("timer_interval", ""))
            hotkey = rune_settings.get("hotkey", "")
            if hotkey:
                index = self.rune_hotkey_combobox.findText(hotkey)
                if index != -1:
                    self.rune_hotkey_combobox.setCurrentIndex(index)
            Addresses.hand_x = rune_settings.get("hand_x", 0)
            Addresses.hand_y = rune_settings.get("hand_y", 0)
            Addresses.charged_dest_x = rune_settings.get("charged_dest_x", 0)
            Addresses.charged_dest_y = rune_settings.get("charged_dest_y", 0)
            Addresses.blank_rune_x = rune_settings.get("blank_rune_x", 0)
            Addresses.blank_rune_y = rune_settings.get("blank_rune_y", 0)

            # Load Food Eater Settings
            food_settings = loaded_data.get("food_eater", {})
            Addresses.food_x = food_settings.get("food_x", 0)
            Addresses.food_y = food_settings.get("food_y", 0)
            self.food_interval_line_edit.setText(food_settings.get("interval", ""))

            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")

    def startSet_thread(self, index) -> None:
        self.set_thread = SetThread(index, self.status_label)
        self.set_thread.status_signal.connect(self.update_status_label)
        self.set_thread.start()

    def update_status_label(self, text, style):
        self.status_label.setText(text)
        if style:
            self.status_label.setStyleSheet(style)
