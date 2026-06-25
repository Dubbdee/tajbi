from PyQt5.QtWidgets import QApplication
import pytesseract
import Addresses
import os
import sys

# Set Tesseract Path - Intelligent discovery for EXE bundling
if getattr(sys, 'frozen', False):
    # If running from EXE, Tesseract will be in the internal _MEIPASS folder
    tesseract_path = os.path.join(sys._MEIPASS, 'Tesseract-OCR', 'tesseract.exe')
else:
    # If running from source, use the local installation
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pytesseract.pytesseract.tesseract_cmd = tesseract_path

from General.SelectTibiaTab import SelectTibiaTab


def main():
    # Make directories
    os.makedirs("Images", exist_ok=True)
    os.makedirs("Save", exist_ok=True)
    os.makedirs("Save/Targeting", exist_ok=True)
    os.makedirs("Save/Settings", exist_ok=True)
    os.makedirs("Save/Waypoints", exist_ok=True)
    os.makedirs("Save/HealingAttack", exist_ok=True)
    os.makedirs("Save/SmartHotkeys", exist_ok=True)
    os.makedirs("Save/Hotkeys", exist_ok=True)
    os.makedirs("Save/Training", exist_ok=True)
    app = QApplication([])
    app.setStyle('Fusion')
    app.setStyleSheet(Addresses.dark_theme)
    
    login_window = SelectTibiaTab()
    login_window.show()

    app.exec()


if __name__ == '__main__':
    main()