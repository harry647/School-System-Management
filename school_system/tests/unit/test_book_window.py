"""
Comprehensive test suite for the Book Window module.

This test file covers:
- Unit tests for all public methods and functions
- Integration tests for window initialization and lifecycle events
- Tests for all user interactions and callbacks
- Verification of proper UI component creation and layout
- Tests for data input handling and validation
- Error handling tests for edge cases and invalid inputs
"""

import pytest
import unittest.mock as mock
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QComboBox, QTableWidgetItem
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


# Mock the PyQt6 application before any imports
@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_book_service():
    """Create a mock book service."""
    mock_service = Mock()
    mock_service.get_all_books.return_value = []
    mock_service.get_book_by_id.return_value = None
    mock_service.create_book.return_value = Mock(id=1, book_number="TEST-001", title="Test Book", author="Test Author", available=1, category="Test", book_condition="New", subject="Mathematics")
    mock_service.update_book.return_value = Mock()
    mock_service.delete_book.return_value = True
    mock_service.check_book_availability.return_value = True
    mock_service.reserve_book.return_value = True
    mock_service.return_book_student.return_value = True
    mock_service.return_book_teacher.return_value = True
    mock_service.search_books.return_value = []
    mock_service.get_all_borrowed_books_student.return_value = []
    mock_service.get_all_borrowed_books_teacher.return_value = []
    mock_service.get_all_distribution_sessions.return_value = []
    mock_service.create_distribution_session_with_students.return_value = 1
    mock_service.import_books_from_excel.return_value = []
    mock_service.export_books_to_excel.return_value = True
    mock_service.get_popular_books.return_value = []
    mock_service.get_all_overdue_books.return_value = []
    mock_service.log_user_action.return_value = None
    return mock_service


class TestBookWindowImports:
    """Test imports from the book_window module."""
    
    def test_book_window_import(self):
        """Test that BookWindow can be imported."""
        from school_system.gui.windows.book_window import BookWindow
        assert BookWindow is not None
    
    def test_ui_components_import(self):
        """Test that UI components can be imported."""
        from school_system.gui.windows.book_window import (
            FlexLayout, Card, InputField, TextArea, Button, 
            ComboBox, Table, SearchBox, ValidationLabel
        )
        assert FlexLayout is not None
        assert Card is not None
        assert InputField is not None
        assert TextArea is not None
        assert Button is not None
        assert ComboBox is not None
        assert Table is not None
        assert SearchBox is not None
        assert ValidationLabel is not None
    
    def test_constants_import(self):
        """Test that constants can be imported."""
        from school_system.gui.windows.book_window import (
            SPACING_SMALL, SPACING_MEDIUM, SPACING_LARGE,
            CARD_PADDING, CARD_SPACING,
            REQUIRED_FIELDS, BOOK_CONDITIONS, REMOVAL_REASONS,
            USER_TYPES, RETURN_CONDITIONS, SESSION_STATUSES,
            STANDARD_SUBJECTS, STANDARD_CLASSES, STANDARD_STREAMS,
            STANDARD_TERMS, EXPORT_FORMATS
        )
        assert SPACING_SMALL == 8
        assert SPACING_MEDIUM == 12
        assert SPACING_LARGE == 20
        assert CARD_PADDING == 20
        assert CARD_SPACING == 15
        assert "Mathematics" in STANDARD_SUBJECTS
        assert "Form 1" in STANDARD_CLASSES
        assert "New" in BOOK_CONDITIONS
        assert "student" in USER_TYPES
    
    def test_workflows_import(self):
        """Test that workflow classes can be imported."""
        from school_system.gui.windows.book_window import (
            BookAddWorkflow, BookEditWorkflow, BookRemoveWorkflow,
            BookBorrowWorkflow, BookReturnWorkflow, BookSearchWorkflow
        )
        assert BookAddWorkflow is not None
        assert BookEditWorkflow is not None
        assert BookRemoveWorkflow is not None
        assert BookBorrowWorkflow is not None
        assert BookReturnWorkflow is not None
        assert BookSearchWorkflow is not None
    
    def test_validation_helper_import(self):
        """Test that BookValidationHelper can be imported."""
        from school_system.gui.windows.book_window import BookValidationHelper
        assert BookValidationHelper is not None


