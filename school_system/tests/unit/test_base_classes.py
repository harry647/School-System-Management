"""
Unit tests for base GUI classes (BaseWindow and BaseDialog).

This module contains comprehensive tests for the base GUI framework classes,
ensuring proper functionality, theming, accessibility, and widget management.
"""

import unittest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QDialogButtonBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from school_system.gui.base.base_window import BaseWindow, BaseApplicationWindow
from school_system.gui.base.base_dialog import BaseDialog, ConfirmationDialog, InputDialog


class TestBaseWindow(unittest.TestCase):
    """Test cases for BaseWindow class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication([])
        self.window = BaseWindow("Test Window")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.window.close()
        del self.window
        self.app.quit()
    
    def test_initialization(self):
        """Test that the window initializes correctly."""
        self.assertIsNotNone(self.window)
        self.assertEqual(self.window.windowTitle(), "Test Window")
        self.assertTrue(self.window.minimumWidth() >= 800)
        self.assertTrue(self.window.minimumHeight() >= 600)
    
    def test_theme_management(self):
        """Test theme management functionality."""
        # Test initial theme
        self.assertEqual(self.window.get_theme(), "light")
        
        # Test theme change
        self.window.set_theme("dark")
        self.assertEqual(self.window.get_theme(), "dark")
    
    def test_widget_registration(self):
        """Test widget registration system."""
        test_widget = QLabel("Test Widget")
        
        # Register widget
        self.window.register_widget("test_label", test_widget)
        
        # Retrieve widget
        retrieved_widget = self.window.get_widget("test_label")
        self.assertIsNotNone(retrieved_widget)
        self.assertEqual(retrieved_widget, test_widget)
    
    def test_widget_addition(self):
        """Test adding widgets to content area."""
        test_widget = QLabel("Content Widget")
        
        # Add widget to content
        self.window.add_widget_to_content(test_widget, name="content_label")
        
        # Verify widget is in layout and registered
        retrieved_widget = self.window.get_widget("content_label")
        self.assertIsNotNone(retrieved_widget)
        self.assertEqual(retrieved_widget, test_widget)
    
    def test_status_updates(self):
        """Test status bar functionality."""
        # Test permanent message
        self.window.update_status("Test message")
        
        # Test temporary message
        self.window.update_status("Temporary message", 100)
    
    def test_progress_indication(self):
        """Test progress bar functionality."""
        # Show progress
        self.window.show_progress(50, 100)
        
        # Hide progress
        self.window.hide_progress()
    
    def test_accessibility_features(self):
        """Test accessibility features."""
        # Test high contrast mode
        self.window.enable_high_contrast(True)
        self.window.enable_high_contrast(False)
        
        # Test accessibility properties
        self.assertTrue(self.window.accessibleName().endswith("Window"))
        self.assertTrue(self.window.accessibleDescription().startswith("Main application window"))
    
    def test_menu_creation(self):
        """Test menu bar creation."""
        menu_bar = self.window.create_menu_bar()
        self.assertIsNotNone(menu_bar)
        
        # Verify file menu exists
        file_menu = menu_bar.findChild(type(menu_bar).__name__, "File")
        self.assertIsNotNone(file_menu)
    
    def test_signal_emission(self):
        """Test signal emission."""
        with patch.object(self.window, 'window_ready') as mock_signal:
            # Window ready signal should have been emitted during initialization
            mock_signal.assert_called_once()


class TestBaseApplicationWindow(unittest.TestCase):
    """Test cases for BaseApplicationWindow class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication([])
        self.window = BaseApplicationWindow("Test App Window")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.window.close()
        del self.window
        self.app.quit()
    
    def test_application_features(self):
        """Test application-specific features."""
        # Verify menu bar exists
        self.assertIsNotNone(self.window._menu_bar)
        
        # Verify help menu exists
        help_menu = self.window._menu_bar.findChild(type(self.window._menu_bar).__name__, "Help")
        self.assertIsNotNone(help_menu)
    
    def test_menu_addition(self):
        """Test adding application menus."""
        new_menu = self.window.add_application_menu("Test Menu")
        self.assertIsNotNone(new_menu)


