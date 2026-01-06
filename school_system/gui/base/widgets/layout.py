"""
Modern Layout System

A flexible grid/flexbox-like layout manager for adaptive arrangements.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt


class ModernLayout(QWidget):
    """
    A modern layout manager with flexible grid/flexbox-like arrangements.
    
    Features:
        - Adaptive grid and flexbox layouts
        - Customizable spacing and margins
        - Support for dynamic resizing
    """
    
    def __init__(self, layout_type="vbox", parent=None):
        super().__init__(parent)
        self.layout_type = layout_type
        self._layout = None
        
        # Initialize the layout based on the type
        if layout_type == "vbox":
            self._layout = QVBoxLayout(self)
        elif layout_type == "hbox":
            self._layout = QHBoxLayout(self)
        elif layout_type == "grid":
            self._layout = QGridLayout(self)
        else:
            raise ValueError(f"Unsupported layout type: {layout_type}")
        
        # Default settings
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    
    def add_widget(self, widget, row=None, col=None, rowspan=1, colspan=1):
        """Add a widget to the layout."""
        if isinstance(self._layout, QGridLayout):
            if row is None or col is None:
                raise ValueError("Row and column must be specified for grid layout")
            self._layout.addWidget(widget, row, col, rowspan, colspan)
        else:
            self._layout.addWidget(widget)
    
    def set_spacing(self, spacing):
        """Set the spacing between widgets."""
        self._layout.setSpacing(spacing)
    
    def set_margins(self, left, top, right, bottom):
        """Set the margins around the layout."""
        self._layout.setContentsMargins(left, top, right, bottom)
    
    def set_alignment(self, alignment):
        """Set the alignment of the layout."""
        self._layout.setAlignment(alignment)
    
    def clear(self):
        """Clear all widgets from the layout."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class FlexLayout(ModernLayout):
    """
    A flexbox-like layout manager for adaptive arrangements.
    
    Features:
        - Flexible direction (row or column)
        - Wrapping support
        - Justify and align content
    """
    
    def __init__(self, direction="row", wrap=False, parent=None):
        super().__init__("hbox" if direction == "row" else "vbox", parent)
        self.direction = direction
        self.wrap = wrap
        
        # Configure layout based on direction
        if direction == "row":
            self._layout = QHBoxLayout(self)
        else:
            self._layout = QVBoxLayout(self)
        
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
    
    def set_justify_content(self, justify):
        """Set the justify content alignment."""
        if justify == "flex-start":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        elif justify == "flex-end":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        elif justify == "center":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif justify == "space-between":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignRight)
        elif justify == "space-around":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignRight)
    
    def set_align_items(self, align):
        """Set the align items alignment."""
        if align == "flex-start":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        elif align == "flex-end":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        elif align == "center":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        elif align == "stretch":
            self._layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignBottom)