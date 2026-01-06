"""
Base Dialog Implementation for the School System GUI Framework

This module provides a robust base dialog class that implements:
- Consistent dialog behavior across the application
- Theming support synchronized with parent windows
- Accessibility compliance for dialogs
- Standardized button layouts and actions
- Modal and modeless dialog support
- Centralized widget repository with pre-configured components
- Clean, consistent interface for widget creation and management
- Efficient reuse across the application
- Design coherence and reduced boilerplate code

The BaseDialog serves as the foundation for all application dialogs,
ensuring consistent user experience and behavior. It also acts as a
centralized widget repository, providing easy access to all GUI components
including buttons, inputs, cards, layouts, search boxes, tables, and containers.
This eliminates redundant imports and reimplementation across the application.

Key Features:
    1. Centralized Widget Repository: Pre-configured instances of all essential GUI components
    2. Consistent Interface: Clean, uniform methods for widget creation and management
    3. Theme Synchronization: Automatic theme inheritance from parent windows
    4. Accessibility Compliance: Built-in accessibility features for all widgets
    5. Event-Driven Architecture: Signals for widget creation and registration events
    6. Reduced Boilerplate: Convenience methods for common dialog patterns

Usage Examples:

    # Basic usage with pre-configured widgets
    dialog = BaseDialog("User Settings", parent=main_window)
    
    # Access pre-configured widgets from repository
    primary_button = dialog.get_widget_from_repository('buttons', 'primary')
    search_input = dialog.get_widget_from_repository('inputs', 'search')
    
    # Create and add widgets directly to content
    dialog.add_button_to_content("Save", "primary", name="save_button")
    dialog.add_input_to_content("Enter username...", "text", name="username_input")
    dialog.add_search_box_to_content("Search users...", "advanced", name="user_search")
    
    # Create widgets programmatically
    custom_button = dialog.create_button("Custom Action", "secondary")
    custom_input = dialog.create_input("Enter email...", "email")
    custom_card = dialog.create_card("User Info", "User details go here")
    
    # Register widgets for centralized management
    dialog.register_widget("custom_button", custom_button)
    dialog.register_widget("custom_input", custom_input)
    
    # Theme management
    dialog.set_theme("dark")  # Set theme explicitly
    dialog.synchronize_theme_with_parent()  # Inherit parent window theme
    
    # Access managers
    theme_manager = dialog.get_theme_manager()
    state_manager = dialog.get_state_manager()

Widget Categories Available:
    - Buttons: primary, secondary, danger, cancel
    - Inputs: text, search, email
    - Layouts: main, form, horizontal
    - Search Boxes: default, advanced
    - Containers: card, scrollable
    - Tables: custom table widget
    - Cards: modern card component
    - Progress Indicators: loading indicators

The BaseDialog class ensures that all dialogs in the application have access to
the same set of pre-configured, themed widgets, reducing code duplication and
ensuring visual consistency throughout the application.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QDialogButtonBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from school_system.gui.base.widgets import (
    ThemeManager, AccessibleWidget, ModernButton, ScrollableContainer, ModernCard,
    ModernInput, ModernLayout, FlexLayout, SearchBox, AdvancedSearchBox, MemoizedSearchBox,
    CustomTableWidget, SortFilterProxyModel, VirtualScrollModel, ScrollableCardContainer,
    ModernStatusBar, ProgressIndicator, StateManager
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
        - Centralized widget repository with pre-configured components
        - Clean, consistent interface for widget creation and management
        - Efficient reuse across the application
        - Design coherence and reduced boilerplate code
    """
     
    # Dialog result signals
    dialog_accepted = pyqtSignal()
    dialog_rejected = pyqtSignal()
    dialog_closed = pyqtSignal()
    
    # Widget repository signals
    widget_created = pyqtSignal(str, object)
    widget_registered = pyqtSignal(str, object)
    
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
          
        # Core systems
        self._theme_manager = None
        if parent and hasattr(parent, 'get_theme_manager'):
            self._theme_manager = parent.get_theme_manager()
        else:
            self._theme_manager = ThemeManager(self)
        
        self._state_manager = StateManager(self)
        self._widget_registry = {}
          
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
         
        # Initialize systems
        self._initialize_accessibility()
        self._initialize_widget_repository()
        self._apply_theme(self._theme_manager.get_theme())
         
        logger.info(f"BaseDialog '{title}' initialized with centralized widget repository")
    
    def _initialize_accessibility(self):
        """Initialize accessibility features."""
        self.setAccessibleName(f"{self.windowTitle()} Dialog")
        self.setAccessibleDescription(f"Dialog window for {self.windowTitle()}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
         
        # Make content frame accessible
        self._content_frame.setAccessibleName("Dialog content")
        self._content_frame.setAccessibleDescription("Main content area of the dialog")
    
    def _initialize_widget_repository(self):
        """Initialize the centralized widget repository with pre-configured instances."""
        # Pre-configured widget instances for easy reuse
        self._widget_repository = {
            'buttons': {},
            'inputs': {},
            'cards': {},
            'layouts': {},
            'search_boxes': {},
            'tables': {},
            'containers': {}
        }
         
        # Initialize with some common pre-configured widgets
        self._widget_repository['buttons']['primary'] = self._create_primary_button()
        self._widget_repository['buttons']['secondary'] = self._create_secondary_button()
        self._widget_repository['buttons']['danger'] = self._create_danger_button()
        self._widget_repository['buttons']['cancel'] = self._create_cancel_button()
         
        self._widget_repository['inputs']['text'] = self._create_text_input()
        self._widget_repository['inputs']['search'] = self._create_search_input()
        self._widget_repository['inputs']['email'] = self._create_email_input()
         
        self._widget_repository['layouts']['main'] = self._create_main_layout()
        self._widget_repository['layouts']['form'] = self._create_form_layout()
        self._widget_repository['layouts']['horizontal'] = self._create_horizontal_layout()
         
        self._widget_repository['search_boxes']['default'] = self._create_default_search_box()
        self._widget_repository['search_boxes']['advanced'] = self._create_advanced_search_box()
         
        self._widget_repository['containers']['card'] = self._create_card_container()
        self._widget_repository['containers']['scrollable'] = self._create_scrollable_container()
        
        logger.debug(f"Widget repository initialized for dialog '{self.windowTitle()}'")
    
    def _apply_theme(self, theme_name: str):
        """Apply theme to the dialog and all registered widgets."""
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
            
            # Apply theme to all registered widgets
            for widget_name, widget in self._widget_registry.items():
                if hasattr(widget, 'apply_theme'):
                    widget.apply_theme(theme_name)
            
            # Apply theme to all repository widgets
            for category in self._widget_repository.values():
                for widget in category.values():
                    if hasattr(widget, 'apply_theme'):
                        widget.apply_theme(theme_name)
             
            logger.debug(f"Theme '{theme_name}' applied to dialog '{self.windowTitle()}' and all widgets")
    
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
    
    # Convenience methods for adding widgets to content with automatic registration
    def add_button_to_content(self, text: str = "Button", button_type: str = "primary",
                            stretch: int = 0, name: str = None) -> ModernButton:
        """
        Create and add a button to the dialog content area.
         
        Args:
            text: Button text
            button_type: Type of button (primary, secondary, danger, cancel)
            stretch: Layout stretch factor
            name: Optional name to register the button
             
        Returns:
            The created button instance
        """
        button = self.create_button(text, button_type)
        self._content_layout.addWidget(button, stretch)
        
        if name:
            self.register_widget(name, button)
            
        return button
    
    def add_input_to_content(self, placeholder: str = "Enter text...", input_type: str = "text",
                            stretch: int = 0, name: str = None) -> ModernInput:
        """
        Create and add an input field to the dialog content area.
         
        Args:
            placeholder: Placeholder text
            input_type: Type of input (text, search, email)
            stretch: Layout stretch factor
            name: Optional name to register the input
             
        Returns:
            The created input instance
        """
        input_field = self.create_input(placeholder, input_type)
        self._content_layout.addWidget(input_field, stretch)
        
        if name:
            self.register_widget(name, input_field)
            
        return input_field
    
    def add_card_to_content(self, title: str = "Card Title", content: str = "Card Content",
                           stretch: int = 0, name: str = None) -> ModernCard:
        """
        Create and add a card to the dialog content area.
         
        Args:
            title: Card title
            content: Card content
            stretch: Layout stretch factor
            name: Optional name to register the card
             
        Returns:
            The created card instance
        """
        card = self.create_card(title, content)
        self._content_layout.addWidget(card, stretch)
        
        if name:
            self.register_widget(name, card)
            
        return card
    
    def add_search_box_to_content(self, placeholder: str = "Search...", search_type: str = "default",
                                 stretch: int = 0, name: str = None):
        """
        Create and add a search box to the dialog content area.
         
        Args:
            placeholder: Placeholder text
            search_type: Type of search box (default, advanced, memoized)
            stretch: Layout stretch factor
            name: Optional name to register the search box
             
        Returns:
            The created search box instance
        """
        if search_type == "advanced":
            search_box = self.create_advanced_search_box(placeholder)
        elif search_type == "memoized":
            search_box = self.create_memoized_search_box(placeholder)
        else:
            search_box = self.create_search_box(placeholder)
        
        self._content_layout.addWidget(search_box, stretch)
        
        if name:
            self.register_widget(name, search_box)
            
        return search_box
    
    def add_table_to_content(self, rows: int = 0, columns: int = 0, stretch: int = 0,
                            name: str = None) -> CustomTableWidget:
        """
        Create and add a table to the dialog content area.
         
        Args:
            rows: Number of rows
            columns: Number of columns
            stretch: Layout stretch factor
            name: Optional name to register the table
             
        Returns:
            The created table instance
        """
        table = self.create_table(rows, columns)
        self._content_layout.addWidget(table, stretch)
        
        if name:
            self.register_widget(name, table)
            
        return table
    
    def add_scrollable_container_to_content(self, horizontal_scroll: bool = True, vertical_scroll: bool = True,
                                           stretch: int = 0, name: str = None) -> ScrollableContainer:
        """
        Create and add a scrollable container to the dialog content area.
         
        Args:
            horizontal_scroll: Enable horizontal scrolling
            vertical_scroll: Enable vertical scrolling
            stretch: Layout stretch factor
            name: Optional name to register the container
             
        Returns:
            The created scrollable container instance
        """
        container = self.create_scrollable_container(horizontal_scroll, vertical_scroll)
        self._content_layout.addWidget(container, stretch)
        
        if name:
            self.register_widget(name, container)
            
        return container
    
    def add_card_container_to_content(self, stretch: int = 0, name: str = None) -> ScrollableCardContainer:
        """
        Create and add a card container to the dialog content area.
         
        Args:
            stretch: Layout stretch factor
            name: Optional name to register the card container
             
        Returns:
            The created card container instance
        """
        container = self.create_card_container()
        self._content_layout.addWidget(container, stretch)
        
        if name:
            self.register_widget(name, container)
            
        return container
    
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
    
    # Widget creation methods for centralized repository
    def _create_primary_button(self) -> ModernButton:
        """Create a primary button with default styling."""
        button = ModernButton("Primary", self)
        button.set_custom_style("#4CAF50", "#45a049", "#3d8b40")
        button.setAccessibleName("Primary button")
        button.setAccessibleDescription("Primary action button")
        return button
    
    def _create_secondary_button(self) -> ModernButton:
        """Create a secondary button with default styling."""
        button = ModernButton("Secondary", self)
        button.set_custom_style("#2196F3", "#1e88e5", "#1976d2")
        button.setAccessibleName("Secondary button")
        button.setAccessibleDescription("Secondary action button")
        return button
    
    def _create_danger_button(self) -> ModernButton:
        """Create a danger button with default styling."""
        button = ModernButton("Danger", self)
        button.set_custom_style("#F44336", "#e53935", "#d32f2f")
        button.setAccessibleName("Danger button")
        button.setAccessibleDescription("Danger action button")
        return button
    
    def _create_cancel_button(self) -> ModernButton:
        """Create a cancel button with default styling."""
        button = ModernButton("Cancel", self)
        button.set_custom_style("#9E9E9E", "#757575", "#616161")
        button.setAccessibleName("Cancel button")
        button.setAccessibleDescription("Cancel action button")
        return button
    
    def _create_text_input(self) -> ModernInput:
        """Create a text input with default styling."""
        input_field = ModernInput("Enter text...", self)
        input_field.setAccessibleName("Text input")
        input_field.setAccessibleDescription("Text input field")
        return input_field
    
    def _create_search_input(self) -> ModernInput:
        """Create a search input with default styling."""
        input_field = ModernInput("Search...", self)
        input_field.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 1px solid #888;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
                background-color: #fff;
                outline: 2px solid #4CAF50;
            }
        """)
        input_field.setAccessibleName("Search input")
        input_field.setAccessibleDescription("Search input field")
        return input_field
    
    def _create_email_input(self) -> ModernInput:
        """Create an email input with default styling."""
        input_field = ModernInput("Enter email...", self)
        input_field.setStyleSheet("""
            QLineEdit {
                background-color: #fff;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 1px solid #888;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
                background-color: #fff;
                outline: 2px solid #2196F3;
            }
        """)
        input_field.setAccessibleName("Email input")
        input_field.setAccessibleDescription("Email input field")
        return input_field
    
    def _create_main_layout(self) -> ModernLayout:
        """Create a main layout with default settings."""
        layout = ModernLayout("vbox", self)
        layout.setAccessibleName("Main layout")
        layout.setAccessibleDescription("Main dialog layout")
        return layout
    
    def _create_form_layout(self) -> ModernLayout:
        """Create a form layout with default settings."""
        layout = ModernLayout("vbox", self)
        layout.set_spacing(12)
        layout.set_margins(0, 0, 0, 0)
        layout.setAccessibleName("Form layout")
        layout.setAccessibleDescription("Form dialog layout")
        return layout
    
    def _create_horizontal_layout(self) -> ModernLayout:
        """Create a horizontal layout with default settings."""
        layout = ModernLayout("hbox", self)
        layout.set_spacing(10)
        layout.set_margins(0, 0, 0, 0)
        layout.setAccessibleName("Horizontal layout")
        layout.setAccessibleDescription("Horizontal dialog layout")
        return layout
    
    def _create_default_search_box(self) -> SearchBox:
        """Create a default search box."""
        search_box = SearchBox("Search...", self)
        search_box.setAccessibleName("Search box")
        search_box.setAccessibleDescription("Default search box")
        return search_box
    
    def _create_advanced_search_box(self) -> AdvancedSearchBox:
        """Create an advanced search box."""
        search_box = AdvancedSearchBox("Search...", self)
        search_box.setAccessibleName("Advanced search box")
        search_box.setAccessibleDescription("Advanced search box with additional features")
        return search_box
    
    def _create_card_container(self) -> ScrollableCardContainer:
        """Create a card container with default settings."""
        container = ScrollableCardContainer(self)
        container.setAccessibleName("Card container")
        container.setAccessibleDescription("Scrollable card container")
        return container
    
    def _create_scrollable_container(self) -> ScrollableContainer:
        """Create a scrollable container with default settings."""
        container = ScrollableContainer(self)
        container.setAccessibleName("Scrollable container")
        container.setAccessibleDescription("Scrollable content container")
        return container
    
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
    
    def get_state_manager(self) -> StateManager:
        """
        Get the state manager instance.
         
        Returns:
            The StateManager instance
        """
        return self._state_manager
    
    # Public interface for widget repository
    def get_widget_from_repository(self, category: str, name: str):
        """
        Get a pre-configured widget from the repository.
         
        Args:
            category: Widget category (buttons, inputs, layouts, etc.)
            name: Widget name within the category
             
        Returns:
            The widget instance, or None if not found
        """
        return self._widget_repository.get(category, {}).get(name)
    
    def register_widget(self, name: str, widget):
        """
        Register a widget for centralized management.
         
        Args:
            name: Unique identifier for the widget
            widget: Widget instance to register
        """
        if name in self._widget_registry:
            logger.warning(f"Widget '{name}' already registered, overwriting")
        
        self._widget_registry[name] = widget
        self.widget_registered.emit(name, widget)
        
        # Ensure widget has accessibility features
        if isinstance(widget, AccessibleWidget):
            widget.set_accessible_name(name)
            widget.set_accessible_description(f"{name} widget in {self.windowTitle()} dialog")
        
        logger.debug(f"Widget '{name}' registered in dialog '{self.windowTitle()}'")
    
    def get_registered_widget(self, name: str):
        """
        Get a registered widget by name.
         
        Args:
            name: Name of the widget to retrieve
             
        Returns:
            The widget instance, or None if not found
        """
        return self._widget_registry.get(name)
    
    # Widget creation methods for easy use
    def create_button(self, text: str = "Button", button_type: str = "primary") -> ModernButton:
        """
        Create a button with specified type and text.
         
        Args:
            text: Button text
            button_type: Type of button (primary, secondary, danger, cancel, or custom)
             
        Returns:
            Configured ModernButton instance
        """
        button = ModernButton(text, self)
        
        if button_type == "primary":
            button.set_custom_style("#4CAF50", "#45a049", "#3d8b40")
        elif button_type == "secondary":
            button.set_custom_style("#2196F3", "#1e88e5", "#1976d2")
        elif button_type == "danger":
            button.set_custom_style("#F44336", "#e53935", "#d32f2f")
        elif button_type == "cancel":
            button.set_custom_style("#9E9E9E", "#757575", "#616161")
        
        button.setAccessibleName(f"{text} button")
        button.setAccessibleDescription(f"{text} button in {self.windowTitle()} dialog")
        
        self.widget_created.emit(text, button)
        return button
    
    def create_input(self, placeholder: str = "Enter text...", input_type: str = "text") -> ModernInput:
        """
        Create an input field with specified placeholder and type.
         
        Args:
            placeholder: Placeholder text
            input_type: Type of input (text, search, email, etc.)
             
        Returns:
            Configured ModernInput instance
        """
        input_field = ModernInput(placeholder, self)
        
        if input_type == "search":
            input_field.setStyleSheet("""
                QLineEdit {
                    background-color: #f5f5f5;
                    color: #333;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 14px;
                }
                QLineEdit:hover {
                    border: 1px solid #888;
                }
                QLineEdit:focus {
                    border: 1px solid #4CAF50;
                    background-color: #fff;
                    outline: 2px solid #4CAF50;
                }
            """)
        elif input_type == "email":
            input_field.setStyleSheet("""
                QLineEdit {
                    background-color: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 14px;
                }
                QLineEdit:hover {
                    border: 1px solid #888;
                }
                QLineEdit:focus {
                    border: 1px solid #2196F3;
                    background-color: #fff;
                    outline: 2px solid #2196F3;
                }
            """)
        
        input_field.setAccessibleName(f"{placeholder} input")
        input_field.setAccessibleDescription(f"{placeholder} input field in {self.windowTitle()} dialog")
        
        self.widget_created.emit(placeholder, input_field)
        return input_field
    
    def create_card(self, title: str = "Card Title", content: str = "Card Content") -> ModernCard:
        """
        Create a card with specified title and content.
         
        Args:
            title: Card title
            content: Card content
             
        Returns:
            Configured ModernCard instance
        """
        card = ModernCard(title, content, self)
        card.setAccessibleName(f"{title} card")
        card.setAccessibleDescription(f"{title} card in {self.windowTitle()} dialog")
        
        self.widget_created.emit(title, card)
        return card
    
    def create_layout(self, layout_type: str = "vbox") -> ModernLayout:
        """
        Create a layout with specified type.
         
        Args:
            layout_type: Type of layout (vbox, hbox, grid)
             
        Returns:
            Configured ModernLayout instance
        """
        layout = ModernLayout(layout_type, self)
        layout.setAccessibleName(f"{layout_type} layout")
        layout.setAccessibleDescription(f"{layout_type} layout in {self.windowTitle()} dialog")
        
        self.widget_created.emit(layout_type, layout)
        return layout
    
    def create_flex_layout(self, direction: str = "row", wrap: bool = False) -> FlexLayout:
        """
        Create a flex layout with specified direction.
         
        Args:
            direction: Layout direction (row or column)
            wrap: Whether to enable wrapping
             
        Returns:
            Configured FlexLayout instance
        """
        layout = FlexLayout(direction, wrap, self)
        layout.setAccessibleName(f"{direction} flex layout")
        layout.setAccessibleDescription(f"{direction} flex layout in {self.windowTitle()} dialog")
        
        self.widget_created.emit(f"{direction}_flex", layout)
        return layout
    
    def create_search_box(self, placeholder: str = "Search...") -> SearchBox:
        """
        Create a search box with specified placeholder.
         
        Args:
            placeholder: Placeholder text for search box
             
        Returns:
            Configured SearchBox instance
        """
        search_box = SearchBox(placeholder, self)
        search_box.setAccessibleName(f"{placeholder} search box")
        search_box.setAccessibleDescription(f"{placeholder} search box in {self.windowTitle()} dialog")
        
        self.widget_created.emit(placeholder, search_box)
        return search_box
    
    def create_advanced_search_box(self, placeholder: str = "Search...") -> AdvancedSearchBox:
        """
        Create an advanced search box with specified placeholder.
         
        Args:
            placeholder: Placeholder text for search box
             
        Returns:
            Configured AdvancedSearchBox instance
        """
        search_box = AdvancedSearchBox(placeholder, self)
        search_box.setAccessibleName(f"{placeholder} advanced search box")
        search_box.setAccessibleDescription(f"{placeholder} advanced search box in {self.windowTitle()} dialog")
        
        self.widget_created.emit(f"{placeholder}_advanced", search_box)
        return search_box
    
    def create_memoized_search_box(self, placeholder: str = "Search...", cache_size: int = 100) -> MemoizedSearchBox:
        """
        Create a memoized search box with specified placeholder and cache size.
         
        Args:
            placeholder: Placeholder text for search box
            cache_size: Maximum cache size for memoization
             
        Returns:
            Configured MemoizedSearchBox instance
        """
        search_box = MemoizedSearchBox(placeholder, self, cache_size)
        search_box.setAccessibleName(f"{placeholder} memoized search box")
        search_box.setAccessibleDescription(f"{placeholder} memoized search box in {self.windowTitle()} dialog")
        
        self.widget_created.emit(f"{placeholder}_memoized", search_box)
        return search_box
    
    def create_table(self, rows: int = 0, columns: int = 0) -> CustomTableWidget:
        """
        Create a custom table with specified rows and columns.
         
        Args:
            rows: Number of rows
            columns: Number of columns
             
        Returns:
            Configured CustomTableWidget instance
        """
        table = CustomTableWidget(self)
        if rows > 0 and columns > 0:
            table.setRowCount(rows)
            table.setColumnCount(columns)
        
        table.setAccessibleName("Data table")
        table.setAccessibleDescription(f"Data table with {rows} rows and {columns} columns in {self.windowTitle()} dialog")
        
        self.widget_created.emit("table", table)
        return table
    
    def create_scrollable_container(self, horizontal_scroll: bool = True, vertical_scroll: bool = True) -> ScrollableContainer:
        """
        Create a scrollable container with specified scroll options.
         
        Args:
            horizontal_scroll: Enable horizontal scrolling
            vertical_scroll: Enable vertical scrolling
             
        Returns:
            Configured ScrollableContainer instance
        """
        container = ScrollableContainer(self, horizontal_scroll, vertical_scroll)
        container.setAccessibleName("Scrollable container")
        container.setAccessibleDescription(f"Scrollable container in {self.windowTitle()} dialog")
        
        self.widget_created.emit("scrollable_container", container)
        return container
    
    def create_card_container(self) -> ScrollableCardContainer:
        """
        Create a scrollable card container.
         
        Returns:
            Configured ScrollableCardContainer instance
        """
        container = ScrollableCardContainer(self)
        container.setAccessibleName("Card container")
        container.setAccessibleDescription(f"Card container in {self.windowTitle()} dialog")
        
        self.widget_created.emit("card_container", container)
        return container
    
    def create_progress_indicator(self, size: int = 24) -> ProgressIndicator:
        """
        Create a progress indicator.
         
        Args:
            size: Size of the progress indicator (default: 24)
             
        Returns:
            Configured ProgressIndicator instance
        """
        indicator = ProgressIndicator(size, self)
        indicator.setAccessibleName("Progress indicator")
        indicator.setAccessibleDescription(f"Progress indicator in {self.windowTitle()} dialog")
        
        self.widget_created.emit("progress_indicator", indicator)
        return indicator
    
    def set_theme(self, theme_name: str):
        """
        Set the dialog theme and synchronize with all widgets.
         
        Args:
            theme_name: Name of the theme to apply
        """
        if self._theme_manager:
            self._theme_manager.set_theme(theme_name)
            self._apply_theme(theme_name)
            logger.debug(f"Theme '{theme_name}' applied to dialog '{self.windowTitle()}' and all widgets")
    
    def synchronize_theme_with_parent(self):
        """
        Synchronize the dialog theme with the parent window's theme.
        
        This method ensures that the dialog uses the same theme as its parent window,
        maintaining visual consistency across the application.
        """
        parent = self.parent()
        if parent and hasattr(parent, 'get_theme_manager'):
            parent_theme_manager = parent.get_theme_manager()
            current_theme = parent_theme_manager.get_theme()
            
            # Update our theme manager to match parent
            self._theme_manager.set_theme(current_theme)
            self._apply_theme(current_theme)
            
            logger.debug(f"Dialog '{self.windowTitle()}' theme synchronized with parent window")
        else:
            logger.debug(f"No parent theme manager found for dialog '{self.windowTitle()}'")
    
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



