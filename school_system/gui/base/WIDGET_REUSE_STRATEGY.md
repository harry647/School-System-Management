# Widget Reuse Strategy for School System GUI Framework

## Overview

This document outlines the comprehensive widget reuse strategy for the School System Management application. The strategy ensures visual and functional consistency across the application while maximizing code reuse and maintainability.

## Core Principles

1. **Modular Design**: Widgets are designed as self-contained, reusable components
2. **Consistent Styling**: All widgets adhere to the application's theme system
3. **Accessibility First**: Every widget includes accessibility features by default
4. **State Management**: Widgets integrate with the centralized state management system
5. **Event-Driven Architecture**: Widgets communicate through signals and events

## Widget Hierarchy

```
BaseWindow (QMainWindow)
├── BaseDialog (QDialog)
├── Widget Registry (Centralized management)
├── ThemeManager (Consistent theming)
├── StateManager (Shared state)
└── AccessibleWidget (Accessibility base)
    ├── ModernButton
    ├── ModernInput
    ├── ModernCard
    ├── CustomTableWidget
    ├── SearchBox
    ├── ModernStatusBar
    └── ScrollableContainer
```

## Widget Reuse Implementation

### 1. Centralized Widget Registry

The `BaseWindow` class includes a widget registry system that:

- Tracks all widgets in the application
- Provides centralized access to widgets
- Ensures consistent theming and accessibility
- Facilitates cleanup and resource management

**Usage Example:**
```python
# Register a widget
self.register_widget("student_table", student_table_widget)

# Retrieve a widget
table = self.get_widget("student_table")
```

### 2. Theming System

The `ThemeManager` provides:

- Light and dark mode support
- Custom theme definitions
- Automatic theme propagation to all widgets
- Consistent color schemes

**Theme Application:**
```python
# Set theme for entire window
window.set_theme("dark")

# All registered widgets automatically receive theme updates
```

### 3. Accessibility Compliance

All widgets inherit from `AccessibleWidget` which provides:

- Keyboard navigation support
- Screen reader compatibility
- High-contrast mode
- Focus management
- ARIA-like properties

**Accessibility Features:**
```python
# Enable high-contrast mode for all widgets
window.enable_high_contrast(True)

# Set accessible names and descriptions
widget.set_accessible_name("Student Search")
widget.set_accessible_description("Search field for finding students")
```

### 4. State Management

The `StateManager` enables:

- Shared state across widgets
- Reactive UI updates
- Consistent data flow
- Undo/redo functionality

**State Management Usage:**
```python
# Set state
state_manager.set_state("search_query", "John Doe")

# Get state
query = state_manager.get_state("search_query")

# React to state changes
state_manager.state_changed.connect(self._handle_state_change)
```

## Widget Reuse Patterns

### 1. Composition Pattern

Widgets are composed of smaller, reusable components:

```python
class StudentCard(ModernCard):
    def __init__(self, student_data):
        super().__init__()
        
        # Reuse existing widgets
        self._name_label = ModernLabel(student_data.name)
        self._id_label = ModernLabel(f"ID: {student_data.id}")
        self._edit_button = ModernButton("Edit")
        
        # Compose layout
        layout = ModernLayout()
        layout.add_widget(self._name_label)
        layout.add_widget(self._id_label)
        layout.add_widget(self._edit_button)
        
        self.set_layout(layout)
```

### 2. Inheritance Pattern

Create specialized widgets by extending base classes:

```python
class StudentSearchBox(SearchBox):
    def __init__(self):
        super().__init__(placeholder_text="Search students...")
        
        # Custom behavior
        self.search_text_changed.connect(self._handle_student_search)
    
    def _handle_student_search(self, text):
        # Custom search logic for students
        pass
```

### 3. Factory Pattern

Use widget factories for consistent creation:

```python
class WidgetFactory:
    @staticmethod
    def create_student_table(parent):
        table = CustomTableWidget(parent)
        table.set_data([], ["ID", "Name", "Class", "Status"])
        table.sort_by_column(1, Qt.SortOrder.AscendingOrder)
        return table

# Usage
student_table = WidgetFactory.create_student_table(self)
self.register_widget("student_table", student_table)
```

## Best Practices for Widget Reuse

### 1. Naming Conventions