class TestBookValidationHelper:
    """Test the BookValidationHelper class."""
    
    def test_validate_book_number_empty(self):
        """Test validation of empty book number."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        result = BookValidationHelper.validate_book_number("", [])
        assert result[0] is False
        assert "required" in result[1].lower()
    
    def test_validate_book_number_whitespace_only(self):
        """Test validation of whitespace-only book number."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        result = BookValidationHelper.validate_book_number("   ", [])
        assert result[0] is False
    
    def test_validate_book_number_unique(self):
        """Test validation of unique book number."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        existing_books = [{'book_number': 'TEST-001'}, {'book_number': 'TEST-002'}]
        result = BookValidationHelper.validate_book_number('TEST-003', existing_books)
        assert result[0] is True
        assert result[1] == ""
    
    def test_validate_book_number_duplicate(self):
        """Test validation of duplicate book number."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        existing_books = [{'book_number': 'TEST-001'}, {'book_number': 'TEST-002'}]
        result = BookValidationHelper.validate_book_number('TEST-001', existing_books)
        assert result[0] is False
        assert "already exists" in result[1].lower()
    
    def test_validate_book_number_case_insensitive(self):
        """Test that book number validation is case-insensitive."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        existing_books = [{'book_number': 'test-001'}]
        result = BookValidationHelper.validate_book_number('TEST-001', existing_books)
        assert result[0] is False
    
    def test_validate_required_fields_all_present(self):
        """Test validation when all required fields are present."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        data = {
            'subject': 'Mathematics',
            'class': 'Form 1',
            'book_number': 'TEST-001',
            'title': 'Test Book',
            'author': 'Test Author'
        }
        result = BookValidationHelper.validate_required_fields(data)
        assert result[0] is True
    
    def test_validate_required_fields_missing(self):
        """Test validation when required fields are missing."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        data = {
            'subject': 'Mathematics',
            # Missing other required fields
        }
        result = BookValidationHelper.validate_required_fields(data)
        assert result[0] is False
        assert "is required" in result[1].lower()
    
    def test_validate_book_data_valid(self):
        """Test complete book data validation."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        data = {
            'subject': 'Mathematics',
            'class': 'Form 1',
            'book_number': 'TEST-001',
            'title': 'Test Book',
            'author': 'Test Author'
        }
        result = BookValidationHelper.validate_book_data(data)
        assert result[0] is True
    
    def test_validate_book_data_invalid(self):
        """Test complete book data validation with invalid data."""
        from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
        
        data = {
            'subject': 'Mathematics',
            'class': 'Form 1',
            # Missing book_number, title, author
        }
        result = BookValidationHelper.validate_book_data(data)
        assert result[0] is False


