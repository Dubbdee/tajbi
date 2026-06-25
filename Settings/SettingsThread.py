import win32api
import win32gui
from PyQt5.QtCore import QThread, pyqtSignal
from win32con import VK_LBUTTON

import Addresses
from Addresses import coordinates_x, coordinates_y, screen_x, screen_y, screen_width, screen_height, battle_x, battle_y


class SettingsThread(QThread):
    # Signals for overlay control (thread-safe)
    show_overlay = pyqtSignal()
    update_overlay = pyqtSignal(int, int, int, int)  # start_x, start_y, end_x, end_y
    hide_overlay = pyqtSignal()

    def __init__(self, index, status_label):
        super().__init__()
        self.index = index
        self.status_label = status_label
        self.running = True

    def run(self):
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        
        if self.index >= 0:
            # Single point selection for tools/coordinates
            while self.running:
                cur_x, cur_y = win32gui.ScreenToClient(Addresses.game, win32api.GetCursorPos())
                QThread.msleep(10)
                self.status_label.setText(
                    f"Current: X={cur_x}  Y={cur_y}"
                )
                if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                    coordinates_x[self.index], coordinates_y[self.index] = cur_x, cur_y
                    self.status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.status_label.setText(f"Coordinates set at X={coordinates_x[self.index]}, Y={coordinates_y[self.index]}")
                    self.running = False
                    return
        
        else:
            # Drag selection for Loot Area (-1) and Battle List (-2) with visual overlay
            start_x, start_y = None, None
            dragging = False
            
            while self.running:
                cur_pos = win32api.GetCursorPos()
                cur_x, cur_y = win32gui.ScreenToClient(Addresses.game, cur_pos)
                screen_cur_x, screen_cur_y = cur_pos  # Screen coordinates for overlay
                is_pressed = win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000
                
                if is_pressed and not dragging:
                    # Start dragging
                    start_x, start_y = cur_x, cur_y
                    self.screen_start_x, self.screen_start_y = screen_cur_x, screen_cur_y
                    dragging = True
                    self.show_overlay.emit()
                    self.status_label.setText(f"Drag started at X={start_x}, Y={start_y}")
                
                elif is_pressed and dragging:
                    # Currently dragging - update overlay via signal
                    self.update_overlay.emit(
                        self.screen_start_x, 
                        self.screen_start_y, 
                        screen_cur_x, 
                        screen_cur_y
                    )
                    self.status_label.setText(
                        f"Dragging... From ({start_x},{start_y}) to ({cur_x},{cur_y})"
                    )
                
                elif not is_pressed and dragging:
                    # Finished dragging
                    self.hide_overlay.emit()
                    
                    if self.index == -1:
                        # Loot Area
                        screen_x[0] = min(start_x, cur_x)
                        screen_y[0] = min(start_y, cur_y)
                        screen_width[0] = max(start_x, cur_x)
                        screen_height[0] = max(start_y, cur_y)
                        self.status_label.setStyleSheet("color: green; font-weight: bold;")
                        self.status_label.setText(
                            f"Loot area set: ({screen_x[0]},{screen_y[0]}) to ({screen_width[0]},{screen_height[0]})"
                        )
                    else:  # index == -2
                        # Battle List
                        battle_x[0] = min(start_x, cur_x)
                        battle_y[0] = min(start_y, cur_y)
                        screen_width[1] = max(start_x, cur_x)
                        screen_height[1] = max(start_y, cur_y)
                        self.status_label.setStyleSheet("color: green; font-weight: bold;")
                        self.status_label.setText(
                            f"Battle List set: ({battle_x[0]},{battle_y[0]}) to ({screen_width[1]},{screen_height[1]})"
                        )
                    
                    self.running = False
                    return
                
                elif not dragging:
                    # Waiting for user to start dragging
                    self.status_label.setText(f"Click and drag to select area. Current: X={cur_x}, Y={cur_y}")
                
                QThread.msleep(10)
            
            # Cleanup - hide overlay if thread is stopped
            self.hide_overlay.emit()