- **Base Classes**: `BaseWindow`, `BaseDialog`, `AccessibleWidget`
- **Reusable Widgets**: `ModernButton`, `ModernInput`, `CustomTableWidget`
- **Specialized Widgets**: `StudentCard`, `BookSearchBox`
- **Layout Widgets**: `ModernLayout`, `FlexLayout`

### 2. Widget Registration

Always register widgets for centralized management:

```python
# Good practice
self.register_widget("main_table", table_widget)

# Bad practice - unregistered widget
self._content_layout.addWidget(table_widget)
```

### 3. Theming Consistency

Ensure all widgets respect the current theme:

```python
# Good - uses theme colors
widget.setStyleSheet(f"""
    background-color: {theme_manager.get_color('background')};
    color: {theme_manager.get_color('text')};
""")

# Bad - hardcoded colors
widget.setStyleSheet("background-color: white; color: black;")
```

### 4. Accessibility Requirements

All widgets must include accessibility features:

```python
# Required for all widgets
widget.setAccessibleName("Descriptive name")
widget.setAccessibleDescription("Detailed description")
widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
```

### 5. Event Handling

Use signals for widget communication:

```python
# Good - event-driven
class StudentTable(CustomTableWidget):
    student_selected = pyqtSignal(int)
    
    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        if selected.indexes():
            row = selected.indexes()[0].row()
            self.student_selected.emit(row)

# Bad - direct method calls
class StudentTable(CustomTableWidget):
    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        if selected.indexes():
            row = selected.indexes()[0].row()
            parent.handle_student_selection(row)  # Tight coupling
```

## Widget Reuse Examples

### Example 1: Reusable Student Card

```python
from school_system.gui.base.widgets import ModernCard, ModernButton, ModernLabel

class StudentCard(ModernCard):
    """Reusable student information card."""
    
    def __init__(self, student_data, parent=None):
        super().__init__(parent)
        
        # Widget composition
        self._name_label = ModernLabel(student_data.name)
        self._name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self._id_label = ModernLabel(f"ID: {student_data.id}")
        self._class_label = ModernLabel(f"Class: {student_data.class_name}")
        
        self._edit_button = ModernButton("Edit")
        self._view_button = ModernButton("View Details")
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self._name_label)
        layout.addWidget(self._id_label)
        layout.addWidget(self._class_label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self._edit_button)
        button_layout.addWidget(self._view_button)
        layout.addLayout(button_layout)
        
        # Accessibility
        self.setAccessibleName(f"Student card for {student_data.name}")
        self.setAccessibleDescription(f"Student information: {student_data.name}, ID: {student_data.id}")

# Usage in a window
class StudentWindow(BaseWindow):
    def __init__(self):
        super().__init__("Students")
        
        # Create and register student cards
        for student in students:
            card = StudentCard(student)
            self.register_widget(f"student_card_{student.id}", card)
            self.add_widget_to_content(card)
```

### Example 2: Themed Search Dialog

```python
from school_system.gui.base.base_dialog import BaseDialog
from school_system.gui.base.widgets import SearchBox

class StudentSearchDialog(BaseDialog):
    """Reusable student search dialog."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Search Students",
            parent=parent,
            standard_buttons=QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        
        # Reuse SearchBox widget
        self._search_box = SearchBox(placeholder_text="Search students by name or ID...")
        self._search_box.setAccessibleName("Student search")
        self._search_box.setAccessibleDescription("Search field for finding students")
        
        # Add to dialog
        self.add_content_widget(self._search_box)
        
        # Connect signals
        self._search_box.search_text_changed.connect(self._handle_search)
    
    def _handle_search(self, text):
        """Handle search text changes."""
        # Implement search logic
        results = search_students(text)
        self._update_results(results)
    
    def get_search_query(self) -> str:
        """Get the current search query."""
        return self._search_box.get_search_text()

# Usage
class MainWindow(BaseWindow):
    def _show_search_dialog(self):
        dialog = StudentSearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            query = dialog.get_search_query()
            self._perform_search(query)
```

## Performance Considerations

### 1. Widget Caching

Cache frequently used widgets to avoid recreation:

```python
class StudentWindow(BaseWindow):
    def __init__(self):
        super().__init__("Students")
        self._widget_cache = {}
    
    def get_cached_widget(self, widget_type, cache_key):
        if cache_key not in self._widget_cache:
            if widget_type == "search_box":
                widget = SearchBox(placeholder_text="Search students...")
                self._widget_cache[cache_key] = widget
                self.register_widget(f"cached_{cache_key}", widget)
        
        return self._widget_cache[cache_key]
```