class TestBookWorkflows:
    """Test the book workflow classes."""
    
    def test_book_workflow_base_init(self, mock_book_service):
        """Test BookWorkflowBase initialization."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookWorkflowBase
        
        workflow = BookWorkflowBase(mock_book_service, "test_user")
        assert workflow.book_service == mock_book_service
        assert workflow.current_user == "test_user"
        assert workflow.last_action is None
    
    def test_book_add_workflow_execute_valid(self, mock_book_service):
        """Test BookAddWorkflow execution with valid data."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookAddWorkflow
        
        workflow = BookAddWorkflow(mock_book_service, "test_user")
        book_data = {
            'subject': 'Mathematics',
            'class': 'Form 1',
            'book_number': 'TEST-001',
            'title': 'Test Book',
            'author': 'Test Author'
        }
        
        result = workflow.execute_add_book(book_data)
        assert result[0] is not None
        assert "success" in result[1].lower()
    
    def test_book_add_workflow_execute_missing_fields(self, mock_book_service):
        """Test BookAddWorkflow execution with missing required fields."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookAddWorkflow
        
        workflow = BookAddWorkflow(mock_book_service, "test_user")
        book_data = {
            'subject': 'Mathematics',
            # Missing other required fields
        }
        
        result = workflow.execute_add_book(book_data)
        assert result[0] is None
        assert "required" in result[1].lower()
    
    def test_book_add_workflow_duplicate_book_number(self, mock_book_service):
        """Test BookAddWorkflow with duplicate book number."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookAddWorkflow
        
        # Mock existing books
        mock_book = Mock()
        mock_book.book_number = 'TEST-001'
        mock_book_service.get_all_books.return_value = [mock_book]
        
        workflow = BookAddWorkflow(mock_book_service, "test_user")
        book_data = {
            'subject': 'Mathematics',
            'class': 'Form 1',
            'book_number': 'TEST-001',
            'title': 'Test Book',
            'author': 'Test Author'
        }
        
        result = workflow.execute_add_book(book_data)
        assert result[0] is None
        assert "already exists" in result[1].lower()
    
    def test_book_edit_workflow_book_not_found(self, mock_book_service):
        """Test BookEditWorkflow when book doesn't exist."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookEditWorkflow
        
        mock_book_service.get_book_by_id.return_value = None
        workflow = BookEditWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_edit_book(999, {'title': 'New Title'})
        assert result[0] is False
        assert "not found" in result[1].lower()
    
    def test_book_edit_workflow_empty_update_data(self, mock_book_service):
        """Test BookEditWorkflow with empty update data."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookEditWorkflow
        
        mock_book = Mock()
        mock_book_service.get_book_by_id.return_value = mock_book
        workflow = BookEditWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_edit_book(1, {})
        assert result[0] is False
        assert "at least one field" in result[1].lower()
    
    def test_book_edit_workflow_success(self, mock_book_service):
        """Test BookEditWorkflow with valid update data."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookEditWorkflow
        
        mock_book = Mock()
        mock_book.title = "Old Title"
        mock_book.author = "Old Author"
        mock_book.book_condition = "Good"
        mock_book_service.get_book_by_id.return_value = mock_book
        mock_book_service.update_book.return_value = Mock()
        
        workflow = BookEditWorkflow(mock_book_service, "test_user")
        result = workflow.execute_edit_book(1, {'title': 'New Title'})
        
        assert result[0] is True
        assert "success" in result[1].lower()
    
    def test_book_remove_workflow_book_not_found(self, mock_book_service):
        """Test BookRemoveWorkflow when book doesn't exist."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookRemoveWorkflow
        
        mock_book_service.get_book_by_id.return_value = None
        workflow = BookRemoveWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_remove_book(999, "Damaged beyond repair")
        assert result[0] is False
        assert "not found" in result[1].lower()
    
    def test_book_remove_workflow_book_borrowed(self, mock_book_service):
        """Test BookRemoveWorkflow when book is currently borrowed."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookRemoveWorkflow
        
        mock_book = Mock()
        mock_book.available = False  # Book is borrowed
        mock_book_service.get_book_by_id.return_value = mock_book
        workflow = BookRemoveWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_remove_book(1, "Damaged beyond repair")
        assert result[0] is False
        assert "borrowed" in result[1].lower()
    
    def test_book_remove_workflow_success(self, mock_book_service):
        """Test BookRemoveWorkflow with valid data."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookRemoveWorkflow
        
        mock_book = Mock()
        mock_book.available = True
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.book_number = "TEST-001"
        mock_book.author = "Test Author"
        mock_book.category = "Test"
        mock_book.subject = ""
        mock_book.class_field = ""
        mock_book.isbn = ""
        mock_book.publication_date = ""
        mock_book.book_condition = "Good"
        mock_book_service.get_book_by_id.return_value = mock_book
        mock_book_service.delete_book.return_value = True
        
        workflow = BookRemoveWorkflow(mock_book_service, "test_user")
        result = workflow.execute_remove_book(1, "Damaged beyond repair", "Additional notes")
        
        assert result[0] is True
        assert "success" in result[1].lower()
    
    def test_book_borrow_workflow_book_not_available(self, mock_book_service):
        """Test BookBorrowWorkflow when book is not available."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookBorrowWorkflow
        
        mock_book_service.check_book_availability.return_value = False
        workflow = BookBorrowWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_borrow_book("student", "S1234", 1)
        assert result[0] is False
        assert "not available" in result[1].lower()
    
    def test_book_borrow_workflow_success(self, mock_book_service):
        """Test BookBorrowWorkflow with valid data."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookBorrowWorkflow
        
        mock_book_service.check_book_availability.return_value = True
        mock_book_service.reserve_book.return_value = True
        workflow = BookBorrowWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_borrow_book("student", "S1234", 1)
        assert result[0] is True
        assert "success" in result[1].lower()
    
    def test_book_return_workflow_student_success(self, mock_book_service):
        """Test BookReturnWorkflow for student with valid data."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookReturnWorkflow
        
        mock_book_service.return_book_student.return_value = True
        workflow = BookReturnWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_return_book("student", "S1234", 1, "Good", 0.0)
        assert result[0] is True
        assert "success" in result[1].lower()
    
    def test_book_return_workflow_teacher_success(self, mock_book_service):
        """Test BookReturnWorkflow for teacher with valid data."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookReturnWorkflow
        
        mock_book_service.return_book_teacher.return_value = True
        workflow = BookReturnWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_return_book("teacher", "T1234", 1, "Good", 0.0)
        assert result[0] is True
        assert "success" in result[1].lower()
    
    def test_book_search_workflow_empty_query(self, mock_book_service):
        """Test BookSearchWorkflow with empty query."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookSearchWorkflow
        
        mock_book_service.get_all_books.return_value = []
        workflow = BookSearchWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_search_books("")
        assert result[0] == []
        assert result[1] == ""
    
    def test_book_search_workflow_with_query(self, mock_book_service):
        """Test BookSearchWorkflow with search query."""
        from school_system.gui.windows.book_window.workflows.book_workflows import BookSearchWorkflow
        
        mock_book = Mock()
        mock_book.title = "Test Book"
        mock_book_service.search_books.return_value = [mock_book]
        workflow = BookSearchWorkflow(mock_book_service, "test_user")
        
        result = workflow.execute_search_books("test")
        assert len(result[0]) == 1
        assert result[1] == ""


class TestBookManagementTab:
    """Test the BookManagementTab class."""
    
    def test_book_management_tab_creation(self, qapp):
        """Test that BookManagementTab can be created."""
        from school_system.gui.windows.book_window.tabs.book_management_tab import BookManagementTab
        
        tab = BookManagementTab()
        assert tab is not None
        assert isinstance(tab, QWidget)
    
    def test_book_management_tab_signals(self, qapp):
        """Test that BookManagementTab emits signals."""
        from school_system.gui.windows.book_window.tabs.book_management_tab import BookManagementTab
        
        tab = BookManagementTab()
        
        # Check signals exist
        assert hasattr(tab, 'add_book_requested')
        assert hasattr(tab, 'edit_book_requested')
        assert hasattr(tab, 'remove_book_requested')
        assert hasattr(tab, 'refresh_books_requested')
        assert hasattr(tab, 'search_books_requested')
    
    def test_book_management_tab_ui_components(self, qapp):
        """Test that BookManagementTab has required UI components."""
        from school_system.gui.windows.book_window.tabs.book_management_tab import BookManagementTab
        
        tab = BookManagementTab()
        
        # Check add form components exist
        assert hasattr(tab, 'add_subject_combo')
        assert hasattr(tab, 'add_class_combo')
        assert hasattr(tab, 'add_book_number_input')
        assert hasattr(tab, 'add_title_input')
        assert hasattr(tab, 'add_author_input')
        assert hasattr(tab, 'add_condition_combo')
        
        # Check edit form components exist
        assert hasattr(tab, 'edit_book_id_input')
        assert hasattr(tab, 'edit_title_input')
        assert hasattr(tab, 'edit_author_input')
        assert hasattr(tab, 'edit_condition_combo')
        
        # Check remove form components exist
        assert hasattr(tab, 'remove_book_id_input')
        assert hasattr(tab, 'remove_reason_combo')
        assert hasattr(tab, 'remove_notes_input')
        
        # Check view section components exist
        assert hasattr(tab, 'search_box')
        assert hasattr(tab, 'books_table')
    
    def test_book_management_tab_search_signal_exists(self, qapp):
        """Test that search_books_requested signal exists and is a pyqtSignal."""
        from school_system.gui.windows.book_window.tabs.book_management_tab import BookManagementTab
        from PyQt6.QtCore import pyqtSignal
        
        # Check that the class has the signal defined as a pyqtSignal
        assert hasattr(BookManagementTab, 'search_books_requested')
        assert isinstance(BookManagementTab.search_books_requested, pyqtSignal)
        
        # Also verify the instance has a callable signal
        tab = BookManagementTab()
        assert hasattr(tab, 'search_books_requested')
        assert callable(tab.search_books_requested.emit)
    
    def test_book_management_tab_refresh_signal_exists(self, qapp):
        """Test that refresh_books_requested signal exists and is a pyqtSignal."""
        from school_system.gui.windows.book_window.tabs.book_management_tab import BookManagementTab
        from PyQt6.QtCore import pyqtSignal
        
        # Check that the class has the signal defined as a pyqtSignal
        assert hasattr(BookManagementTab, 'refresh_books_requested')
        assert isinstance(BookManagementTab.refresh_books_requested, pyqtSignal)
        
        # Also verify the instance has a callable signal
        tab = BookManagementTab()
        assert hasattr(tab, 'refresh_books_requested')
        assert callable(tab.refresh_books_requested.emit)
    
    def test_book_management_tab_populate_books_table(self, qapp):
        """Test populating the books table with data."""
        from school_system.gui.windows.book_window.tabs.book_management_tab import BookManagementTab
        
        tab = BookManagementTab()
        
        # Create mock book data
        mock_book = Mock()
        mock_book.id = 1
        mock_book.book_number = "TEST-001"
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        mock_book.category = "Test"
        mock_book.available = True
        mock_book.book_condition = "Good"
        mock_book.subject = "Mathematics"
        
        # Populate table
        tab.populate_books_table([mock_book])
        
        # Check that row was added
        assert tab.books_table.rowCount() == 1
        
        # Check cell content
        item = tab.books_table.item(0, 0)
        assert item.text() == "1"


class TestUIComponents:
    """Test the UI components."""
    
    def test_flex_layout_column(self):
        """Test FlexLayout in column mode."""
        from school_system.gui.windows.book_window.components.base_components import FlexLayout
        
        layout = FlexLayout("column", False)
        assert layout is not None
        assert hasattr(layout, 'add_widget')
        assert hasattr(layout, 'set_spacing')
        assert hasattr(layout, 'set_contents_margins')
    
    def test_flex_layout_row(self):
        """Test FlexLayout in row mode."""
        from school_system.gui.windows.book_window.components.base_components import FlexLayout
        
        layout = FlexLayout("row", False)
        assert layout is not None
    
    def test_card_creation(self):
        """Test Card creation."""
        from school_system.gui.windows.book_window.components.base_components import Card
        
        card = Card("Test Title", "Test Subtitle")
        assert card is not None
        assert isinstance(card, QWidget)
    
    def test_input_field_creation(self):
        """Test InputField creation."""
        from school_system.gui.windows.book_window.components.base_components import InputField
        
        input_field = InputField("Enter text...")
        assert input_field is not None
        assert input_field.placeholderText() == "Enter text..."
    
    def test_text_area_creation(self):
        """Test TextArea creation."""
        from school_system.gui.windows.book_window.components.base_components import TextArea
        
        text_area = TextArea("Enter text...")
        assert text_area is not None
    
    def test_button_creation_primary(self):
        """Test Button creation with primary type."""
        from school_system.gui.windows.book_window.components.base_components import Button
        
        button = Button("Click Me", "primary")
        assert button is not None
        assert button.text() == "Click Me"
    
    def test_button_creation_secondary(self):
        """Test Button creation with secondary type."""
        from school_system.gui.windows.book_window.components.base_components import Button
        
        button = Button("Click Me", "secondary")
        assert button is not None
    
    def test_button_creation_danger(self):
        """Test Button creation with danger type."""
        from school_system.gui.windows.book_window.components.base_components import Button
        
        button = Button("Delete", "danger")
        assert button is not None
    
    def test_combo_box_creation(self):
        """Test ComboBox creation."""
        from school_system.gui.windows.book_window.components.base_components import ComboBox
        from PyQt6.QtWidgets import QComboBox
        
        combo = ComboBox()
        assert combo is not None
        assert isinstance(combo, QComboBox)
    
    def test_table_creation(self):
        """Test Table creation."""
        from school_system.gui.windows.book_window.components.base_components import Table
        
        table = Table(0, 5)
        assert table is not None
        assert table.columnCount() == 5
    
    def test_search_box_creation(self):
        """Test SearchBox creation."""
        from school_system.gui.windows.book_window.components.base_components import SearchBox
        
        search_box = SearchBox("Search...")
        assert search_box is not None
        assert isinstance(search_box, QWidget)
    
    def test_validation_label_set_success(self):
        """Test ValidationLabel set_success method."""
        from school_system.gui.windows.book_window.components.base_components import ValidationLabel
        
        label = ValidationLabel()
        label.set_success("Success message")
        assert "✓" in label.text()
    
    def test_validation_label_set_error(self):
        """Test ValidationLabel set_error method."""
        from school_system.gui.windows.book_window.components.base_components import ValidationLabel
        
        label = ValidationLabel()
        label.set_error("Error message")
        assert "✗" in label.text()
    
    def test_validation_label_clear(self):
        """Test ValidationLabel clear method."""
        from school_system.gui.windows.book_window.components.base_components import ValidationLabel
        
        label = ValidationLabel()
        label.set_error("Error")
        label.clear()
        assert label.text() == ""


class TestBookWindowConstants:
    """Test the constants module."""
    
    def test_spacing_constants(self):
        """Test spacing constants have correct values."""
        from school_system.gui.windows.book_window.utils.constants import (
            SPACING_SMALL, SPACING_MEDIUM, SPACING_LARGE
        )
        assert SPACING_SMALL > 0
        assert SPACING_MEDIUM > 0
        assert SPACING_LARGE > 0
        assert SPACING_SMALL < SPACING_MEDIUM < SPACING_LARGE
    
    def test_card_constants(self):
        """Test card constants have correct values."""
        from school_system.gui.windows.book_window.utils.constants import (
            CARD_PADDING, CARD_SPACING
        )
        assert CARD_PADDING > 0
        assert CARD_SPACING > 0
    
    def test_required_fields(self):
        """Test required fields list."""
        from school_system.gui.windows.book_window.utils.constants import REQUIRED_FIELDS
        assert isinstance(REQUIRED_FIELDS, list)
        assert len(REQUIRED_FIELDS) > 0
        assert 'book_number' in REQUIRED_FIELDS
        assert 'subject' in REQUIRED_FIELDS
        assert 'class' in REQUIRED_FIELDS
    
    def test_book_conditions(self):
        """Test book conditions list."""
        from school_system.gui.windows.book_window.utils.constants import BOOK_CONDITIONS
        assert isinstance(BOOK_CONDITIONS, list)
        assert len(BOOK_CONDITIONS) > 0
        assert "New" in BOOK_CONDITIONS
        assert "Good" in BOOK_CONDITIONS
    
    def test_user_types(self):
        """Test user types list."""
        from school_system.gui.windows.book_window.utils.constants import USER_TYPES
        assert isinstance(USER_TYPES, list)
        assert "student" in USER_TYPES
        assert "teacher" in USER_TYPES
    
    def test_return_conditions(self):
        """Test return conditions list."""
        from school_system.gui.windows.book_window.utils.constants import RETURN_CONDITIONS
        assert isinstance(RETURN_CONDITIONS, list)
        assert len(RETURN_CONDITIONS) > 0
    
    def test_standard_subjects(self):
        """Test standard subjects list."""
        from school_system.gui.windows.book_window.utils.constants import STANDARD_SUBJECTS
        assert isinstance(STANDARD_SUBJECTS, list)
        assert len(STANDARD_SUBJECTS) > 0
        assert "Mathematics" in STANDARD_SUBJECTS
        assert "English" in STANDARD_SUBJECTS
    
    def test_standard_classes(self):
        """Test standard classes list."""
        from school_system.gui.windows.book_window.utils.constants import STANDARD_CLASSES
        assert isinstance(STANDARD_CLASSES, list)
        assert len(STANDARD_CLASSES) > 0
        assert "Form 1" in STANDARD_CLASSES
    
    def test_standard_streams(self):
        """Test standard streams list."""
        from school_system.gui.windows.book_window.utils.constants import STANDARD_STREAMS
        assert isinstance(STANDARD_STREAMS, list)
        assert len(STANDARD_STREAMS) > 0
    
    def test_standard_terms(self):
        """Test standard terms list."""
        from school_system.gui.windows.book_window.utils.constants import STANDARD_TERMS
        assert isinstance(STANDARD_TERMS, list)
        assert len(STANDARD_TERMS) > 0


class TestBookWindowEdgeCases:
    """Test edge cases and error handling."""
    
    def test_book_window_non_admin_role_denied(self, qapp, mock_book_service):
        """Test that non-admin users are denied access."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.show_error_message'):
            with patch('PyQt6.QtWidgets.QMainWindow.close'):
                # Use None as parent since we can't use Mock for QMainWindow
                window = BookWindow(None, "test_user", "student")
                # Window should close immediately for non-admin
                assert not window.isVisible()
    
    def test_book_window_admin_role_allowed(self, qapp, mock_book_service):
        """Test that admin users are allowed access."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                assert window is not None
                window.close()
    
    def test_book_window_librarian_role_allowed(self, qapp, mock_book_service):
        """Test that librarian users are allowed access."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "librarian_user", "librarian")
                assert window is not None
                window.close()
    
    def test_borrow_book_invalid_book_id(self, qapp, mock_book_service):
        """Test handling of invalid book ID in borrow workflow."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                with patch('school_system.gui.windows.book_window.book_window.show_error_message') as mock_error:
                    window = BookWindow(None, "admin_user", "admin")
                    
                    # Set invalid book ID (non-numeric)
                    window.borrow_book_id_input.setText("invalid")
                    window._on_borrow_book()
                    
                    mock_error.assert_called()
                    window.close()
    
    def test_return_book_invalid_fine_amount(self, qapp, mock_book_service):
        """Test handling of invalid fine amount in return workflow."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                with patch('school_system.gui.windows.book_window.book_window.show_error_message') as mock_error:
                    window = BookWindow(None, "admin_user", "admin")
                    
                    # Set invalid fine amount (non-numeric)
                    window.return_fine_input.setText("invalid")
                    window._on_return_book()
                    
                    mock_error.assert_called()
                    window.close()


