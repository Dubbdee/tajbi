import random
import os
import win32gui

import numpy as np
from PyQt5.QtCore import QThread, QMutex, QMutexLocker
from PyQt5.QtWidgets import QLabel, QComboBox

import Addresses
from Addresses import coordinates_x, coordinates_y, screen_width, screen_height, screen_x, screen_y, walker_Lock
from Functions.GeneralFunctions import WindowCapture, merge_close_points
from Functions.MouseFunctions import manage_collect, mouse_function
import cv2 as cv


class LootThread(QThread):

    def __init__(self, loot_data, target_state, one_shot=False):
        super().__init__()
        self.loot_data = loot_data
        self.running = True
        self.target_state = target_state
        self.state_lock = QMutex()
        self.item_templates = {}
        self.one_shot = one_shot

    def run(self):
        self.prepare_templates()

        # Calculate capture area
        w = screen_width[0] - screen_x[0]
        h = screen_height[0] - screen_y[0]
        x = screen_x[0]
        y = screen_y[0] + Addresses.TITLE_BAR_OFFSET

        # Fallback if dimensions are invalid (e.g. loot area not set)
        if w <= 0 or h <= 0:
            try:
                if Addresses.game:
                    rect = win32gui.GetClientRect(Addresses.game)
                    w = rect[2]
                    h = rect[3]
                    # Default to client area offsets if not set
                    if x == 0: x = 0 # Assuming 0 is fine for left border or handled by offset
                    if y == Addresses.TITLE_BAR_OFFSET: y = Addresses.TITLE_BAR_OFFSET # Keep default offset
            except Exception as e:
                print(f"Error calculating fallback dimensions: {e}")

        capture_screen = WindowCapture(w, h, x, y)

        # If one_shot, we don't loop continuously
        if self.one_shot:
            for _ in range(2):
                self.process_looting(capture_screen)
        else:
            while self.running:
                try:
                    self.process_looting(capture_screen)
                except Exception as e:
                    print(f"Looting error: {e}")

    def process_looting(self, capture_screen):
        resize_factor = 3
        for image_path, data in self.item_templates.items():
            if not self.running:
                break
        
            action = data['action']
            templates = data['templates']
            screenshot = capture_screen.get_screenshot()
            screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
            screenshot = cv.GaussianBlur(screenshot, (7, 7), 0)
            screenshot = cv.resize(screenshot, None, fx=resize_factor, fy=resize_factor, interpolation=cv.INTER_CUBIC)
            for template in templates:
                if not self.running:
                    break
                result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
                locations = np.where(result >= Addresses.collect_threshold)
                all_locations = []
                for pt in zip(*locations[::-1]):
                    x = int(pt[0])
                    y = int(pt[1])
                    all_locations.append((x, y))
                if all_locations:
                    all_locations = merge_close_points(all_locations, 30)
                    all_locations = sorted(all_locations, key=lambda point: (point[1], point[0]))
                    for lx,ly in all_locations:
                        lx_scaled = lx / resize_factor
                        ly_scaled = ly / resize_factor
                        self.perform_action(lx_scaled, ly_scaled, action, data.get('use_ctrl', False))
        
    def prepare_templates(self):
        resize_factor = 3
        """Load and prepare all item templates"""
        self.item_templates.clear()
        for entry in self.loot_data:
            image_path = entry.get("ImagePath")
            if image_path and os.path.exists(image_path):
                action = entry.get("Action", "RightClick")
                use_ctrl = entry.get("UseCtrl", False)

                templates_list = []
                if image_path.lower().endswith('.gif'):
                    try:
                        from PIL import Image, ImageSequence
                        import numpy as np

                        gif = Image.open(image_path)

                        for frame in ImageSequence.Iterator(gif):
                            frame = np.array(frame.convert('RGB'))
                            frame = frame[:22, :]
                            opencv_image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                            item = cv.GaussianBlur(opencv_image, (7, 7), 0)
                            item = cv.resize(item, None, fx=resize_factor, fy=resize_factor,interpolation=cv.INTER_CUBIC)
                            templates_list.append(item)

                    except Exception as e:
                        print(f"Error loading GIF template: {e}")
                        continue
                else:
                    template = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
                    if template is not None:
                        template = template[:22, :]
                        item = cv.GaussianBlur(template, (7, 7), 0)
                        item = cv.resize(item, None, fx=resize_factor, fy=resize_factor, interpolation=cv.INTER_CUBIC)
                        templates_list.append(item)

                if templates_list:
                    self.item_templates[image_path] = {
                        'action': action,
                        'templates': templates_list,
                        'use_ctrl': use_ctrl
                    }


    def perform_action(self, x, y, action, use_ctrl=False):
        """Perform the specified action at the given coordinates"""
        import win32api, win32con
        VK_CONTROL = 0x11
        
        abs_x = int(screen_x[0] + x)
        abs_y = int(screen_y[0] + Addresses.TITLE_BAR_OFFSET/2 + y)
        
        if use_ctrl:
            win32api.keybd_event(VK_CONTROL, 0, 0, 0) # Press CTRL

        try:
            if action == "RightClick":
                mouse_function(abs_x, abs_y, option=1)
            elif action == "LeftClick":
                mouse_function(abs_x, abs_y, option=2)
            elif action == "DoubleLeftClick":
                mouse_function(abs_x, abs_y, option=2)
                mouse_function(abs_x, abs_y, option=2)
            elif action.endswith("Container"):
                container_num = int(action.split()[0])
                manage_collect(abs_x, abs_y, container_num)
        finally:
            if use_ctrl:
                win32api.keybd_event(VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0) # Release CTRL

    def update_states(self, state):
        """Thread-safe method to update target state."""
        with QMutexLocker(self.state_lock):
            self.target_state = state

    def stop(self):
        self.running = False
