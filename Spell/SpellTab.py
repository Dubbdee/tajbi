import json, os
from PyQt5.QtWidgets import (QWidget, QComboBox, QLineEdit, QListWidget, QGridLayout, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QListWidgetItem)
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtCore import Qt
from Spell.SpellThread import SpellThread
from Functions.GeneralFunctions import delete_item, manage_profile


class SpellTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.spell_thread = None

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))
        # Set Title and Size
        self.setWindowTitle("Spell")
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
        self.create_spell_ui()

        # Add status label at the bottom
        self.layout.addWidget(self.status_label, 1, 0, 1, 2)

    def init_widgets(self):
        """Initialize all widgets used in the UI"""
        # Validators
        int_validator = QIntValidator(0, 100, self)
        
        # Spell widgets  
        self.spellKey_comboBox = QComboBox(self)
        self.minDist_comboBox = QComboBox(self)
        self.targetName_lineEdit = QLineEdit(self)
        self.hpFrom_lineEdit = QLineEdit(self)
        self.hpTo_lineEdit = QLineEdit(self)
        self.minMPSpell_lineEdit = QLineEdit(self)
        self.minHPSpell_lineEdit = QLineEdit(self)
        self.spellList_listWidget = QListWidget(self)
        
        # Set validators
        self.hpFrom_lineEdit.setValidator(int_validator)
        self.hpTo_lineEdit.setValidator(int_validator)
        
        # Set fixed widths
        self.hpFrom_lineEdit.setFixedWidth(40)
        self.hpTo_lineEdit.setFixedWidth(40)
        self.minMPSpell_lineEdit.setFixedWidth(40)
        self.minHPSpell_lineEdit.setFixedWidth(40)
        
        # Populate combo boxes
        self.spellKey_comboBox.addItems([f"F{i}" for i in range(1, 10)] + ["First Rune", "Second Rune"])
        self.minDist_comboBox.addItems(["No dist"] + [str(i) for i in range(1, 6)])
        
        # Connect signals
        self.spellList_listWidget.itemDoubleClicked.connect(
            lambda item: delete_item(self.spellList_listWidget, item)
        )

    def create_spell_ui(self):
        """Create the spell UI section"""
        groupbox = QGroupBox("Spell")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # List widget
        groupbox_layout.addWidget(self.spellList_listWidget)

        # Input section
        input_layout = QVBoxLayout()

        # Row 1: Target and key
        layout1 = QHBoxLayout()
        layout1.addWidget(self.targetName_lineEdit)
        self.targetName_lineEdit.setPlaceholderText("Orc, Minotaur, etc., * - All Monsters")
        layout1.addWidget(QLabel("Key:", self), alignment=Qt.AlignLeft)
        layout1.addWidget(self.spellKey_comboBox)
        layout1.addWidget(QLabel("Min Dist:", self), alignment=Qt.AlignLeft)
        layout1.addWidget(self.minDist_comboBox)
        input_layout.addLayout(layout1)

        # Row 2: HP range and conditions
        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel("HP%:", self), alignment=Qt.AlignLeft)
        layout2.addWidget(self.hpFrom_lineEdit)
        layout2.addWidget(QLabel("-", self), alignment=Qt.AlignLeft)
        layout2.addWidget(self.hpTo_lineEdit, alignment=Qt.AlignLeft)
        layout2.addWidget(QLabel("Min. MP:", self))
        layout2.addWidget(self.minMPSpell_lineEdit)
        layout2.addWidget(QLabel("Min. HP%:", self))
        layout2.addWidget(self.minHPSpell_lineEdit)
        input_layout.addLayout(layout2)

        # Row 3: Add Button
        layout3 = QHBoxLayout()
        add_spell_button = QPushButton("Add", self)
        add_spell_button.clicked.connect(self.add_spell)
        layout3.addWidget(add_spell_button)
        input_layout.addLayout(layout3)

        groupbox_layout.addLayout(input_layout)

        # Set placeholders
        self.minMPSpell_lineEdit.setPlaceholderText("300")
        self.hpFrom_lineEdit.setPlaceholderText("100")
        self.hpTo_lineEdit.setPlaceholderText("0")
        self.minHPSpell_lineEdit.setPlaceholderText("50")

        self.layout.addWidget(groupbox, 0, 0, 1, 2)

    def add_spell(self) -> None:
        """Add a spell action to the list"""
        self.status_label.setText("")
        self.targetName_lineEdit.setStyleSheet("")
        self.hpFrom_lineEdit.setStyleSheet("")
        self.hpTo_lineEdit.setStyleSheet("")
        self.status_label.setStyleSheet("color: Red; font-weight: bold;")

        has_error = False

        if not self.targetName_lineEdit.text().strip():
            self.targetName_lineEdit.setStyleSheet("border: 2px solid red;")
            self.status_label.setText("Please fill in the 'Name' field.")
            has_error = True

        if not self.hpFrom_lineEdit.text().strip():
            self.hpFrom_lineEdit.setStyleSheet("border: 2px solid red;")
            if not has_error:
                self.status_label.setText("Please fill in the 'From' field.")
            has_error = True

        if not self.hpTo_lineEdit.text().strip():
            self.hpTo_lineEdit.setStyleSheet("border: 2px solid red;")
            if not has_error:
                self.status_label.setText("Please fill in the 'To' field.")
            has_error = True

        if has_error:
            return

        self.status_label.setStyleSheet("color: Green; font-weight: bold;")

        if not self.minMPSpell_lineEdit.text():
            self.minMPSpell_lineEdit.setText("0")
        if not self.minHPSpell_lineEdit.text():
            self.minHPSpell_lineEdit.setText("0")

        monsters_name = self.targetName_lineEdit.text().strip()
        hp_from_val = int(self.hpFrom_lineEdit.text())
        hp_to_val = int(self.hpTo_lineEdit.text())
        min_mp_val = int(self.minMPSpell_lineEdit.text())
        min_hp_val = int(self.minHPSpell_lineEdit.text())

        min_dist_text = self.minDist_comboBox.currentText()
        min_dist_val = 0 if min_dist_text == "No dist" else int(min_dist_text)

        spell_name = (
            f"{monsters_name} : ({hp_from_val}%-{hp_to_val}%)"
            f"  :  Use {self.spellKey_comboBox.currentText()}"
            f"  :  Dist {min_dist_text}"
        )

        spell_data = {
            "Name": monsters_name,
            "Key": self.spellKey_comboBox.currentText(),
            "HpFrom": hp_from_val,
            "HpTo": hp_to_val,
            "MinMp": min_mp_val,
            "MinHp": min_hp_val,
            "MinDist": min_dist_val
        }

        spell_item = QListWidgetItem(spell_name)
        spell_item.setData(Qt.UserRole, spell_data)
        self.spellList_listWidget.addItem(spell_item)

        self.targetName_lineEdit.clear()
        self.hpFrom_lineEdit.clear()
        self.hpTo_lineEdit.clear()
        self.minMPSpell_lineEdit.clear()
        self.minHPSpell_lineEdit.clear()
        self.status_label.setText("Spell action added successfully!")

    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        spell_list = [
            self.spellList_listWidget.item(i).data(Qt.UserRole) 
            for i in range(self.spellList_listWidget.count())
        ]
        data_to_save = {
            "spells": spell_list
        }

        if manage_profile("save", "Save/Spell", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")

    def load_settings(self, profile_name) -> None:
        self.status_label.setText("")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        filename = f"Save/Spell/{profile_name}.json"
        self.spellList_listWidget.clear()
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)
            for spell_data in loaded_data.get("spells", []):
                min_dist = spell_data.get('MinDist', 0)
                min_dist_text = "No dist" if min_dist == 0 else str(min_dist)
                spell_name = (
                    f"{spell_data['Name']} : ({spell_data['HpFrom']}%-{spell_data['HpTo']}%)"
                    f"  :  Use {spell_data['Key']}"
                    f"  :  Dist {min_dist_text}"
                )
                spell_item = QListWidgetItem(spell_name)
                spell_item.setData(Qt.UserRole, spell_data)
                self.spellList_listWidget.addItem(spell_item)
            
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")

    def start_spell_thread(self, state) -> None:
        if state == Qt.Checked:
            # Stop existing thread if running
            if self.spell_thread and self.spell_thread.isRunning():
                self.spell_thread.stop()
                self.spell_thread.wait(2000)
            
            # Extract data while in GUI thread
            spell_data_list = [
                self.spellList_listWidget.item(i).data(Qt.UserRole) 
                for i in range(self.spellList_listWidget.count())
            ]
            
            self.spell_thread = SpellThread(spell_data_list)
            self.spell_thread.start()
        else:
            if self.spell_thread:
                self.spell_thread.stop()
                self.spell_thread.wait(2000)
                self.spell_thread = None