class TestBookWindowIntegration:
    """Integration tests for the BookWindow."""
    
    def test_book_window_tab_count(self, qapp, mock_book_service):
        """Test that BookWindow has all expected tabs."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                # Find the tab widget
                tab_widget = None
                for child in window.findChildren(QTabWidget):
                    tab_widget = child
                    break
                
                assert tab_widget is not None
                assert tab_widget.count() == 6  # Book Management, Borrowing, Distribution, Advanced Returns, Import/Export, Reports
                window.close()
    
    def test_book_window_workflows_initialized(self, qapp, mock_book_service):
        """Test that all workflows are properly initialized."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                assert hasattr(window, 'add_workflow')
                assert hasattr(window, 'edit_workflow')
                assert hasattr(window, 'remove_workflow')
                assert hasattr(window, 'borrow_workflow')
                assert hasattr(window, 'return_workflow')
                assert hasattr(window, 'search_workflow')
                window.close()
    
    def test_book_window_undo_timer_initialized(self, qapp, mock_book_service):
        """Test that undo timer is properly initialized."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                assert hasattr(window, 'undo_timer')
                assert isinstance(window.undo_timer, QTimer)
                assert window.last_action is None
                window.close()
    
    def test_book_window_clear_undo_state(self, qapp, mock_book_service):
        """Test clearing the undo state."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                # Set some undo state
                window.last_action = {'type': 'add', 'data': {}}
                
                # Clear undo state
                window._clear_undo_state()
                
                assert window.last_action is None
                assert not window.undo_timer.isActive()
                window.close()


