import ctypes as c
import os
import threading
import win32gui
import win32process
import pytesseract

from Functions.MemoryFunctions import enable_debug_privilege_pywin32
TITLE_BAR_OFFSET = 35
# Locks
walker_Lock = threading.Lock()
attack_Lock = threading.Lock()

enable_debug_privilege_pywin32()
# Keystrokes codes
lParam = [
    0X00480001, 0x00500001, 0X004D0001,  # 8, 2, 6
    0X004B0001, 0X00490001, 0X00470001,  # 4, 9, 7
    0X00510001, 0X004F0001  # 3, 1
]
rParam = [
    0X26, 0x28, 0X27,  # 8, 2, 6
    0x25, 0x21, 0x24,  # 4, 9, 7
    0x22, 0x23  # 3, 1
]


my_y_address = None
my_y_address_offset = None
my_y_type = 3

my_z_address = None
my_z_address_offset = None
my_z_type = 2

my_stats_address = None

my_hp_offset = None
my_hp_max_offset = None
my_hp_type = 2

my_mp_offset = None
my_mp_max_offset = None
my_mp_type = 2


# Target Addresses
attack_address = None
attack_address_offset = None
my_attack_type = 3

target_x_offset = None
target_x_type = 3

target_y_offset = None
target_y_type = 3

target_z_offset = None
target_z_type = 2

target_hp_offset = None
target_hp_type = 1

target_name_offset = None
target_name_type = 6


# Game Variables
game_name = None
game = None
base_address = None
process_handle = None
proc_id = None
client_name = None
square_size = 75
application_architecture = 32
collect_threshold = 0.85

# Coordinates
screen_x = [0] * 1
screen_y = [0] * 1
battle_x = [0] * 1
battle_y = [0] * 1
screen_width = [0] * 2
screen_height = [0] * 2
coordinates_x = [0] * 12
coordinates_y = [0] * 12

fishing_x = [0] * 4
fishing_y = [0] * 4

# Rune Maker coordinates
hand_x = 0
hand_y = 0
charged_dest_x = 0
charged_dest_y = 0
blank_rune_x = 0
blank_rune_y = 0

# Food eater coordinates
food_x = 0
food_y = 0

# List of (x, y) tuples for multiple water fishing spots
fishing_water_spots = []

# Other Variables
item_list = {}


# Your OTS Client
def load_tibia(window_title=None, proc_id=None, hwnd=None) -> None:
    global my_x_address, my_x_address_offset, my_y_address, my_y_address_offset, my_z_address, my_z_address_offset,\
        my_stats_address, my_hp_offset, my_hp_max_offset, my_mp_offset, my_mp_max_offset, \
        attack_address, attack_address_offset, target_name_offset, target_x_offset, target_y_offset, target_z_offset, target_hp_offset, \
        client_name, base_address, game, process_handle, game_name, \
        square_size, application_architecture, collect_threshold

    # Game variables
    square_size = 75 # In pixels
    application_architecture = 32 # If game 64 - 64Bit 32 - 32 Bit
    collect_threshold = 0.95

    # Default Values
    my_x_address = None
    my_stats_address = None
    attack_address = None
    
    my_x_address_offset = []
    my_y_address_offset = []
    my_z_address_offset = []
    my_hp_offset = []
    my_hp_max_offset = []
    my_mp_offset = []
    my_mp_max_offset = []
    attack_address_offset = []

    load_custom_addresses()

    # Target Addresses
    target_x_offset = None
    target_y_offset = None
    target_z_offset = None
    target_hp_offset = None
    target_name_offset = None

    # Game 'n' Client names
    if window_title and proc_id and hwnd:
        # Use provided process info
        game_name = window_title
        game = hwnd
        # proc_id is already set from parameter
        
        # Extract client name from window title (take first word or up to first space/parenthesis)
        client_name = window_title.split()[0] if window_title else "Client"
    else:
        # Fallback to old method (hardcoded)
        client_name = ""
        game_name = fin_window_name(client_name)
        game = win32gui.FindWindow(None, game_name)
        thread_id, proc_id = win32process.GetWindowThreadProcessId(game)
    
    os.makedirs("Images/" + client_name, exist_ok=True)
    print(f"Connected to: {game_name}")

    # Loading Addresses
    process_handle = c.windll.kernel32.OpenProcess(0x1F0FFF, False, proc_id)
    modules = win32process.EnumProcessModules(process_handle)
    base_address = modules[0]


