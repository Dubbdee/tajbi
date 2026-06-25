import json, os
from PyQt5.QtWidgets import (QWidget, QCheckBox, QComboBox, QLineEdit, QListWidget, QGridLayout, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QListWidgetItem)
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtCore import Qt
from HealAttack.HealingAttackThread import HealThread
from Functions.GeneralFunctions import delete_item, manage_profile


class HealingTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.heal_thread = None

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))
        # Set Title and Size
        self.setWindowTitle("Healing")
        self.setFixedSize(450, 300)

        # Main layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Status label
        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: Red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Initialize all widgets first
        self.init_widgets()
        
        # Create UI
        self.create_heal_ui()

        # Add status label at the bottom
        self.layout.addWidget(self.status_label, 1, 0, 1, 2)

    def init_widgets(self):
        """Initialize all widgets used in the UI"""
        # Validators
        int_validator = QIntValidator(0, 100, self)
        
        # Heal widgets
        self.healType_comboBox = QComboBox(self)
        self.healKey_comboBox = QComboBox(self)
        self.hpBelow_lineEdit = QLineEdit(self)
        self.hpAbove_lineEdit = QLineEdit(self)
        self.minMPHeal_lineEdit = QLineEdit(self)
        self.minLabel = QLabel("Min MP:", self)
        self.healList_listWidget = QListWidget(self)
        
        # Set validators
        self.hpBelow_lineEdit.setValidator(int_validator)
        self.hpAbove_lineEdit.setValidator(int_validator)
        
        # Set fixed widths
        self.hpBelow_lineEdit.setFixedWidth(40)
        self.hpAbove_lineEdit.setFixedWidth(40)
        self.minMPHeal_lineEdit.setFixedWidth(40)
        
        # Populate combo boxes
        self.healType_comboBox.addItems(["HP%", "MP%"])
        self.healKey_comboBox.addItems([f"F{i}" for i in range(1, 10)] + ["Health", "Mana"])
        
        # Connect signals
        self.healType_comboBox.currentTextChanged.connect(self.update_min_label)
        self.healList_listWidget.itemDoubleClicked.connect(
            lambda item: delete_item(self.healList_listWidget, item)
        )

    def create_heal_ui(self):
        """Create the healing UI section"""
        groupbox = QGroupBox("Heal")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # List widget
        groupbox_layout.addWidget(self.healList_listWidget)

        # Input section
        input_layout = QVBoxLayout()

        # Row 1: Type and Key
        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel("Type:", self))
        layout1.addWidget(self.healType_comboBox)
        layout1.addWidget(QLabel("Key:", self))
        layout1.addWidget(self.healKey_comboBox)
        input_layout.addLayout(layout1)

        # Row 2: Below and Above
        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel("Below:", self))
        layout2.addWidget(self.hpBelow_lineEdit)
        layout2.addWidget(QLabel("Above:", self))
        layout2.addWidget(self.hpAbove_lineEdit)
        layout2.addWidget(self.minLabel)
        layout2.addWidget(self.minMPHeal_lineEdit)
        input_layout.addLayout(layout2)

        # Set placeholders
        self.hpBelow_lineEdit.setPlaceholderText("100")
        self.hpAbove_lineEdit.setPlaceholderText("90")
        self.minMPHeal_lineEdit.setPlaceholderText("100")

        # Row 3: Add button
        layout3 = QHBoxLayout()
        add_heal_button = QPushButton("Add", self)
        add_heal_button.clicked.connect(self.add_heal)
        layout3.addWidget(add_heal_button)
        input_layout.addLayout(layout3)

        groupbox_layout.addLayout(input_layout)
        self.layout.addWidget(groupbox, 0, 0, 1, 2)

    def update_min_label(self, text):
        """Update the min label based on heal type selection"""
        if text.startswith("MP"):
            self.minLabel.setText("Min HP%:")
        else:
            self.minLabel.setText("Min MP:")

    def add_heal(self) -> None:
        """Add a heal action to the list"""
        self.status_label.setText("")
        self.hpBelow_lineEdit.setStyleSheet("")
        self.hpAbove_lineEdit.setStyleSheet("")
        self.status_label.setStyleSheet("color: Red; font-weight: bold;")

        has_error = False

        if not self.hpBelow_lineEdit.text().strip():
            self.hpBelow_lineEdit.setStyleSheet("border: 2px solid red;")
            self.status_label.setText("Please fill in the 'Below' field.")
            has_error = True

        if not self.hpAbove_lineEdit.text().strip():
            self.hpAbove_lineEdit.setStyleSheet("border: 2px solid red;")
            if not has_error:
                self.status_label.setText("Please fill in the 'Above' field.")
            has_error = True

        if has_error:
            return

        self.status_label.setStyleSheet("color: Green; font-weight: bold;")

        if not self.minMPHeal_lineEdit.text():
            self.minMPHeal_lineEdit.setText("0")

        hp_below_val = int(self.hpBelow_lineEdit.text())
        hp_above_val = int(self.hpAbove_lineEdit.text())
        min_mp_val = int(self.minMPHeal_lineEdit.text())

        heal_name = (
                f"{self.healType_comboBox.currentText()}  {hp_below_val}-{hp_above_val}"
                f"  :  Press "
                f"{self.healKey_comboBox.currentText()} "
        )

        heal_data = {
            "Type": self.healType_comboBox.currentText(),
            "Key": self.healKey_comboBox.currentText(),
            "Below": hp_below_val,
            "Above": hp_above_val,
            "MinMp": min_mp_val
        }

        heal_item = QListWidgetItem(heal_name)
        heal_item.setData(Qt.UserRole, heal_data)
        self.healList_listWidget.addItem(heal_item)

        self.hpAbove_lineEdit.clear()
        self.hpBelow_lineEdit.clear()
        self.minMPHeal_lineEdit.clear()
        self.status_label.setText("Heal action added successfully!")

    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        heal_list = [
            self.healList_listWidget.item(i).data(Qt.UserRole) 
            for i in range(self.healList_listWidget.count())
        ]
        data_to_save = {
            "heals": heal_list
        }

        if manage_profile("save", "Save/Healing", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")

    def load_settings(self, profile_name) -> None:
        self.status_label.setText("")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        filename = f"Save/Healing/{profile_name}.json"
        self.healList_listWidget.clear()
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)
            for heal_data in loaded_data.get("heals", []):
                heal_name = (
                    f"{heal_data['Type']}  {heal_data['Below']}-{heal_data['Above']}"
                    f"  :  Press {heal_data['Key']} "
                )
                heal_item = QListWidgetItem(heal_name)
                heal_item.setData(Qt.UserRole, heal_data)
                self.healList_listWidget.addItem(heal_item)
            
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")

    def startHeal_thread(self, state) -> None:
        if state == Qt.Checked:
            # Stop existing thread if running
            if self.heal_thread:
                self.heal_thread.stop()
                self.heal_thread.wait(2000)

            # Extract data while in GUI thread
            healing_data = [
                self.healList_listWidget.item(i).data(Qt.UserRole) 
                for i in range(self.healList_listWidget.count())
            ]
            
            self.heal_thread = HealThread(healing_data)
            self.heal_thread.start()
        else:
            if self.heal_thread:
                self.heal_thread.stop()
                self.heal_thread.wait(2000)
                self.heal_thread = None
