import random
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QListWidgetItem

import Addresses
from Addresses import walker_Lock, coordinates_x, coordinates_y, attack_Lock
from Functions.MemoryFunctions import *
from Functions.KeyboardFunctions import walk
from Functions.MouseFunctions import mouse_function
from Functions.PathfindingFunctions import expand_waypoints, calculate_path_astar


class WalkerThread(QThread):
    index_update = pyqtSignal(int, object)

    def __init__(self, waypoints):
        super().__init__()
        self.last_target_pos = None
        self.waypoints = waypoints
        self.running = True

    def run(self):
        if not self.waypoints:
            return
        current_wpt = self.find_wpt(self.waypoints)
        timer = 0
        second_timer = 0
        self.discovered_obstacles = set()
        self.last_target_pos = None
        my_x, my_y, my_z = read_my_wpt()
        previous_pos = (my_x, my_y, my_z)
        while self.running:
            try:
                sleep_value = random.randint(10, 50)
                QThread.msleep(sleep_value)
                if not walker_Lock.locked():
                    timer += sleep_value
                    second_timer += (sleep_value / 1000)
                if (timer / 1000) >= 5: # 5 Second no wpt
                    current_wpt = self.find_wpt(self.waypoints)
                    self.discovered_obstacles.clear()
                    timer = 0
                    second_timer = 0
                self.index_update.emit(0, current_wpt)
                wpt_data = self.waypoints[current_wpt]
                wpt_action = wpt_data['Action']
                wpt_direction = wpt_data['Direction']
                map_x = wpt_data['X']
                map_y = wpt_data['Y']
                map_z = wpt_data['Z']
                my_x, my_y, my_z = read_my_wpt()
                if my_x == map_x  and my_y == map_y and my_z == map_z:
                    current_wpt = (current_wpt + 1) % len(self.waypoints)
                    self.discovered_obstacles.clear()
                    timer = 0
                    continue
                while walker_Lock.locked() and wpt_action != 4 and self.running: # If attacking and not Luring
                    QThread.msleep(200)
                
                if not self.running: break

                if wpt_action == 0:
                    if wpt_direction == 0:
                        path = calculate_path_astar(my_x, my_y, map_x, map_y, self.discovered_obstacles)
                        if path:
                            next_step = path[0]
                            self.last_target_pos = (my_x + next_step[0], my_y + next_step[1])
                            walk(0, my_x, my_y, my_z, my_x + next_step[0], my_y + next_step[1], map_z)
                    else:
                        walk(wpt_direction, my_x, my_y, my_z, map_x, map_y, map_z)
                elif wpt_action == 1: # Rope
                    QThread.msleep(random.randint(500, 600))
                    mouse_function(coordinates_x[10], coordinates_y[10], option=1)
                    QThread.msleep(random.randint(100, 200))
                    my_x, my_y, my_z = read_my_wpt()
                    map_x = wpt_data['X']
                    map_y = wpt_data['Y']
                    mouse_function(coordinates_x[0] + (map_x - my_x) * Addresses.square_size, coordinates_y[0] + (map_y - my_y) * Addresses.square_size, option=2)
                    current_wpt = (current_wpt + 1) % len(self.waypoints)
                elif wpt_action == 2: # Shovel
                    QThread.msleep(random.randint(500, 600))
                    mouse_function(coordinates_x[9], coordinates_y[9], option=1)
                    QThread.msleep(random.randint(100, 200))
                    my_x, my_y, my_z = read_my_wpt()
                    map_x = wpt_data['X']
                    map_y = wpt_data['Y']
                    mouse_function(coordinates_x[0] + (map_x - my_x) * Addresses.square_size,
                        coordinates_y[0] + (map_y - my_y) * Addresses.square_size,
                                   option=2)
                    current_wpt = (current_wpt + 1) % len(self.waypoints)
                elif wpt_action == 3: # Ladder
                    QThread.msleep(random.randint(500, 600))
                    mouse_function(coordinates_x[0], coordinates_y[0], option=1)
                    current_wpt = (current_wpt + 1) % len(self.waypoints)
                elif wpt_action == 4:  # Lure
                    if wpt_direction == 0:
                        path = calculate_path_astar(my_x, my_y, map_x, map_y, self.discovered_obstacles)
                        if path:
                            next_step = path[0]
                            self.last_target_pos = (my_x + next_step[0], my_y + next_step[1])
                            walk(0, my_x, my_y, my_z, my_x + next_step[0], my_y + next_step[1], map_z)
                    else:
                         walk(wpt_direction, my_x, my_y, my_z, map_x, map_y, map_z)
                if (my_x, my_y, my_z) == previous_pos:
                    if not walker_Lock.locked():
                        second_timer += (sleep_value / 1000)
                else:
                    previous_pos = (my_x, my_y, my_z)
                    second_timer = 0
                if second_timer > 3:
                    if self.last_target_pos:
                        self.discovered_obstacles.add(self.last_target_pos)
                        self.last_target_pos = None
                    
            except Exception as e:
                print("WalkerThread error:", e)

    def stop(self):
        self.running = False

    def find_wpt(self, waypoints):
        x, y, z = read_my_wpt()
        for wpt in range(0, len(waypoints)):
            wpt_data = waypoints[wpt]
            map_z = wpt_data['Z']
            map_x = wpt_data['X']
            map_y = wpt_data['Y']
            wpt_direction = wpt_data['Direction']
            if z == map_z and abs(map_x - x) <= 4 and abs(map_y - y) <= 4 and wpt_direction == 0:
                return wpt
        return 0


