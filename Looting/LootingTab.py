import os
import json
from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QPushButton, QLabel, QGridLayout,
    QGroupBox, QVBoxLayout, QComboBox, QHeaderView, QFileDialog, QHBoxLayout, QCheckBox
)
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtCore import Qt, QSize
from PIL import Image, ImageSequence
import Addresses

from Looting.LootingThread import LootThread


class LootingTab(QWidget):
    def __init__(self):
        super().__init__()

        # Thread Variables
        self.loot_thread = None
        
        # State Variables
        self.looting_enabled = False

        # Load Icon
        self.setWindowIcon(QIcon('Images/Icon.jpg'))

        # Set Title and Size
        self.setWindowTitle("Looting")
        self.setFixedSize(400, 400)

        # --- Status label at the bottom
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        # Main Layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Table Widget with 3 columns: ItemImage, Action, CTRL
        self.loot_tableWidget = QTableWidget(self)
        self.loot_tableWidget.setColumnCount(3)
        self.loot_tableWidget.setHorizontalHeaderLabels(["Item Image", "Action", "CTRL"])
        
        # Configure table
        header = self.loot_tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        # Buttons
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_item)
        
        self.remove_button = QPushButton("Remove", self)
        self.remove_button.clicked.connect(self.remove_item)

        # Layout Arrangement
        self.layout.addWidget(self.loot_tableWidget, 0, 0, 1, 2)
        self.layout.addWidget(self.add_button, 1, 0)
        self.layout.addWidget(self.remove_button, 1, 1)
        self.layout.addWidget(self.status_label, 2, 0, 1, 2)

    def add_item(self):
        """Add a new editable row to the table"""
        row_position = self.loot_tableWidget.rowCount()
        self.loot_tableWidget.insertRow(row_position)
        
        # Column 0: Image selector + preview
        image_widget = QWidget()
        image_layout = QHBoxLayout(image_widget)
        image_layout.setContentsMargins(5, 5, 5, 5)
        
        # Preview label
        preview_label = QLabel()
        preview_label.setMinimumSize(50, 50)
        preview_label.setMaximumSize(50, 50)
        preview_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        preview_label.setText("No Image")
        preview_label.setAlignment(Qt.AlignCenter)
        
        # Select button
        select_button = QPushButton("Select Image")
        select_button.clicked.connect(lambda: self.select_image(row_position, preview_label))
        
        image_layout.addWidget(preview_label)
        image_layout.addWidget(select_button)
        
        self.loot_tableWidget.setCellWidget(row_position, 0, image_widget)
        
        # Column 1: Action ComboBox
        action_combo = QComboBox()
        action_combo.addItems([
            "RightClick",
            "LeftClick", 
            "DoubleLeftClick",
            "1 Container",
            "2 Container",
            "3 Container",
            "4 Container"
        ])
        self.loot_tableWidget.setCellWidget(row_position, 1, action_combo)

        # Column 2: CTRL Checkbox
        ctrl_widget = QWidget()
        ctrl_layout = QHBoxLayout(ctrl_widget)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        ctrl_layout.setAlignment(Qt.AlignCenter)
        ctrl_checkbox = QCheckBox()
        ctrl_layout.addWidget(ctrl_checkbox)
        self.loot_tableWidget.setCellWidget(row_position, 2, ctrl_widget)
        
        # Set row height to accommodate the image
        self.loot_tableWidget.setRowHeight(row_position, 60)
        
        self.status_label.setText("")

    def process_image_remove_white_bg(self, input_path):
        """
        Process image/GIF to remove white background and composite onto game background.
        Returns path to processed file.
        """
        try:
            # Create processed directory
            client_name = Addresses.client_name or "default"
            processed_dir = f"Images/{client_name}/processed"
            os.makedirs(processed_dir, exist_ok=True)
            
            # Get background image path
            bg_path = f"Images/{client_name}/background.png"
            if not os.path.exists(bg_path):
                # If background doesn't exist, just return original
                self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                self.status_label.setText(f"Warning: background.png not found, using original image")
                return input_path
            
            # Load background
            background = Image.open(bg_path).convert("RGBA")
            
            # Generate output filename
            base_name = os.path.basename(input_path)
            output_path = os.path.join(processed_dir, base_name)
            
            # Check if it's a GIF
            if input_path.lower().endswith('.gif'):
                # Process animated GIF
                img = Image.open(input_path)
                frames = []
                durations = []
                
                for frame in ImageSequence.Iterator(img):
                    # Convert frame to RGBA
                    frame_rgba = frame.convert("RGBA")
                    
                    # Remove white background (make white pixels transparent)
                    datas = frame_rgba.getdata()
                    new_data = []
                    for item in datas:
                        # If pixel is white or near-white, make it transparent
                        if item[0] > 240 and item[1] > 240 and item[2] > 240:
                            new_data.append((255, 255, 255, 0))  # Transparent
                        else:
                            new_data.append(item)
                    
                    frame_rgba.putdata(new_data)
                    
                    # Composite onto background
                    bg_copy = background.copy()
                    # Resize to match if needed
                    if bg_copy.size != frame_rgba.size:
                        frame_rgba = frame_rgba.resize(bg_copy.size, Image.Resampling.LANCZOS)
                    
                    bg_copy.paste(frame_rgba, (0, 0), frame_rgba)
                    frames.append(bg_copy.convert("P", palette=Image.ADAPTIVE))
                    
                    # Get frame duration
                    durations.append(frame.info.get('duration', 100))
                
                # Save as GIF
                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0,
                    optimize=False
                )
            else:
                # Process static image
                img = Image.open(input_path).convert("RGBA")
                
                # Remove white background
                datas = img.getdata()
                new_data = []
                for item in datas:
                    # If pixel is white or near-white, make it transparent
                    if item[0] > 240 and item[1] > 240 and item[2] > 240:
                        new_data.append((255, 255, 255, 0))  # Transparent
                    else:
                        new_data.append(item)
                
                img.putdata(new_data)
                
                # Composite onto background
                bg_copy = background.copy()
                if bg_copy.size != img.size:
                    img = img.resize(bg_copy.size, Image.Resampling.LANCZOS)
                
                bg_copy.paste(img, (0, 0), img)
                
                # Save as PNG
                bg_copy.save(output_path, "PNG")
            
            return output_path
            
        except Exception as e:
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.status_label.setText(f"Error processing image: {str(e)}")
            return input_path  # Fallback to original

    def select_image(self, row, preview_label):
        """Open file dialog to select an image (including GIF)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Item Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            # Process image to remove white background and composite onto game background
            processed_path = self.process_image_remove_white_bg(file_path)
            
            # Store the PROCESSED path in the preview label's property
            preview_label.setProperty("image_path", processed_path)
            
            # Check if it's a GIF file
            if processed_path.lower().endswith('.gif'):
                # Use QMovie for animated GIFs
                movie = QMovie(processed_path)
                if movie.isValid():
                    # Scale the movie to fit the preview size
                    movie.setScaledSize(QSize(50, 50))
                    preview_label.setMovie(movie)
                    movie.start()
                    preview_label.setText("")
                    # Store movie reference to prevent garbage collection
                    preview_label.setProperty("movie", movie)
                    self.status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.status_label.setText(f"GIF processed & loaded: {os.path.basename(file_path)}")
                else:
                    self.status_label.setStyleSheet("color: red; font-weight: bold;")
                    self.status_label.setText("Failed to load GIF")
            else:
                # Use QPixmap for static images
                pixmap = QPixmap(processed_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    preview_label.setPixmap(scaled_pixmap)
                    preview_label.setText("")
                    # Clear any previous movie
                    preview_label.setProperty("movie", None)
                    self.status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.status_label.setText(f"Image processed & loaded: {os.path.basename(file_path)}")
                else:
                    self.status_label.setStyleSheet("color: red; font-weight: bold;")
                    self.status_label.setText("Failed to load image")

    def remove_item(self):
        """Remove selected row(s) from the table"""
        selected_rows = set()
        for index in self.loot_tableWidget.selectedIndexes():
            selected_rows.add(index.row())
        
        if not selected_rows:
            current_row = self.loot_tableWidget.currentRow()
            if current_row >= 0:
                selected_rows.add(current_row)
        
        # Remove rows in reverse order to avoid index shifting issues
        for row in sorted(selected_rows, reverse=True):
            self.loot_tableWidget.removeRow(row)

    def save_settings(self, profile_name) -> None:
        if not profile_name:
            return
        
        loot_list = []
        for row in range(self.loot_tableWidget.rowCount()):
            # Get image path from preview label
            image_widget = self.loot_tableWidget.cellWidget(row, 0)
            preview_label = image_widget.findChild(QLabel)
            image_path = preview_label.property("image_path") if preview_label else ""
            
            # Get action from ComboBox
            action_combo = self.loot_tableWidget.cellWidget(row, 1)
            action = action_combo.currentText() if action_combo else "RightClick"
            
            # Get CTRL state from Checkbox
            ctrl_widget = self.loot_tableWidget.cellWidget(row, 2)
            use_ctrl = False
            if ctrl_widget:
                ctrl_checkbox = ctrl_widget.findChild(QCheckBox)
                use_ctrl = ctrl_checkbox.isChecked() if ctrl_checkbox else False

            if image_path:  # Only save if image is selected
                loot_data = {
                    "ImagePath": image_path,
                    "Action": action,
                    "UseCtrl": use_ctrl
                }
                loot_list.append(loot_data)
        
        data_to_save = {"loot": loot_list}

        from Functions.GeneralFunctions import manage_profile
        if manage_profile("save", "Save/Looting", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' saved!")

    def load_settings(self, profile_name) -> None:
        filename = f"Save/Looting/{profile_name}.json"
        
        try:
            with open(filename, "r") as f:
                loaded_data = json.load(f)

            # Clear existing rows
            self.loot_tableWidget.setRowCount(0)
            
            for entry in loaded_data.get("loot", []):
                row_position = self.loot_tableWidget.rowCount()
                self.loot_tableWidget.insertRow(row_position)
                
                # Column 0: Image widget
                image_widget = QWidget()
                image_layout = QHBoxLayout(image_widget)
                image_layout.setContentsMargins(5, 5, 5, 5)
                
                preview_label = QLabel()
                preview_label.setMinimumSize(50, 50)
                preview_label.setMaximumSize(50, 50)
                preview_label.setStyleSheet("border: 1px solid gray; background-color: white;")
                
                # Load and display the image
                image_path = entry.get("ImagePath", "")
                if image_path and os.path.exists(image_path):
                    preview_label.setProperty("image_path", image_path)
                    
                    # Check if it's a GIF
                    if image_path.lower().endswith('.gif'):
                        movie = QMovie(image_path)
                        if movie.isValid():
                            movie.setScaledSize(QSize(50, 50))
                            preview_label.setMovie(movie)
                            movie.start()
                            preview_label.setProperty("movie", movie)
                        else:
                            preview_label.setText("Error")
                            preview_label.setAlignment(Qt.AlignCenter)
                    else:
                        pixmap = QPixmap(image_path)
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            preview_label.setPixmap(scaled_pixmap)
                            preview_label.setProperty("movie", None)
                        else:
                            preview_label.setText("Error")
                            preview_label.setAlignment(Qt.AlignCenter)
                else:
                    preview_label.setText("Missing")
                    preview_label.setAlignment(Qt.AlignCenter)
                
                select_button = QPushButton("Select Image")
                select_button.clicked.connect(lambda checked, r=row_position, p=preview_label: self.select_image(r, p))
                
                image_layout.addWidget(preview_label)
                image_layout.addWidget(select_button)
                
                self.loot_tableWidget.setCellWidget(row_position, 0, image_widget)
                
                # Column 1: Action ComboBox
                action_combo = QComboBox()
                action_combo.addItems([
                    "RightClick",
                    "LeftClick",
                    "DoubleLeftClick",
                    "1 Container",
                    "2 Container",
                    "3 Container",
                    "4 Container"
                ])
                action_combo.setCurrentText(entry.get("Action", "RightClick"))
                self.loot_tableWidget.setCellWidget(row_position, 1, action_combo)
                
                # Column 2: CTRL Checkbox
                ctrl_widget = QWidget()
                ctrl_layout = QHBoxLayout(ctrl_widget)
                ctrl_layout.setContentsMargins(0, 0, 0, 0)
                ctrl_layout.setAlignment(Qt.AlignCenter)
                ctrl_checkbox = QCheckBox()
                ctrl_checkbox.setChecked(entry.get("UseCtrl", False))
                ctrl_layout.addWidget(ctrl_checkbox)
                self.loot_tableWidget.setCellWidget(row_position, 2, ctrl_widget)
                
                # Set row height to accommodate the image
                self.loot_tableWidget.setRowHeight(row_position, 60)

            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' loaded!")
        except FileNotFoundError:
            self.status_label.setText(f"Profile '{profile_name}' not found.")

    def get_loot_data(self):
        """Extract loot data from table widget in a thread-safe way (to be called from GUI thread)"""
        loot_list = []
        for row in range(self.loot_tableWidget.rowCount()):
            # Get image path from preview label
            image_widget = self.loot_tableWidget.cellWidget(row, 0)
            if not image_widget: continue
            preview_label = image_widget.findChild(QLabel)
            image_path = preview_label.property("image_path") if preview_label else ""
            
            # Get action from ComboBox
            action_combo = self.loot_tableWidget.cellWidget(row, 1)
            action = action_combo.currentText() if action_combo else "RightClick"
            
            # Get CTRL state from Checkbox
            ctrl_widget = self.loot_tableWidget.cellWidget(row, 2)
            use_ctrl = False
            if ctrl_widget:
                ctrl_checkbox = ctrl_widget.findChild(QCheckBox)
                use_ctrl = ctrl_checkbox.isChecked() if ctrl_checkbox else False

            if image_path:
                loot_list.append({
                    "ImagePath": image_path,
                    "Action": action,
                    "UseCtrl": use_ctrl
                })
        return loot_list

    def start_loot_thread(self, state) -> None:
        self.looting_enabled = (state == Qt.Checked)
        
        if state == Qt.Checked:
            # Stop existing thread if running
            if self.loot_thread:
                self.loot_thread.stop()
                self.loot_thread.wait(2000)
            
            # Extract data while still in GUI thread
            loot_data = self.get_loot_data()
            
            self.loot_thread = LootThread(loot_data, Qt.Unchecked)
            self.loot_thread.start()
        else:
            if self.loot_thread:
                self.loot_thread.stop()
                self.loot_thread.wait(2000)
                self.loot_thread = None

