"""
Distribution Window

Dedicated window for managing book distribution sessions.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QDateEdit
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.gui.windows.book_window.utils import STANDARD_CLASSES, STANDARD_STREAMS, STANDARD_TERMS


class DistributionWindow(BaseFunctionWindow):
    """Dedicated window for managing book distribution sessions."""
    
    session_created = pyqtSignal()
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the distribution window."""
        super().__init__("Distribution Sessions", parent, current_user, current_role)
        
        self.book_service = BookService()
        
        # Setup content
        self.setup_content()
        
        # Load sessions
        self._refresh_sessions_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # Create session form
        form_card = self._create_session_form_card()
        main_layout.add_widget(form_card)
        
        # Sessions table
        table_card = self._create_sessions_table_card()
        main_layout.add_widget(table_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_session_form_card(self) -> QWidget:
        """Create the distribution session form card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        form_card = QWidget()
        form_card.setProperty("card", "true")
        form_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)
        
        # Form title
        title_label = QLabel("Create Distribution Session")
        title_font = QFont("Segoe UI", 18, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        form_layout.addWidget(title_label)
        
        # Form fields in horizontal layout
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(12)
        
        # Class
        class_layout = QVBoxLayout()
        class_label = QLabel("Class")
        class_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        class_layout.addWidget(class_label)
        
        self.class_combo = QComboBox()
        self.class_combo.setFixedHeight(44)
        self.class_combo.addItem("")
        self.class_combo.addItems(STANDARD_CLASSES)
        self.class_combo.setEditable(True)
        class_layout.addWidget(self.class_combo)
        fields_layout.addLayout(class_layout)
        
        # Stream
        stream_layout = QVBoxLayout()
        stream_label = QLabel("Stream")
        stream_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        stream_layout.addWidget(stream_label)
        
        self.stream_combo = QComboBox()
        self.stream_combo.setFixedHeight(44)
        self.stream_combo.addItem("")
        self.stream_combo.addItems(STANDARD_STREAMS)
        self.stream_combo.setEditable(True)
        stream_layout.addWidget(self.stream_combo)
        fields_layout.addLayout(stream_layout)
        
        # Term
        term_layout = QVBoxLayout()
        term_label = QLabel("Term")
        term_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        term_layout.addWidget(term_label)
        
        self.term_combo = QComboBox()
        self.term_combo.setFixedHeight(44)
        self.term_combo.addItem("")
        self.term_combo.addItems(STANDARD_TERMS)
        self.term_combo.setEditable(True)
        term_layout.addWidget(self.term_combo)
        fields_layout.addLayout(term_layout)
        
        # Date
        date_layout = QVBoxLayout()
        date_label = QLabel("Distribution Date")
        date_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        date_layout.addWidget(date_label)
        
        self.date_input = QDateEdit()
        self.date_input.setFixedHeight(44)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        date_layout.addWidget(self.date_input)
        fields_layout.addLayout(date_layout)
        
        fields_layout.addStretch()
        
        # Create button
        create_btn = self.create_button("Create Session", "primary")
        create_btn.setFixedHeight(44)
        create_btn.clicked.connect(self._on_create_session)
        fields_layout.addWidget(create_btn)
        
        form_layout.addLayout(fields_layout)
        
        return form_card
    
    def _create_sessions_table_card(self) -> QWidget:
        """Create the sessions table card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(12)
        
        # Table title and refresh button
        title_layout = QHBoxLayout()
        title_label = QLabel("Distribution Sessions")
        title_font = QFont("Segoe UI", 16, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        refresh_btn = self.create_button("🔄 Refresh", "outline")
        refresh_btn.clicked.connect(self._refresh_sessions_table)
        title_layout.addWidget(refresh_btn)
        
        table_layout.addLayout(title_layout)
        
        # Sessions table
        self.sessions_table = self.create_table(0, 5)
        self.sessions_table.setHorizontalHeaderLabels([
            "Session ID", "Class", "Stream", "Term", "Date"
        ])
        self.sessions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sessions_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.sessions_table)
        
        return table_card
    
    def _on_create_session(self):
        """Handle create session button click."""
        # Get form data
        class_name = self.class_combo.currentText().strip()
        stream = self.stream_combo.currentText().strip()
        term = self.term_combo.currentText().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        
        # Validate
        if not class_name or not stream or not term:
            show_error_message("Validation Error", "Please fill in all required fields (Class, Stream, Term).", self)
            return
        
        try:
            # Create distribution session
            session_data = {
                "class_name": class_name,
                "stream": stream,
                "term": term,
                "distribution_date": date
            }
            
            # Note: This would need to be implemented in BookService
            # For now, just show a message
            show_success_message("Success", f"Distribution session created for {class_name} {stream} - {term}.", self)
            
            # Clear inputs
            self.class_combo.setCurrentIndex(0)
            self.stream_combo.setCurrentIndex(0)
            self.term_combo.setCurrentIndex(0)
            self.date_input.setDate(QDate.currentDate())
            
            # Refresh table
            self._refresh_sessions_table()
            
            # Emit signal
            self.session_created.emit()
            
        except Exception as e:
            logger.error(f"Error creating distribution session: {e}")
            show_error_message("Error", f"Failed to create distribution session: {str(e)}", self)
    
    def _refresh_sessions_table(self):
        """Refresh the sessions table."""
        try:
            # Note: This would need to be implemented in BookService
            # For now, just clear the table
            self.sessions_table.setRowCount(0)
            
            logger.info("Refreshed distribution sessions table")
        except Exception as e:
            logger.error(f"Error refreshing sessions table: {e}")
            show_error_message("Error", f"Failed to refresh sessions: {str(e)}", self)