class TestBaseDialog(unittest.TestCase):
    """Test cases for BaseDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication([])
        self.dialog = BaseDialog("Test Dialog")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.dialog.close()
        del self.dialog
        self.app.quit()
    
    def test_initialization(self):
        """Test dialog initialization."""
        self.assertIsNotNone(self.dialog)
        self.assertEqual(self.dialog.windowTitle(), "Test Dialog")
        self.assertTrue(self.dialog.isModal())
    
    def test_content_addition(self):
        """Test adding content to dialog."""
        test_widget = QLabel("Dialog Content")
        
        # Add widget to content
        self.dialog.add_content_widget(test_widget, name="dialog_label")
        
        # Verify widget is in layout
        self.assertTrue(test_widget.parent() is not None)
    
    def test_theme_management(self):
        """Test dialog theme management."""
        # Verify theme manager exists
        self.assertIsNotNone(self.dialog.get_theme_manager())
        
        # Test theme change
        self.dialog.set_theme("dark")
        self.assertEqual(self.dialog.get_theme_manager().get_theme(), "dark")
    
    def test_button_management(self):
        """Test button management."""
        # Test adding custom button
        custom_button = self.dialog.add_custom_button("Custom Action")
        self.assertIsNotNone(custom_button)
        self.assertEqual(custom_button.text(), "Custom Action")
        
        # Test setting standard buttons
        self.dialog.set_standard_buttons(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
    
    def test_accessibility_features(self):
        """Test dialog accessibility features."""
        # Test accessibility properties
        self.assertTrue(self.dialog.accessibleName().endswith("Dialog"))
        self.assertTrue(self.dialog.accessibleDescription().startswith("Dialog window"))
    
    def test_signal_emission(self):
        """Test dialog signal emission."""
        # Test dialog acceptance
        with patch.object(self.dialog, 'accept') as mock_accept:
            with patch.object(self.dialog, 'dialog_accepted') as mock_signal:
                self.dialog.accept()
                mock_accept.assert_called_once()
                mock_signal.assert_called_once()
        
        # Test dialog rejection
        with patch.object(self.dialog, 'reject') as mock_reject:
            with patch.object(self.dialog, 'dialog_rejected') as mock_signal:
                self.dialog.reject()
                mock_reject.assert_called_once()
                mock_signal.assert_called_once()


class TestConfirmationDialog(unittest.TestCase):
    """Test cases for ConfirmationDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication([])
        self.dialog = ConfirmationDialog("Confirm Action", "Are you sure you want to proceed?")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.dialog.close()
        del self.dialog
        self.app.quit()
    
    def test_initialization(self):
        """Test confirmation dialog initialization."""
        self.assertEqual(self.dialog.windowTitle(), "Confirm Action")
        
        # Verify message label exists
        message_label = self.dialog._content_frame.findChild(QLabel)
        self.assertIsNotNone(message_label)
        self.assertEqual(message_label.text(), "Are you sure you want to proceed?")
    
    def test_buttons(self):
        """Test confirmation dialog buttons."""
        # Verify Yes button
        yes_button = self.dialog._button_box.button(QDialogButtonBox.StandardButton.Yes)
        self.assertIsNotNone(yes_button)
        self.assertEqual(yes_button.text(), "Yes")
        
        # Verify No button
        no_button = self.dialog._button_box.button(QDialogButtonBox.StandardButton.No)
        self.assertIsNotNone(no_button)
        self.assertEqual(no_button.text(), "No")


