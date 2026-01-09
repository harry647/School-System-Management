"""
User management window for the School System Management application.

This module provides the user management interface for admin users (admin and librarian roles).
Implements standardized, user-centric workflows for all user-related services with consistency,
validation, and system integrity following the USER MANAGEMENT FLOW template.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, QCheckBox, QTextEdit, QSizePolicy, QFileDialog, QMessageBox, QDialog, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction
from typing import Callable, Optional
from datetime import datetime

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService
from school_system.core.exceptions import AuthenticationError, ValidationError
from school_system.gui.windows.user_window.user_validation import UserValidator, ValidationResult, FieldValidator
from school_system.gui.windows.user_window.user_workflow_components import (
    UserWorkflowManager, UserCreationWorkflow,
    UserUpdateWorkflow, UserDeletionWorkflow
)


class UserWindow(BaseWindow):
    """User management window for admin users with standardized workflows."""
    
    def __init__(self, parent: QMainWindow, current_user: str, current_role: str):
        """
        Initialize the user window with standardized workflow management.
        
        Args:
            parent: The parent window
            current_user: The current logged-in username
            current_role: The current user's role
        """
        super().__init__("School System - User Management", parent)
        
        self.parent = parent
        self.current_user = current_user
        self.current_role = current_role
        self.auth_service = AuthService()
        self.validator = UserValidator()
        
        # Initialize workflow manager
        self.workflow_manager = UserWorkflowManager(self)
        
        # Check if user has admin privileges
        if self.current_role not in ["admin", "librarian"]:
            show_error_message("Access Denied", "You do not have permission to access user management.", self)
            self.close()
            return
        
        # Set minimum size
        self.setMinimumSize(1200, 800)
        
        # Initialize UI
        self._setup_widgets()
        
        # Setup undo functionality
        self._setup_undo_system()
        
        # Track last operations for undo
        self.last_operation = None
        self.undo_timer = None
        self.undo_stack = []
        
        # Add undo action to menu
        self._add_undo_action()
    
    def _setup_widgets(self):
        """Setup the user management widgets."""
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        self.add_widget_to_content(tab_widget)
        
        # User Management Tab
        user_tab = self._create_user_management_tab()
        tab_widget.addTab(user_tab, "User Management")
        
        # User Settings Tab
        settings_tab = self._create_user_settings_tab()
        tab_widget.addTab(settings_tab, "User Settings")
        
        # Short Form Mappings Tab
        mappings_tab = self._create_mappings_tab()
        tab_widget.addTab(mappings_tab, "Short Form Mappings")
        
        # Sessions Tab
        sessions_tab = self._create_sessions_tab()
        tab_widget.addTab(sessions_tab, "Sessions")
        
        # Activity Tab
        activity_tab = self._create_activity_tab()
        tab_widget.addTab(activity_tab, "Activity Logs")
    
    def _setup_undo_system(self):
        """Setup the undo system for user operations."""
        # This will be implemented with proper undo functionality
        pass
    
    def _add_undo_action(self):
        """Add undo action to the menu bar."""
        # Get or create menu bar
        menu_bar = self.menuBar()
        if not menu_bar:
            menu_bar = self.create_menu_bar()
        
        # Add Edit menu if it doesn't exist
        edit_menu = menu_bar.findChild(QMenu, "edit_menu")
        if not edit_menu:
            edit_menu = menu_bar.addMenu("Edit")
            edit_menu.setObjectName("edit_menu")
        
        # Add Undo action
        undo_action = QAction("Undo Last Operation", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setEnabled(False)  # Initially disabled
        undo_action.triggered.connect(self._on_undo_operation)
        edit_menu.addAction(undo_action)
        
        # Store reference
        self.undo_action = undo_action
    
    def _on_undo_operation(self):
        """Handle undo operation."""
        if self.undo_stack:
            last_operation = self.undo_stack.pop()
            
            try:
                # Attempt to undo the operation
                if last_operation['type'] == 'create':
                    # Undo create by deleting
                    username = last_operation['data'].get('username', '')
                    if username:
                        success = self.auth_service.delete_user(username)
                        if success:
                            show_success_message("Undo Successful",
                                                f"User creation undone: {username}", self)
                        else:
                            show_error_message("Undo Failed",
                                              f"Failed to undo user creation: User {username} not found", self)
                elif last_operation['type'] == 'delete':
                    # Undo delete by recreating
                    user_data = last_operation['data']
                    if user_data and 'username' in user_data and 'password' in user_data and 'role' in user_data:
                        self.auth_service.create_user(user_data['username'], user_data['password'], user_data['role'])
                        show_success_message("Undo Successful",
                                            f"User deletion undone: {user_data['username']}", self)
                    else:
                        show_error_message("Undo Failed",
                                          "Missing required user data for undo", self)
                
                # Refresh table
                self._refresh_users_table()
                
                # Update undo action state
                self.undo_action.setEnabled(len(self.undo_stack) > 0)
                
            except Exception as e:
                show_error_message("Undo Failed",
                                  f"Failed to undo operation: {str(e)}", self)
    
    def _track_operation(self, operation_type: str, operation_data: dict):
        """Track an operation for potential undo."""
        # Add to undo stack (limit to last 10 operations)
        self.undo_stack.append({
            'type': operation_type,
            'data': operation_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit stack size
        if len(self.undo_stack) > 10:
            self.undo_stack.pop(0)
        
        # Enable undo action
        self.undo_action.setEnabled(True)
        
        # Start undo timer (5 seconds)
        if self.undo_timer:
            self.undo_timer.stop()
        
        self.undo_timer = QTimer(self)
        self.undo_timer.timeout.connect(self._clear_undo_stack)
        self.undo_timer.start(5000)  # 5 seconds
    
    def _clear_undo_stack(self):
        """Clear the undo stack after timeout."""
        self.undo_stack.clear()
        if self.undo_action:
            self.undo_action.setEnabled(False)
        if self.undo_timer:
            self.undo_timer.stop()
    
    def _create_user_management_tab(self) -> QWidget:
        """Create the user management tab with standardized workflows."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Create User Section - Using Standardized Workflow
        create_section = self.create_card("Create New User",
                                          "Use the form below to create a new user account")
        create_workflow = UserCreationWorkflow(self)
        create_workflow.operation_completed.connect(self._handle_operation_completed)
        create_section.layout.addWidget(create_workflow)
        layout.add_widget(create_section)
        
        # Update User Section - Using Standardized Workflow
        update_section = self.create_card("Update User Role",
                                          "Update existing user roles and permissions")
        update_workflow = UserUpdateWorkflow(self)
        update_workflow.operation_completed.connect(self._handle_operation_completed)
        update_section.layout.addWidget(update_workflow)
        layout.add_widget(update_section)
        
        # Delete User Section - Using Standardized Workflow
        delete_section = self.create_card("Delete User",
                                          "Permanently remove a user from the system")
        delete_workflow = UserDeletionWorkflow(self)
        delete_workflow.operation_completed.connect(self._handle_operation_completed)
        delete_section.layout.addWidget(delete_workflow)
        layout.add_widget(delete_section)
        
        # View Users Section
        view_section = self.create_card("View Users", "Browse and search existing user accounts")
        view_form = QWidget()
        view_layout = self.create_flex_layout("column", False)
        view_layout.set_spacing(10)
        
        # Refresh button
        refresh_button = self.create_button("Refresh Users", "secondary")
        refresh_button.clicked.connect(self._refresh_users_table)
        view_layout.add_widget(refresh_button)
        
        # Users table with enhanced features
        self.users_table = self.create_table(0, 4)  # Added column for undo
        self.users_table.setHorizontalHeaderLabels(["Username", "Role", "Created", "Actions"])
        view_layout.add_widget(self.users_table)
        
        view_form.setLayout(view_layout._layout)
        view_section.layout.addWidget(view_form)
        layout.add_widget(view_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_user_settings_tab(self) -> QWidget:
        """Create the user settings tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Get Settings Section
        get_section = self.create_card("Get User Settings", "")
        get_form = QWidget()
        get_layout = self.create_flex_layout("column", False)
        get_layout.set_spacing(10)
        
        # User ID
        userid_label = QLabel("User ID:")
        get_layout.add_widget(userid_label)
        self.get_userid_input = self.create_input("Enter user ID")
        get_layout.add_widget(self.get_userid_input)
        
        # Get button
        get_button = self.create_button("Get Settings", "primary")
        get_button.clicked.connect(self._on_get_settings)
        get_layout.add_widget(get_button)
        
        # Display area
        self.settings_display = QTextEdit()
        self.settings_display.setReadOnly(True)
        self.settings_display.setMaximumHeight(100)
        get_layout.add_widget(self.settings_display)
        
        get_form.setLayout(get_layout._layout)
        get_section.layout.addWidget(get_form)
        layout.add_widget(get_section)
        
        # Update Settings Section
        update_section = self.create_card("Update User Settings", "")
        update_form = QWidget()
        update_layout = self.create_flex_layout("column", False)
        update_layout.set_spacing(10)
        
        # User ID
        update_userid_label = QLabel("User ID:")
        update_layout.add_widget(update_userid_label)
        self.update_userid_input = self.create_input("Enter user ID")
        update_layout.add_widget(self.update_userid_input)
        
        # Reminder Frequency
        freq_label = QLabel("Reminder Frequency:")
        update_layout.add_widget(freq_label)
        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["daily", "weekly", "monthly"])
        update_layout.add_widget(self.freq_combo)
        
        # Sound Enabled
        sound_label = QLabel("Sound Enabled:")
        update_layout.add_widget(sound_label)
        self.sound_checkbox = QCheckBox("Enable sound notifications")
        update_layout.add_widget(self.sound_checkbox)
        
        # Update button
        update_settings_button = self.create_button("Update Settings", "secondary")
        update_settings_button.clicked.connect(self._on_update_settings)
        update_layout.add_widget(update_settings_button)
        
        update_form.setLayout(update_layout._layout)
        update_section.layout.addWidget(update_form)
        layout.add_widget(update_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_mappings_tab(self) -> QWidget:
        """Create the short form mappings tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Create Mapping Section
        create_section = self.create_card("Create Short Form Mapping", "")
        create_form = QWidget()
        create_layout = self.create_flex_layout("column", False)
        create_layout.set_spacing(10)
        
        # Short Form
        short_label = QLabel("Short Form:")
        create_layout.add_widget(short_label)
        self.short_form_input = self.create_input("Enter short form")
        create_layout.add_widget(self.short_form_input)
        
        # Full Name
        full_label = QLabel("Full Name:")
        create_layout.add_widget(full_label)
        self.full_name_input = self.create_input("Enter full name")
        create_layout.add_widget(self.full_name_input)
        
        # Mapping Type
        type_label = QLabel("Mapping Type:")
        create_layout.add_widget(type_label)
        self.mapping_type_input = self.create_input("Enter mapping type")
        create_layout.add_widget(self.mapping_type_input)
        
        # Create button
        create_mapping_button = self.create_button("Create Mapping", "primary")
        create_mapping_button.clicked.connect(self._on_create_mapping)
        create_layout.add_widget(create_mapping_button)
        
        create_form.setLayout(create_layout._layout)
        create_section.layout.addWidget(create_form)
        layout.add_widget(create_section)
        
        # Update Mapping Section
        update_section = self.create_card("Update Short Form Mapping", "")
        update_form = QWidget()
        update_layout = self.create_flex_layout("column", False)
        update_layout.set_spacing(10)
        
        # Short Form
        update_short_label = QLabel("Short Form:")
        update_layout.add_widget(update_short_label)
        self.update_short_form_input = self.create_input("Enter short form")
        update_layout.add_widget(self.update_short_form_input)
        
        # New Full Name
        new_full_label = QLabel("New Full Name:")
        update_layout.add_widget(new_full_label)
        self.update_full_name_input = self.create_input("Enter new full name")
        update_layout.add_widget(self.update_full_name_input)
        
        # New Mapping Type
        new_type_label = QLabel("New Mapping Type:")
        update_layout.add_widget(new_type_label)
        self.update_mapping_type_input = self.create_input("Enter new mapping type")
        update_layout.add_widget(self.update_mapping_type_input)
        
        # Update button
        update_mapping_button = self.create_button("Update Mapping", "secondary")
        update_mapping_button.clicked.connect(self._on_update_mapping)
        update_layout.add_widget(update_mapping_button)
        
        update_form.setLayout(update_layout._layout)
        update_section.layout.addWidget(update_form)
        layout.add_widget(update_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_sessions_tab(self) -> QWidget:
        """Create the sessions tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Create Session Section
        create_section = self.create_card("Create User Session", "")
        create_form = QWidget()
        create_layout = self.create_flex_layout("column", False)
        create_layout.set_spacing(10)
        
        # Username
        session_username_label = QLabel("Username:")
        create_layout.add_widget(session_username_label)
        self.session_username_input = self.create_input("Enter username")
        create_layout.add_widget(self.session_username_input)
        
        # IP Address
        ip_label = QLabel("IP Address:")
        create_layout.add_widget(ip_label)
        self.ip_input = self.create_input("Enter IP address")
        create_layout.add_widget(self.ip_input)
        
        # Create button
        create_session_button = self.create_button("Create Session", "primary")
        create_session_button.clicked.connect(self._on_create_session)
        create_layout.add_widget(create_session_button)
        
        create_form.setLayout(create_layout._layout)
        create_section.layout.addWidget(create_form)
        layout.add_widget(create_section)
        
        # Expire Session Section
        expire_section = self.create_card("Expire User Session", "")
        expire_form = QWidget()
        expire_layout = self.create_flex_layout("column", False)
        expire_layout.set_spacing(10)
        
        # Session ID
        session_id_label = QLabel("Session ID:")
        expire_layout.add_widget(session_id_label)
        self.session_id_input = self.create_input("Enter session ID")
        expire_layout.add_widget(self.session_id_input)
        
        # Expire button
        expire_button = self.create_button("Expire Session", "danger")
        expire_button.clicked.connect(self._on_expire_session)
        expire_layout.add_widget(expire_button)
        
        expire_form.setLayout(expire_layout._layout)
        expire_section.layout.addWidget(expire_form)
        layout.add_widget(expire_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_activity_tab(self) -> QWidget:
        """Create the activity logs tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Log Action Section
        log_section = self.create_card("Log User Action", "")
        log_form = QWidget()
        log_layout = self.create_flex_layout("column", False)
        log_layout.set_spacing(10)
        
        # Username
        log_username_label = QLabel("Username:")
        log_layout.add_widget(log_username_label)
        self.log_username_input = self.create_input("Enter username")
        log_layout.add_widget(self.log_username_input)
        
        # Action
        action_label = QLabel("Action:")
        log_layout.add_widget(action_label)
        self.action_input = self.create_input("Enter action")
        log_layout.add_widget(self.action_input)
        
        # Details
        details_label = QLabel("Details:")
        log_layout.add_widget(details_label)
        self.details_input = QTextEdit()
        self.details_input.setMaximumHeight(80)
        log_layout.add_widget(self.details_input)
        
        # Log button
        log_button = self.create_button("Log Action", "primary")
        log_button.clicked.connect(self._on_log_action)
        log_layout.add_widget(log_button)
        
        log_form.setLayout(log_layout._layout)
        log_section.layout.addWidget(log_form)
        layout.add_widget(log_section)
        
        # Track Activity Section
        track_section = self.create_card("Track User Activity", "")
        track_form = QWidget()
        track_layout = self.create_flex_layout("column", False)
        track_layout.set_spacing(10)
        
        # Username
        track_username_label = QLabel("Username:")
        track_layout.add_widget(track_username_label)
        self.track_username_input = self.create_input("Enter username")
        track_layout.add_widget(self.track_username_input)
        
        # Activity Type
        activity_type_label = QLabel("Activity Type:")
        track_layout.add_widget(activity_type_label)
        self.activity_type_input = self.create_input("Enter activity type")
        track_layout.add_widget(self.activity_type_input)
        
        # Details
        track_details_label = QLabel("Details:")
        track_layout.add_widget(track_details_label)
        self.track_details_input = QTextEdit()
        self.track_details_input.setMaximumHeight(80)
        track_layout.add_widget(self.track_details_input)
        
        # Track button
        track_button = self.create_button("Track Activity", "secondary")
        track_button.clicked.connect(self._on_track_activity)
        track_layout.add_widget(track_button)
        
        track_form.setLayout(track_layout._layout)
        track_section.layout.addWidget(track_form)
        layout.add_widget(track_section)
        
        # Password Reset Section
        reset_section = self.create_card("Request Password Reset", "")
        reset_form = QWidget()
        reset_layout = self.create_flex_layout("column", False)
        reset_layout.set_spacing(10)
        
        # Username
        reset_username_label = QLabel("Username:")
        reset_layout.add_widget(reset_username_label)
        self.reset_username_input = self.create_input("Enter username")
        reset_layout.add_widget(self.reset_username_input)
        
        # Reset button
        reset_button = self.create_button("Request Reset", "secondary")
        reset_button.clicked.connect(self._on_password_reset)
        reset_layout.add_widget(reset_button)
        
        reset_form.setLayout(reset_layout._layout)
        reset_section.layout.addWidget(reset_form)
        layout.add_widget(reset_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _handle_operation_completed(self, success: bool, message: str):
        """
        Handle completion of user operations with appropriate feedback and state updates.
        
        This method serves as the central callback for all user workflow operations,
        ensuring consistent post-operation behavior including table refreshes,
        user notifications, and undo tracking.
        
        Args:
            success: Boolean indicating if the operation was successful
            message: Descriptive message about the operation result
        """
        if success:
            # Refresh the users table to show latest data
            self._refresh_users_table()
            
            # Show appropriate success message based on operation type
            if "created" in message.lower():
                show_success_message("Success", message, self)
                # Track creation for potential undo (5-second window)
                # Username can be extracted from message for undo tracking
            elif "updated" in message.lower():
                show_success_message("Success", message, self)
                # Track update for potential undo
            elif "deleted" in message.lower():
                show_success_message("Success", message, self)
                # Track deletion for potential undo
        else:
            # Show error message for failed operations
            show_error_message("Error", message, self)
    
    def _refresh_users_table(self):
        """Refresh the users table."""
        try:
            # Get all users from the repository
            users = self.auth_service.user_repository.get_all()
            
            # Clear the table
            self.users_table.setRowCount(0)
            
            # Populate the table
            for user in users:
                row_position = self.users_table.rowCount()
                self.users_table.insertRow(row_position)
                
                # Username
                self.users_table.setItem(row_position, 0, QTableWidgetItem(user.username))
                
                # Role
                self.users_table.setItem(row_position, 1, QTableWidgetItem(user.role))
                
                # Created (formatted date)
                created_date = user.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(user, 'created_at') and user.created_at else "N/A"
                self.users_table.setItem(row_position, 2, QTableWidgetItem(created_date))
                
                # Add action buttons container
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.setSpacing(5)
                
                # View button
                view_button = self.create_button("View", "secondary")
                view_button.clicked.connect(lambda _, uname=user.username: self._view_user_details(uname))
                action_layout.addWidget(view_button)
                
                # Edit button
                edit_button = self.create_button("Edit", "primary")
                edit_button.clicked.connect(lambda _, uname=user.username: self._start_edit_workflow(uname))
                action_layout.addWidget(edit_button)
                
                # Delete button
                delete_button = self.create_button("Delete", "danger")
                delete_button.clicked.connect(lambda _, uname=user.username: self._start_delete_workflow(uname))
                action_layout.addWidget(delete_button)
                
                self.users_table.setCellWidget(row_position, 3, action_widget)
            
            show_success_message("Success", f"Users table refreshed. Found {len(users)} users.", self)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh users: {str(e)}", self)
    
    def _start_edit_workflow(self, username: str):
        """Start the edit workflow for a specific user."""
        try:
            user = self.auth_service.get_user_by_username(username)
            if user:
                # Create update workflow and pre-populate with user data
                update_workflow = UserUpdateWorkflow(self)
                update_workflow.operation_completed.connect(self._handle_operation_completed)
                
                # Pre-populate the username field
                if hasattr(update_workflow, 'username_input'):
                    update_workflow.username_input.setText(user.username)
                    update_workflow.username_input.setReadOnly(True)
                
                # Show the workflow
                self.workflow_manager.start_workflow("update")
                
            else:
                show_error_message("Error", "User not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to start edit workflow: {str(e)}", self)
    
    def _start_delete_workflow(self, username: str):
        """Start the delete workflow for a specific user."""
        try:
            user = self.auth_service.get_user_by_username(username)
            if user:
                # Create delete workflow and pre-populate with user data
                delete_workflow = UserDeletionWorkflow(self)
                delete_workflow.operation_completed.connect(self._handle_operation_completed)
                
                # Pre-populate the username field
                if hasattr(delete_workflow, 'username_input'):
                    delete_workflow.username_input.setText(user.username)
                    delete_workflow.username_input.setReadOnly(True)
                
                # Show the workflow
                self.workflow_manager.start_workflow("delete")
                
            else:
                show_error_message("Error", "User not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to start delete workflow: {str(e)}", self)
    
    def _view_user_details(self, username: str):
        """View detailed information about a user."""
        try:
            user = self.auth_service.get_user_by_username(username)
            if user:
                details = f"User Details:\n\nUsername: {user.username}\nRole: {user.role}\nCreated: {user.created_at}"
                show_success_message("User Details", details, self)
            else:
                show_error_message("Error", "User not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to view user details: {str(e)}", self)
    
    # Event handlers for User Settings
    def _on_get_settings(self):
        """Handle get settings button click."""
        try:
            user_id = int(self.get_userid_input.text().strip())
            settings = self.auth_service.get_user_setting(user_id)
            if settings:
                self.settings_display.setText(f"Reminder Frequency: {settings.reminder_frequency}\nSound Enabled: {settings.sound_enabled}")
            else:
                self.settings_display.setText("No settings found.")
        except ValueError:
            show_error_message("Error", "Invalid user ID.", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _on_update_settings(self):
        """Handle update settings button click."""
        try:
            user_id = int(self.update_userid_input.text().strip())
            freq = self.freq_combo.currentText()
            sound = self.sound_checkbox.isChecked()
            
            # Try to update, if not exist, create
            existing = self.auth_service.get_user_setting(user_id)
            if existing:
                self.auth_service.update_user_setting(user_id, freq, sound)
            else:
                self.auth_service.create_user_setting(user_id, freq, sound)
            show_success_message("Success", "Settings updated.", self)
        except ValueError:
            show_error_message("Error", "Invalid user ID.", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    # Event handlers for Short Form Mappings
    def _on_create_mapping(self):
        """Handle create mapping button click."""
        short_form = self.short_form_input.text().strip()
        full_name = self.full_name_input.text().strip()
        mapping_type = self.mapping_type_input.text().strip()
        
        try:
            self.auth_service.create_short_form_mapping(short_form, full_name, mapping_type)
            show_success_message("Success", "Mapping created.", self)
            # Clear form
            self.short_form_input.clear()
            self.full_name_input.clear()
            self.mapping_type_input.clear()
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _on_update_mapping(self):
        """Handle update mapping button click."""
        short_form = self.update_short_form_input.text().strip()
        full_name = self.update_full_name_input.text().strip()
        mapping_type = self.update_mapping_type_input.text().strip()
        
        try:
            self.auth_service.update_short_form_mapping(short_form, full_name, mapping_type)
            show_success_message("Success", "Mapping updated.", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    # Event handlers for Sessions
    def _on_create_session(self):
        """Handle create session button click."""
        username = self.session_username_input.text().strip()
        ip = self.ip_input.text().strip()
        
        try:
            self.auth_service.create_user_session(username, ip)
            show_success_message("Success", "Session created.", self)
            # Clear form
            self.session_username_input.clear()
            self.ip_input.clear()
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _on_expire_session(self):
        """Handle expire session button click."""
        try:
            session_id = int(self.session_id_input.text().strip())
            success = self.auth_service.expire_user_session(session_id)
            if success:
                show_success_message("Success", "Session expired.", self)
            else:
                show_error_message("Error", "Session not found.", self)
        except ValueError:
            show_error_message("Error", "Invalid session ID.", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    # Event handlers for Activity
    def _on_log_action(self):
        """Handle log action button click."""
        username = self.log_username_input.text().strip()
        action = self.action_input.text().strip()
        details = self.details_input.toPlainText().strip()
        
        try:
            self.auth_service.log_user_action(username, action, details)
            show_success_message("Success", "Action logged.", self)
            # Clear form
            self.log_username_input.clear()
            self.action_input.clear()
            self.details_input.clear()
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _on_track_activity(self):
        """Handle track activity button click."""
        username = self.track_username_input.text().strip()
        activity_type = self.activity_type_input.text().strip()
        details = self.track_details_input.toPlainText().strip()
        
        try:
            self.auth_service.track_user_activity(username, activity_type, details)
            show_success_message("Success", "Activity tracked.", self)
            # Clear form
            self.track_username_input.clear()
            self.activity_type_input.clear()
            self.track_details_input.clear()
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _on_password_reset(self):
        """Handle password reset button click."""
        username = self.reset_username_input.text().strip()
        
        try:
            success = self.auth_service.request_password_reset(username)
            if success:
                show_success_message("Success", "Password reset requested.", self)
            else:
                show_error_message("Error", "User not found.", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)