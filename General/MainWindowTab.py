from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QCheckBox, QGroupBox, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QTimer, QTime
from Target.TargetTab import TargetTab
from HealAttack.HealingAttackTab import HealingTab
from Spell.SpellTab import SpellTab
from Walker.WalkerTab import WalkerTab
from Settings.SettingsTab import SettingsTab
from SmartHotkeys.SmartHotkeysTab import SmartHotkeysTab
from Hotkeys.HotkeysTab import HotkeysTab
from Looting.LootingTab import LootingTab
from Training.TrainingTab import TrainingTab
import os

class MainWindowTab(QWidget):
    def __init__(self):
        super().__init__()
        self.targetLootTab_instance = None
        self.healingTab_instance = None
        self.spellTab_instance = None
        self.walkerTab_instance = None
        self.settingsTab_instance = None
        self.smartHotkeysTab_instance = None
        self.hotkeysTab_instance = None
        self.lootingTab_instance = None
        self.trainingTab_instance = None
        
        # Bot timer
        self.bot_start_time = QTime.currentTime()
        self.bot_timer = QTimer(self)
        self.bot_timer.timeout.connect(self.update_timer)
        self.bot_timer.start(1000)  # Update every second

        self.layout = QGridLayout(self)

        # --- Buttons ---
        self.healing_button = QPushButton("Healing", self)
        self.healing_button.clicked.connect(self.healing)
        
        self.spell_button = QPushButton("Spell", self)
        self.spell_button.clicked.connect(self.spell)
        
        self.target_button = QPushButton("Targeting", self)
        self.target_button.clicked.connect(self.targetLoot)
        
        self.walker_button = QPushButton("Walker", self)
        self.walker_button.clicked.connect(self.walker)
        
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.settings)
        
        self.smart_hotkeys_button = QPushButton("Smart Hotkeys", self)
        self.smart_hotkeys_button.clicked.connect(self.smartHotkeys)
        
        self.hotkeys_button = QPushButton("Hotkeys", self)
        self.hotkeys_button.clicked.connect(self.hotkeys)
        
        self.looting_button = QPushButton("Looting", self)
        self.looting_button.clicked.connect(self.looting)

        self.training_button = QPushButton("Training", self)
        self.training_button.clicked.connect(self.training)

        self.layout.addWidget(self.healing_button, 0, 0)
        self.layout.addWidget(self.spell_button, 0, 1)
        self.layout.addWidget(self.target_button, 1, 0)
        self.layout.addWidget(self.walker_button, 1, 1)
        self.layout.addWidget(self.settings_button, 2, 0)
        self.layout.addWidget(self.smart_hotkeys_button, 2, 1)
        self.layout.addWidget(self.hotkeys_button, 3, 0)
        self.layout.addWidget(self.looting_button, 3, 1)
        self.layout.addWidget(self.training_button, 4, 0)

        # --- Bot Status GroupBox ---
        self.status_groupbox = QGroupBox("Bot Status", self)
        self.status_layout = QGridLayout()
        
        self.healing_checkbox = QCheckBox("Healing", self)
        self.healing_checkbox.stateChanged.connect(self.toggle_healing)
        
        self.spell_checkbox = QCheckBox("Spell", self)
        self.spell_checkbox.stateChanged.connect(self.toggle_spell)
        
        self.targeting_checkbox = QCheckBox("Targeting", self)
        self.targeting_checkbox.stateChanged.connect(self.toggle_targeting)
        
        self.walker_checkbox = QCheckBox("Walker", self)
        self.walker_checkbox.stateChanged.connect(self.toggle_walker)
        
        self.smart_hotkeys_checkbox = QCheckBox("Smart Hotkeys", self)
        self.smart_hotkeys_checkbox.stateChanged.connect(self.toggle_smart_hotkeys)
        
        self.looting_checkbox = QCheckBox("Looting", self)
        self.looting_checkbox.stateChanged.connect(self.toggle_looting)
        
        self.status_layout.addWidget(self.healing_checkbox, 0, 0)
        self.status_layout.addWidget(self.spell_checkbox, 0, 1)
        self.status_layout.addWidget(self.targeting_checkbox, 1, 0)
        self.status_layout.addWidget(self.walker_checkbox, 1, 1)
        self.status_layout.addWidget(self.smart_hotkeys_checkbox, 2, 0)
        self.status_layout.addWidget(self.looting_checkbox, 2, 1)
        
        self.status_groupbox.setLayout(self.status_layout)
        self.layout.addWidget(self.status_groupbox, 5, 0, 1, 2)

        # --- Save & Load GroupBox ---
        self.profile_groupbox = QGroupBox("Save && Load", self)
        self.profile_layout = QGridLayout()
        
        self.tab_comboBox = QComboBox(self)
        self.tab_comboBox.addItems(["All", "Healing", "Spell", "Targeting", "Walker", "Settings", "Smart Hotkeys", "Hotkeys", "Looting", "Training"])
        self.tab_comboBox.currentIndexChanged.connect(self.refresh_profile_list)
        
        self.profile_lineEdit = QLineEdit(self)
        self.profile_lineEdit.setPlaceholderText("Profile Name")
        
        self.profile_listWidget = QListWidget(self)
        self.profile_listWidget.itemClicked.connect(self.on_profile_selected)
        self.profile_listWidget.setMaximumHeight(70)
        
        self.save_button = QPushButton('Save', self)
        self.load_button = QPushButton('Load', self)
        
        self.save_button.clicked.connect(self.save_settings)
        self.load_button.clicked.connect(self.load_settings)
        
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        self.profile_layout.addWidget(self.tab_comboBox, 0, 0, 1, 2)
        self.profile_layout.addWidget(self.profile_lineEdit, 1, 0, 1, 2)
        self.profile_layout.addWidget(self.profile_listWidget, 2, 0, 1, 2)
        self.profile_layout.addWidget(self.save_button, 3, 0)
        self.profile_layout.addWidget(self.load_button, 3, 1)
        self.profile_layout.addWidget(self.status_label, 4, 0, 1, 2)
        
        self.profile_groupbox.setLayout(self.profile_layout)
        self.layout.addWidget(self.profile_groupbox, 6, 0, 1, 2)
        
        # Bot Timer at the bottom
        self.timer_label = QLabel("Bot running: 00:00:00", self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-weight: bold; font-size: 12px; color: green;")
        self.layout.addWidget(self.timer_label, 7, 0, 1, 2)

        self.refresh_profile_list()

    def targetLoot(self):
        if self.targetLootTab_instance is None:
            self.targetLootTab_instance = TargetTab()
        self.targetLootTab_instance.show()

    def healing(self):
        if self.healingTab_instance is None:
            self.healingTab_instance = HealingTab()
        self.healingTab_instance.show()

    def spell(self):
        if self.spellTab_instance is None:
            self.spellTab_instance = SpellTab()
            self.spellTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.spellTab_instance.show()

    def walker(self):
        if self.walkerTab_instance is None:
            self.walkerTab_instance = WalkerTab()
            self.walkerTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.walkerTab_instance.show()

    def settings(self):
        if self.settingsTab_instance is None:
            self.settingsTab_instance = SettingsTab()
            self.settingsTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.settingsTab_instance.show()

    def smartHotkeys(self):
        if self.smartHotkeysTab_instance is None:
            self.smartHotkeysTab_instance = SmartHotkeysTab()
            self.smartHotkeysTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.smartHotkeysTab_instance.show()

    def hotkeys(self):
        if self.hotkeysTab_instance is None:
            self.hotkeysTab_instance = HotkeysTab()
            self.hotkeysTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.hotkeysTab_instance.show()

    def looting(self):
        if self.lootingTab_instance is None:
            self.lootingTab_instance = LootingTab()
            self.lootingTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.lootingTab_instance.show()

    def training(self):
        if self.trainingTab_instance is None:
            self.trainingTab_instance = TrainingTab()
            self.trainingTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.trainingTab_instance.show()

    def toggle_healing(self, state):
        if self.healingTab_instance is None:
            self.healingTab_instance = HealingTab()
        if hasattr(self.healingTab_instance, 'startHeal_thread'):
            self.healingTab_instance.startHeal_thread(state)

    def toggle_spell(self, state):
        if self.spellTab_instance is None:
            self.spellTab_instance = SpellTab()
            self.spellTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        if hasattr(self.spellTab_instance, 'start_spell_thread'):
            self.spellTab_instance.start_spell_thread(state)

    def toggle_targeting(self, state):
        if self.targetLootTab_instance is None:
            self.targetLootTab_instance = TargetTab()
            
        # Get loot data from Looting if available
        loot_data = None
        if self.lootingTab_instance:
             loot_data = self.lootingTab_instance.get_loot_data()

        # Get blacklist from Walker if available
        blacklist = set()
        if self.walkerTab_instance and hasattr(self.walkerTab_instance, 'get_blacklist'):
            blacklist = self.walkerTab_instance.get_blacklist()

        if state == Qt.Checked:
            # If Looting is currently running in continuous mode, stop it
            if self.lootingTab_instance and self.lootingTab_instance.loot_thread:
                self.lootingTab_instance.start_loot_thread(Qt.Unchecked)
            
            # Start Targeting with Loot Table (if looting is checked) and blacklist
            if self.looting_checkbox.isChecked():
                 self.targetLootTab_instance.start_target_thread(state, loot_data, blacklist)
            else:
                 self.targetLootTab_instance.start_target_thread(state, None, blacklist)
        else:
            if hasattr(self.targetLootTab_instance, 'start_target_thread'):
                self.targetLootTab_instance.start_target_thread(state)
            
            # If Looting is checked, restart it in continuous mode
            if self.looting_checkbox.isChecked():
                if self.lootingTab_instance is None:
                    self.lootingTab_instance = LootingTab()
                self.lootingTab_instance.start_loot_thread(Qt.Checked)


    def toggle_walker(self, state):
        if self.walkerTab_instance is None:
            self.walkerTab_instance = WalkerTab()
            self.walkerTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        if hasattr(self.walkerTab_instance, 'start_walker_thread'):
            self.walkerTab_instance.start_walker_thread(state)

    def toggle_smart_hotkeys(self, state):
        if self.smartHotkeysTab_instance is None:
            self.smartHotkeysTab_instance = SmartHotkeysTab()
            self.smartHotkeysTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        if hasattr(self.smartHotkeysTab_instance, 'start_smart_hotkeys_thread'):
            self.smartHotkeysTab_instance.start_smart_hotkeys_thread(state)

    def toggle_looting(self, state):
        if self.lootingTab_instance is None:
            self.lootingTab_instance = LootingTab()
            self.lootingTab_instance.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        if state == Qt.Checked:
            # If Targeting is ON, don't start continuous thread, but update Targeting
            if self.targeting_checkbox.isChecked():
                 loot_data = self.lootingTab_instance.get_loot_data()
                 # Get blacklist from Walker for restart
                 blacklist = set()
                 if self.walkerTab_instance and hasattr(self.walkerTab_instance, 'get_blacklist'):
                     blacklist = self.walkerTab_instance.get_blacklist()
                 # Restart Targeting to pick up new loot templates
                 if self.targetLootTab_instance:
                     self.targetLootTab_instance.start_target_thread(Qt.Unchecked)
                     self.targetLootTab_instance.start_target_thread(Qt.Checked, loot_data, blacklist)
            else:
                # Targeting OFF, start continuous looting
                if hasattr(self.lootingTab_instance, 'start_loot_thread'):
                    self.lootingTab_instance.start_loot_thread(state)
        else:
            # Stop continuous thread
            if hasattr(self.lootingTab_instance, 'start_loot_thread'):
                self.lootingTab_instance.start_loot_thread(state)
            
            # If Targeting is ON, restart it without loot table but with blacklist
            if self.targeting_checkbox.isChecked() and self.targetLootTab_instance:
                 blacklist = set()
                 if self.walkerTab_instance and hasattr(self.walkerTab_instance, 'get_blacklist'):
                     blacklist = self.walkerTab_instance.get_blacklist()
                 self.targetLootTab_instance.start_target_thread(Qt.Unchecked)
                 self.targetLootTab_instance.start_target_thread(Qt.Checked, None, blacklist)


    def save_settings(self):
        profile_name = self.profile_lineEdit.text().strip()
        if not profile_name:
            self.status_label.setText("Enter Profile Name")
            self.status_label.setStyleSheet("color: red")
            return

        selected_tab = self.tab_comboBox.currentText()
        
        if selected_tab == "All":
            tabs = [
                ("Healing", self.healingTab_instance, self.healing),
                ("Spell", self.spellTab_instance, self.spell),
                ("Targeting", self.targetLootTab_instance, self.targetLoot),
                ("Walker", self.walkerTab_instance, self.walker),
                ("Settings", self.settingsTab_instance, self.settings),
                ("Smart Hotkeys", self.smartHotkeysTab_instance, self.smartHotkeys),
                ("Hotkeys", self.hotkeysTab_instance, self.hotkeys),
                ("Looting", self.lootingTab_instance, self.looting),
                ("Training", self.trainingTab_instance, self.training)
            ]
            for name, instance, opener in tabs:
                if instance is None:
                    opener()
                    instance = getattr(self, f"{opener.__name__}Tab_instance")
                    instance.hide()
                
                if instance:
                    if hasattr(instance, 'save_settings'):
                        instance.save_settings(profile_name)
            
            self.status_label.setText(f"All profiles '{profile_name}' saved!")
            self.status_label.setStyleSheet("color: green")

        else:
            instance = None
            opener = None
            if selected_tab == "Healing":
                instance = self.healingTab_instance
                opener = self.healing
            elif selected_tab == "Spell":
                instance = self.spellTab_instance
                opener = self.spell
            elif selected_tab == "Targeting":
                instance = self.targetLootTab_instance
                opener = self.targetLoot
            elif selected_tab == "Walker":
                instance = self.walkerTab_instance
                opener = self.walker
            elif selected_tab == "Settings":
                instance = self.settingsTab_instance
                opener = self.settings
            elif selected_tab == "Smart Hotkeys":
                instance = self.smartHotkeysTab_instance
                opener = self.smartHotkeys
            elif selected_tab == "Hotkeys":
                instance = self.hotkeysTab_instance
                opener = self.hotkeys
            elif selected_tab == "Looting":
                instance = self.lootingTab_instance
                opener = self.looting
            elif selected_tab == "Training":
                instance = self.trainingTab_instance
                opener = self.training
            
            if instance is None and opener:
                opener()
                instance = getattr(self, f"{opener.__name__}Tab_instance")
                instance.hide()

            if instance and hasattr(instance, 'save_settings'):
                instance.save_settings(profile_name)
                self.status_label.setText(f"{selected_tab} '{profile_name}' saved!")
                self.status_label.setStyleSheet("color: green")
        
        self.refresh_profile_list()

    def load_settings(self):
        profile_name = self.profile_lineEdit.text().strip()
        if not profile_name:
            self.status_label.setText("Enter Profile Name")
            self.status_label.setStyleSheet("color: red")
            return

        selected_tab = self.tab_comboBox.currentText()
        
        if selected_tab == "All":
            tabs = [
                ("Healing", self.healingTab_instance, self.healing),
                ("Spell", self.spellTab_instance, self.spell),
                ("Targeting", self.targetLootTab_instance, self.targetLoot),
                ("Walker", self.walkerTab_instance, self.walker),
                ("Settings", self.settingsTab_instance, self.settings),
                ("Smart Hotkeys", self.smartHotkeysTab_instance, self.smartHotkeys),
                ("Hotkeys", self.hotkeysTab_instance, self.hotkeys),
                ("Looting", self.lootingTab_instance, self.looting),
                ("Training", self.trainingTab_instance, self.training)
            ]
            for name, instance, opener in tabs:
                if instance is None:
                    opener()
                    instance = getattr(self, f"{opener.__name__}Tab_instance")
                    instance.hide()
                
                if instance:
                    if hasattr(instance, 'load_settings'):
                        instance.load_settings(profile_name)
            
            self.status_label.setText(f"All profiles '{profile_name}' loaded!")
            self.status_label.setStyleSheet("color: green")

        else:
            instance = None
            opener = None
            if selected_tab == "Healing":
                instance = self.healingTab_instance
                opener = self.healing
            elif selected_tab == "Spell":
                instance = self.spellTab_instance
                opener = self.spell
            elif selected_tab == "Targeting":
                instance = self.targetLootTab_instance
                opener = self.targetLoot
            elif selected_tab == "Walker":
                instance = self.walkerTab_instance
                opener = self.walker
            elif selected_tab == "Settings":
                instance = self.settingsTab_instance
                opener = self.settings
            elif selected_tab == "Smart Hotkeys":
                instance = self.smartHotkeysTab_instance
                opener = self.smartHotkeys
            elif selected_tab == "Hotkeys":
                instance = self.hotkeysTab_instance
                opener = self.hotkeys
            elif selected_tab == "Looting":
                instance = self.lootingTab_instance
                opener = self.looting
            elif selected_tab == "Training":
                instance = self.trainingTab_instance
                opener = self.training
            
            if instance is None and opener:
                opener()
                instance = getattr(self, f"{opener.__name__}Tab_instance")
                instance.hide()

            if instance and hasattr(instance, 'load_settings'):
                instance.load_settings(profile_name)
                self.status_label.setText(f"{selected_tab} '{profile_name}' loaded!")
                self.status_label.setStyleSheet("color: green")

    def refresh_profile_list(self):
        self.profile_listWidget.clear()
        selected_tab = self.tab_comboBox.currentText()
        
        directories = []
        if selected_tab == "All":
            directories = ["Save/Healing", "Save/Spell", "Save/Targeting", "Save/Waypoints", "Save/Settings", "Save/SmartHotkeys", "Save/Hotkeys", "Save/Looting", "Save/Training"]
        elif selected_tab == "Healing":
            directories = ["Save/Healing"]
        elif selected_tab == "Spell":
            directories = ["Save/Spell"]
        elif selected_tab == "Targeting":
            directories = ["Save/Targeting"]
        elif selected_tab == "Walker":
            directories = ["Save/Waypoints"]
        elif selected_tab == "Settings":
            directories = ["Save/Settings"]
        elif selected_tab == "Smart Hotkeys":
            directories = ["Save/SmartHotkeys"]
        elif selected_tab == "Hotkeys":
            directories = ["Save/Hotkeys"]
        elif selected_tab == "Looting":
            directories = ["Save/Looting"]
        elif selected_tab == "Training":
            directories = ["Save/Training"]
            
        profiles = set()
        for directory in directories:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if file.endswith(".json"):
                        profiles.add(file.split('.')[0])
                        
        for profile in sorted(profiles):
            self.profile_listWidget.addItem(profile)

    def on_profile_selected(self, item):
        self.profile_lineEdit.setText(item.text())
    
    def closeEvent(self, event):
        """Handle application close event to stop all threads"""
        # Stop Walker Threads
        if self.walkerTab_instance:
            if self.walkerTab_instance.walker_thread:
                self.walkerTab_instance.walker_thread.stop()
                self.walkerTab_instance.walker_thread.wait()
            if self.walkerTab_instance.record_thread:
                self.walkerTab_instance.record_thread.stop()
                self.walkerTab_instance.record_thread.wait()

        # Stop Looting Thread
        if self.lootingTab_instance:
            if self.lootingTab_instance.loot_thread:
                self.lootingTab_instance.loot_thread.stop()
                self.lootingTab_instance.loot_thread.wait()

        # Stop Target Thread
        if self.targetLootTab_instance:
            if self.targetLootTab_instance.target_thread:
                self.targetLootTab_instance.target_thread.stop()
                self.targetLootTab_instance.target_thread.wait()

        # Stop Healing Thread
        if self.healingTab_instance:
            if self.healingTab_instance.heal_thread:
                self.healingTab_instance.heal_thread.stop()
                self.healingTab_instance.heal_thread.wait()

        # Stop Spell Thread
        if self.spellTab_instance:
            if self.spellTab_instance.spell_thread:
                self.spellTab_instance.spell_thread.stop()
                self.spellTab_instance.spell_thread.wait()

        # Stop Smart Hotkeys Threads
        if self.smartHotkeysTab_instance:
            if self.smartHotkeysTab_instance.smart_hotkeys_thread:
                self.smartHotkeysTab_instance.smart_hotkeys_thread.stop()
                self.smartHotkeysTab_instance.smart_hotkeys_thread.wait()
            if self.smartHotkeysTab_instance.set_smart_hotkey_thread:
                if hasattr(self.smartHotkeysTab_instance.set_smart_hotkey_thread, 'stop'):
                     self.smartHotkeysTab_instance.set_smart_hotkey_thread.stop()
                self.smartHotkeysTab_instance.set_smart_hotkey_thread.wait()

        # Stop Training Threads
        if self.trainingTab_instance:
            if self.trainingTab_instance.training_thread:
                self.trainingTab_instance.training_thread.stop()
                self.trainingTab_instance.training_thread.wait()
            if self.trainingTab_instance.click_thread:
                self.trainingTab_instance.click_thread.stop()
                self.trainingTab_instance.click_thread.wait()
            if self.trainingTab_instance.fishing_thread:
                self.trainingTab_instance.fishing_thread.stop()
                self.trainingTab_instance.fishing_thread.wait()
            if self.trainingTab_instance.set_thread:
                self.trainingTab_instance.set_thread.stop()
                self.trainingTab_instance.set_thread.wait()
            if self.trainingTab_instance.rune_maker_thread:
                self.trainingTab_instance.rune_maker_thread.stop()
                self.trainingTab_instance.rune_maker_thread.wait()
            if self.trainingTab_instance.food_eater_thread:
                self.trainingTab_instance.food_eater_thread.stop()
                self.trainingTab_instance.food_eater_thread.wait()

        event.accept()

    def update_timer(self):
        """Update the bot runtime timer"""
        elapsed = self.bot_start_time.secsTo(QTime.currentTime())
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        self.timer_label.setText(f"Bot running: {hours:02d}:{minutes:02d}:{seconds:02d}")