class TestInputDialog(unittest.TestCase):
    """Test cases for InputDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication([])
        self.dialog = InputDialog("Enter Value", "Please enter a value:")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.dialog.close()
        del self.dialog
        self.app.quit()
    
    def test_initialization(self):
        """Test input dialog initialization."""
        self.assertEqual(self.dialog.windowTitle(), "Enter Value")
        
        # Verify input field exists
        self.assertIsNotNone(self.dialog._input_field)
        self.assertEqual(self.dialog._input_field.placeholderText(), "Please enter a value:")
    
    def test_input_management(self):
        """Test input field management."""
        # Set input value
        self.dialog.set_input_value("Test Input")
        self.assertEqual(self.dialog.get_input_value(), "Test Input")
        
        # Clear input
        self.dialog.set_input_value("")
        self.assertEqual(self.dialog.get_input_value(), "")


class TestWidgetReuse(unittest.TestCase):
    """Test cases for widget reuse functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication([])
        self.window = BaseWindow("Widget Reuse Test")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.window.close()
        del self.window
        self.app.quit()
    
    def test_widget_reuse_across_windows(self):
        """Test widget reuse across multiple windows."""
        # Create a reusable widget
        shared_widget = QLabel("Shared Widget")
        
        # Register in first window
        self.window.register_widget("shared_label", shared_widget)
        
        # Create second window
        second_window = BaseWindow("Second Window")
        
        # Verify widget can be reused (conceptually)
        # In practice, widgets should be recreated or properly shared
        self.assertIsNotNone(self.window.get_widget("shared_label"))
        
        second_window.close()
    
    def test_theme_consistency(self):
        """Test theme consistency across widgets."""
        # Create multiple widgets
        label1 = QLabel("Widget 1")
        label2 = QLabel("Widget 2")
        button = QPushButton("Action")
        
        # Register widgets
        self.window.register_widget("label1", label1)
        self.window.register_widget("label2", label2)
        self.window.register_widget("button", button)
        
        # Change theme
        self.window.set_theme("dark")
        
        # Verify all widgets receive theme updates
        # (This is more of a conceptual test as actual theme application
        # depends on widget implementation)
        self.assertEqual(self.window.get_theme(), "dark")
    
    def test_accessibility_consistency(self):
        """Test accessibility consistency across widgets."""
        # Create widgets with accessibility features
        label = QLabel("Accessible Label")
        label.setAccessibleName("Test Label")
        label.setAccessibleDescription("A test label for accessibility")
        
        self.window.register_widget("accessible_label", label)
        
        # Verify accessibility properties are maintained
        retrieved_label = self.window.get_widget("accessible_label")
        self.assertEqual(retrieved_label.accessibleName(), "Test Label")
        self.assertEqual(retrieved_label.accessibleDescription(), "A test label for accessibility")


class TestIntegration(unittest.TestCase):
    """Integration tests for base classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication([])
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.app.quit()
    
    def test_window_dialog_integration(self):
        """Test integration between window and dialog."""
        # Create window
        window = BaseWindow("Main Window")
        
        # Create dialog with window as parent
        dialog = BaseDialog("Child Dialog", parent=window)
        
        # Verify dialog inherits theme from window
        self.assertEqual(dialog.get_theme_manager().get_theme(), window.get_theme())
        
        # Clean up
        dialog.close()
        window.close()
    
    def test_complex_widget_hierarchy(self):
        """Test complex widget hierarchy."""
        # Create window
        window = BaseApplicationWindow("Complex Window")
        
        # Add multiple widgets
        label = QLabel("Main Label")
        button = QPushButton("Action")
        
        window.add_widget_to_content(label, name="main_label")
        window.add_widget_to_content(button, name="action_button")
        
        # Create and add dialog
        dialog = ConfirmationDialog("Test Confirmation", "Confirm action?", parent=window)
        
        # Verify all components work together
        self.assertIsNotNone(window.get_widget("main_label"))
        self.assertIsNotNone(window.get_widget("action_button"))
        
        # Clean up
        dialog.close()
        window.close()


if __name__ == '__main__':
    unittest.main()