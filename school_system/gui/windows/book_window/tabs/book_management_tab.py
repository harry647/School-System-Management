"""
Book Management Tab for the book window.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QTableWidgetItem
from PyQt6.QtCore import pyqtSignal

from school_system.gui.windows.book_window.components import (
    FlexLayout, Card, InputField, TextArea, Button, ComboBox, Table, SearchBox, ValidationLabel
)
from school_system.gui.windows.book_window.utils import (
    SPACING_SMALL, SPACING_MEDIUM, SPACING_LARGE,
    CARD_PADDING, CARD_SPACING,
    BOOK_CONDITIONS, STANDARD_SUBJECTS, STANDARD_CLASSES
)


class BookManagementTab(QWidget):
    """Book management tab with standardized workflows."""
    
    # Signals for communication with main window
    add_book_requested = pyqtSignal(dict)
    edit_book_requested = pyqtSignal(int, dict)
    remove_book_requested = pyqtSignal(int, str, str)
    refresh_books_requested = pyqtSignal()
    search_books_requested = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the book management tab."""
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = FlexLayout("column", False)
        layout.set_contents_margins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        layout.set_spacing(CARD_SPACING)
        
        # Add Books Section (Cataloging Workflow)
        add_section = Card("Add Books (Cataloging)", "Create new book entries in the system")
        add_form = self._create_add_book_form()
        add_section.layout.add_widget(add_form)
        layout.add_widget(add_section)
        
        # Edit Books Section (Editing Workflow)
        edit_section = Card("Edit Books", "Modify existing book information")
        edit_form = self._create_edit_book_form()
        edit_section.layout.add_widget(edit_form)
        layout.add_widget(edit_section)
        
        # Remove Books Section (Decommissioning Workflow)
        remove_section = Card("Remove Books (Decommissioning)", "Permanently remove books from the system")
        remove_form = self._create_remove_book_form()
        remove_section.layout.add_widget(remove_form)
        layout.add_widget(remove_section)
        
        # View Books Section
        view_section = Card("View Books", "Browse and search existing books")
        view_form = self._create_view_books_section()
        view_section.layout.add_widget(view_form)
        layout.add_widget(view_section)
        
        self.setLayout(layout._layout)
    
    def _create_add_book_form(self) -> QWidget:
        """Create the add book form following the standardized workflow."""
        form = QWidget()
        form_layout = FlexLayout("column", False)
        form_layout.set_spacing(SPACING_SMALL)
        
        # Subject (validated against school curriculum)
        subject_label = QLabel("Subject:")
        form_layout.add_widget(subject_label)
        self.add_subject_combo = ComboBox()
        self.add_subject_combo.addItems(STANDARD_SUBJECTS)
        self.add_subject_combo.setEditable(True)
        form_layout.add_widget(self.add_subject_combo)
        
        # Class/Form (linked to active academic years)
        class_label = QLabel("Class/Form:")
        form_layout.add_widget(class_label)
        self.add_class_combo = ComboBox()
        self.add_class_combo.addItems(STANDARD_CLASSES)
        self.add_class_combo.setEditable(True)
        form_layout.add_widget(self.add_class_combo)
        
        # Book Number (physical label with real-time validation)
        book_number_label = QLabel("Book Number:")
        form_layout.add_widget(book_number_label)
        self.add_book_number_input = InputField("Enter book number (must be unique)")
        self.add_book_number_input.textChanged.connect(self._validate_book_number_real_time)
        form_layout.add_widget(self.add_book_number_input)
        
        # Validation feedback
        self.book_number_validation_label = ValidationLabel()
        form_layout.add_widget(self.book_number_validation_label)
        
        # Title
        title_label = QLabel("Title:")
        form_layout.add_widget(title_label)
        self.add_title_input = InputField("Enter book title")
        form_layout.add_widget(self.add_title_input)
        
        # Author
        author_label = QLabel("Author:")
        form_layout.add_widget(author_label)
        self.add_author_input = InputField("Enter author name")
        form_layout.add_widget(self.add_author_input)
        
        # Condition (enum with auto-flagging)
        condition_label = QLabel("Condition:")
        form_layout.add_widget(condition_label)
        self.add_condition_combo = ComboBox()
        self.add_condition_combo.addItems(BOOK_CONDITIONS)
        form_layout.add_widget(self.add_condition_combo)
        
        # Additional fields
        category_label = QLabel("Category:")
        form_layout.add_widget(category_label)
        self.add_category_input = InputField("Enter category")
        form_layout.add_widget(self.add_category_input)
        
        isbn_label = QLabel("ISBN:")
        form_layout.add_widget(isbn_label)
        self.add_isbn_input = InputField("Enter ISBN")
        form_layout.add_widget(self.add_isbn_input)
        
        pub_date_label = QLabel("Publication Date:")
        form_layout.add_widget(pub_date_label)
        self.add_pub_date_input = InputField("YYYY-MM-DD")
        form_layout.add_widget(self.add_pub_date_input)
        
        # Notes
        notes_label = QLabel("Notes:")
        form_layout.add_widget(notes_label)
        self.add_notes_input = TextArea()
        self.add_notes_input.setMaximumHeight(80)
        form_layout.add_widget(self.add_notes_input)
        
        # Action button
        add_button = Button("Add Book", "primary")
        add_button.clicked.connect(self._start_add_book_workflow)
        form_layout.add_widget(add_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_edit_book_form(self) -> QWidget:
        """Create the edit book form following the standardized workflow."""
        form = QWidget()
        form_layout = FlexLayout("column", False)
        form_layout.set_spacing(SPACING_SMALL)
        
        # Book ID for lookup
        book_id_label = QLabel("Book ID:")
        form_layout.add_widget(book_id_label)
        self.edit_book_id_input = InputField("Enter book ID to edit")
        form_layout.add_widget(self.edit_book_id_input)
        
        # Load button
        load_button = Button("Load Book Details", "secondary")
        load_button.clicked.connect(self._load_book_for_editing)
        form_layout.add_widget(load_button)
        
        # Editable fields (initially disabled)
        self.edit_title_label = QLabel("New Title:")
        form_layout.add_widget(self.edit_title_label)
        self.edit_title_input = InputField("Enter new title")
        self.edit_title_input.setEnabled(False)
        form_layout.add_widget(self.edit_title_input)
        
        self.edit_author_label = QLabel("New Author:")
        form_layout.add_widget(self.edit_author_label)
        self.edit_author_input = InputField("Enter new author")
        self.edit_author_input.setEnabled(False)
        form_layout.add_widget(self.edit_author_input)
        
        self.edit_condition_label = QLabel("New Condition:")
        form_layout.add_widget(self.edit_condition_label)
        self.edit_condition_combo = ComboBox()
        self.edit_condition_combo.addItems(BOOK_CONDITIONS)
        self.edit_condition_combo.setEnabled(False)
        form_layout.add_widget(self.edit_condition_combo)
        
        self.edit_notes_label = QLabel("Edit Notes:")
        form_layout.add_widget(self.edit_notes_label)
        self.edit_notes_input = TextArea()
        self.edit_notes_input.setMaximumHeight(80)
        self.edit_notes_input.setEnabled(False)
        form_layout.add_widget(self.edit_notes_input)
        
        # Action button
        edit_button = Button("Update Book", "primary")
        edit_button.clicked.connect(self._start_edit_book_workflow)
        edit_button.setEnabled(False)
        self.edit_button = edit_button
        form_layout.add_widget(edit_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_remove_book_form(self) -> QWidget:
        """Create the remove book form following the standardized workflow."""
        form = QWidget()
        form_layout = FlexLayout("column", False)
        form_layout.set_spacing(SPACING_SMALL)
        
        # Book ID for removal
        book_id_label = QLabel("Book ID:")
        form_layout.add_widget(book_id_label)
        self.remove_book_id_input = InputField("Enter book ID to remove")
        form_layout.add_widget(self.remove_book_id_input)
        
        # Reason for removal
        reason_label = QLabel("Reason for Removal:")
        form_layout.add_widget(reason_label)
        self.remove_reason_combo = ComboBox()
        self.remove_reason_combo.addItems([
            "Damaged beyond repair",
            "Lost",
            "Obsolete curriculum",
            "Duplicate entry",
            "Other"
        ])
        self.remove_reason_combo.setEditable(True)
        form_layout.add_widget(self.remove_reason_combo)
        
        # Additional notes
        notes_label = QLabel("Additional Notes:")
        form_layout.add_widget(notes_label)
        self.remove_notes_input = TextArea()
        self.remove_notes_input.setMaximumHeight(80)
        form_layout.add_widget(self.remove_notes_input)
        
        # Action button
        remove_button = Button("Remove Book", "danger")
        remove_button.clicked.connect(self._start_remove_book_workflow)
        form_layout.add_widget(remove_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_view_books_section(self) -> QWidget:
        """Create the view books section."""
        form = QWidget()
        form_layout = FlexLayout("column", False)
        form_layout.set_spacing(SPACING_SMALL)
        
        # Search box
        self.search_box = SearchBox("Search books...")
        self.search_box.search_input.textChanged.connect(self._on_search_books)
        form_layout.add_widget(self.search_box)
        
        # Refresh button
        refresh_button = Button("Refresh Books", "secondary")
        refresh_button.clicked.connect(self._refresh_books_table)
        form_layout.add_widget(refresh_button)
        
        # Books table
        self.books_table = Table(0, 8)
        self.books_table.setHorizontalHeaderLabels([
            "ID", "Book Number", "Title", "Author", "Category",
            "Available", "Condition", "Subject"
        ])
        form_layout.add_widget(self.books_table)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _validate_book_number_real_time(self, text: str):
        """Real-time validation for book number uniqueness."""
        # This would be connected to the main window's validation logic
        pass
    
    def _load_book_for_editing(self):
        """Load book details for editing."""
        # This would be connected to the main window's book loading logic
        pass
    
    def _start_add_book_workflow(self):
        """Start the standardized add book workflow."""
        # This would be connected to the main window's add book workflow
        pass
    
    def _start_edit_book_workflow(self):
        """Start the standardized edit book workflow."""
        # This would be connected to the main window's edit book workflow
        pass
    
    def _start_remove_book_workflow(self):
        """Start the standardized remove book workflow."""
        # This would be connected to the main window's remove book workflow
        pass
    
    def _on_search_books(self, query: str):
        """Handle book search."""
        self.search_books_requested.emit(query)
    
    def _refresh_books_table(self):
        """Refresh the books table."""
        self.refresh_books_requested.emit()
    
    def populate_books_table(self, books):
        """Populate the books table with data."""
        self.books_table.setRowCount(0)
        
        for book in books:
            row_position = self.books_table.rowCount()
            self.books_table.insertRow(row_position)
            
            self.books_table.setItem(row_position, 0, QTableWidgetItem(str(book.id)))
            self.books_table.setItem(row_position, 1, QTableWidgetItem(book.book_number))
            self.books_table.setItem(row_position, 2, QTableWidgetItem(book.title))
            self.books_table.setItem(row_position, 3, QTableWidgetItem(book.author))
            self.books_table.setItem(row_position, 4, QTableWidgetItem(book.category or ""))
            self.books_table.setItem(row_position, 5, QTableWidgetItem("Yes" if book.available else "No"))
            self.books_table.setItem(row_position, 6, QTableWidgetItem(book.book_condition or ""))
            self.books_table.setItem(row_position, 7, QTableWidgetItem(getattr(book, 'subject', '') or ""))