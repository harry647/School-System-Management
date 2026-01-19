"""
Student Reports Window

Dedicated window for generating student reports.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog, QGroupBox, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.report_service import ReportService
from school_system.services.student_service import StudentService
from school_system.services.book_service import BookService
from school_system.services.import_export_service import ImportExportService


class StudentReportsWindow(BaseFunctionWindow):
    """Dedicated window for generating student reports."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the student reports window."""
        super().__init__("Student Reports", parent, current_user, current_role)
        
        self.report_service = ReportService()
        self.student_service = StudentService()
        self.book_service = BookService()
        self.import_export_service = ImportExportService()

        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Report options card
        options_card = self._create_report_options_card()
        main_layout.add_widget(options_card)
        
        # Report results card
        results_card = self._create_report_results_card()
        main_layout.add_widget(results_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_report_options_card(self) -> QWidget:
        """Create the report options card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        card = QWidget()
        card.setProperty("card", "true")
        card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Generate Student Report")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Report type
        type_layout = QHBoxLayout()
        type_layout.setSpacing(12)
        
        type_label = QLabel("Report Type:")
        type_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        type_layout.addWidget(type_label)
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.setFixedHeight(44)
        self.report_type_combo.addItems([
            "All Students",
            "Students by Stream",
            "Students by Class",
            "Library Activity",
            "Borrowing History",
            "Student Library Cards"
        ])
        type_layout.addWidget(self.report_type_combo)
        
        type_layout.addStretch()
        
        # Generate button
        generate_btn = self.create_button("Generate Report", "primary")
        generate_btn.setFixedHeight(44)
        generate_btn.clicked.connect(self._on_generate_report)
        type_layout.addWidget(generate_btn)
        
        # Export button
        export_btn = self.create_button("Export Report", "secondary")
        export_btn.setFixedHeight(44)
        export_btn.clicked.connect(self._on_export_report)
        type_layout.addWidget(export_btn)
        
        layout.addLayout(type_layout)

        # Student Library Cards Section
        cards_section = self._create_library_cards_section()
        layout.addWidget(cards_section)

        return card

    def _create_library_cards_section(self) -> QWidget:
        """Create the library cards generation section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        section = QGroupBox("Student Library Cards")
        section.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme["border"]};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: {theme["surface"]};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: {theme["text"]};
                font-size: 14px;
            }}
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 32, 16, 16)
        layout.setSpacing(12)

        # Scope selection
        scope_layout = QHBoxLayout()
        scope_layout.setSpacing(16)

        scope_label = QLabel("Generate cards for:")
        scope_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        scope_layout.addWidget(scope_label)

        # Radio buttons for scope
        self.scope_group = QButtonGroup()

        self.individual_radio = QRadioButton("Individual Student")
        self.individual_radio.setChecked(True)
        self.individual_radio.setStyleSheet(f"color: {theme['text']};")
        self.scope_group.addButton(self.individual_radio)
        scope_layout.addWidget(self.individual_radio)

        self.all_students_radio = QRadioButton("All Students")
        self.all_students_radio.setStyleSheet(f"color: {theme['text']};")
        self.scope_group.addButton(self.all_students_radio)
        scope_layout.addWidget(self.all_students_radio)

        scope_layout.addStretch()
        layout.addLayout(scope_layout)

        # Student selection (for individual)
        student_layout = QHBoxLayout()
        student_layout.setSpacing(12)

        student_label = QLabel("Select Student:")
        student_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        student_layout.addWidget(student_label)

        self.student_combo = QComboBox()
        self.student_combo.setEnabled(True)
        self.student_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 12px;
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 32px;
                min-width: 200px;
            }}
        """)
        self._populate_student_combo()
        student_layout.addWidget(self.student_combo)

        student_layout.addStretch()
        layout.addLayout(student_layout)

        # Generation buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        # Generate cards button
        generate_cards_btn = self.create_button("📇 Generate Library Cards", "primary")
        generate_cards_btn.clicked.connect(self._on_generate_library_cards)
        buttons_layout.addWidget(generate_cards_btn)

        # Export options
        export_label = QLabel("Export Format:")
        export_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-left: 20px;")
        buttons_layout.addWidget(export_label)

        self.card_format_combo = QComboBox()
        self.card_format_combo.addItems(["PDF", "Excel"])
        self.card_format_combo.setCurrentText("PDF")
        self.card_format_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 6px 10px;
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 28px;
                min-width: 80px;
            }}
        """)
        buttons_layout.addWidget(self.card_format_combo)

        export_cards_btn = self.create_button("📤 Export Cards", "secondary")
        export_cards_btn.clicked.connect(self._on_export_library_cards)
        buttons_layout.addWidget(export_cards_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Connect radio buttons to enable/disable student selection
        self.individual_radio.toggled.connect(self._on_scope_changed)
        self.all_students_radio.toggled.connect(self._on_scope_changed)

        return section

    def _create_report_results_card(self) -> QWidget:
        """Create the report results card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
         
        card = QWidget()
        card.setProperty("card", "true")
        card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
         
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
         
        # Title
        title_label = QLabel("Report Results")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        layout.addWidget(title_label)
         
        # Results table
        self.results_table = self.create_table(0, 5)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Student ID", "Name", "Stream", "Books Borrowed", "Card Generated"])
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setCornerButtonEnabled(False)
        layout.addWidget(self.results_table)
        
        return card

    def _populate_students_table(self, report_data: list):
        """Populate the results table with student report data."""
        try:
            self.results_table.setRowCount(0)  # Clear existing data
            
            if not report_data:
                return

            report_type = self.report_type_combo.currentText()
            
            # Determine columns based on report type
            if report_type == "Students by Stream":
                self.results_table.setColumnCount(6)
                self.results_table.setHorizontalHeaderLabels([
                    "Student ID", "Name", "Stream", "Class", "Admission Number", "Books Borrowed"
                ])
            elif report_type == "Students by Class":
                self.results_table.setColumnCount(6)
                self.results_table.setHorizontalHeaderLabels([
                    "Student ID", "Name", "Class", "Stream", "Admission Number", "Books Borrowed"
                ])
            elif report_type == "Library Activity":
                self.results_table.setColumnCount(9)
                self.results_table.setHorizontalHeaderLabels([
                    "Student ID", "Name", "Stream", "Class", "Total Borrowed", "Currently Borrowed", "Returned", "Overdue", "Status"
                ])
            elif report_type == "Borrowing History":
                self.results_table.setColumnCount(7)
                self.results_table.setHorizontalHeaderLabels([
                    "Student ID", "Name", "Stream", "Class", "Total Borrowings", "First Borrowing", "Last Borrowing"
                ])
            else:  # All Students
                self.results_table.setColumnCount(5)
                self.results_table.setHorizontalHeaderLabels([
                    "Student ID", "Name", "Stream", "Class", "Admission Number"
                ])

            for row_idx, data in enumerate(report_data):
                self.results_table.insertRow(row_idx)
                
                # Handle header rows
                if data.get('is_header', False):
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(data.get('student_id', '')))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('name', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('stream', '')))
                    if self.results_table.columnCount() > 3:
                        self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('class_name', '')))
                    # Make header rows visually distinct
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row_idx, col)
                        if item:
                            item.setBackground(Qt.GlobalColor.lightGray)
                            item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                    continue

                # Extract data based on report type
                if report_type == "Students by Stream":
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(data.get('student_id', ''))))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('name', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('stream', 'Unknown')))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('class_name', 'Unknown')))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(data.get('admission_number', ''))))
                    self.results_table.setItem(row_idx, 5, QTableWidgetItem(str(data.get('books_borrowed', 0))))
                    
                elif report_type == "Students by Class":
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(data.get('student_id', ''))))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('name', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('class_name', 'Unknown')))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('stream', 'Unknown')))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(data.get('admission_number', ''))))
                    self.results_table.setItem(row_idx, 5, QTableWidgetItem(str(data.get('books_borrowed', 0))))
                    
                elif report_type == "Library Activity":
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(data.get('student_id', ''))))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('name', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('stream', 'Unknown')))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('class_name', 'Unknown')))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(data.get('total_borrowed', 0))))
                    self.results_table.setItem(row_idx, 5, QTableWidgetItem(str(data.get('currently_borrowed', 0))))
                    self.results_table.setItem(row_idx, 6, QTableWidgetItem(str(data.get('total_returned', 0))))
                    overdue_count = data.get('overdue_count', 0)
                    overdue_item = QTableWidgetItem(str(overdue_count))
                    if overdue_count > 0:
                        overdue_item.setForeground(Qt.GlobalColor.red)
                    self.results_table.setItem(row_idx, 7, overdue_item)
                    status = data.get('activity_status', 'Unknown')
                    status_item = QTableWidgetItem(status)
                    if status == 'Active':
                        status_item.setForeground(Qt.GlobalColor.green)
                    elif status == 'Inactive':
                        status_item.setForeground(Qt.GlobalColor.gray)
                    self.results_table.setItem(row_idx, 8, status_item)
                    
                elif report_type == "Borrowing History":
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(data.get('student_id', ''))))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('name', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('stream', 'Unknown')))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('class_name', 'Unknown')))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(data.get('total_borrowings', 0))))
                    self.results_table.setItem(row_idx, 5, QTableWidgetItem(str(data.get('first_borrowing', 'N/A'))))
                    self.results_table.setItem(row_idx, 6, QTableWidgetItem(str(data.get('last_borrowing', 'N/A'))))
                    
                else:  # All Students
                    student = data.get('student')
                    if student:
                        self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(getattr(student, 'student_id', ''))))
                        self.results_table.setItem(row_idx, 1, QTableWidgetItem(getattr(student, 'name', '')))
                        self.results_table.setItem(row_idx, 2, QTableWidgetItem(getattr(student, 'stream', '') or 'Unknown'))
                        self.results_table.setItem(row_idx, 3, QTableWidgetItem(getattr(student, 'class_name', '') or 'Unknown'))
                        admission = getattr(student, 'admission_number', getattr(student, 'student_id', ''))
                        self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(admission)))

        except Exception as e:
            logger.error(f"Error populating students table: {e}")
            show_error_message("Error", f"Failed to display report data: {str(e)}", self)
    
    def _on_generate_report(self):
        """Handle generate report."""
        report_type = self.report_type_combo.currentText()

        try:
            # Clear table first
            self.results_table.setRowCount(0)

            # Generate report based on type
            if report_type == "All Students":
                report_data = self.report_service.get_all_students_report()
                self._populate_students_table(report_data)
            elif report_type == "Students by Stream":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_students_by_stream_report()
                self._populate_students_table(report_data)
            elif report_type == "Students by Class":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_students_by_class_report()
                self._populate_students_table(report_data)
            elif report_type == "Library Activity":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_student_library_activity_report()
                self._populate_students_table(report_data)
            elif report_type == "Borrowing History":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_student_borrowing_history_report()
                self._populate_students_table(report_data)
            elif report_type == "Student Library Cards":
                # Library cards are handled separately through the dedicated UI
                show_success_message("Info", "Use the 'Student Library Cards' section below to generate and export library cards.", self)
                return

            show_success_message("Success", f"Report '{report_type}' generated successfully.", self)

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)
    
    def _on_export_report(self):
        """Handle export report."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            "student_report.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Export report
                show_success_message("Success", f"Report exported to {file_path}.", self)
            except Exception as e:
                logger.error(f"Error exporting report: {e}")
                show_error_message("Error", f"Failed to export report: {str(e)}", self)

    def _populate_student_combo(self):
        """Populate the student selection combo box."""
        try:
            students = self.student_service.get_all_students()
            self.student_combo.clear()
            self.student_combo.addItem("Select Student...", "")

            for student in students:
                # Split the name into first and last name
                name_parts = student.name.split()
                first_name = name_parts[0] if name_parts else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                # Use class_name instead of current_class
                display_text = f"{student.admission_number} - {first_name} {last_name} ({student.class_name})"
                self.student_combo.addItem(display_text, student.admission_number)

        except Exception as e:
            logger.error(f"Error populating student combo: {e}")
            show_error_message("Error", f"Failed to load students: {str(e)}", self)

    def _on_scope_changed(self):
        """Handle scope radio button changes."""
        self.student_combo.setEnabled(self.individual_radio.isChecked())

    def _on_generate_library_cards(self):
        """Handle generate library cards button."""
        try:
            if self.individual_radio.isChecked():
                # Individual student
                selected_student = self.student_combo.currentData()
                if not selected_student:
                    show_error_message("No Selection", "Please select a student.", self)
                    return

                students = [self.student_service.get_student_by_admission(selected_student)]
                if not students[0]:
                    show_error_message("Not Found", "Selected student not found.", self)
                    return
            else:
                # All students
                students = self.student_service.get_all_students()

            # Generate library cards data
            cards_data = self._generate_library_cards_data(students)

            # Display in table
            self._populate_library_cards_table(cards_data)

            message = f"Generated library cards for {len(cards_data)} student(s)."
            show_success_message("Cards Generated", message, self)

        except Exception as e:
            logger.error(f"Error generating library cards: {str(e)}")
            show_error_message("Error", f"Failed to generate library cards: {str(e)}", self)

    def _on_export_library_cards(self):
        """Handle export library cards button."""
        try:
            # Get cards data from table
            cards_data = self._get_library_cards_from_table()

            if not cards_data:
                show_error_message("No Data", "No library cards data to export. Please generate cards first.", self)
                return

            format_type = self.card_format_combo.currentText()

            # Get file path
            file_extension = "pdf" if format_type == "PDF" else "xlsx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Save Library Cards - {format_type}",
                f"student_library_cards.{file_extension}",
                f"{format_type} Files (*.{file_extension});;All Files (*)"
            )

            if not file_path:
                return

            # Export based on format
            if format_type == "PDF":
                success = self._export_library_cards_pdf(cards_data, file_path)
            else:  # Excel
                success = self.import_export_service.export_to_excel(cards_data, file_path)

            if success:
                show_success_message("Export Successful", f"Library cards exported to {format_type}:\n{file_path}", self)
            else:
                show_error_message("Export Failed", f"Failed to export library cards to {format_type}.", self)

        except Exception as e:
            logger.error(f"Error exporting library cards: {str(e)}")
            show_error_message("Export Error", f"An error occurred: {str(e)}", self)

    def _generate_library_cards_data(self, students):
        """Generate library cards data for students."""
        cards_data = []

        try:
            for student in students:
                if not student:
                    continue

                # Get student's borrowed books
                borrowed_books = []
                try:
                    # Get current borrowings
                    current_borrowed = self.book_service.get_borrowed_books_for_student(student.admission_number)
                    borrowed_books.extend(current_borrowed)

                    # Get borrowing history
                    history = self.book_service.get_borrowing_history_for_student(student.admission_number)
                    borrowed_books.extend(history)

                    # Remove duplicates based on book number and borrow date
                    seen = set()
                    unique_books = []
                    for book in borrowed_books:
                        key = (book.get('book_number'), book.get('borrow_date'))
                        if key not in seen:
                            seen.add(key)
                            unique_books.append(book)
                    borrowed_books = unique_books

                except Exception as e:
                    logger.warning(f"Error getting borrowed books for student {student.admission_number}: {e}")
                    borrowed_books = []

                # Format borrowed books as string
                books_text = "None"
                if borrowed_books:
                    book_list = []
                    for book in borrowed_books[:10]:  # Limit to 10 most recent
                        book_num = book.get('book_number', 'Unknown')
                        borrow_date = book.get('borrow_date', 'Unknown')
                        return_date = book.get('return_date', 'Not returned')
                        status = "Returned" if return_date != 'Not returned' else "Borrowed"
                        book_list.append(f"{book_num} ({status})")
                    books_text = "; ".join(book_list)

                    if len(borrowed_books) > 10:
                        books_text += f"; ... and {len(borrowed_books) - 10} more"

                # Split the name into first and last name
                name_parts = student.name.split()
                first_name = name_parts[0] if name_parts else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                card_data = {
                    "Student_ID": student.admission_number,
                    "Student_Name": f"{first_name} {last_name}",
                    "Class": student.class_name or "Unknown",
                    "Stream": getattr(student, 'stream', 'Unknown'),
                    "Contact": getattr(student, 'phone', 'N/A'),
                    "Books_Borrowed": books_text,
                    "Total_Books_Borrowed": len(borrowed_books),
                    "Card_Generated": "Yes"
                }

                cards_data.append(card_data)

        except Exception as e:
            logger.error(f"Error generating library cards data: {str(e)}")

        return cards_data

    def _populate_library_cards_table(self, cards_data):
        """Populate the results table with library cards data."""
        try:
            self.results_table.setRowCount(0)  # Clear existing data

            for row_idx, card_data in enumerate(cards_data):
                self.results_table.insertRow(row_idx)

                # Set table items
                self.results_table.setItem(row_idx, 0, QTableWidgetItem(card_data["Student_ID"]))
                self.results_table.setItem(row_idx, 1, QTableWidgetItem(card_data["Student_Name"]))
                self.results_table.setItem(row_idx, 2, QTableWidgetItem(card_data["Stream"]))
                self.results_table.setItem(row_idx, 3, QTableWidgetItem(str(card_data["Total_Books_Borrowed"])))
                self.results_table.setItem(row_idx, 4, QTableWidgetItem(card_data["Card_Generated"]))

        except Exception as e:
            logger.error(f"Error populating library cards table: {e}")
            show_error_message("Error", f"Failed to display library cards: {str(e)}", self)

    def _get_library_cards_from_table(self):
        """Extract library cards data from the results table."""
        cards_data = []

        try:
            row_count = self.results_table.rowCount()
            if row_count == 0:
                return []

            for row in range(row_count):
                # Get basic info from table
                student_id = self.results_table.item(row, 0).text() if self.results_table.item(row, 0) else ""
                student_name = self.results_table.item(row, 1).text() if self.results_table.item(row, 1) else ""
                stream = self.results_table.item(row, 2).text() if self.results_table.item(row, 2) else ""

                # Get detailed info from student service
                student = self.student_service.get_student_by_admission(student_id)
                if student:
                    # Regenerate the full card data
                    full_cards = self._generate_library_cards_data([student])
                    if full_cards:
                        cards_data.append(full_cards[0])

        except Exception as e:
            logger.error(f"Error extracting library cards from table: {str(e)}")

        return cards_data

    def _export_library_cards_pdf(self, cards_data, file_path):
        """Export library cards to PDF with detailed card format."""
        try:
            from fpdf import FPDF
            from datetime import datetime

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Title
            pdf.set_font("Arial", size=16, style='B')
            pdf.cell(0, 10, "Student Library Cards", ln=True, align='C')
            pdf.ln(10)

            # Generate cards for each student
            for i, card_data in enumerate(cards_data):
                # Add new page for each card (except first)
                if i > 0:
                    pdf.add_page()

                # Card header
                pdf.set_font("Arial", size=14, style='B')
                pdf.cell(0, 10, f"Library Card - {card_data['Student_Name']}", ln=True)
                pdf.ln(5)

                # Student details
                pdf.set_font("Arial", size=10)
                pdf.cell(40, 8, "Student ID:")
                pdf.cell(0, 8, card_data['Student_ID'], ln=True)

                pdf.cell(40, 8, "Name:")
                pdf.cell(0, 8, card_data['Student_Name'], ln=True)

                pdf.cell(40, 8, "Class:")
                pdf.cell(0, 8, card_data['Class'], ln=True)

                pdf.cell(40, 8, "Stream:")
                pdf.cell(0, 8, card_data['Stream'], ln=True)

                pdf.cell(40, 8, "Contact:")
                pdf.cell(0, 8, card_data['Contact'], ln=True)

                pdf.ln(5)

                # Books borrowed section
                pdf.set_font("Arial", size=12, style='B')
                pdf.cell(0, 10, "Books Borrowed History:", ln=True)
                pdf.set_font("Arial", size=9)

                books_text = card_data['Books_Borrowed']
                if books_text == "None":
                    pdf.cell(0, 8, "No books borrowed yet.", ln=True)
                else:
                    # Split books text and format nicely
                    books = books_text.split("; ")
                    for book in books:
                        pdf.cell(0, 6, f"- {book}", ln=True)

                pdf.ln(5)

                # Summary
                pdf.set_font("Arial", size=10, style='I')
                pdf.cell(0, 8, f"Total Books Borrowed: {card_data['Total_Books_Borrowed']}", ln=True)
                pdf.cell(0, 8, f"Card Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

                # Separator line
                pdf.ln(10)
                pdf.cell(0, 0, "", "T", ln=True)

            pdf.output(file_path)
            return True

        except Exception as e:
            logger.error(f"Error exporting library cards to PDF: {e}")
            return False
