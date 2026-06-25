import random
import time
import win32api
import win32gui
import Addresses
import win32con
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QCheckBox, QLineEdit, QComboBox

class HotkeysThread(QThread):
    def __init__(self, hotkey_data_list=None):
        super().__init__()
        self.running = True
        self.hotkey_data_list = hotkey_data_list if hotkey_data_list else []
        self.last_execution_times = {}
        self.next_delays = {}
        self.data_lock = QMutex()

    def update_hotkey_data(self, new_data):
        with QMutexLocker(self.data_lock):
            self.hotkey_data_list = new_data
            # We might want to clear execution times if the list changed significantly,
            # but let's keep it simple for now.

    def run(self):
        while self.running:
            current_time = time.time()
            
            try:
                with QMutexLocker(self.data_lock):
                    current_list = list(self.hotkey_data_list)
                
                for index, entry in enumerate(current_list):
                    if not entry.get("Active", False):
                        continue
                    
                    hotkey_name = entry.get("Hotkey")
                    interval = entry.get("Interval", 2.0)
                    randomize = entry.get("Randomize", 0.5)
                    
                    if not hotkey_name:
                        continue
                    
                    # Initialize last execution time if not present
                    if index not in self.last_execution_times:
                        self.last_execution_times[index] = current_time
                        self.next_delays[index] = interval + random.uniform(0, randomize)
                        continue
                    
                    last_time = self.last_execution_times[index]
                    
                    # Check if enough time has passed
                    if current_time - last_time >= self.next_delays[index]:
                        # Execute Hotkey
                        self.press_hotkey(hotkey_name)
                        
                        # Update time and calculate next delay
                        self.last_execution_times[index] = current_time
                        self.next_delays[index] = interval + random.uniform(0, randomize)
            except Exception as e:
                print(f"HotkeysThread error: {e}")
            
            QThread.msleep(10)


    def press_hotkey(self, hotkey_name):
        # Map F1-F12 to VK codes
        # F1 is 0x70 (112)
        try:
            f_key_num = int(hotkey_name[1:])
            vk_code = 111 + f_key_num # F1=112, so 111+1
            
            # Use keybd_event for key simulation
            win32gui.PostMessage(Addresses.game, win32con.WM_KEYDOWN, vk_code, vk_code)
            win32gui.PostMessage(Addresses.game, win32con.WM_KEYUP, vk_code, vk_code)
            
        except Exception as e:
            print(f"Error pressing hotkey {hotkey_name}: {e}")

    def stop(self):
        self.running = False
