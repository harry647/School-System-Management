"""
Sample Scrollable Container Demo

A demo to showcase the ScrollableContainer and ScrollableCardContainer widgets.
"""

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from .button import ModernButton
from .card import ModernCard
from .scrollable_container import ScrollableContainer, ScrollableCardContainer
from .theme import ThemeManager


class SampleScrollableDemo(QWidget):
    """
    A demo widget to showcase the ScrollableContainer and ScrollableCardContainer.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scrollable Container Demo")
        self.setGeometry(100, 100, 400, 500)
        
        # Theme manager
        self.theme_manager = ThemeManager()
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Scrollable container with both vertical and horizontal scrolling
        self.scrollable_container = ScrollableContainer()
        layout.addWidget(self.scrollable_container)
        
        # Add buttons to the scrollable container
        for i in range(20):
            button = ModernButton(f"Button {i + 1}")
            self.scrollable_container.add_widget(button)
        
        # Horizontal scrollable container
        self.horizontal_scrollable_container = ScrollableContainer(horizontal_scroll=True, vertical_scroll=False)
        self.horizontal_scrollable_container.setFixedHeight(100)
        layout.addWidget(self.horizontal_scrollable_container)
        
        # Add buttons horizontally
        horizontal_layout = QHBoxLayout()
        for i in range(10):
            button = ModernButton(f"H-Button {i + 1}")
            horizontal_layout.addWidget(button)
        
        # Create a widget to hold the horizontal layout
        horizontal_widget = QWidget()
        horizontal_widget.setLayout(horizontal_layout)
        self.horizontal_scrollable_container.setWidget(horizontal_widget)
        
        # Scrollable card container
        self.scrollable_card_container = ScrollableCardContainer()
        layout.addWidget(self.scrollable_card_container)
        
        # Add cards to the scrollable card container
        for i in range(10):
            card = ModernCard(f"Card {i + 1}", f"This is the content of card {i + 1}.")
            self.scrollable_card_container.add_card(card)
        
        # Theme switch button
        self.theme_button = ModernButton("Toggle Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)
        
        # Keyboard navigation instructions
        self.instructions_label = QLabel(
            "Keyboard Navigation: Use Arrow Keys, Page Up/Down, Home/End. Press Tab to focus widgets."
        )
        self.instructions_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.instructions_label)
        
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
    demo = SampleScrollableDemo()
    demo.show()
    app.exec()