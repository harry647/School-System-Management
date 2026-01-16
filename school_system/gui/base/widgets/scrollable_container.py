"""
Scrollable Container Widget

A scrollable container widget for displaying large amounts of content.
"""

from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QKeyEvent


class ScrollableContainer(QScrollArea):
    """
    A scrollable container widget for displaying large amounts of content.
    
    Features:
        - Vertical and horizontal scrolling
        - Customizable scrollbar styles
        - Smooth scrolling
    """
    
    def __init__(self, parent=None, horizontal_scroll=True, vertical_scroll=True):
        super().__init__(parent)
        
        # Configure the scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded if horizontal_scroll else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded if vertical_scroll else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        
        # Create the content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setWidget(self.content_widget)
        
        # Default styling
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #ccc;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #ccc;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        # Keyboard navigation and focus management
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Scrollable Container")
        self.setAccessibleDescription("A scrollable container for displaying large amounts of content")
    
    def add_widget(self, widget):
        """Add a widget to the scrollable container."""
        self.content_layout.addWidget(widget)
    
    def clear(self):
        """Clear all widgets from the scrollable container."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def set_spacing(self, spacing):
        """Set the spacing between widgets."""
        self.content_layout.setSpacing(spacing)
    
    def set_margins(self, left, top, right, bottom):
        """Set the margins around the content."""
        self.content_layout.setContentsMargins(left, top, right, bottom)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for keyboard navigation."""
        if event.key() == Qt.Key.Key_Up:
            self._scroll_up()
        elif event.key() == Qt.Key.Key_Down:
            self._scroll_down()
        elif event.key() == Qt.Key.Key_Left:
            self._scroll_left()
        elif event.key() == Qt.Key.Key_Right:
            self._scroll_right()
        elif event.key() == Qt.Key.Key_PageUp:
            self._scroll_page_up()
        elif event.key() == Qt.Key.Key_PageDown:
            self._scroll_page_down()
        elif event.key() == Qt.Key.Key_Home:
            self._scroll_to_top()
        elif event.key() == Qt.Key.Key_End:
            self._scroll_to_bottom()
        else:
            super().keyPressEvent(event)
    
    def _scroll_up(self):
        """Scroll up by a small amount."""
        vertical_scrollbar = self.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.value() - 20)
    
    def _scroll_down(self):
        """Scroll down by a small amount."""
        vertical_scrollbar = self.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.value() + 20)
    
    def _scroll_left(self):
        """Scroll left by a small amount."""
        horizontal_scrollbar = self.horizontalScrollBar()
        horizontal_scrollbar.setValue(horizontal_scrollbar.value() - 20)
    
    def _scroll_right(self):
        """Scroll right by a small amount."""
        horizontal_scrollbar = self.horizontalScrollBar()
        horizontal_scrollbar.setValue(horizontal_scrollbar.value() + 20)
    
    def _scroll_page_up(self):
        """Scroll up by a page."""
        vertical_scrollbar = self.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.value() - vertical_scrollbar.pageStep())
    
    def _scroll_page_down(self):
        """Scroll down by a page."""
        vertical_scrollbar = self.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.value() + vertical_scrollbar.pageStep())
    
    def _scroll_to_top(self):
        """Scroll to the top."""
        vertical_scrollbar = self.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.minimum())
    
    def _scroll_to_bottom(self):
        """Scroll to the bottom."""
        vertical_scrollbar = self.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.maximum())
    
    def focusInEvent(self, event):
        """Handle focus in event."""
        super().focusInEvent(event)
        # Ensure the first focusable widget gets focus
        self._focus_first_widget()
    
    def _focus_first_widget(self):
        """Focus the first focusable widget in the container."""
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if widget.focusPolicy() != Qt.FocusPolicy.NoFocus:
                    widget.setFocus()
                    break


class ScrollableCardContainer(ScrollableContainer):
    """
    A scrollable container specifically designed for cards.
    
    Features:
        - Optimized for card layouts
        - Customizable card spacing
    """
    
    def __init__(self, parent=None, horizontal_scroll=True, vertical_scroll=True):
        super().__init__(parent, horizontal_scroll, vertical_scroll)
        
        # Configure for cards
        self.content_layout.setSpacing(12)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        
        # Card-specific styling
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #ccc;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
    
    def add_card(self, card):
        """Add a card to the scrollable container."""
        self.content_layout.addWidget(card)
