"""
Class and Stream Selection Dialog

A dialog for selecting class and stream combinations for student operations.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Optional, List

from school_system.config.logging import logger
from school_system.services.class_management_service import ClassManagementService


class ClassStreamSelectionDialog(QDialog):
    """Dialog for selecting class and stream combinations."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        super().__init__(parent)
        self.current_user = current_user
        self.current_role = current_role

        self.class_management_service = ClassManagementService()
        self.selected_class = None
        self.selected_stream = None

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Select Class and Stream")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title_label = QLabel("Select Class and Stream")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title_label)

        # Class selection
        class_frame = QFrame()
        class_layout = QVBoxLayout(class_frame)
        class_layout.setContentsMargins(0, 0, 0, 0)

        class_label = QLabel("Class:")
        class_label.setStyleSheet("font-weight: bold;")
        class_layout.addWidget(class_label)

        self.class_combo = QComboBox()
        self.class_combo.setMinimumHeight(32)
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        class_layout.addWidget(self.class_combo)

        layout.addWidget(class_frame)

        # Stream selection
        stream_frame = QFrame()
        stream_layout = QVBoxLayout(stream_frame)
        stream_layout.setContentsMargins(0, 0, 0, 0)

        stream_label = QLabel("Stream:")
        stream_label.setStyleSheet("font-weight: bold;")
        stream_layout.addWidget(stream_label)

        self.stream_combo = QComboBox()
        self.stream_combo.setMinimumHeight(32)
        self.stream_combo.setEnabled(False)  # Disabled until class is selected
        stream_layout.addWidget(self.stream_combo)

        layout.addWidget(stream_frame)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._on_ok_clicked)
        self.ok_btn.setDefault(True)
        buttons_layout.addWidget(self.ok_btn)

        layout.addLayout(buttons_layout)

    def load_data(self):
        """Load available classes."""
        try:
            classes = self.class_management_service.get_all_classes()
            if classes:
                self.class_combo.addItem("-- Select Class --")
                self.class_combo.addItems(classes)
            else:
                QMessageBox.warning(self, "No Classes", "No classes found in the system.")
                self.reject()
        except Exception as e:
            logger.error(f"Error loading classes: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load classes: {e}")
            self.reject()

    def _on_class_changed(self, class_name: str):
        """Handle class selection change."""
        if class_name and class_name != "-- Select Class --":
            try:
                # Load streams for the selected class
                streams = self.class_management_service.get_streams_for_class(class_name)
                self.stream_combo.clear()
                if streams:
                    self.stream_combo.addItem("-- Select Stream --")
                    self.stream_combo.addItems(streams)
                    self.stream_combo.setEnabled(True)
                else:
                    self.stream_combo.addItem("No streams available")
                    self.stream_combo.setEnabled(False)
            except Exception as e:
                logger.error(f"Error loading streams for class {class_name}: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load streams: {e}")
        else:
            # No class selected
            self.stream_combo.clear()
            self.stream_combo.setEnabled(False)

    def _on_ok_clicked(self):
        """Handle OK button click."""
        selected_class = self.class_combo.currentText()
        selected_stream = self.stream_combo.currentText()

        if selected_class == "-- Select Class --" or not selected_class:
            QMessageBox.warning(self, "Selection Required", "Please select a class.")
            return

        if not self.stream_combo.isEnabled() or selected_stream == "-- Select Stream --" or not selected_stream:
            QMessageBox.warning(self, "Selection Required", "Please select a stream.")
            return

        self.selected_class = selected_class
        self.selected_stream = selected_stream
        self.accept()

    def get_class_level(self) -> Optional[str]:
        """Get the selected class name."""
        return self.selected_class

    def get_stream(self) -> Optional[str]:
        """Get the selected stream name."""
        return self.selected_stream