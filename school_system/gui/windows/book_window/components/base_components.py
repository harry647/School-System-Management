"""
Base reusable components for the book management system.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from school_system.gui.windows.book_window.utils import (
    SPACING_SMALL, SPACING_MEDIUM, SPACING_LARGE,
    CARD_PADDING, CARD_SPACING,
    BOOK_CONDITIONS, REMOVAL_REASONS, USER_TYPES, RETURN_CONDITIONS,
    STANDARD_SUBJECTS, STANDARD_CLASSES, STANDARD_STREAMS, STANDARD_TERMS
)


class FlexLayout:
    """Flexible layout wrapper for consistent spacing and alignment."""
    
    def __init__(self, direction="column", stretch=False):
        """
        Initialize the flex layout.
        
        Args:
            direction: 'column' or 'row'
            stretch: Whether to stretch the layout
        """
        self._layout = QVBoxLayout() if direction == "column" else QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        if stretch:
            self._layout.setStretch(0, 1)
    
    def add_widget(self, widget):
        """Add a widget to the layout."""
        if isinstance(widget, FlexLayout):
            # If it's a FlexLayout, add its underlying layout
            self._layout.addLayout(widget._layout)
        else:
            # Otherwise, add it as a widget
            self._layout.addWidget(widget)
    
    def addWidget(self, widget):
        """Alias for add_widget to support camelCase naming convention."""
        return self.add_widget(widget)
    
    def add_Widget(self, widget):
        """Alias for add_widget to support mixed case naming convention."""
        return self.add_widget(widget)
    
    def add_layout(self, layout):
        """Add a layout to this layout."""
        if isinstance(layout, FlexLayout):
            # If it's a FlexLayout, add its underlying layout
            self._layout.addLayout(layout._layout)
        else:
            # Otherwise, add it as a regular layout
            self._layout.addLayout(layout)
    
    def addLayout(self, layout):
        """Alias for add_layout to support camelCase naming convention."""
        return self.add_layout(layout)
    
    def add_Layout(self, layout):
        """Alias for add_layout to support mixed case naming convention."""
        return self.add_layout(layout)
    
    def set_spacing(self, spacing):
        """Set the spacing between widgets."""
        self._layout.setSpacing(spacing)
    
    def set_contents_margins(self, left, top, right, bottom):
        """Set the contents margins."""
        self._layout.setContentsMargins(left, top, right, bottom)


class Card(QWidget):
    """Card component with consistent styling."""
    
    def __init__(self, title: str = "", subtitle: str = ""):
        """
        Initialize the card.
        
        Args:
            title: Card title
            subtitle: Card subtitle/description
        """
        super().__init__()
        self.setObjectName("card")
        self.setStyleSheet("""
            #card {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
            }
        """)
        
        self.layout = FlexLayout("column", False)
        self.layout.set_spacing(SPACING_SMALL)
        self.layout.set_contents_margins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")
            self.layout.add_widget(title_label)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
            self.layout.add_widget(subtitle_label)
        
        self.setLayout(self.layout._layout)


class InputField(QLineEdit):
    """Custom input field with consistent styling."""
    
    def __init__(self, placeholder: str = ""):
        """
        Initialize the input field.
        
        Args:
            placeholder: Placeholder text
        """
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #DDD;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498DB;
            }
        """)
        self.setMinimumHeight(36)


class TextArea(QTextEdit):
    """Custom text area with consistent styling."""
    
    def __init__(self, placeholder: str = ""):
        """
        Initialize the text area.
        
        Args:
            placeholder: Placeholder text
        """
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QTextEdit {
                padding: 8px 12px;
                border: 1px solid #DDD;
                border-radius: 4px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 1px solid #3498DB;
            }
        """)


class Button(QPushButton):
    """Custom button with styling options."""
    
    def __init__(self, text: str, button_type: str = "primary"):
        """
        Initialize the button.
        
        Args:
            text: Button text
            button_type: 'primary', 'secondary', 'success', 'danger', or 'default'
        """
        super().__init__(text)
        self.setMinimumHeight(36)
        
        # Set styles based on button type
        if button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
                QPushButton:pressed {
                    background-color: #1F618D;
                }
            """)
        elif button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #ECF0F1;
                    color: #2C3E50;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #DDDDDD;
                }
                QPushButton:pressed {
                    background-color: #CCCCCC;
                }
            """)
        elif button_type == "success":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #219653;
                }
                QPushButton:pressed {
                    background-color: #1A7F46;
                }
            """)
        elif button_type == "danger":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
                QPushButton:pressed {
                    background-color: #992D22;
                }
            """)
        else:  # default
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F8F9FA;
                    color: #2C3E50;
                    border: 1px solid #DDD;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #E9ECEF;
                }
                QPushButton:pressed {
                    background-color: #DEE2E6;
                }
            """)


class ComboBox(QComboBox):
    """Custom combo box with consistent styling."""
    
    def __init__(self):
        """Initialize the combo box."""
        super().__init__()
        self.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #DDD;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 1px solid #3498DB;
            }
            QComboBox::drop-down {
                border: 0px;
            }
        """)
        self.setMinimumHeight(36)


class Table(QTableWidget):
    """Custom table with consistent styling."""
    
    def __init__(self, rows: int, columns: int):
        """
        Initialize the table.
        
        Args:
            rows: Number of rows
            columns: Number of columns
        """
        super().__init__(rows, columns)
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #DDD;
                border-radius: 4px;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #2C3E50;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)


class SearchBox(QWidget):
    """Search box component with icon."""
    
    def __init__(self, placeholder: str = "Search..."):
        """
        Initialize the search box.
         
        Args:
            placeholder: Placeholder text
        """
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self.search_input = InputField(placeholder)
        layout.addWidget(self.search_input)
        
        self.setLayout(layout)
    
    def text(self) -> str:
        """Get the search text."""
        return self.search_input.text()
    
    def set_text(self, text: str):
        """Set the search text."""
        self.search_input.setText(text)
    
    @property
    def textChanged(self):
        """Expose the textChanged signal from the search input."""
        return self.search_input.textChanged


class ValidationLabel(QLabel):
    """Validation feedback label."""
    
    def __init__(self):
        """Initialize the validation label."""
        super().__init__()
        self.setStyleSheet("font-size: 12px;")
        self.setWordWrap(True)
    
    def set_success(self, message: str):
        """Set success validation message."""
        self.setText(f"✓ {message}")
        self.setStyleSheet("font-size: 12px; color: #27AE60;")
    
    def set_error(self, message: str):
        """Set error validation message."""
        self.setText(f"✗ {message}")
        self.setStyleSheet("font-size: 12px; color: #E74C3C;")
    
    def clear(self):
        """Clear the validation message."""
        self.setText("")
