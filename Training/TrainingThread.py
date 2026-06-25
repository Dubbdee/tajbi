import random

import win32gui
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from win32con import VK_LBUTTON

from Addresses import fishing_x, fishing_y
import Addresses
import win32api
from Functions.MemoryFunctions import *
from Functions.KeyboardFunctions import press_hotkey
from Functions.MouseFunctions import mouse_function


class TrainingThread(QThread):

    def __init__(self, training_list):
        super().__init__()
        self.training_list = training_list
        self.running = True

    def run(self):
        while self.running:
            try:
                for index in range(self.training_list.count()):
                    current_hp, current_max_hp, current_mp, current_max_mp = read_my_stats()
                    while (current_hp or current_max_hp or current_mp or current_max_mp) is None:
                        current_hp, current_max_hp, current_mp, current_max_mp = read_my_stats()
                    hotkey_data = self.training_list.item(index).data(Qt.UserRole)
                    hotkey_mana = hotkey_data['Mana']
                    if current_mp >= hotkey_mana:
                        press_hotkey(int(self.training_list.item(index).text()[1:]))
                        QThread.msleep(random.randint(500, 600))
                QThread.msleep(random.randint(500, 600))
            except Exception as e:
                print(e)

    def stop(self):
        self.running = False


class ClickThread(QThread):
    def __init__(self, timer, hotkey):
        super().__init__()
        self.timer = timer
        self.hotkey = hotkey
        self.running = True

    def run(self):
        timer = 0
        while self.running:
            try:
                if timer/1000 >= self.timer:
                    press_hotkey(int(self.hotkey[1:]))
                    timer = 0
                sleep_value = random.randint(500, 600)
                QThread.msleep(sleep_value)
                timer += sleep_value

            except Exception as e:
                print(e)

    def stop(self):
        self.running = False


class FishingThread(QThread):
    status_signal = pyqtSignal(str, str)

    def __init__(self, status_label, tries_per_spot=5):
        super().__init__()
        self.status_label = status_label
        self.running = True
        self.current_spot_index = 0
        self.tries_per_spot = tries_per_spot
        self.attempts_on_current_spot = 0

    def run(self):
        timer = 0
        counter = 0
        baits = 0
        spots = Addresses.fishing_water_spots if Addresses.fishing_water_spots else [(fishing_x[1], fishing_y[1])]

        if not spots or all(x == 0 and y == 0 for x, y in spots):
            self.status_signal.emit("No water spots set! Use 'Add Water' to set coordinates.", "color: red; font-weight: bold;")
            return

        # Re-bait at start using first water spot
        if fishing_x[2] != 0:
            QThread.msleep(random.randint(1000, 1100))
            mouse_function(fishing_x[2], fishing_y[2], option=1)
            QThread.msleep(random.randint(1000, 1100))
            water_x, water_y = spots[0]
            mouse_function(water_x, water_y, option=2)
            QThread.msleep(random.randint(1000, 1100))
            baits += 1
        while self.running:
            water_x, water_y = spots[self.current_spot_index]
            self.attempts_on_current_spot += 1

            # Right-click on fishing rod, wait a moment, then left-click on water
            mouse_function(fishing_x[0], fishing_y[0], option=1)
            QThread.msleep(300)
            mouse_function(water_x, water_y, option=2)
            counter += 1
            randomizer = random.randint(1000, 1100)
            timer += randomizer
            QThread.msleep(randomizer)
            spot_info = f"Spot {self.current_spot_index + 1}/{len(spots)} (try {self.attempts_on_current_spot}/{self.tries_per_spot})"
            self.status_signal.emit(f"{spot_info} | Clicked {counter} times | used {baits} baits", "")
            
            # Only move to next spot after enough attempts on this one
            if self.attempts_on_current_spot >= self.tries_per_spot:
                self.current_spot_index = (self.current_spot_index + 1) % len(spots)
                self.attempts_on_current_spot = 0
            
            # Re-bait periodically using current water spot
            if counter % 1015 == 0 and fishing_x[2] != 0:
                QThread.msleep(random.randint(1000, 1100))
                mouse_function(fishing_x[2], fishing_y[2], option=1)
                QThread.msleep(random.randint(1000, 1100))
                water_x, water_y = spots[self.current_spot_index]
                mouse_function(water_x, water_y, option=2)
                QThread.msleep(random.randint(1000, 1100))
                baits += 1
            if int(timer/1000) >= 20 and fishing_x[3] != 0:
                for _ in range(3):
                    mouse_function(fishing_x[3], fishing_y[3], option=1)
                    QThread.msleep(random.randint(300, 500))
                timer = 0

        return
    def stop(self):
        self.running = False


class SetThread(QThread):
    status_signal = pyqtSignal(str, str)

    def __init__(self, index, status_label):
        super().__init__()
        self.index = index
        self.status_label = status_label
        self.running = True

    def run(self):
        self.status_signal.emit("Current: X=...  Y=...", "color: blue; font-weight: bold;")
        while self.running:
            cur_x, cur_y = win32gui.ScreenToClient(Addresses.game, win32api.GetCursorPos())
            QThread.msleep(10)
            self.status_signal.emit(f"Current: X={cur_x}  Y={cur_y}", "color: blue; font-weight: bold;")
            if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                fishing_x[self.index], fishing_y[self.index] = cur_x, cur_y
                self.status_signal.emit(f"Coordinates set at X={fishing_x[self.index]}, Y={fishing_y[self.index]}", "color: green; font-weight: bold;")
                self.running = False
                return


class AddWaterSpotThread(QThread):
    status_signal = pyqtSignal(str, str)

    def __init__(self, status_label, max_spots=50):
        super().__init__()
        self.status_label = status_label
        self.running = True
        self.max_spots = max_spots

    def run(self):
        try:
            timeout = 0
            while self.running and (win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000) and timeout < 500:
                QThread.msleep(10)
                timeout += 10
            if not self.running:
                return

            self.status_signal.emit("Hover over a water square and click LMB to add it...", "color: blue; font-weight: bold;")
            while self.running:
                cur_x, cur_y = win32gui.ScreenToClient(Addresses.game, win32api.GetCursorPos())
                QThread.msleep(50)
                self.status_signal.emit(f"Current: X={cur_x}  Y={cur_y}  |  Click LMB to add", "color: blue; font-weight: bold;")
                if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                    if len(Addresses.fishing_water_spots) >= self.max_spots:
                        self.status_signal.emit(f"Max {self.max_spots} spots reached!", "color: orange; font-weight: bold;")
                        self.running = False
                        return
                    Addresses.fishing_water_spots.append((cur_x, cur_y))
                    self.status_signal.emit(f"Added water spot at X={cur_x}, Y={cur_y}  (Total: {len(Addresses.fishing_water_spots)})", "color: green; font-weight: bold;")
                    self.running = False
                    return
        except Exception as e:
            print(f"AddWaterSpotThread error: {e}")
            self.running = False

    def stop(self):
        self.running = False