class TestBookWindowDataValidation:
    """Tests for data input handling and validation."""
    
    def test_borrowing_tab_user_type_combo(self, qapp, mock_book_service):
        """Test that borrowing tab has user type combo box."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                assert hasattr(window, 'borrow_user_type_combo')
                assert window.borrow_user_type_combo.count() > 0
                window.close()
    
    def test_borrowing_tab_user_id_input(self, qapp, mock_book_service):
        """Test that borrowing tab has user ID input field."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                assert hasattr(window, 'borrow_user_id_input')
                window.close()
    
    def test_borrowing_tab_book_id_input(self, qapp, mock_book_service):
        """Test that borrowing tab has book ID input field."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                assert hasattr(window, 'borrow_book_id_input')
                window.close()
    
    def test_distribution_tab_inputs(self, qapp, mock_book_service):
        """Test that distribution tab has all required input fields."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                assert hasattr(window, 'create_class_name_input')
                assert hasattr(window, 'create_stream_input')
                assert hasattr(window, 'create_subject_input')
                assert hasattr(window, 'create_term_input')
                assert hasattr(window, 'create_student_ids_input')
                window.close()
    
    def test_reports_tab_inputs(self, qapp, mock_book_service):
        """Test that reports tab has all required input fields."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                assert hasattr(window, 'popular_limit_input')
                assert hasattr(window, 'popular_books_display')
                assert hasattr(window, 'overdue_books_display')
                window.close()
    
    def test_advanced_return_tab_inputs(self, qapp, mock_book_service):
        """Test that advanced return tab has all required input fields."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                window = BookWindow(None, "admin_user", "admin")
                
                assert hasattr(window, 'bulk_stream_combo')
                assert hasattr(window, 'bulk_subject_combo')
                assert hasattr(window, 'bulk_return_condition_combo')
                assert hasattr(window, 'bulk_return_fine_input')
                assert hasattr(window, 'student_return_id_input')
                assert hasattr(window, 'book_return_number_input')
                window.close()


