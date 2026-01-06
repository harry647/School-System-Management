"""
School System GUI Base Module

This module provides the foundation for the School System Management GUI framework,
including base window and dialog classes, widget management, theming, and accessibility.

Core Components:
    - BaseWindow: Foundation for all application windows
    - BaseDialog: Foundation for all application dialogs
    - BaseApplicationWindow: Extended window with application features
    - Widget Registry: Centralized widget management system
    - ThemeManager: Comprehensive theming support
    - StateManager: Application state management
    - Accessibility: Full WCAG 2.1 compliance

Usage:
    from school_system.gui.base import BaseWindow, BaseDialog, BaseApplicationWindow
    from school_system.gui.base.widgets import ModernButton, ModernInput, CustomTableWidget
"""

from .base_window import BaseWindow, BaseApplicationWindow
from .base_dialog import BaseDialog

# Import key widgets for convenience
from .widgets import (
    ThemeManager, StateManager, AccessibleWidget,
    ModernButton, ModernInput, ModernCard,
    ModernLayout, FlexLayout, CustomTableWidget,
    SearchBox, AdvancedSearchBox, MemoizedSearchBox,
    ModernStatusBar, ProgressIndicator,
    ScrollableContainer, ScrollableCardContainer
)

__all__ = [
    # Base classes
    "BaseWindow",
    "BaseApplicationWindow", 
    "BaseDialog",
    "ConfirmationDialog",
    "InputDialog",
    
    # Widget management
    "ThemeManager",
    "StateManager",
    "AccessibleWidget",
    
    # Reusable widgets
    "ModernButton",
    "ModernInput",
    "ModernCard",
    "ModernLayout",
    "FlexLayout",
    "CustomTableWidget",
    "SearchBox",
    "AdvancedSearchBox",
    "MemoizedSearchBox",
    "ModernStatusBar",
    "ProgressIndicator",
    "ScrollableContainer",
    "ScrollableCardContainer",
]