class RuneMakerThread(QThread):
    status_signal = pyqtSignal(str, str)

    def __init__(self, mana_cost, hotkey, timer_mode=False, timer_interval=10):
        super().__init__()
        self.mana_cost = mana_cost
        self.hotkey = hotkey
        self.timer_mode = timer_mode
        self.timer_interval = timer_interval
        self.running = True
        self.rune_count = 0
        self.diagnostic_shown = False

    def run(self):
        while self.running:
            try:
                if self.timer_mode:
                    # Timer mode: skip MP reading, just press hotkey every X seconds
                    press_hotkey(int(self.hotkey[1:]))
                    QThread.msleep(random.randint(600, 800))
                    
                    if Addresses.hand_x != 0 and Addresses.charged_dest_x != 0:
                        mouse_function(Addresses.hand_x, Addresses.hand_y, Addresses.charged_dest_x, Addresses.charged_dest_y, option=4)
                        QThread.msleep(random.randint(300, 400))
                    
                    if Addresses.blank_rune_x != 0 and Addresses.hand_x != 0:
                        mouse_function(Addresses.blank_rune_x, Addresses.blank_rune_y, Addresses.hand_x, Addresses.hand_y, option=4)
                        QThread.msleep(random.randint(300, 400))
                    
                    self.rune_count += 1
                    self.status_signal.emit(f"Runes made: {self.rune_count} | Next cast in {self.timer_interval}s", "")
                    QThread.msleep(self.timer_interval * 1000)
                    continue

                # MP reading mode
                current_hp, current_max_hp, current_mp, current_max_mp = read_my_stats()
                
                # Check if MP reading is broken (all zeros or None)
                if current_mp is None or (current_hp == 0 and current_max_hp == 0 and current_mp == 0 and current_max_mp == 0):
                    if not self.diagnostic_shown:
                        self.status_signal.emit("MP reading failed! Enable Timer Mode or set p_mystats in Addresses.py", "color: red; font-weight: bold;")
                        self.diagnostic_shown = True
                    QThread.msleep(1000)
                    continue
                
                self.diagnostic_shown = False
                
                if current_mp >= self.mana_cost:
                    press_hotkey(int(self.hotkey[1:]))
                    QThread.msleep(random.randint(600, 800))
                    
                    if Addresses.hand_x != 0 and Addresses.charged_dest_x != 0:
                        mouse_function(Addresses.hand_x, Addresses.hand_y, Addresses.charged_dest_x, Addresses.charged_dest_y, option=4)
                        QThread.msleep(random.randint(300, 400))
                    
                    if Addresses.blank_rune_x != 0 and Addresses.hand_x != 0:
                        mouse_function(Addresses.blank_rune_x, Addresses.blank_rune_y, Addresses.hand_x, Addresses.hand_y, option=4)
                        QThread.msleep(random.randint(300, 400))
                    
                    self.rune_count += 1
                    self.status_signal.emit(f"Runes made: {self.rune_count} | Next cast when MP >= {self.mana_cost}", "")
                else:
                    self.status_signal.emit(f"Runes made: {self.rune_count} | MP: {current_mp}/{self.mana_cost} | Waiting...", "")
                
                QThread.msleep(random.randint(800, 1000))
            except Exception as e:
                self.status_signal.emit(f"Rune Maker error: {e}", "color: red; font-weight: bold;")
                QThread.msleep(1000)

    def stop(self):
        self.running = False


class RuneSetThread(QThread):
    status_signal = pyqtSignal(str, str)

    def __init__(self, coord_name, status_label):
        super().__init__()
        self.coord_name = coord_name
        self.status_label = status_label
        self.running = True

    def run(self):
        self.status_signal.emit(f"Hover and click LMB to set {self.coord_name}...", "color: blue; font-weight: bold;")
        while self.running:
            cur_x, cur_y = win32gui.ScreenToClient(Addresses.game, win32api.GetCursorPos())
            QThread.msleep(10)
            self.status_signal.emit(f"Current: X={cur_x}  Y={cur_y}  |  Click LMB for {self.coord_name}", "color: blue; font-weight: bold;")
            if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                if self.coord_name == "Hand":
                    Addresses.hand_x, Addresses.hand_y = cur_x, cur_y
                elif self.coord_name == "Charged Dest":
                    Addresses.charged_dest_x, Addresses.charged_dest_y = cur_x, cur_y
                elif self.coord_name == "Blank Rune":
                    Addresses.blank_rune_x, Addresses.blank_rune_y = cur_x, cur_y
                self.status_signal.emit(f"{self.coord_name} set at X={cur_x}, Y={cur_y}", "color: green; font-weight: bold;")
                self.running = False
                return


