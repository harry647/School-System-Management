"""
Short Form Mappings Window

Dedicated window for managing short form mappings (create and update).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGroupBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService


class ShortFormMappingsWindow(BaseFunctionWindow):
    """Dedicated window for managing short form mappings."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the short form mappings window."""
        super().__init__("Short Form Mappings Management", parent, current_user, current_role)

        self.auth_service = AuthService()

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the short form mappings management interface."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # Create Mapping Section
        create_section = self._create_mapping_section()
        main_layout.add_widget(create_section)

        # Update Mapping Section
        update_section = self._update_mapping_section()
        main_layout.add_widget(update_section)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_mapping_section(self) -> QWidget:
        """Create the create short form mapping section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        # Create section container
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(16)

        # Section styling
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Title
        title = QLabel("Create Short Form Mapping")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Create a new short form mapping for quick access to commonly used terms.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Short Form input
        short_label = QLabel("Short Form:")
        short_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(short_label)

        self.short_form_input = self.create_input("Enter short form")
        self.short_form_input.setPlaceholderText("e.g., 'CS' for Computer Science")
        form_layout.addWidget(self.short_form_input)

        # Full Name input
        full_label = QLabel("Full Name:")
        full_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(full_label)

        self.full_name_input = self.create_input("Enter full name")
        self.full_name_input.setPlaceholderText("e.g., 'Computer Science Department'")
        form_layout.addWidget(self.full_name_input)

        # Mapping Type input
        type_label = QLabel("Mapping Type:")
        type_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(type_label)

        self.mapping_type_input = self.create_input("Enter mapping type")
        self.mapping_type_input.setPlaceholderText("e.g., 'department', 'course', 'building'")
        form_layout.addWidget(self.mapping_type_input)

        # Create button
        create_button = self.create_button("Create Mapping", "primary")
        create_button.clicked.connect(self._on_create_mapping)
        form_layout.addWidget(create_button)

        section_layout.addWidget(form_container)
        return section

    def _update_mapping_section(self) -> QWidget:
        """Create the update short form mapping section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        # Create section container
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(16)

        # Section styling
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Title
        title = QLabel("Update Short Form Mapping")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Update an existing short form mapping with new information.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Short Form input (for lookup)
        update_short_label = QLabel("Short Form to Update:")
        update_short_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(update_short_label)

        self.update_short_form_input = self.create_input("Enter existing short form")
        self.update_short_form_input.setPlaceholderText("Enter the short form you want to update")
        form_layout.addWidget(self.update_short_form_input)

        # New Full Name input
        new_full_label = QLabel("New Full Name:")
        new_full_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(new_full_label)

        self.update_full_name_input = self.create_input("Enter new full name")
        self.update_full_name_input.setPlaceholderText("Enter the updated full name")
        form_layout.addWidget(self.update_full_name_input)

        # New Mapping Type input
        new_type_label = QLabel("New Mapping Type:")
        new_type_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(new_type_label)

        self.update_mapping_type_input = self.create_input("Enter new mapping type")
        self.update_mapping_type_input.setPlaceholderText("Enter the updated mapping type")
        form_layout.addWidget(self.update_mapping_type_input)

        # Update button
        update_button = self.create_button("Update Mapping", "secondary")
        update_button.clicked.connect(self._on_update_mapping)
        form_layout.addWidget(update_button)

        section_layout.addWidget(form_container)
        return section

    def _on_create_mapping(self):
        """Handle create mapping button click."""
        try:
            short_form = self.short_form_input.text().strip()
            full_name = self.full_name_input.text().strip()
            mapping_type = self.mapping_type_input.text().strip()

            # Validation
            if not short_form:
                show_error_message("Error", "Short form is required.", self)
                return
            if not full_name:
                show_error_message("Error", "Full name is required.", self)
                return
            if not mapping_type:
                show_error_message("Error", "Mapping type is required.", self)
                return

            # Create mapping
            success = self.auth_service.create_short_form_mapping(short_form, full_name, mapping_type)
            if success:
                show_success_message("Success", f"Short form mapping '{short_form}' created successfully.", self)
                # Clear form
                self.short_form_input.clear()
                self.full_name_input.clear()
                self.mapping_type_input.clear()
            else:
                show_error_message("Error", "Failed to create mapping. It may already exist.", self)

        except Exception as e:
            logger.error(f"Error creating short form mapping: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_update_mapping(self):
        """Handle update mapping button click."""
        try:
            short_form = self.update_short_form_input.text().strip()
            full_name = self.update_full_name_input.text().strip()
            mapping_type = self.update_mapping_type_input.text().strip()

            # Validation
            if not short_form:
                show_error_message("Error", "Short form is required.", self)
                return
            if not full_name:
                show_error_message("Error", "New full name is required.", self)
                return
            if not mapping_type:
                show_error_message("Error", "New mapping type is required.", self)
                return

            # Update mapping
            success = self.auth_service.update_short_form_mapping(short_form, full_name, mapping_type)
            if success:
                show_success_message("Success", f"Short form mapping '{short_form}' updated successfully.", self)
                # Clear form
                self.update_short_form_input.clear()
                self.update_full_name_input.clear()
                self.update_mapping_type_input.clear()
            else:
                show_error_message("Error", "Failed to update mapping. It may not exist.", self)

        except Exception as e:
            logger.error(f"Error updating short form mapping: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)