### 2. Lazy Loading

Load widgets only when needed:

```python
class LazyWidgetLoader:
    def __init__(self, window, widget_factory):
        self._window = window
        self._widget_factory = widget_factory
        self._widget = None
        self._loaded = False
    
    def get_widget(self):
        if not self._loaded:
            self._widget = self._widget_factory()
            self._window.register_widget("lazy_widget", self._widget)
            self._loaded = True
        return self._widget
```

### 3. Virtualization

Use virtual scrolling for large datasets:

```python
# Good - uses VirtualScrollModel for large datasets
table = CustomTableWidget()
table.setModel(VirtualScrollModel(
    data_provider=lambda row, col: get_student_data(row, col),
    row_count=10000,
    column_count=5
))

# Bad - loads all data at once
table.set_data(get_all_students(), headers)
```

## Testing Strategy

### Unit Testing

Test individual widgets in isolation:

```python
class TestStudentCard(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.student = Student(id=1, name="John Doe", class_name="10A")
        self.card = StudentCard(self.student)
    
    def test_initialization(self):
        self.assertEqual(self.card._name_label.text(), "John Doe")
        self.assertEqual(self.card._id_label.text(), "ID: 1")
    
    def test_accessibility(self):
        self.assertEqual(self.card.accessibleName(), "Student card for John Doe")
```

### Integration Testing

Test widget interactions:

```python
class TestStudentSearchIntegration(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.window = BaseWindow()
        self.dialog = StudentSearchDialog(self.window)
    
    def test_search_functionality(self):
        # Simulate user input
        self.dialog._search_box.set_search_text("John")
        
        # Verify signal emission
        with patch.object(self.dialog._search_box, 'search_text_changed') as mock_signal:
            self.dialog._search_box._handle_text_change("John")
            mock_signal.emit.assert_called_once_with("John")
```

### Theming Testing

Test theme consistency:

```python
class TestTheming(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.window = BaseWindow()
        self.dialog = BaseDialog(parent=self.window)
    
    def test_theme_propagation(self):
        # Change window theme
        self.window.set_theme("dark")
        
        # Verify dialog inherits theme
        self.assertEqual(self.dialog.get_theme_manager().get_theme(), "dark")
```

## Documentation Requirements

### Widget Documentation Template

```markdown
# Widget Name

**Purpose**: Brief description of the widget's purpose

**Features**:
- Feature 1
- Feature 2
- Feature 3

**Usage**:
```python
# Example usage code
```

**API**:
- `method1()`: Description
- `method2(param)`: Description
- `signal_name`: Description

**Theming**:
- Supports light/dark modes
- Customizable colors
- Theme inheritance

**Accessibility**:
- Keyboard navigation
- Screen reader support
- High-contrast mode

**Dependencies**:
- Depends on WidgetA
- Depends on WidgetB
```

## Future Extensions

### 1. Dynamic Widget Loading

Load widgets based on user role or context:

```python
class RoleBasedWidgetLoader:
    def __init__(self, user_role):
        self._user_role = user_role
    
    def load_widget(self, widget_name):
        if widget_name == "admin_panel" and self._user_role == "admin":
            return AdminPanelWidget()
        elif widget_name == "student_view":
            return StudentViewWidget()
        return None
```

### 2. Internationalization Support

Add i18n support to widgets:

```python
class InternationalizedWidget(AccessibleWidget):
    def __init__(self):
        super().__init__()
        self._translator = TranslationManager()
    
    def update_translations(self):
        self.setAccessibleName(self._translator.translate(self._base_name))
        # Update all child widgets
```

### 3. Responsive Design

Enhance widgets for different screen sizes:

```python
class ResponsiveWidget(AccessibleWidget):
    def __init__(self):
        super().__init__()
        self._screen_size = QApplication.primaryScreen().size()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adjust_layout_for_screen_size()
```

## Conclusion

This widget reuse strategy ensures:

1. **Consistency**: Uniform look and behavior across the application
2. **Maintainability**: Centralized widget management and updates
3. **Accessibility**: Full compliance with WCAG 2.1 standards
4. **Performance**: Efficient widget loading and rendering
5. **Extensibility**: Easy to add new widgets and features

By following these guidelines, the School System Management application will maintain a professional, accessible, and maintainable GUI framework.