class SetFoodThread(QThread):
    status_signal = pyqtSignal(str, str)

    def __init__(self, status_label):
        super().__init__()
        self.status_label = status_label
        self.running = True

    def run(self):
        self.status_signal.emit("Hover and click LMB to set Food coordinate...", "color: blue; font-weight: bold;")
        while self.running:
            cur_x, cur_y = win32gui.ScreenToClient(Addresses.game, win32api.GetCursorPos())
            QThread.msleep(10)
            self.status_signal.emit(f"Current: X={cur_x}  Y={cur_y}  |  Click LMB for Food", "color: blue; font-weight: bold;")
            if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                Addresses.food_x, Addresses.food_y = cur_x, cur_y
                self.status_signal.emit(f"Food set at X={cur_x}, Y={cur_y}", "color: green; font-weight: bold;")
                self.running = False
                return


class FoodEaterThread(QThread):
    status_signal = pyqtSignal(str, str)

    def __init__(self, interval_seconds):
        super().__init__()
        self.interval = interval_seconds
        self.running = True
        self.food_count = 0

    def run(self):
        while self.running:
            try:
                if Addresses.food_x != 0:
                    mouse_function(Addresses.food_x, Addresses.food_y, option=1)
                    self.food_count += 1
                    self.status_signal.emit(f"Ate food {self.food_count} times | Next in {self.interval}s", "")
                else:
                    self.status_signal.emit("Food coordinate not set! Click 'Set Food' first.", "color: red; font-weight: bold;")
                QThread.msleep(self.interval * 1000)
            except Exception as e:
                print(f"FoodEaterThread error: {e}")
                QThread.msleep(1000)

    def stop(self):
        self.running = False


class BatchAddWaterThread(QThread):
    status_signal = pyqtSignal(str, str)

    def __init__(self, status_label, min_distance=30, max_spots=50):
        super().__init__()
        self.status_label = status_label
        self.running = True
        self.min_distance = min_distance
        self.max_spots = max_spots

    def run(self):
        try:
            # Wait for the button click to be released
            timeout = 0
            while self.running and (win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000) and timeout < 500:
                QThread.msleep(10)
                timeout += 10
            if not self.running:
                return

            start_count = len(Addresses.fishing_water_spots)
            self.status_signal.emit(f"Batch Add: Click/drag LMB on water squares. Click again to finish. (Current: {start_count})", "color: blue; font-weight: bold;")
            
            while self.running:
                if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                    cur_x, cur_y = win32gui.ScreenToClient(Addresses.game, win32api.GetCursorPos())
                    
                    # Check if too close to any existing spot (same square)
                    too_close = False
                    for x, y in Addresses.fishing_water_spots:
                        if abs(x - cur_x) < self.min_distance and abs(y - cur_y) < self.min_distance:
                            too_close = True
                            break
                    
                    if not too_close:
                        if len(Addresses.fishing_water_spots) >= self.max_spots:
                            self.status_signal.emit(f"Max {self.max_spots} spots reached!", "color: orange; font-weight: bold;")
                            self.running = False
                            return
                        Addresses.fishing_water_spots.append((cur_x, cur_y))
                        self.status_signal.emit(f"Added spot {len(Addresses.fishing_water_spots)}! Keep clicking/dragging...", "color: green; font-weight: bold;")
                    else:
                        self.status_signal.emit(f"Too close to existing spot. Skipped. ({len(Addresses.fishing_water_spots)} total)", "color: orange; font-weight: bold;")
                    
                    QThread.msleep(300)  # Debounce so we don't add duplicates while holding LMB
                QThread.msleep(50)
        except Exception as e:
            print(f"BatchAddWaterThread error: {e}")
            self.status_signal.emit(f"Error: {e}", "color: red; font-weight: bold;")

    def stop(self):
        self.running = False
