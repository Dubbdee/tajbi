from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor
import win32gui


class SelectionOverlay(QWidget):
    """Transparent overlay window for displaying selection rectangle during drag."""
    
    def __init__(self, game_hwnd=None):
        super().__init__()
        self.game_hwnd = game_hwnd
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.is_visible = False
        
        # Set window flags for transparent overlay
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Position overlay on the correct screen
        self.position_on_game_screen()
        
    def position_on_game_screen(self):
        """Position the overlay on the same screen as the game window."""
        if self.game_hwnd:
            try:
                # Get game window rect
                rect = win32gui.GetWindowRect(self.game_hwnd)
                game_x, game_y = rect[0], rect[1]
                
                # Find which screen contains the game window
                app = QApplication.instance()
                for screen in app.screens():
                    screen_geo = screen.geometry()
                    if screen_geo.contains(game_x, game_y):
                        # Set overlay to cover this screen
                        self.setGeometry(screen_geo)
                        return
            except:
                pass
        
        # Fallback: use primary screen
        self.showFullScreen()
        
    def set_selection(self, start_x, start_y, end_x, end_y):
        """Update the selection rectangle coordinates."""
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.update()  # Trigger repaint
    
    def show_selection(self):
        """Show the overlay."""
        self.is_visible = True
        self.show()
        self.raise_()
        self.activateWindow()
    
    def hide_selection(self):
        """Hide the overlay."""
        self.is_visible = False
        self.hide()
    
    def paintEvent(self, event):
        """Draw the selection rectangle."""
        if not self.is_visible:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate rectangle bounds (handles dragging in any direction)
        x = min(self.start_x, self.end_x)
        y = min(self.start_y, self.end_y)
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        
        # Draw semi-transparent fill
        fill_color = QColor(0, 120, 255, 80)  # Light blue with more transparency
        painter.fillRect(x, y, width, height, fill_color)
        
        # Draw border
        pen = QPen(QColor(0, 120, 255, 255), 3, Qt.SolidLine)  # Thicker blue border
        painter.setPen(pen)
        painter.drawRect(x, y, width, height)
        
        painter.end()

