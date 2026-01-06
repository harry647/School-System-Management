"""
Base Window Implementation for the School System GUI Framework

This module provides a robust base window class that implements:
- Modular widget reuse across the application
- Comprehensive theming support (light/dark modes)
- Full accessibility compliance (WCAG 2.1)
- Consistent layout management
- State management integration

The BaseWindow serves as the foundation for all application windows,
ensuring visual and functional consistency throughout the application.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from school_system.gui.base.widgets import (
    ThemeManager, StateManager, AccessibleWidget,
    ModernStatusBar, ScrollableContainer, ScrollableCardContainer,
    ModernButton, ModernInput, ModernCard,
    ModernLayout, FlexLayout,
    SearchBox, AdvancedSearchBox, MemoizedSearchBox,
    CustomTableWidget, SortFilterProxyModel, VirtualScrollModel,
    ProgressIndicator
)
from school_system.config.logging import logger


class BaseWindow(QMainWindow):
    """
    Base window class providing core functionality for all application windows.
    
    Features:
        - Centralized widget repository with pre-configured components
        - Modular widget reuse system
        - Comprehensive theming support
        - Full accessibility compliance
        - Consistent layout management
        - State management integration
        - Event-driven architecture
        - Clean, consistent interface for widget creation and management
    
    The BaseWindow serves as a centralized widget repository, providing easy access
    to all GUI components including buttons, inputs, cards, layouts, search boxes,
    tables, and containers. This eliminates redundant imports and reimplementation
    across the application.
    """
    
    # Signals for event-driven architecture
    window_ready = pyqtSignal()
    theme_changed = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    
    def __init__(self, title: str = "School System", parent=None):
        """
        Initialize the base window.
        
        Args:
            title: Window title
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Core systems
        self._theme_manager = ThemeManager(self)
        self._state_manager = StateManager(self)
        self._widget_registry = {}
        
        # Window setup
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        
        # Main layout structure
        self._central_widget = QWidget(self)
        self._main_layout = QVBoxLayout(self._central_widget)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Content area with scrollable container
        self._content_area = ScrollableContainer(self._central_widget)
        # Use the scrollable container's internal content layout
        self._content_layout = self._content_area.content_layout
        logger.info(f"Content layout initialized: {self._content_layout}")
        logger.info(f"Content widget: {self._content_area.content_widget}")
        logger.info(f"Content widget layout: {self._content_area.content_widget.layout()}")
        self._content_layout.setContentsMargins(10, 10, 10, 10)
        self._content_layout.setSpacing(10)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Status bar
        self._status_bar = ModernStatusBar()
        
        # Assemble the window
        logger.info(f"Adding content area to main layout. Content area: {self._content_area}")
        logger.info(f"Content area widget: {self._content_area.widget()}")
        logger.info(f"Content area layout: {self._content_area.layout()}")
        self._main_layout.addWidget(self._content_area, 1)
        self.setCentralWidget(self._central_widget)
        self.setStatusBar(self._status_bar)
        
        # Initialize systems
        self._initialize_themes()
        self._initialize_accessibility()
        self._initialize_state_management()
        self._initialize_widget_repository()
        
        logger.info(f"BaseWindow '{title}' initialized")
        
        # Emit window ready signal
        self.window_ready.emit()
    
    def _initialize_themes(self):
        """Initialize theming system."""
        # Connect theme change signals
        self._theme_manager.theme_changed.connect(self._apply_theme)
        
        # Set default theme
        self.set_theme("light")
    
    def _initialize_accessibility(self):
        """Initialize accessibility features."""
        # Set accessibility properties for the window
        self.setAccessibleName(f"{self.windowTitle()} Window")
        self.setAccessibleDescription(f"Main application window for {self.windowTitle()}")
        
        # Enable keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def _initialize_state_management(self):
        """Initialize state management system."""
        # Connect state change signals
        self._state_manager.state_changed.connect(self._handle_state_change)
    
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
        
        self._widget_repository['inputs']['text'] = self._create_text_input()
        self._widget_repository['inputs']['search'] = self._create_search_input()
        
        self._widget_repository['layouts']['main'] = self._create_main_layout()
        self._widget_repository['layouts']['form'] = self._create_form_layout()
        
        self._widget_repository['search_boxes']['default'] = self._create_default_search_box()
        
        self._widget_repository['containers']['card'] = self._create_card_container()
    
    def _apply_theme(self, theme_name: str):
        """Apply the specified theme to the window and all child widgets."""
        qss = self._theme_manager.generate_qss()
        logger.info(f"Applying theme '{theme_name}' with QSS length: {len(qss)}")
        logger.info(f"Content layout has {self._content_layout.count()} items before theme application")
        
        self.setStyleSheet(qss)
        
        # Apply theme to all registered widgets
        for widget_name, widget in self._widget_registry.items():
            if hasattr(widget, 'apply_theme'):
                widget.apply_theme(theme_name)
        
        # Update status bar theme
        self._status_bar.apply_theme(theme_name)
        
        logger.info(f"Content layout has {self._content_layout.count()} items after theme application")
        logger.info(f"Theme '{theme_name}' applied to window '{self.windowTitle()}'")
        self.theme_changed.emit(theme_name)
    
    def _handle_state_change(self, state_name: str, state_value):
        """Handle state changes from the state manager."""
        logger.debug(f"State change: {state_name} = {state_value}")
        
        # Widgets can override this to handle specific state changes
    
    # Widget creation methods
    def _create_primary_button(self) -> ModernButton:
        """Create a primary button with default styling."""
        button = ModernButton("Primary", self)
        button.set_custom_style("#4CAF50", "#45a049", "#3d8b40")
        return button
    
    def _create_secondary_button(self) -> ModernButton:
        """Create a secondary button with default styling."""
        button = ModernButton("Secondary", self)
        button.set_custom_style("#2196F3", "#1e88e5", "#1976d2")
        return button
    
    def _create_danger_button(self) -> ModernButton:
        """Create a danger button with default styling."""
        button = ModernButton("Danger", self)
        button.set_custom_style("#F44336", "#e53935", "#d32f2f")
        return button
    
    def _create_text_input(self) -> ModernInput:
        """Create a text input with default styling."""
        return ModernInput("Enter text...", self)
    
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
        return input_field
    
    def _create_main_layout(self) -> ModernLayout:
        """Create a main layout with default settings."""
        return ModernLayout("vbox", self)
    
    def _create_form_layout(self) -> ModernLayout:
        """Create a form layout with default settings."""
        layout = ModernLayout("vbox", self)
        layout.set_spacing(12)
        layout.set_margins(0, 0, 0, 0)
        return layout
    
    def _create_default_search_box(self) -> SearchBox:
        """Create a default search box."""
        return SearchBox("Search...", self)
    
    def _create_card_container(self) -> ScrollableCardContainer:
        """Create a card container with default settings."""
        return ScrollableCardContainer(self)
    
    def set_theme(self, theme_name: str):
        """Set the window theme."""
        self._theme_manager.set_theme(theme_name)
    
    def get_theme(self) -> str:
        """Get the current theme name."""
        return self._theme_manager.get_theme()
    
    def register_widget(self, name: str, widget: QWidget):
        """
        Register a widget for centralized management.
        
        Args:
            name: Unique identifier for the widget
            widget: Widget instance to register
        """
        if name in self._widget_registry:
            logger.warning(f"Widget '{name}' already registered, overwriting")
        
        self._widget_registry[name] = widget
        
        # Ensure widget has accessibility features
        if isinstance(widget, AccessibleWidget):
            widget.set_accessible_name(name)
            widget.set_accessible_description(f"{name} widget in {self.windowTitle()}")
        
        logger.debug(f"Widget '{name}' registered")
    
    def get_widget(self, name: str) -> QWidget:
        """
        Get a registered widget by name.
        
        Args:
            name: Name of the widget to retrieve
            
        Returns:
            The widget instance, or None if not found
        """
        return self._widget_registry.get(name)
    
    def add_widget_to_content(self, widget: QWidget, stretch: int = 0, name: str = None):
        """
        Add a widget to the main content area.
        
        Args:
            widget: Widget to add
            stretch: Layout stretch factor
            name: Optional name to register the widget
        """
        self._content_layout.addWidget(widget, stretch)
        
        if name:
            self.register_widget(name, widget)
    
    def add_layout_to_content(self, layout, stretch: int = 0):
        """
        Add a layout to the main content area.

        Args:
            layout: Layout to add (QLayout, ModernLayout, or FlexLayout)
            stretch: Layout stretch factor
        """
        # Handle ModernLayout and FlexLayout by adding them as widgets
        if hasattr(layout, '_layout'):
            # FlexLayout and ModernLayout are QWidgets, add them as widgets
            self._content_layout.addWidget(layout, stretch)
        else:
            # Regular QLayout, add it directly
            self._content_layout.addLayout(layout, stretch)
    
    def add_button_to_content(self, text: str = "Button", button_type: str = "primary",
                            stretch: int = 0, name: str = None) -> ModernButton:
        """
        Create and add a button to the main content area.
        
        Args:
            text: Button text
            button_type: Type of button (primary, secondary, danger)
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
    
    def add_input_to_content(self, placeholder: str = "Enter text...", stretch: int = 0,
                           name: str = None) -> ModernInput:
        """
        Create and add an input field to the main content area.
        
        Args:
            placeholder: Placeholder text
            stretch: Layout stretch factor
            name: Optional name to register the input
            
        Returns:
            The created input instance
        """
        input_field = self.create_input(placeholder)
        self._content_layout.addWidget(input_field, stretch)
        
        if name:
            self.register_widget(name, input_field)
            
        return input_field
    
    def add_card_to_content(self, title: str = "Card Title", content: str = "Card Content",
                          stretch: int = 0, name: str = None) -> ModernCard:
        """
        Create and add a card to the main content area.
        
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
    
    def add_search_box_to_content(self, placeholder: str = "Search...", stretch: int = 0,
                                name: str = None) -> SearchBox:
        """
        Create and add a search box to the main content area.
        
        Args:
            placeholder: Placeholder text
            stretch: Layout stretch factor
            name: Optional name to register the search box
            
        Returns:
            The created search box instance
        """
        search_box = self.create_search_box(placeholder)
        self._content_layout.addWidget(search_box, stretch)
        
        if name:
            self.register_widget(name, search_box)
            
        return search_box
    
    def add_table_to_content(self, rows: int = 0, columns: int = 0, stretch: int = 0,
                           name: str = None) -> CustomTableWidget:
        """
        Create and add a table to the main content area.
        
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
    
    def create_menu_bar(self):
        """
        Create and configure the menu bar.
        
        Returns:
            The menu bar instance
        """
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # Theme submenu
        theme_menu = file_menu.addMenu("Theme")
        
        # Add theme actions
        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_action)
        
        dark_action = QAction("Dark", self)
        dark_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_action)
        
        # Separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        return menu_bar
    
    def update_status(self, message: str, timeout: int = 0):
        """
        Update the status bar message.
        
        Args:
            message: Status message to display
            timeout: Display duration in milliseconds (0 for permanent)
        """
        if timeout > 0:
            self._status_bar.show_temporary_message(message, timeout)
        else:
            self._status_bar.show_permanent_message(message)
        
        self.status_updated.emit(message)
    
    def show_progress(self, value: int, max_value: int = 100):
        """
        Show progress in the status bar.
        
        Args:
            value: Current progress value
            max_value: Maximum progress value
        """
        self._status_bar.show_progress(value, max_value)
    
    def hide_progress(self):
        """Hide the progress indicator."""
        self._status_bar.hide_progress()
    
    def enable_high_contrast(self, enabled: bool):
        """
        Enable or disable high-contrast mode for accessibility.
        
        Args:
            enabled: Whether to enable high-contrast mode
        """
        for widget in self._widget_registry.values():
            if hasattr(widget, 'enable_high_contrast'):
                widget.enable_high_contrast(enabled)
        
        logger.info(f"High-contrast mode {'enabled' if enabled else 'disabled'}")
    
    def get_state_manager(self) -> StateManager:
        """
        Get the state manager instance.
        
        Returns:
            The StateManager instance
        """
        return self._state_manager
    
    def get_theme_manager(self) -> ThemeManager:
        """
        Get the theme manager instance.
        
        Returns:
            The ThemeManager instance
        """
        return self._theme_manager
    
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
    
    def create_button(self, text: str = "Button", button_type: str = "primary") -> ModernButton:
        """
        Create a button with specified type and text.
        
        Args:
            text: Button text
            button_type: Type of button (primary, secondary, danger, or custom)
            
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
        
        return button
    
    def create_input(self, placeholder: str = "Enter text...", input_type: str = "text") -> ModernInput:
        """
        Create an input field with specified placeholder and type.
        
        Args:
            placeholder: Placeholder text
            input_type: Type of input (text, search, etc.)
            
        Returns:
            Configured ModernInput instance
        """
        return ModernInput(placeholder, self)
    
    def create_card(self, title: str = "Card Title", content: str = "Card Content") -> ModernCard:
        """
        Create a card with specified title and content.
        
        Args:
            title: Card title
            content: Card content
            
        Returns:
            Configured ModernCard instance
        """
        return ModernCard(title, content, self)
    
    def create_layout(self, layout_type: str = "vbox") -> ModernLayout:
        """
        Create a layout with specified type.
        
        Args:
            layout_type: Type of layout (vbox, hbox, grid)
            
        Returns:
            Configured ModernLayout instance
        """
        return ModernLayout(layout_type, self)
    
    def create_flex_layout(self, direction: str = "row", wrap: bool = False) -> FlexLayout:
        """
        Create a flex layout with specified direction.
        
        Args:
            direction: Layout direction (row or column)
            wrap: Whether to enable wrapping
            
        Returns:
            Configured FlexLayout instance
        """
        return FlexLayout(direction, wrap, self)
    
    def create_search_box(self, placeholder: str = "Search...") -> SearchBox:
        """
        Create a search box with specified placeholder.
        
        Args:
            placeholder: Placeholder text for search box
            
        Returns:
            Configured SearchBox instance
        """
        return SearchBox(placeholder, self)
    
    def create_advanced_search_box(self, placeholder: str = "Search...") -> AdvancedSearchBox:
        """
        Create an advanced search box with specified placeholder.
        
        Args:
            placeholder: Placeholder text for search box
            
        Returns:
            Configured AdvancedSearchBox instance
        """
        return AdvancedSearchBox(placeholder, self)
    
    def create_memoized_search_box(self, placeholder: str = "Search...", cache_size: int = 100) -> MemoizedSearchBox:
        """
        Create a memoized search box with specified placeholder and cache size.
        
        Args:
            placeholder: Placeholder text for search box
            cache_size: Maximum cache size for memoization
            
        Returns:
            Configured MemoizedSearchBox instance
        """
        return MemoizedSearchBox(placeholder, self, cache_size)
    
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
        return ScrollableContainer(self, horizontal_scroll, vertical_scroll)
    
    def create_card_container(self) -> ScrollableCardContainer:
        """
        Create a scrollable card container.
        
        Returns:
            Configured ScrollableCardContainer instance
        """
        return ScrollableCardContainer(self)
    
    def create_progress_indicator(self, size: int = 24) -> ProgressIndicator:
        """
        Create a progress indicator.
        
        Args:
            size: Size of the progress indicator (default: 24)
            
        Returns:
            Configured ProgressIndicator instance
        """
        return ProgressIndicator(size, self)
    
    def closeEvent(self, event):
        """
        Handle window close events.
        
        Args:
            event: Close event
        """
        logger.info(f"Window '{self.windowTitle()}' closing")
        
        # Clean up resources
        for widget in self._widget_registry.values():
            if hasattr(widget, 'cleanup'):
                widget.cleanup()
        
        super().closeEvent(event)