def load_custom_addresses():
    global my_x_address, my_x_address_offset, my_y_address, my_y_address_offset, my_z_address, my_z_address_offset,\
        my_stats_address, my_hp_offset, my_hp_max_offset, my_mp_offset, my_mp_max_offset, \
        attack_address, attack_address_offset, my_attack_type, my_x_type, my_y_type, my_z_type, my_hp_type, my_mp_type, \
        target_x_offset, target_y_offset, target_z_offset, target_hp_offset, target_name_offset, \
        square_size, application_architecture, collect_threshold

    try:
        with open("Save/Settings/addresses.json", "r") as f:
            import json
            data = json.load(f)
            
            # Load Game Config
            config = data.get("game_config", {})
            if "square_size" in config and config["square_size"]:
                square_size = int(config["square_size"])
            if "collect_threshold" in config and config["collect_threshold"]:
                collect_threshold = float(config["collect_threshold"])
            if "architecture" in config:
                arch_str = config["architecture"]
                if "64" in arch_str:
                    application_architecture = 64
                else:
                    application_architecture = 32

            # Map JSON keys to global variables
            mappings = [
                ("my_x", "my_x_address", "my_x_address_offset", "my_x_type"),
                ("my_y", "my_y_address", "my_y_address_offset", "my_y_type"),
                ("my_z", "my_z_address", "my_z_address_offset", "my_z_type"),
                ("attack", "attack_address", "attack_address_offset", "my_attack_type"),
                ("my_hp", "my_stats_address", "my_hp_offset", "my_hp_type"),
                ("my_hp_max", None, "my_hp_max_offset", None),
                ("my_mp", None, "my_mp_offset", "my_mp_type"),
                ("my_mp_max", None, "my_mp_max_offset", None),
                # Target Offsets
                ("target_x", None, "target_x_offset", "target_x_type"),
                ("target_y", None, "target_y_offset", "target_y_type"),
                ("target_z", None, "target_z_offset", "target_z_type"),
                ("target_hp", None, "target_hp_offset", "target_hp_type"),
                ("target_name", None, "target_name_offset", "target_name_type"),
            ]
            
            type_map = {"Byte": 1, "Short": 2, "Int": 3, "Long": 4, "Double": 5, "String": 6, "Unicode String": 7}

            for key, addr_var, offset_var, type_var in mappings:
                if key in data:
                    entry = data[key]
                    
                    # Set Address
                    if addr_var:
                        val = parse_hex(entry.get("address"))
                        if val is not None:
                            globals()[addr_var] = val
                    
                    # Set Offset
                    if offset_var:
                        raw_offset = entry.get("offset", "")
                        parsed_offsets = parse_offsets(raw_offset)
                        
                        if parsed_offsets:
                            if key.startswith("target_"):
                                globals()[offset_var] = parsed_offsets[0]
                            else:
                                globals()[offset_var] = parsed_offsets
                        elif raw_offset.strip() == "" and not key.startswith("target_"):
                             globals()[offset_var] = []

                    # Set Type
                    if type_var:
                        type_str = entry.get("type")
                        if type_str in type_map:
                            globals()[type_var] = type_map[type_str]

            print("Loaded dynamic addresses")
    except Exception as e:
        print(f"Using default addresses. Error loading dynamic: {e}")

# Helper to parse hex string
def parse_hex(val):
    if isinstance(val, str) and val.strip():
        try:
            return int(val.strip(), 16)
        except ValueError:
            pass
    return None

# Helper to parse offsets
def parse_offsets(val):
    if isinstance(val, str) and val.strip():
        try:
            return [int(x.strip(), 16) for x in val.split(',') if x.strip()]
        except ValueError:
            pass
    return []


def fin_window_name(name) -> str:
    matching_titles = []

    def enum_window_callback(hwnd, _):
        window_text = win32gui.GetWindowText(hwnd)
        if name in window_text and "Easy Bot" not in window_text:
            matching_titles.append(window_text)

    win32gui.EnumWindows(enum_window_callback, None)
    return matching_titles[0]


# User Interface
dark_theme = """
    QWidget {
        background-color: #2e2e2e;
        color: #ffffff;
    }

    QMainWindow {
        background-color: #2e2e2e;
    }

    QPushButton {
        background-color: #444444;
        border: 1px solid #5e5e5e;
        color: #ffffff;
        padding: 5px;
        border-radius: 5px;
    }

    QPushButton:hover {
        background-color: #555555;
    }

    QPushButton:pressed {
        background-color: #666666;
    }

    QLineEdit, QTextEdit {
        background-color: #3e3e3e;
        border: 1px solid #5e5e5e;
        color: #ffffff;
    }

    QLabel {
        color: #ffffff;
    }

    QMenuBar {
        background-color: #3e3e3e;
    }

    QMenuBar::item {
        background-color: #3e3e3e;
        color: #ffffff;
    }

    QMenuBar::item:selected {
        background-color: #555555;
    }

    QMenu {
        background-color: #3e3e3e;
        color: #ffffff;
    }

    QMenu::item:selected {
        background-color: #555555;
    }

    QScrollBar:vertical {
        background-color: #2e2e2e;
        width: 12px;
    }

    QScrollBar::handle:vertical {
        background-color: #666666;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #888888;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background-color: #2e2e2e;
    }
"""