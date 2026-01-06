# School System GUI Development Guidelines

## Overview

This document provides comprehensive guidelines for developing GUI components using the School System Management framework. These guidelines ensure consistency, maintainability, and accessibility across the application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Base Class Usage](#base-class-usage)
3. [Widget Development](#widget-development)
4. [Theming Guidelines](#theming-guidelines)
5. [Accessibility Requirements](#accessibility-requirements)
6. [State Management](#state-management)
7. [Event Handling](#event-handling)
8. [Testing Standards](#testing-standards)
9. [Performance Optimization](#performance-optimization)
10. [Code Organization](#code-organization)
11. [Documentation Standards](#documentation-standards)

## Getting Started

### Basic Setup

```python
from school_system.gui.base import BaseWindow, BaseDialog
from school_system.gui.base.widgets import ModernButton, ModernInput

class MyWindow(BaseWindow):
    def __init__(self):
        super().__init__("My Window")
        
        # Add widgets
        button = ModernButton("Click Me")
        self.add_widget_to_content(button, name="action_button")

class MyDialog(BaseDialog):
    def __init__(self, parent):
        super().__init__("My Dialog", parent=parent)
        
        # Add content
        input_field = ModernInput()
        self.add_content_widget(input_field, name="input_field")
```

### Project Structure

```
school_system/
└── gui/
    ├── base/                  # Base classes and widgets
    │   ├── base_window.py      # BaseWindow implementation
    │   ├── base_dialog.py      # BaseDialog implementation
    │   ├── widgets/            # Reusable widget library
    │   ├── WIDGET_REUSE_STRATEGY.md  # Widget reuse documentation
    │   └── DEVELOPMENT_GUIDELINES.md  # This document
    ├── windows/               # Application windows
    ├── dialogs/               # Application dialogs
    └── resources/             # Icons, styles, templates
```

## Base Class Usage

### BaseWindow

**When to Use:**
- Main application windows
- Complex interfaces with multiple components
- Windows requiring menu bars and status bars

**Best Practices:**

```python
class StudentWindow(BaseWindow):
    def __init__(self):
        super().__init__("Students Management")
        
        # Always create menu bar for main windows
        self.create_menu_bar()
        
        # Add application-specific menus
        students_menu = self.add_application_menu("Students")
        
        # Initialize UI components
        self._initialize_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _initialize_ui(self):
        """Initialize user interface components."""
        # Create and register widgets
        self._student_table = CustomTableWidget()
        self.register_widget("student_table", self._student_table)
        self.add_widget_to_content(self._student_table)
        
        # Add search functionality
        self._search_box = SearchBox(placeholder_text="Search students...")
        self.register_widget("search_box", self._search_box)
        self.add_widget_to_content(self._search_box)
    
    def _connect_signals(self):
        """Connect signals and slots."""
        self._search_box.search_text_changed.connect(self._handle_search)
        self._student_table.row_selected.connect(self._handle_student_selection)
```

### BaseDialog

**When to Use:**
- Modal and modeless dialogs
- User input forms
- Confirmation prompts
- Temporary interfaces

**Best Practices:**

```python
class StudentEditDialog(BaseDialog):
    def __init__(self, student_data, parent=None):
        super().__init__(
            title=f"Edit Student: {student_data.name}",
            parent=parent,
            standard_buttons=QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        
        # Set dialog icon
        self.set_dialog_icon(QIcon("icons/student.png"))
        
        # Initialize form
        self._initialize_form(student_data)
        
        # Connect signals
        self._connect_signals()
    
    def _initialize_form(self, student_data):
        """Initialize form fields."""
        # Name field
        self._name_input = ModernInput()
        self._name_input.setPlaceholderText("Student Name")
        self._name_input.setText(student_data.name)
        self.add_content_widget(self._name_input, name="name_input")
        
        # ID field (read-only)
        self._id_label = ModernLabel(f"ID: {student_data.id}")
        self.add_content_widget(self._id_label, name="id_label")
    
    def _connect_signals(self):
        """Connect form signals."""
        # Validate input on text change
        self._name_input.textChanged.connect(self._validate_input)
    
    def _validate_input(self):
        """Validate form input."""
        is_valid = len(self._name_input.text()) > 0
        
        # Enable/disable save button
        save_button = self._button_box.button(QDialogButtonBox.StandardButton.Save)
        if save_button:
            save_button.setEnabled(is_valid)
    
    def get_student_data(self):
        """Get updated student data from form."""
        return {
            "name": self._name_input.text(),
            "id": self._id_label.text().replace("ID: ", "")
        }
```

## Widget Development

### Creating Reusable Widgets

**Widget Requirements:**
1. Inherit from appropriate base class
2. Support theming
3. Include accessibility features
4. Provide clear API
5. Document usage and behavior

**Example: Custom Student Card**

```python
class StudentCard(ModernCard):
    """
    Reusable student information card.
    
    Features:
        - Student name and ID display
        - Action buttons (edit, view)
        - Theming support
        - Accessibility compliance
    """
    
    # Signal for student actions
    student_action_requested = pyqtSignal(str, int)  # action_type, student_id
    
    def __init__(self, student_data, parent=None):
        super().__init__(parent)
        
        # Store student data
        self._student_data = student_data
        
        # Initialize UI
        self._initialize_ui()
        
        # Set accessibility
        self._initialize_accessibility()
    
    def _initialize_ui(self):
        """Initialize user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Student info
        self._name_label = ModernLabel(self._student_data.name)
        self._name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self._id_label = ModernLabel(f"ID: {self._student_data.id}")
        self._id_label.setStyleSheet("font-size: 14px; color: #666;")
        
        self._class_label = ModernLabel(f"Class: {self._student_data.class_name}")
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        
        self._edit_button = ModernButton("Edit")
        self._edit_button.clicked.connect(lambda: self._handle_action("edit"))
        
        self._view_button = ModernButton("View Details")
        self._view_button.clicked.connect(lambda: self._handle_action("view"))
        
        button_layout.addWidget(self._edit_button)
        button_layout.addWidget(self._view_button)
        
        # Assemble layout
        layout.addWidget(self._name_label)
        layout.addWidget(self._id_label)
        layout.addWidget(self._class_label)
        layout.addLayout(button_layout)
    
    def _initialize_accessibility(self):
        """Initialize accessibility features."""
        self.setAccessibleName(f"Student card for {self._student_data.name}")
        self.setAccessibleDescription(
            f"Student information: {self._student_data.name}, "
            f"ID: {self._student_data.id}, Class: {self._student_data.class_name}"
        )
        
        # Set accessibility for child widgets
        self._name_label.setAccessibleName("Student name")
        self._id_label.setAccessibleName("Student ID")
        self._class_label.setAccessibleName("Student class")
        
        self._edit_button.setAccessibleName("Edit student")
        self._view_button.setAccessibleName("View student details")
    
    def _handle_action(self, action_type):
        """Handle button actions."""
        self.student_action_requested.emit(action_type, self._student_data.id)
    
    def update_student_data(self, new_data):
        """Update student data and refresh display."""
        self._student_data = new_data
        self._name_label.setText(new_data.name)
        self._id_label.setText(f"ID: {new_data.id}")
        self._class_label.setText(f"Class: {new_data.class_name}")
        
        # Update accessibility
        self.setAccessibleName(f"Student card for {new_data.name}")
    
    def apply_theme(self, theme_name):
        """Apply theme to the widget."""
        # Get theme colors
        theme_manager = ThemeManager()
        
        # Apply theme-specific styling
        if theme_name == "dark":
            self.setStyleSheet(f"""
                background-color: {theme_manager.get_color('background')};
                border: 1px solid {theme_manager.get_color('border')};
                border-radius: 6px;
            """)
        else:
            # Light theme or custom
            self.setStyleSheet(f"""
                background-color: {theme_manager.get_color('background')};
                border: 1px solid {theme_manager.get_color('border')};
                border-radius: 6px;
            """)
```

### Widget Registration

Always register widgets for centralized management:

```python
class StudentWindow(BaseWindow):
    def __init__(self):
        super().__init__("Students")
        
        # Good: Register widgets
        self._table = CustomTableWidget()
        self.register_widget("student_table", self._table)
        self.add_widget_to_content(self._table)
        
        # Bad: Unregistered widget
        # self.add_widget_to_content(QPushButton("Unregistered"))
```

## Theming Guidelines

### Theme Management

```python
# Set theme for entire window
window.set_theme("dark")

# Get current theme
current_theme = window.get_theme()

# Access theme manager
theme_manager = window.get_theme_manager()

# Get theme colors
primary_color = theme_manager.get_color("primary")
background_color = theme_manager.get_color("background")
```

### Theme-Aware Widgets

```python
class ThemeAwareWidget(AccessibleWidget):
    def __init__(self):
        super().__init__()
        self._theme_manager = ThemeManager()
        
        # Connect to theme changes
        self._theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, theme_name):
        """Handle theme changes."""
        self._apply_theme(theme_name)
    
    def _apply_theme(self, theme_name):
        """Apply theme-specific styling."""
        colors = {
            "primary": self._theme_manager.get_color("primary"),
            "background": self._theme_manager.get_color("background"),
            "text": self._theme_manager.get_color("text"),
            "border": self._theme_manager.get_color("border")
        }
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
            }}
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
            }}
        """)
```

### Custom Themes

```python
# Add custom theme
theme_manager = ThemeManager()
theme_manager.add_theme("school_theme", {
    "primary": "#2E86C1",
    "secondary": "#1A5276",
    "background": "#F8F9FA",
    "text": "#2C3E50",
    "border": "#BDC3C7"
})

# Apply custom theme
window.set_theme("school_theme")
```

## Accessibility Requirements

### Minimum Requirements

All widgets must implement:

```python
class AccessibleWidgetExample(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Set accessible name and description
        self.setAccessibleName("Widget Name")
        self.setAccessibleDescription("Detailed description of widget purpose")
        
        # 2. Enable keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # 3. Support high-contrast mode
        self._high_contrast = False
    
    def enable_high_contrast(self, enabled):
        """Enable or disable high-contrast mode."""
        self._high_contrast = enabled
        self._update_styles()
    
    def keyPressEvent(self, event):
        """Handle keyboard events for accessibility."""
        if event.key() == Qt.Key.Key_Tab:
            # Handle tab navigation
            event.accept()
        elif event.key() == Qt.Key.Key_Return:
            # Handle activation
            self._handle_activation()
            event.accept()
        else:
            super().keyPressEvent(event)
```

### Keyboard Navigation

**Required Keyboard Support:**

| Key | Function |
|-----|----------|
| Tab | Navigate to next widget |
| Shift+Tab | Navigate to previous widget |
| Enter/Return | Activate current widget |
| Space | Toggle checkboxes/buttons |
| Escape | Close dialogs/cancel actions |
| Arrow Keys | Navigate within widgets |

### Screen Reader Support

```python
# Set proper accessible names
button.setAccessibleName("Submit Form")
button.setAccessibleDescription("Submits the student registration form")

# For complex widgets, provide detailed context
table.setAccessibleName("Students Table")
table.setAccessibleDescription("Table showing all registered students with columns: ID, Name, Class, Status")
```

### High-Contrast Mode

```python
class HighContrastWidget(AccessibleWidget):
    def enable_high_contrast(self, enabled):
        """Enable or disable high-contrast mode."""
        if enabled:
            self.setStyleSheet("""
                background-color: black;
                color: white;
                border: 2px solid white;
                font-size: 16px;
                font-weight: bold;
            """)
        else:
            # Revert to normal theme
            self._apply_theme(self._current_theme)
```

## State Management

### Using StateManager

```python
class StateManagedWindow(BaseWindow):
    def __init__(self):
        super().__init__("State Managed Window")
        
        # Get state manager
        self._state_manager = self.get_state_manager()
        
        # Connect to state changes
        self._state_manager.state_changed.connect(self._handle_state_change)
        
        # Initialize state
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize application state."""
        # Set initial state
        self._state_manager.set_state("search_query", "")
        self._state_manager.set_state("current_student", None)
        self._state_manager.set_state("filter_active", False)
    
    def _handle_state_change(self, state_name, state_value):
        """Handle state changes."""
        if state_name == "search_query":
            self._handle_search_query_change(state_value)
        elif state_name == "current_student":
            self._handle_student_change(state_value)
    
    def _handle_search_query_change(self, query):
        """Handle search query changes."""
        # Update search results
        results = search_students(query)
        self._update_student_table(results)
    
    def _handle_student_change(self, student):
        """Handle current student changes."""
        if student:
            self._show_student_details(student)
        else:
            self._clear_student_details()
```

### State Management Best Practices

1. **Centralize State**: Use StateManager for shared state
2. **Immutable Updates**: Treat state as immutable where possible
3. **Clear Naming**: Use descriptive state names
4. **Validation**: Validate state changes
5. **Documentation**: Document state purpose and usage

```python
# Good: Centralized state management
state_manager.set_state("student_filter", {"class": "10A", "status": "active"})

# Bad: Distributed state
self._current_filter = {"class": "10A", "status": "active"}  # Hard to track
```

## Event Handling

### Signal-Based Communication

```python
class EventDrivenWidget(AccessibleWidget):
    # Define signals
    data_loaded = pyqtSignal(list)
    selection_changed = pyqtSignal(int)
    action_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Connect internal signals
        self._connect_internal_signals()
    
    def _connect_internal_signals(self):
        """Connect internal signals."""
        # Example: Connect button clicks to signal emission
        self._button.clicked.connect(
            lambda: self.action_requested.emit("button_click")
        )
    
    def load_data(self, data):
        """Load data and emit signal."""
        # Process data
        processed_data = self._process_data(data)
        
        # Emit signal
        self.data_loaded.emit(processed_data)
```

### Event Handling Best Practices

```python
class WellDesignedWindow(BaseWindow):
    def __init__(self):
        super().__init__("Well Designed")
        
        # Initialize widgets
        self._initialize_widgets()
        
        # Connect signals (separate method for clarity)
        self._connect_signals()
    
    def _initialize_widgets(self):
        """Initialize all widgets."""
        self._table = CustomTableWidget()
        self._search_box = SearchBox()
        
        # Register widgets
        self.register_widget("table", self._table)
        self.register_widget("search", self._search_box)
    
    def _connect_signals(self):
        """Connect all signals."""
        # Widget to widget communication
        self._search_box.search_text_changed.connect(
            self._table.apply_search_filter
        )
        
        # Widget to window communication
        self._table.row_selected.connect(self._handle_row_selection)
        
        # Window signals
        self.window_ready.connect(self._on_window_ready)
    
    def _handle_row_selection(self, row):
        """Handle table row selection."""
        student_id = self._table.get_row_data(row)['id']
        self._load_student_details(student_id)
    
    def _on_window_ready(self):
        """Handle window ready event."""
        self.update_status("Window initialized and ready")
        self._load_initial_data()
```

### Avoiding Common Pitfalls

**Bad: Direct Method Calls**
```python
# Tight coupling - avoid this
class BadWidget(QWidget):
    def some_method(self):
        parent_widget.handle_event()  # Direct call to parent
```

**Good: Signal-Based Communication**
```python
# Loose coupling - preferred
class GoodWidget(QWidget):
    event_occurred = pyqtSignal(str)
    
    def some_method(self):
        self.event_occurred.emit("event_data")  # Signal-based
```

## Testing Standards

### Unit Testing

```python
class TestMyWidget(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication([])
        self.widget = MyWidget()
    
    def tearDown(self):
        """Clean up test fixtures."""
        del self.widget
        self.app.quit()
    
    def test_initialization(self):
        """Test widget initialization."""
        self.assertIsNotNone(self.widget)
        self.assertEqual(self.widget.windowTitle(), "Expected Title")
    
    def test_functionality(self):
        """Test widget functionality."""
        # Test method calls
        result = self.widget.some_method()
        self.assertEqual(result, expected_value)
    
    def test_signal_emission(self):
        """Test signal emission."""
        with patch.object(self.widget, 'some_signal') as mock_signal:
            self.widget.trigger_signal()
            mock_signal.emit.assert_called_once_with(expected_args)
```

### Integration Testing

```python
class TestWidgetIntegration(unittest.TestCase):
    def setUp(self):
        """Set up integration test."""
        self.app = QApplication([])
        self.window = BaseWindow("Test Window")
        self.dialog = BaseDialog("Test Dialog", parent=self.window)
    
    def tearDown(self):
        """Clean up integration test."""
        self.dialog.close()
        self.window.close()
        self.app.quit()
    
    def test_parent_child_relationship(self):
        """Test parent-child widget relationships."""
        # Verify parent-child relationship
        self.assertEqual(self.dialog.parent(), self.window)
        
        # Verify theme inheritance
        self.window.set_theme("dark")
        self.assertEqual(self.dialog.get_theme_manager().get_theme(), "dark")
```

### Test Coverage Requirements

1. **Unit Tests**: 90%+ coverage for individual widgets
2. **Integration Tests**: Test widget interactions
3. **Theming Tests**: Verify theme consistency
4. **Accessibility Tests**: Test keyboard navigation and screen reader support
5. **State Tests**: Test state management behavior

## Performance Optimization

### Widget Creation

```python
# Good: Lazy loading
class LazyWidgetLoader:
    def __init__(self, window):
        self._window = window
        self._widget = None
    
    def get_widget(self):
        if self._widget is None:
            self._widget = ExpensiveWidget()
            self._window.register_widget("lazy_widget", self._widget)
        return self._widget

# Bad: Immediate loading of all widgets
class BadWindow(BaseWindow):
    def __init__(self):
        super().__init__("Bad Window")
        # Loads all widgets immediately, even if not needed
        self._widget1 = ExpensiveWidget()
        self._widget2 = AnotherExpensiveWidget()
```

### Memory Management

```python
class MemoryEfficientWindow(BaseWindow):
    def closeEvent(self, event):
        """Clean up resources on close."""
        # Clean up widgets
        for widget in self._widget_registry.values():
            if hasattr(widget, 'cleanup'):
                widget.cleanup()
        
        # Clear references
        self._widget_registry.clear()
        
        super().closeEvent(event)
```

### Virtualization

```python
# Good: Use virtual scrolling for large datasets
table = CustomTableWidget()
table.setModel(VirtualScrollModel(
    data_provider=lambda row, col: get_data(row, col),
    row_count=100000,  # Large dataset
    column_count=10
))

# Bad: Load all data at once
table.set_data(get_all_data(), headers)  # Memory intensive
```

## Code Organization

### File Structure

```
# Good organization
school_system/
└── gui/
    ├── base/                  # Base classes
    │   ├── base_window.py      # BaseWindow
    │   ├── base_dialog.py      # BaseDialog
    │   └── widgets/            # Widget library
    ├── windows/               # Application windows
    │   ├── student_window.py   # StudentWindow
    │   ├── book_window.py      # BookWindow
    │   └── ...
    ├── dialogs/               # Application dialogs
    │   ├── student_dialog.py    # StudentDialog
    │   ├── confirm_dialog.py    # ConfirmDialog
    │   └── ...
    └── resources/             # Resources
        ├── icons/              # Icons
        ├── styles/             # Stylesheets
        └── templates/           # Templates
```

### Class Structure

```python
class WellOrganizedWindow(BaseWindow):
    """
    Well-organized window class.
    
    Features:
        - Clear documentation
        - Logical method organization
        - Separation of concerns
    """
    
    def __init__(self):
        super().__init__("Well Organized")
        
        # Initialize components in logical order
        self._initialize_ui()
        self._initialize_data()
        self._connect_signals()
        self._setup_shortcuts()
    
    # UI Initialization
    def _initialize_ui(self):
        """Initialize user interface components."""
        pass
    
    def _initialize_data(self):
        """Initialize data components."""
        pass
    
    # Signal Handling
    def _connect_signals(self):
        """Connect signals and slots."""
        pass
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        pass
    
    # Event Handlers
    def _handle_event_type(self, event_data):
        """Handle specific event type."""
        pass
    
    # Public API
    def refresh_data(self):
        """Public method to refresh data."""
        pass
    
    def export_data(self, format):
        """Public method to export data."""
        pass
```

### Method Organization

1. **Initialization Methods**: `_initialize_*`
2. **Event Handlers**: `_handle_*`
3. **Helper Methods**: `_create_*`, `_setup_*`
4. **Public API**: Regular method names
5. **Signal Handlers**: `_on_*`

## Documentation Standards

### Class Documentation

```python
class WellDocumentedWidget(AccessibleWidget):
    """
    Brief description of the widget's purpose.
    
    Detailed description explaining:
    - What the widget does
    - When to use it
    - Key features
    - Usage examples
    
    Features:
        - Feature 1: Description
        - Feature 2: Description
        - Feature 3: Description
    
    Usage:
        widget = WellDocumentedWidget(parent)
        widget.set_property(value)
        widget.signal.connect(handler)
    
    Signals:
        signal_name: Description of when it's emitted
    """
```

### Method Documentation

```python
def well_documented_method(self, param1, param2):
    """
    Brief description of what the method does.
    
    Detailed description explaining:
    - Purpose of the method
    - What it does
    - Side effects
    - Return value meaning
    
    Args:
        param1 (type): Description of parameter 1
        param2 (type): Description of parameter 2
        
    Returns:
        return_type: Description of return value
        
    Raises:
        ExceptionType: Description of when/why raised
        
    Example:
        result = obj.well_documented_method(value1, value2)
    """
    # Method implementation
```

### Signal Documentation

```python
class DocumentedSignals(QWidget):
    """Widget with well-documented signals."""
    
    # Signal documentation should be near the signal definition
    data_loaded = pyqtSignal(list)
    """
    Emitted when data loading is complete.
    
    Args:
        data (list): List of loaded data items
    """
    
    selection_changed = pyqtSignal(int, str)
    """
    Emitted when selection changes.
    
    Args:
        index (int): Index of selected item
        item_id (str): ID of selected item
    """
```

## Best Practices Checklist

### Before Committing Code

- [ ] All widgets inherit from appropriate base classes
- [ ] Widgets are properly registered in parent windows
- [ ] Theming is consistently applied
- [ ] Accessibility features are implemented
- [ ] Signals are used for communication
- [ ] State management is centralized
- [ ] Code is properly documented
- [ ] Unit tests are added/updated
- [ ] Integration tests pass
- [ ] Performance considerations addressed

### Code Review Checklist

- [ ] Follows established patterns and conventions
- [ ] Proper error handling
- [ ] Memory management (no leaks)
- [ ] Thread safety (if applicable)
- [ ] Internationalization support (if needed)
- [ ] Cross-platform compatibility
- [ ] Consistent naming conventions
- [ ] Proper exception handling
- [ ] Logging for important events

## Conclusion

By following these guidelines, you ensure:

1. **Consistency**: Uniform look and behavior across the application
2. **Maintainability**: Easy to understand and modify code
3. **Accessibility**: Full compliance with WCAG 2.1 standards
4. **Performance**: Efficient resource usage
5. **Reliability**: Robust error handling and testing
6. **Extensibility**: Easy to add new features

These guidelines help maintain a professional, accessible, and maintainable GUI framework for the School System Management application.