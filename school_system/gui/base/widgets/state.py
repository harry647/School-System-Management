"""
State Management

A lightweight state handler for widget reactivity.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class StateManager(QObject):
    """
    A lightweight state manager for widget reactivity.
    
    Features:
        - Reactive state management
        - Signal-based updates
        - Support for complex state objects
    """
    
    state_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = {}
    
    def set_state(self, key, value):
        """Set a state value."""
        self._state[key] = value
        self.state_changed.emit(key, value)
    
    def get_state(self, key):
        """Get a state value."""
        return self._state.get(key)
    
    def update_state(self, key, updater_func):
        """Update a state value using a function."""
        if key in self._state:
            self._state[key] = updater_func(self._state[key])
            self.state_changed.emit(key, self._state[key])
    
    def clear_state(self):
        """Clear all state values."""
        self._state.clear()


class ReactiveWidget(QObject):
    """
    A base class for reactive widgets.
    
    Features:
        - Automatic state updates
        - Signal-based reactivity
    """
    
    def __init__(self, state_manager, parent=None):
        super().__init__(parent)
        self._state_manager = state_manager
        self._state_manager.state_changed.connect(self._on_state_changed)
    
    def _on_state_changed(self, key, value):
        """Handle state changes."""
        self.update_from_state(key, value)
    
    def update_from_state(self, key, value):
        """Update the widget based on state changes."""
        pass