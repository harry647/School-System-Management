"""
Base Dialog Implementation for the School System GUI Framework

This module provides a robust base dialog class that implements:
- Consistent dialog behavior across the application
- Theming support synchronized with parent windows
- Accessibility compliance for dialogs
- Standardized button layouts and actions
- Modal and modeless dialog support

The BaseDialog serves as the foundation for all application dialogs,
ensuring consistent user experience and behavior.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QDialogButtonBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from school_system.gui.base.widgets import (
    ThemeManager, AccessibleWidget, ModernButton, ScrollableContainer, ModernCard
)
from school_system.config.logging import logger


class BaseDialog(QDialog):
    """
    Base dialog class providing core functionality for all application dialogs.
    
    Features:
        - Consistent dialog behavior
        - Theming support
        - Accessibility compliance
        - Standardized button layouts
        - Modal and modeless support
        - Event-driven architecture
    """
    
    # Dialog result signals
    dialog_accepted = pyqtSignal()
    dialog_rejected = pyqtSignal()
    dialog_closed = pyqtSignal()
    
    def __init__(
        self,
        title: str = "Dialog",
        parent=None,
        modal: bool = True,
        standard_buttons: QDialogButtonBox.StandardButton =
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        scrollable: bool = False
    ):
        """
        Initialize the base dialog.
        
        Args:
            title: Dialog title
            parent: Parent widget
            modal: Whether the dialog is modal
            standard_buttons: Standard buttons to include
            scrollable: Whether to make content area scrollable
        """
        super().__init__(parent)
         
        # Dialog properties
        self.setWindowTitle(title)
        self.setModal(modal)
         
        # Theme management
        self._theme_manager = None
        if parent and hasattr(parent, 'get_theme_manager'):
            self._theme_manager = parent.get_theme_manager()
        else:
            self._theme_manager = ThemeManager(self)
         
        # Main layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(15, 15, 15, 15)
        self._main_layout.setSpacing(12)
         
        # Content area - use scrollable container if requested
        if scrollable:
            self._content_frame = ScrollableContainer(self)
            self._content_frame.setWidgetResizable(True)
            self._content_layout = QVBoxLayout(self._content_frame.content_widget)
        else:
            self._content_frame = QFrame(self)
            self._content_layout = QVBoxLayout(self._content_frame)
            
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(10)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
         
        # Button box
        self._button_box = QDialogButtonBox(standard_buttons)
        self._button_box.setCenterButtons(False)
         
        # Assemble dialog
        self._main_layout.addWidget(self._content_frame, 1)
        self._main_layout.addWidget(self._button_box)
        
        # Connect signals
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        
        # Accessibility
        self._initialize_accessibility()
        
        # Apply theme
        self._apply_theme(self._theme_manager.get_theme())
        
        logger.info(f"BaseDialog '{title}' initialized")
    
    def _initialize_accessibility(self):
        """Initialize accessibility features."""
        self.setAccessibleName(f"{self.windowTitle()} Dialog")
        self.setAccessibleDescription(f"Dialog window for {self.windowTitle()}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Make content frame accessible
        self._content_frame.setAccessibleName("Dialog content")
        self._content_frame.setAccessibleDescription("Main content area of the dialog")
    
    def _apply_theme(self, theme_name: str):
        """Apply theme to the dialog."""
        if self._theme_manager:
            qss = self._theme_manager.generate_qss()
            self.setStyleSheet(qss)
            
            # Apply theme to button box
            self._button_box.setStyleSheet(f"""
                QDialogButtonBox {{
                    background-color: {self._theme_manager.get_color('background')};
                    border-top: 1px solid {self._theme_manager.get_color('border')};
                    padding-top: 10px;
                }}
            """)
            
            logger.debug(f"Theme '{theme_name}' applied to dialog '{self.windowTitle()}'")
    
    def add_content_widget(self, widget, stretch: int = 0, name: str = None):
        """
        Add a widget to the dialog content area.
        
        Args:
            widget: Widget to add
            stretch: Layout stretch factor
            name: Optional name for accessibility
        """
        self._content_layout.addWidget(widget, stretch)
        
        if name:
            widget.setAccessibleName(name)
            widget.setAccessibleDescription(f"{name} in {self.windowTitle()} dialog")
    
    def add_content_layout(self, layout, stretch: int = 0):
        """
        Add a layout to the dialog content area.
        
        Args:
            layout: Layout to add
            stretch: Layout stretch factor
        """
        self._content_layout.addLayout(layout, stretch)
    
    def set_dialog_icon(self, icon: QIcon):
        """
        Set the dialog window icon.
        
        Args:
            icon: Icon to set
        """
        self.setWindowIcon(icon)
    
    def set_content_title(self, title: str):
        """
        Set a title for the content area.
        
        Args:
            title: Title text
        """
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {self._theme_manager.get_color('text')};
            margin-bottom: 8px;
        """)
        title_label.setAccessibleName("Dialog content title")
        
        # Insert at the beginning
        self._content_layout.insertWidget(0, title_label)
    
    def add_custom_button(self, text: str, role: QDialogButtonBox.ButtonRole = QDialogButtonBox.ButtonRole.ActionRole):
        """
        Add a custom button to the dialog.
        
        Args:
            text: Button text
            role: Button role
            
        Returns:
            The created button
        """
        button = ModernButton(text)
        button.setAccessibleName(f"{text} button")
        button.setAccessibleDescription(f"{text} action button in dialog")
        
        self._button_box.addButton(button, role)
        
        return button
    
    def set_standard_buttons(self, buttons: QDialogButtonBox.StandardButton):
        """
        Set the standard buttons for the dialog.
        
        Args:
            buttons: Standard buttons to set
        """
        self._button_box.setStandardButtons(buttons)
    
    def get_theme_manager(self) -> ThemeManager:
        """
        Get the theme manager instance.
        
        Returns:
            The ThemeManager instance
        """
        return self._theme_manager
    
    def set_theme(self, theme_name: str):
        """
        Set the dialog theme.
        
        Args:
            theme_name: Name of the theme to apply
        """
        if self._theme_manager:
            self._theme_manager.set_theme(theme_name)
            self._apply_theme(theme_name)
            logger.debug(f"Theme '{theme_name}' applied to dialog '{self.windowTitle()}'")
    
    def showEvent(self, event):
        """
        Handle dialog show events.
        
        Args:
            event: Show event
        """
        super().showEvent(event)
        logger.debug(f"Dialog '{self.windowTitle()}' shown")
    
    def closeEvent(self, event):
        """
        Handle dialog close events.
        
        Args:
            event: Close event
        """
        logger.debug(f"Dialog '{self.windowTitle()}' closing")
        self.dialog_closed.emit()
        super().closeEvent(event)
    
    def accept(self):
        """Handle dialog acceptance."""
        logger.debug(f"Dialog '{self.windowTitle()}' accepted")
        self.dialog_accepted.emit()
        super().accept()
    
    def reject(self):
        """Handle dialog rejection."""
        logger.debug(f"Dialog '{self.windowTitle()}' rejected")
        self.dialog_rejected.emit()
        super().reject()



