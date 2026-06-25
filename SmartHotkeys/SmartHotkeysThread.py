import random
import win32api
import win32con
import win32gui
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QListWidgetItem

from Addresses import coordinates_x, coordinates_y
import Addresses
from Functions.MemoryFunctions import read_target_info, read_my_wpt, read_targeting_status
from Functions.MouseFunctions import mouse_function


from PyQt5.QtCore import QThread, Qt, pyqtSignal

class SetSmartHotkeyThread(QThread):
    status_signal = pyqtSignal(str, str) # text, style
    hotkey_set_signal = pyqtSignal(dict) # smart_hotkey_data

    def __init__(self, hotkey_name, rune_option):
        super().__init__()
        self.running = True
        self.hotkey_name = hotkey_name
        self.rune_option = rune_option

    def run(self):
        self.status_signal.emit("Move mouse to target location...", "color: blue; font-weight: bold;")
        while self.running:
            x, y = win32gui.ScreenToClient(Addresses.game, win32api.GetCursorPos())
            self.status_signal.emit(f"Current: X={x}  Y={y}", "color: blue; font-weight: bold;")
            
            if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                self.status_signal.emit(f"Coordinates set at X={x}, Y={y}", "color: green; font-weight: bold;")
                
                smart_hotkey_data = {
                    "Hotkey": self.hotkey_name,
                    "Option": self.rune_option,
                    "X": x,
                    "Y": y
                }
                self.hotkey_set_signal.emit(smart_hotkey_data)
                self.running = False
                return
            QThread.msleep(50)

    def stop(self):
        self.running = False


class SmartHotkeysThread(QThread):
    def __init__(self, hotkeys_data):
        super().__init__()
        self.running = True
        self.hotkeys_data = hotkeys_data

    def run(self):
        while self.running:
            for hotkey_data in self.hotkeys_data:
                if not self.running: break
                hotkey_number = int(hotkey_data['Hotkey'][1:])
                vk_code = 111 + hotkey_number
                if win32api.GetAsyncKeyState(vk_code) & 1:
                    mouse_function(hotkey_data['X'], hotkey_data['Y'], option=1)
                    if hotkey_data['Option'] == 'On Target':
                        target_id = read_targeting_status()
                        if target_id:
                            target_x, target_y, target_z, target_name, target_hp = read_target_info()
                            x, y, z = read_my_wpt()
                            dx = (target_x - x) * Addresses.square_size
                            dy = (target_y - y) * Addresses.square_size
                            mouse_function(coordinates_x[0] + dx, coordinates_y[0] + dy, option=2)
                    elif hotkey_data['Option'] == 'On Yourself':
                        mouse_function(coordinates_x[0], coordinates_y[0], option=2)
                    elif hotkey_data['Option'] == 'With Crosshair':
                        cur_x, cur_y = win32gui.ScreenToClient(Addresses.game, win32api.GetCursorPos())
                        mouse_function(cur_x, cur_y, option=2)
            QThread.msleep(int(random.uniform(10, 20)))

    def stop(self):
        self.running = False