class BaseApplicationWindow(BaseWindow):
    """
    Extended base window with application-specific features.
    
    This class extends BaseWindow with additional functionality
    commonly needed in application windows.
    """
    
    def __init__(self, title: str = "School System", parent=None):
        """
        Initialize the application window.
        
        Args:
            title: Window title
            parent: Parent widget
        """
        super().__init__(title, parent)
        
        # Application-specific features
        self._initialize_application_features()
    
    def _initialize_application_features(self):
        """Initialize application-specific features."""
        # Create menu bar with application menus
        self._menu_bar = self.create_menu_bar()
        
        # Add help menu
        help_menu = self._menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _show_about(self):
        """Show about dialog."""
        about_text = f"""{self.windowTitle()}

Version: 1.0.0

A comprehensive school management system for:
• Students and Teachers
• Books and Library
• Furniture and Equipment
• User Accounts and Permissions

Developed for efficient school administration."""
        
        # This would typically show a proper dialog
        logger.info(f"About dialog shown for {self.windowTitle()}")
        self.update_status(f"About {self.windowTitle()} displayed")
    
    def add_application_menu(self, menu_title: str):
        """
        Add an application-specific menu.
        
        Args:
            menu_title: Title of the menu to add
            
        Returns:
            The created menu
        """
        return self._menu_bar.addMenu(menu_title)