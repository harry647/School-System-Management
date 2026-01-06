"""
Sample Modern Button Widget

A sample demonstrating the usage of the ModernButton widget.
"""

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from .button import ModernButton
from .theme import ThemeManager


class SampleButtonDemo(QWidget):
    """
    A demo widget to showcase the ModernButton.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Button Demo")
        self.setGeometry(100, 100, 300, 200)
        
        # Theme manager
        self.theme_manager = ThemeManager()
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Default button
        self.default_button = ModernButton("Default Button")
        layout.addWidget(self.default_button)
        
        # Custom styled button
        self.custom_button = ModernButton("Custom Button")
        self.custom_button.set_custom_style(
            bg_color="#2196F3",
            hover_color="#0b7dda",
            pressed_color="#0b6e99",
            text_color="white"
        )
        layout.addWidget(self.custom_button)
        
        # Theme switch button
        self.theme_button = ModernButton("Toggle Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)
        
        # Apply initial theme
        self.apply_theme()
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = self.theme_manager.get_theme()
        new_theme = "dark" if current_theme == "light" else "light"
        self.theme_manager.set_theme(new_theme)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme to all widgets."""
        qss = self.theme_manager.generate_qss()
        self.setStyleSheet(qss)
        
        # Update button text
        current_theme = self.theme_manager.get_theme()
        self.theme_button.setText(f"Toggle Theme (Current: {current_theme})")


if __name__ == "__main__":
    app = QApplication([])
    demo = SampleButtonDemo()
    demo.show()
    app.exec()