class TestBookWindowUserInteractions:
    """Tests for user interactions and callbacks."""
    
    def test_borrow_book_button_click(self, qapp, mock_book_service):
        """Test borrow book button click handler."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                with patch.object(mock_book_service, 'check_book_availability', return_value=True):
                    with patch.object(mock_book_service, 'reserve_book', return_value=True):
                        with patch('school_system.gui.windows.book_window.book_window.show_success_message') as mock_success:
                            window = BookWindow(None, "admin_user", "admin")
                            
                            # Set values
                            window.borrow_user_type_combo.setCurrentIndex(0)  # student
                            window.borrow_user_id_input.setText("S1234")
                            window.borrow_book_id_input.setText("1")
                            
                            # Click borrow button
                            window._on_borrow_book()
                            
                            mock_success.assert_called()
                            window.close()
    
    def test_return_book_button_click(self, qapp, mock_book_service):
        """Test return book button click handler."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                with patch.object(mock_book_service, 'return_book_student', return_value=True):
                    with patch('school_system.gui.windows.book_window.book_window.show_success_message') as mock_success:
                        window = BookWindow(None, "admin_user", "admin")
                        
                        # Set values
                        window.return_user_type_combo.setCurrentIndex(0)  # student
                        window.return_user_id_input.setText("S1234")
                        window.return_book_id_input.setText("1")
                        window.return_condition_combo.setCurrentIndex(0)  # Good
                        window.return_fine_input.setText("0")
                        
                        # Click return button
                        window._on_return_book()
                        
                        mock_success.assert_called()
                        window.close()
    
    def test_create_distribution_session(self, qapp, mock_book_service):
        """Test create distribution session handler."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                with patch.object(mock_book_service, 'create_distribution_session_with_students', return_value=1):
                    with patch('school_system.gui.windows.book_window.book_window.show_success_message') as mock_success:
                        window = BookWindow(None, "admin_user", "admin")
                        
                        # Set values
                        window.create_class_name_input.setText("Form 1")
                        window.create_stream_input.setText("East")
                        window.create_subject_input.setText("Mathematics")
                        window.create_term_input.setText("Term 1")
                        window.create_student_ids_input.setText("S1234,S1235")
                        
                        # Click create session button
                        window._on_create_distribution_session()
                        
                        mock_success.assert_called()
                        window.close()
    
    def test_generate_popular_books_report(self, qapp, mock_book_service):
        """Test generate popular books report handler."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        mock_book = Mock()
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        mock_book.borrow_count = 10
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                with patch.object(mock_book_service, 'get_popular_books', return_value=[mock_book]):
                    window = BookWindow(None, "admin_user", "admin")
                    
                    # Set limit
                    window.popular_limit_input.setText("10")
                    
                    # Click generate button
                    window._on_generate_popular_books()
                    
                    # Check that report was generated
                    assert window.popular_books_display.toPlainText() != ""
                    window.close()
    
    def test_generate_overdue_books_report(self, qapp, mock_book_service):
        """Test generate overdue books report handler."""
        from school_system.gui.windows.book_window.book_window import BookWindow
        
        mock_overdue = Mock()
        mock_overdue.book_id = 1
        mock_overdue.student_id = "S1234"
        mock_overdue.borrowed_on = "2025-01-01"
        
        with patch('school_system.gui.windows.book_window.book_window.BookService', return_value=mock_book_service):
            with patch.object(mock_book_service, 'get_all_books', return_value=[]):
                with patch.object(mock_book_service, 'get_all_overdue_books', return_value=[mock_overdue]):
                    window = BookWindow(None, "admin_user", "admin")
                    
                    # Click generate button
                    window._on_generate_overdue_books()
                    
                    # Check that report was generated
                    assert window.overdue_books_display.toPlainText() != ""
                    window.close()


