"""
Modern Search Box Widget

A real-time search widget with debouncing for performance optimization.
"""

from PyQt6.QtWidgets import QLineEdit, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from typing import Optional, Callable, Dict, Any
from functools import lru_cache
import os


class SearchBox(QWidget):
    """
    A real-time search widget with debouncing for performance optimization.
    
    Features:
        - Real-time search with configurable debounce delay
        - Clear button for easy reset
        - Customizable placeholder text
        - Accessibility support
    """
    
    # Signal emitted when search text changes (after debounce)
    search_text_changed = pyqtSignal(str)
    
    def __init__(self, placeholder_text: str = "Search...", parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        
        # Create search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder_text)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 4px 8px;
                border: 1px solid #ddd;
                border-radius: 4px 0 0 4px;
                font-size: 13px;
                min-width: 150px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
                outline: none;
            }
        """)
        
        # Create search button
        self.search_button = QPushButton()
        icon_path = os.path.join("school_system", "gui", "resources", "icons", "search.png")
        if os.path.exists(icon_path):
            self.search_button.setIcon(QIcon(icon_path))
        else:
            self.search_button.setText("🔍")
        
        self.search_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                background-color: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
                border-radius: 0 4px 4px 0;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # Add widgets to layout
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.search_button)
        
        # Set overall widget styling - will be overridden by theme manager
        self.setStyleSheet("""
            SearchBox {
                border-radius: 4px;
            }
        """)
        
        # Accessibility
        self.setAccessibleName("Search Box")
        self.setAccessibleDescription("Real-time search input with debouncing")
        self.search_input.setAccessibleName("Search Input")
        self.search_button.setAccessibleName("Search Button")
        
        # Debounce timer
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)  # 300ms debounce delay
        self._debounce_timer.timeout.connect(self._emit_search_text)
        
        # Connect signals
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_button.clicked.connect(self._on_search_clicked)
    
    def _on_text_changed(self, text: str):
        """Handle text changes with debouncing."""
        self._debounce_timer.start()
    
    def _emit_search_text(self):
        """Emit the search text signal after debounce delay."""
        text = self.search_input.text()
        self.search_text_changed.emit(text)
    
    def _on_search_clicked(self):
        """Handle search button click."""
        # Force immediate search when button is clicked
        self._debounce_timer.stop()
        self._emit_search_text()
    
    def set_debounce_delay(self, delay_ms: int):
        """
        Set the debounce delay in milliseconds.
        
        Args:
            delay_ms: Debounce delay in milliseconds
        """
        self._debounce_timer.setInterval(delay_ms)
    
    def get_search_text(self) -> str:
        """
        Get the current search text.
        
        Returns:
            Current search text
        """
        return self.search_input.text()
    
    def set_search_text(self, text: str):
        """
        Set the search text programmatically.
        
        Args:
            text: Text to set in the search input
        """
        self.search_input.setText(text)
    
    def clear(self):
        """Clear the search input."""
        self.search_input.clear()
        self.search_text_changed.emit("")
    
    def set_placeholder_text(self, text: str):
        """
        Set the placeholder text.
        
        Args:
            text: Placeholder text to display
        """
        self.search_input.setPlaceholderText(text)


class MemoizedSearchBox(SearchBox):
    """
    A search box with memoization for expensive search operations.
    
    Features:
        - Memoization of search results
        - Configurable cache size
        - Automatic cache invalidation
    """
    
    def __init__(self, placeholder_text: str = "Search...", parent: Optional[QWidget] = None, cache_size: int = 100):
        super().__init__(placeholder_text, parent)
        self._cache_size = cache_size
        self._search_cache: Dict[str, Any] = {}
        
        # Override the search text changed signal to use memoization
        original_signal = self.search_text_changed
        self.search_text_changed = pyqtSignal(str)
        
        def memoized_search(text: str):
            # Check cache first
            if text in self._search_cache:
                print(f"Cache hit for search: {text}")
                original_signal.emit(self._search_cache[text])
            else:
                print(f"Cache miss for search: {text}")
                # Store result in cache
                self._search_cache[text] = text
                original_signal.emit(text)
                
                # Limit cache size
                if len(self._search_cache) > self._cache_size:
                    # Remove oldest entry (simple FIFO cache)
                    oldest_key = next(iter(self._search_cache))
                    del self._search_cache[oldest_key]
        
        # Connect the memoized search function
        self._debounce_timer.timeout.connect(lambda: memoized_search(self.search_input.text()))
    
    def set_cache_size(self, size: int):
        """
        Set the maximum cache size.
        
        Args:
            size: Maximum number of search results to cache
        """
        self._cache_size = size
        
        # Trim cache if needed
        while len(self._search_cache) > self._cache_size:
            oldest_key = next(iter(self._search_cache))
            del self._search_cache[oldest_key]
    
    def clear_cache(self):
        """Clear the search cache."""
        self._search_cache.clear()


class AdvancedSearchBox(SearchBox):
    """
    Advanced search box with additional features like search suggestions.
    
    Features:
        - Search suggestions dropdown
        - Recent searches history
        - Customizable suggestion provider
    """
    
    def __init__(self, placeholder_text: str = "Search...", parent: Optional[QWidget] = None):
        super().__init__(placeholder_text, parent)
        
        # TODO: Implement advanced features
        # - Search suggestions
        # - Recent searches history
        # - Custom suggestion provider
        pass
