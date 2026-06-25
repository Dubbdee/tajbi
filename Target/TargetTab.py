import os
import json
from Functions.GeneralFunctions import delete_item, manage_profile
from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QComboBox, QLineEdit, QListWidget, QGridLayout,
    QGroupBox, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QListWidgetItem
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from Target.TargetThread import TargetThread


class TargetTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.target_thread = None
        
        # State Variables
        self.targeting_enabled = False

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))

        # Set Title and Size
        self.setWindowTitle("Targeting")
        self.setFixedSize(350, 300)

        # --- Status "bar" label at the bottom
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        # Combo Boxes
        self.attackDist_comboBox = QComboBox(self)
        self.attackDist_comboBox.addItems(["All", "1", "2", "3", "4", "5", "6", "7"])
        self.stance_comboBox = QComboBox(self)
        self.stance_comboBox.addItems(["Do Nothing", "Chase", "Diagonal", "Chase-Diagonal"])
        self.attackKey_comboBox = QComboBox(self)
        self.attackKey_comboBox.addItems(f'F{i}' for i in range(1, 13))
        self.attackKey_comboBox.addItem("OCR Battle List")
        self.skin_comboBox = QComboBox(self)
        self.skin_comboBox.addItem("No Action")
        self.skin_comboBox.addItems(f'F{i}' for i in range(1, 13))

        # Line Edits
        self.targetName_lineEdit = QLineEdit(self)

        # List Widgets
        self.targetList_listWidget = QListWidget(self)
        self.targetList_listWidget.setFixedSize(150, 150)

        # Main Layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Initialize UI components
        self.targetList()

        # Finally, add the status label at the bottom
        self.layout.addWidget(self.status_label, 1, 0, 1, 2)

    def targetList(self) -> None:
        groupbox = QGroupBox("Targeting", self)
        groupbox_layout = QHBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Buttons
        clearTargetList_button = QPushButton("Clear List", self)
        addTarget_button = QPushButton("Add", self)

        # Button Functions
        clearTargetList_button.clicked.connect(self.clearTarget_list)
        addTarget_button.clicked.connect(self.add_target)

        # Double-click to delete
        self.targetList_listWidget.itemDoubleClicked.connect(
            lambda item: delete_item(self.targetList_listWidget, item)
        )

        # Layouts
        groupbox2_layout = QVBoxLayout()
        layout1 = QVBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout5 = QHBoxLayout()
        layout6 = QHBoxLayout()
        layout7 = QHBoxLayout()

        layout1.addWidget(self.targetList_listWidget)
        layout1.addWidget(clearTargetList_button)

        layout2.addWidget(self.targetName_lineEdit)
        layout2.addWidget(addTarget_button)

        layout3.addWidget(QLabel("Stance:", self))
        layout3.addWidget(self.stance_comboBox)


        layout5.addWidget(QLabel("Dist:", self))
        layout5.addWidget(self.attackDist_comboBox)

        layout6.addWidget(QLabel("Attack Key:", self))
        layout6.addWidget(self.attackKey_comboBox)

        layout7.addWidget(QLabel("Skin:", self))
        layout7.addWidget(self.skin_comboBox)

        self.targetName_lineEdit.setPlaceholderText("Orc, * - All Monsters")

        groupbox2_layout.addLayout(layout2)
        groupbox2_layout.addLayout(layout5)
        groupbox2_layout.addLayout(layout3)
        groupbox2_layout.addLayout(layout6)
        groupbox2_layout.addLayout(layout7)
        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(groupbox2_layout)
        self.layout.addWidget(groupbox, 0, 0, 1, 2)

    def add_target(self) -> None:
        self.status_label.setText("")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.targetName_lineEdit.setStyleSheet("")

        monster_name = self.targetName_lineEdit.text().strip()
        if not monster_name:
            self.targetName_lineEdit.setStyleSheet("border: 2px solid red;")
            self.status_label.setText("Please enter a monster name.")
            return

        for index in range(self.targetList_listWidget.count()):
            existing_name = self.targetList_listWidget.item(index).text().split(' | ')[0].upper()
            if monster_name.upper() == existing_name:
                return

        target_data = {
            "Name": monster_name,
            "Dist": self.attackDist_comboBox.currentIndex(),
            "Stance": self.stance_comboBox.currentIndex(),
            "Skin": self.skin_comboBox.currentIndex(),
        }

        monster = QListWidgetItem(monster_name)
        monster.setData(Qt.UserRole, target_data)
        self.targetList_listWidget.addItem(monster)

        # Clear field
        self.targetName_lineEdit.clear()
        self.attackDist_comboBox.setCurrentIndex(0)
        self.stance_comboBox.setCurrentIndex(0)
        self.skin_comboBox.setCurrentIndex(0)

        # Success message
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText(f"Target '{monster_name}' has been added!")

    def clearTarget_list(self) -> None:
        self.targetList_listWidget.clear()
        self.status_label.setText("")  # optional

    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        target_list = [
            self.targetList_listWidget.item(i).data(Qt.UserRole)
            for i in range(self.targetList_listWidget.count())
        ]
        data_to_save = {
            "targets": target_list
        }

        if manage_profile("save", "Save/Targeting", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")

    def load_settings(self, profile_name) -> None:
        self.status_label.setText("")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        filename = f"Save/Targeting/{profile_name}.json"
        self.targetList_listWidget.clear()
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)
            for target_data in loaded_data.get("targets", []):
                # Backward compatibility: add Skin field if missing
                if 'Skin' not in target_data:
                    target_data['Skin'] = 0
                target_item = QListWidgetItem(target_data['Name'])
                target_item.setData(Qt.UserRole, target_data)
                self.targetList_listWidget.addItem(target_item)
            
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")

    def start_target_thread(self, state, loot_data=None, blacklist=None) -> None:
        self.targeting_enabled = (state == Qt.Checked)
        
        if state == Qt.Checked:
            # Stop existing thread if running
            if self.target_thread:
                self.target_thread.stop()
                self.target_thread.wait(2000)

            targets = [
                self.targetList_listWidget.item(i).data(Qt.UserRole)
                for i in range(self.targetList_listWidget.count())
            ]
            # Use provided blacklist or default to empty set
            if blacklist is None:
                blacklist = set()
            
            self.target_thread = TargetThread(targets, Qt.Unchecked, self.attackKey_comboBox.currentIndex(), loot_data, blacklist)
            self.target_thread.start()
        else:
            if self.target_thread:
                self.target_thread.stop()
                self.target_thread.wait(2000)
                self.target_thread = None