class TestBookWindowPackageExports:
    """Test the package __all__ exports."""
    
    def test_all_exports_main_window(self):
        """Test that main window is in __all__."""
        from school_system.gui.windows.book_window import __all__
        
        assert 'BookWindow' in __all__
    
    def test_all_exports_ui_components(self):
        """Test that UI components are in __all__."""
        from school_system.gui.windows.book_window import __all__
        
        assert 'FlexLayout' in __all__
        assert 'Card' in __all__
        assert 'InputField' in __all__
        assert 'Button' in __all__
        assert 'ComboBox' in __all__
        assert 'Table' in __all__
        assert 'SearchBox' in __all__
    
    def test_all_exports_workflows(self):
        """Test that workflows are in __all__."""
        from school_system.gui.windows.book_window import __all__
        
        assert 'BookAddWorkflow' in __all__
        assert 'BookEditWorkflow' in __all__
        assert 'BookRemoveWorkflow' in __all__
        assert 'BookBorrowWorkflow' in __all__
        assert 'BookReturnWorkflow' in __all__
        assert 'BookSearchWorkflow' in __all__
    
    def test_all_exports_constants(self):
        """Test that constants are in __all__."""
        from school_system.gui.windows.book_window import __all__
        
        assert 'SPACING_SMALL' in __all__
        assert 'CARD_PADDING' in __all__
        assert 'BOOK_CONDITIONS' in __all__
        assert 'USER_TYPES' in __all__
        assert 'STANDARD_SUBJECTS' in __all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
