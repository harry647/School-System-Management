"""
Modern PyQt GUI Framework - Widgets Module

This module provides a modular widget system with a focus on clean aesthetics,
responsive layouts, and intuitive interactions akin to contemporary web applications.

Features:
    - Core Widget Library: Reusable, stylish base widgets (buttons, inputs, cards, etc.)
    - Layout System: Flexible grid/flexbox-like layout manager
    - Theming Engine: Dynamic theming (light/dark modes, custom palettes) via QSS
    - State Management: Lightweight state handler for widget reactivity
    - Accessibility: Keyboard navigation, screen reader support, and high-contrast modes

Usage:
    from gui.base.widgets import ModernButton, ModernInput, ModernCard, ModernLayout, ThemeManager, StateManager
"""

from .button import ModernButton
from .input import ModernInput
from .card import ModernCard
from .layout import ModernLayout, FlexLayout
from .theme import ThemeManager
from .state import StateManager
from .accessibility import AccessibleWidget, AccessibleButton, AccessibleInput
from .scrollable_container import ScrollableContainer, ScrollableCardContainer
from .custom_table import CustomTableWidget, SortFilterProxyModel, VirtualScrollModel
from .search_box import SearchBox, AdvancedSearchBox, MemoizedSearchBox
from .status_bar import ModernStatusBar, ProgressIndicator

__all__ = [
    "ModernButton",
    "ModernInput",
    "ModernCard",
    "ModernLayout",
    "FlexLayout",
    "ThemeManager",
    "StateManager",
    "AccessibleWidget",
    "AccessibleButton",
    "AccessibleInput",
    "ScrollableContainer",
    "ScrollableCardContainer",
    "CustomTableWidget",
    "SortFilterProxyModel",
    "VirtualScrollModel",
    "SearchBox",
    "AdvancedSearchBox",
    "MemoizedSearchBox",
    "ModernStatusBar",
    "ProgressIndicator",
]