class RecordThread(QThread):
    request_data_signal = pyqtSignal()
    wpt_recorded_signal = pyqtSignal(dict)

    def __init__(self, interval=1):
        super().__init__()
        self.running = True
        self.interval = interval
        self.current_action_id = 0
        self.current_direction_id = 0
        self.current_direction_text = "Center"
        self.data_lock = QMutex()

    def update_snapshot(self, action_id, direction_id, direction_text):
        with QMutexLocker(self.data_lock):
            self.current_action_id = action_id
            self.current_direction_id = direction_id
            self.current_direction_text = direction_text

    def run(self):
        x, y, z = read_my_wpt()
        
        with QMutexLocker(self.data_lock):
            act_id = self.current_action_id
            dir_id = self.current_direction_id
            dir_text = self.current_direction_text

        waypoint_data = {
            "Action": act_id,
            "Direction": dir_id,
            "X": x, "Y": y, "Z": z,
            "Display": dir_text
        }
        self.wpt_recorded_signal.emit(waypoint_data)
        
        last_recorded_x, last_recorded_y, last_recorded_z = x, y, z
        old_x, old_y, old_z = x, y, z

        while self.running:
            try:
                x, y, z = read_my_wpt()
                if z != old_z:  # Stair, hole, etc.
                    # Determine direction based on movement
                    new_dir_id = 0
                    new_dir_text = "Center"
                    if y > old_y and x == old_x: new_dir_id, new_dir_text = 2, "South"
                    elif y < old_y and x == old_x: new_dir_id, new_dir_text = 1, "North"
                    elif y == old_y and x > old_x: new_dir_id, new_dir_text = 3, "East"
                    elif y == old_y and x < old_x: new_dir_id, new_dir_text = 4, "West"

                    if new_dir_id != 0:
                        self.wpt_recorded_signal.emit({
                            "Action": 0, "Direction": new_dir_id,
                            "X": x, "Y": y, "Z": z,
                            "Display": new_dir_text
                        })

                if (x != old_x or y != old_y) and z == old_z:
                    dist = abs(x - last_recorded_x) + abs(y - last_recorded_y)
                    if dist >= self.interval:
                        with QMutexLocker(self.data_lock):
                            act_id = self.current_action_id
                            dir_id = self.current_direction_id
                            dir_text = self.current_direction_text

                        self.wpt_recorded_signal.emit({
                            "Action": act_id, "Direction": dir_id,
                            "X": x, "Y": y, "Z": z,
                            "Display": dir_text
                        })
                        last_recorded_x, last_recorded_y, last_recorded_z = x, y, z
                
                old_x, old_y, old_z = x, y, z
                QThread.msleep(100)
            except Exception as e:
                print("RecordThread error:", e)

    def stop(self):
        self.running = False

