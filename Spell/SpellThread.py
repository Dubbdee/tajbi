import random
from PyQt5.QtCore import QThread, Qt

from Addresses import coordinates_x, coordinates_y
from Functions.KeyboardFunctions import press_hotkey
from Functions.MemoryFunctions import *
from Functions.MouseFunctions import mouse_function
from Addresses import attack_Lock


def attack_monster(attack_data) -> bool:
    target_x, target_y, target_z, target_name, target_hp = read_target_info()
    current_hp, current_max_hp, current_mp, current_max_mp = read_my_stats()
    if target_hp is None or target_hp < 0 or target_hp > 100:
        target_hp = 100
    hp_percentage = (current_hp * 100) / current_max_hp
    hp_from = int(attack_data['HpFrom'])
    hp_to = int(attack_data['HpTo'])
    min_mp = int(attack_data['MinMp'])
    if attack_data['Name'] == "*":
        target_name = "*"
    current_name = attack_data['Name']
    min_hp = int(attack_data['MinHp'])
    min_dist = int(attack_data.get('MinDist', 0))
    
    # Check distance if min_dist is set
    if min_dist != 0:
        x, y, z = read_my_wpt()
        dist_x = abs(x - target_x)
        dist_y = abs(y - target_y)
        # Only cast spell if target is within the specified distance
        if not (min_dist >= dist_x and min_dist >= dist_y):
            return False
    
    if (hp_from >= target_hp > hp_to) and current_mp >= min_mp and (target_name in target_name) and min_hp <= hp_percentage:
        return True
    return False


class SpellThread(QThread):

    def __init__(self, spell_data_list):
        super().__init__()
        self.spell_data_list = spell_data_list
        self.running = True

    def run(self):
        while self.running:
            try:
                if not attack_Lock.locked():
                    for spell_data in self.spell_data_list:
                        if not self.running: break
                        if read_targeting_status() != 0:
                            if attack_monster(spell_data):
                                
                                if spell_data['Key'][0] == 'F':
                                    press_hotkey(int(spell_data['Key'][1:]))
                                    QThread.msleep(random.randint(150, 250))
                                else:
                                    if spell_data['Key'] == 'First Rune':
                                        mouse_function(coordinates_x[6],
                                                    coordinates_y[6],
                                                       option=1)
                                    elif spell_data['Key'] == 'Second Rune':
                                        mouse_function(coordinates_x[8],
                                                    coordinates_y[8],
                                                       option=1)
                                    x, y, z = read_my_wpt()
                                    target_x, target_y, target_z, target_name, target_hp = read_target_info()
                                    x = target_x - x
                                    y = target_y - y
                                    mouse_function(coordinates_x[0] + x * Addresses.square_size, coordinates_y[0] + y * Addresses.square_size, option=2)
                                    QThread.msleep(random.randint(800, 1000))
                    QThread.msleep(random.randint(100, 200))
            except Exception as e:
                print(e)

    def stop(self):
        self.running = False

