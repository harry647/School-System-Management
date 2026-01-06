# School System Widget Library

A comprehensive widget library for the School System Management application, featuring modern, reusable components with advanced UI features.

## Features

- **Interactive Data Tables**: Sorting, filtering, and virtual scrolling for large datasets
- **Real-time Search**: Debounced search functionality with memoization support
- **Dynamic Status Bars**: Progress indicators and notification system
- **Accessibility Compliance**: WCAG 2.1 compliant components
- **Responsive Design**: Adaptive layouts for different screen sizes
- **Performance Optimizations**: Virtual scrolling and memoization
- **Theming Support**: Integration with the existing design system

## Installation

The widget library is automatically available when you import the school system GUI module:

```python
from school_system.gui.base.widgets import (
    CustomTableWidget, SortFilterProxyModel, VirtualScrollModel,
    SearchBox, AdvancedSearchBox, MemoizedSearchBox,
    ModernStatusBar, ProgressIndicator,
    ThemeManager
)
```

## Components

### CustomTableWidget

An interactive data table with advanced features.

**Features:**
- Column sorting (ascending/descending)
- Row filtering
- Context menu for actions
- Virtual scrolling for large datasets
- Customizable styling

**Usage:**

```python
# Create table
table = CustomTableWidget(parent)

# Set data
data = [
    {"name": "John Doe", "age": 30, "role": "Teacher"},
    {"name": "Jane Smith", "age": 25, "role": "Student"}
]
headers = ["name", "age", "role"]
table.set_data(data, headers)

# Enable sorting
table.sort_by_column(1, Qt.SortOrder.AscendingOrder)

# Connect to selection changes
table.row_selected.connect(lambda row: print(f"Row {row} selected"))
```

**API:**

- `set_data(data: List[Dict], headers: List[str])` - Set table data
- `sort_by_column(column: int, order: Qt.SortOrder)` - Sort by column
- `add_filter_widgets(filter_widgets: Dict[str, QWidget])` - Add filter widgets
- `apply_filters()` - Apply current filters
- `row_selected` - Signal emitted when row selection changes

### SortFilterProxyModel

A proxy model for sorting and filtering table data.

**Features:**
- Custom sorting logic
- Column-specific filtering
- Case-insensitive search

**Usage:**

```python
proxy_model = SortFilterProxyModel()
proxy_model.setSourceModel(source_model)
proxy_model.set_filter_column(0)
proxy_model.set_filter_text("search term")
```

### VirtualScrollModel

A virtual scrolling model for large datasets.

**Features:**
- Only loads visible rows into memory
- Efficient scrolling for large datasets
- Custom data provider interface

**Usage:**

```python
def data_provider(row, col):
    # Fetch data for specific row/column
    return database.get_item(row, col)

model = VirtualScrollModel(
    data_provider=data_provider,
    row_count=10000,
    column_count=5,
    headers=["ID", "Name", "Age", "Role", "Status"]
)
```

### SearchBox

A real-time search widget with debouncing.

**Features:**
- Real-time search with configurable debounce delay
- Clear button for easy reset
- Customizable placeholder text

**Usage:**

```python
search_box = SearchBox(placeholder_text="Search students...")
search_box.search_text_changed.connect(lambda text: perform_search(text))

# Configure debounce delay
search_box.set_debounce_delay(300)  # 300ms delay
```

**API:**

- `get_search_text()` - Get current search text
- `set_search_text(text: str)` - Set search text programmatically
- `clear()` - Clear the search input
- `set_debounce_delay(delay_ms: int)` - Set debounce delay
- `search_text_changed` - Signal emitted when search text changes

### MemoizedSearchBox

A search box with memoization for expensive operations.

**Features:**
- Memoization of search results
- Configurable cache size
- Automatic cache invalidation

**Usage:**

```python
search_box = MemoizedSearchBox(cache_size=100)
search_box.search_text_changed.connect(handle_search)

# Clear cache when needed
search_box.clear_cache()
```

### ModernStatusBar

A dynamic status bar with progress indicators.

**Features:**
- Progress indicators for ongoing operations
- Temporary and permanent messages
- Customizable styling

**Usage:**

```python
status_bar = ModernStatusBar()

# Show progress
status_bar.show_progress(50, 100)

# Show temporary message
status_bar.show_temporary_message("Operation completed successfully", 3000)

# Show permanent message
status_bar.show_permanent_message("Ready")
```

**API:**

- `show_progress(value: int, max_value: int = 100)` - Show progress
- `hide_progress()` - Hide progress bar
- `show_message(message: str, timeout: int = 0)` - Show message
- `clear_message()` - Clear current message
- `show_temporary_message(message: str, duration: int = 3000)` - Show temporary message
- `show_permanent_message(message: str)` - Show permanent message

### ProgressIndicator

A circular progress indicator widget.

**Features:**
- Circular progress animation
- Customizable colors
- Size control

**Usage:**

```python
indicator = ProgressIndicator(size=32)
indicator.set_value(75)
indicator.set_max_value(100)
```

**API:**

- `set_value(value: int)` - Set current progress value
- `set_max_value(max_value: int)` - Set maximum progress value
- `set_color(color: QColor)` - Set progress indicator color

## Theming

All widgets support the existing theme system and automatically adapt to light/dark modes.

```python
# Get theme manager
theme_manager = ThemeManager()

# Set theme
theme_manager.set_theme("dark")

# Apply theme to application
app.setStyleSheet(theme_manager.generate_qss())
```

## Accessibility

All widgets are designed with accessibility in mind:

- Keyboard navigation support
- Screen reader compatibility
- High contrast modes
- Proper focus management

## Performance

The widget library includes several performance optimizations:

1. **Virtual Scrolling**: For tables with large datasets
2. **Memoization**: For expensive search operations
3. **Debouncing**: For real-time search inputs
4. **Efficient Rendering**: Minimal repaints and layout updates

## Testing

Unit tests are provided for all components:

```bash
# Run widget tests
python -m unittest school_system.tests.unit.test_widgets
```

## TypeScript Support

TypeScript type definitions are available in `widgets.d.ts` for web integrations.

## Browser Compatibility

While this is primarily a PyQt6-based desktop application, the design patterns and TypeScript definitions enable potential web integrations.

## License

This widget library is part of the School System Management application and is licensed under the same terms.

## Contributing

Contributions to the widget library are welcome. Please follow the existing code style and ensure all tests pass.

## Support

For issues or questions about the widget library, please contact the development team.