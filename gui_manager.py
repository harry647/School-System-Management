import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime, timedelta, date
import pandas as pd
from tkinter import ttk, messagebox, simpledialog, filedialog, Canvas, Scrollbar, scrolledtext
import logging
import winsound
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import LongTable
import csv
import os
import openpyxl
from PIL import Image, ImageTk 

class Tooltip:
    """A class to create tooltips for Tkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert") if self.widget.bbox("insert") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, font=("Arial", 10))
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class GUIManager:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.logger = logging.getLogger('GUIManager')
        try:
            self.logger.info("Initializing GUIManager")
            self.root.configure(bg="#f0f8ff")
            self.root.title("HarLuFran InnoFlux SMS")
            self.root.geometry("1400x700")
            self.style = ttk.Style()
            self._configure_styles()
            self.logger.info("GUIManager initialized successfully")
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to configure GUI: {tcl_err}")
            messagebox.showerror("Initialization Error", "Failed to configure GUI.")
            raise

        self.welcome_font_separator = ('Arial', 18, 'bold')
        self.welcome_font_main = ('Georgia', 28, 'bold italic')
        self.welcome_color_separator = '#333333'  # Dark gray
        self.welcome_color_main = '#2E8B57'    # Sea green
        self.welcome_bg = "#F0FFF0" 

        # Color mapping for frames
        self.color_map = {
            "LibraryFrame.TFrame": "#D1C4E9",  # Light Purple
            "ReportsFrame.TFrame": "#B2EBF2",  # Light Cyan
            "MembershipFrame.TFrame": "#F8BBD0",  # Light Pink
            "FurnitureReportsFrame.TFrame": "#B3E5FC",  # Light Blue
            "OtherFrame.TFrame": "#DCEDC8",  # Light Lime
            "ReamsFrame.TFrame": "#FFF9C4",  # Light Yellow
            "DeleteFrame.TFrame": "#FFCDD2",  # Light Red
            "FurnitureFrame.TFrame": "#C8E6C9"  # Light Green
        }

        self.notebook = None  # To hold the notebook widget
        self.notebook_frames = {}  # To store frames for each notebook
        self.button_frames = {}  # To store frames for buttons within each notebook

    def _configure_styles(self):
        try:
            self.style.configure("TLabel", background="#f0f8ff", foreground='black')
            self.style.configure("LibraryFrame.TFrame", background="#D1C4E9", padding=5)
            self.style.configure("ReportsFrame.TFrame", background="#B2EBF2", padding=5)
            self.style.configure("MembershipFrame.TFrame", background="#F8BBD0", padding=5)
            self.style.configure("FurnitureReportsFrame.TFrame", background="#B3E5FC", padding=5)
            self.style.configure("OtherFrame.TFrame", background="#DCEDC8", padding=5)
            self.style.configure("ReamsFrame.TFrame", background="#FFF9C4", padding=5)
            self.style.configure("DeleteFrame.TFrame", background="#FFCDD2", padding=5)
            self.style.configure("FurnitureFrame.TFrame", background="#C8E6C9", padding=5)
            self.style.configure("Clicked.TButton", background="#4CAF50", foreground="white")
        except tk.TclError as tcl_err:
            messagebox.showerror("Style Error", f"Failed to configure styles: {tcl_err}")

    def create_button_grid(self, parent_frame, buttons):
        """Arranges buttons in a responsive grid within the given frame."""
        self.logger.info(f"Creating button grid for {parent_frame}")
        for i, (text, cmd, tooltip) in enumerate(buttons):
            row = i // 3  # Adjust number of columns as needed
            col = i % 3
            btn = tk.Button(parent_frame, text=f"• {text}", command=lambda c=cmd: self.button_click(c), 
                           bg=parent_frame.cget('bg'), relief="raised", padx=10, pady=5)
            btn.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
            Tooltip(btn, tooltip)
            parent_frame.grid_columnconfigure(col, weight=1)  # Make columns resizable
        for i in range((len(buttons) + 2) // 3):
            parent_frame.grid_rowconfigure(i, weight=1)
        self.logger.info(f"Button grid created with {len(buttons)} buttons")

    def create_button_column(self, parent_frame, buttons):
        """Arranges buttons in a responsive column within the given frame."""
        for i, (text, cmd, tooltip) in enumerate(buttons):
            btn = tk.Button(parent_frame, text=f"• {text}", command=lambda c=cmd: self.button_click(c), 
                           bg=parent_frame.cget('bg'), relief="flat", anchor="w", padx=10, pady=2)
            btn.pack(fill="x", padx=5, pady=2)
            Tooltip(btn, tooltip)

    def create_notebook_tab(self, notebook, tab_name, frame_style, buttons):
        """Creates a tab in the notebook and arranges buttons."""
        self.logger.info(f"Attempting to create tab: {tab_name}")
        try:
            tab_frame = tk.Frame(notebook, bg=self.color_map[frame_style])
            notebook.add(tab_frame, text=tab_name)
            self.logger.info(f"Tab {tab_name} added to notebook")
            self.notebook_frames[tab_name] = tab_frame
            self.button_frames[tab_name] = tk.Frame(tab_frame, bg=self.color_map[frame_style])
            self.button_frames[tab_name].pack(fill="both", expand=True, padx=10, pady=10)
            self.create_button_grid(self.button_frames[tab_name], buttons)
            self.logger.info(f"Tab {tab_name} fully configured with {len(buttons)} buttons")
        except Exception as e:
            self.logger.error(f"Failed to create tab {tab_name}: {e}")

    def create_dashboard(self, frame):
        """Creates a notebook-based dashboard with buttons arranged within each tab."""
        self.logger.info("Creating dashboard")
        frame.grid_rowconfigure(0, weight=1, minsize=100)  # Welcome frame
        frame.grid_rowconfigure(1, weight=0)  # Utility buttons frame
        frame.grid_rowconfigure(2, weight=10)  # Notebook area
        frame.grid_rowconfigure(3, weight=1, minsize=40)  # Logout/Register frame
        frame.grid_columnconfigure(0, weight=1)

        # Welcome Frame with grid layout and appealing background
        welcome_frame = tk.Frame(frame, bg=self.welcome_bg)
        welcome_frame.grid(row=0, column=0, sticky="nsew")
        welcome_frame.grid_columnconfigure(0, weight=1) # Center content

        separator_top_text = "🏫📚═══════════✨═══════════🎓📜═══════════✥═══════════🏫📚═══════════✨"
        welcome_text = "SCHOOL MANAGEMENT SYSTEM - HarLuFran InnoFlux SMS"
        tagline_text = "Empowering Education & Management, Your Hub for Success"
        separator_bottom_text = "🏫📚═══════════📚═══════════🎓📜═══════════✥═══════════🏫📚═══════════✨"

        separator_top_label = tk.Label(welcome_frame, text=separator_top_text, font=self.welcome_font_separator, bg=self.welcome_bg, fg=self.welcome_color_separator)
        separator_top_label.pack(pady=(20, 5))

        welcome_label = tk.Label(welcome_frame, text=welcome_text, font=self.welcome_font_main, bg=self.welcome_bg, fg=self.welcome_color_main)
        welcome_label.pack(pady=5)

        tagline_label = tk.Label(welcome_frame, text=tagline_text, font=('Arial', 14, 'italic'), bg=self.welcome_bg, fg=self.welcome_color_separator)
        tagline_label.pack(pady=2)

        separator_bottom_label = tk.Label(welcome_frame, text=separator_bottom_text, font=self.welcome_font_separator, bg=self.welcome_bg, fg=self.welcome_color_separator)
        separator_bottom_label.pack(pady=(5, 20))

        # Utility Buttons Frame
        utility_frame = tk.Frame(frame, bg="#f0f8ff")
        utility_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

        utility_buttons = [
            ("Settings", self.show_settings, "Customize theme and other settings"),
            ("Refresh", self.refresh_dashboard, "Refresh the dashboard"),
            ("Help", self.show_help, "View help documentation"),
            ("Backup Database", self.app.backup_database, "Export the database to a file"),
            ("Restore Database", self.app.restore_database, "Restore data from a backup file"),
            ("Notifications", self.show_notifications, "View overdue book notifications"),
            ("Reminder Settings", self.reminder_settings_gui, "Customize reminder frequency and sound settings"),
        ]

        num_buttons = len(utility_buttons)
        for i, (text, cmd, tooltip) in enumerate(utility_buttons):
            btn = tk.Button(utility_frame, text=text, command=lambda c=cmd: self.button_click(c),
                            bg="#D3D3D3", relief="flat")
            btn.grid(row=0, column=i, sticky="ew", padx=2, pady=2)
            Tooltip(btn, tooltip)
            utility_frame.grid_columnconfigure(i, weight=1) # Make each column resizable

        # Clock Label (aligned to the right)
        self.clock_label = tk.Label(utility_frame, text="", font=('Arial', 10, "bold"),
                                     bg="#f0f8ff", fg="black")
        self.clock_label.grid(row=0, column=num_buttons, sticky="e", padx=5)
        utility_frame.grid_columnconfigure(num_buttons, weight=0) # Don't make the clock column resizable

        self.update_clock()

        # Main Content Frame (Notebook)
        content_frame = tk.Frame(frame, bg="#f0f8ff")
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Notebook
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill="both", expand=True)
        self.logger.info("Main notebook initialized")

        # Library Services Tab
        library_buttons = [
            ("Borrow Book By Teacher", self.app.borrow_book, "Borrow a book for a teacher using their ID"),
            ("QR Code Scanner Management", self.app.open_qr_scanner, "Borrow a book by scanning a QR code"),
            ("Return Book By Teacher", self.app.return_book, "Return a book borrowed by a teacher"),
            ("Add New Book", self.app.add_new_book, "Add a new book to the library manually"),
            ("Load Books Data From Excel", self.app.load_books_from_excel, "Import books from an Excel file, book_ids and conditions(new or Good)"),
            ("Borrow Books By Student", self.app.borrow_books_by_student, "Borrow multiple books for a student"),
            ("Return Books By Student", self.app.return_book_by_student, "Return books borrowed by a student"),
            ("Generate QR", self.generate_qr_code_gui, "Generate a QR code for a book ID"),
            ("Bulk Borrow", self.bulk_borrow_gui, "Borrow multiple books for users via Excel or selection"),
            ("Bulk Return", self.bulk_return_gui, "Return multiple books for users via Excel or selection"),
            ("Manage Categories", self.manage_categories_gui, "Add tags to existing books"),
            ("Manage Short Form Mappings", self.manage_short_form_mappings_gui, "Define short forms and full names for classes and subjects"),
            ("Add Revision Book", self.add_revision_book, "Add a new revision book"),
            ("Borrow Revision Book", self.borrow_revision_book_gui, "Borrow a revision book for a student"),
            ("Return Revision Book", self.return_revision_book_gui, "Return a revision book"),
        ]
        self.create_notebook_tab(self.notebook, "Library Services", "LibraryFrame.TFrame", library_buttons)

        # Library Reports Tab
        report_buttons = [
            ("View All Books And Print", self.open_view_all_books, "View and optionally print all books in the library"),
            ("Search Unreturned Books", self.app.display_unreturned_books_gui, "Find books that haven’t been returned"),
            ("Display All Books In Inventory", self.app.display_books_gui, "Show all books currently in the library"),
            ("Books by Condition", self.display_books_by_condition_gui, "View books grouped by their condition"),
            ("Export Data", self.export_data_gui, "Export all library data to CSV or JSON files"),
            ("Import Data", self.import_data_gui, "Import library data from CSV or JSON files"),
            ("Search Book Borrow", self.search_book_borrow_gui, "Search for a book’s borrowing details by ID"),
            ("View Revision Books", self.view_revision_books_gui, "View all revision books"),
            ("Students with Revision Books", self.view_students_with_revision_books_gui, "View students who borrowed revision books"),
        ]
        self.create_notebook_tab(self.notebook, "Library Reports", "ReportsFrame.TFrame", report_buttons)

        # Membership Services Tab
        membership_buttons = [
            ("Add Student", self.app.add_student, "Add a new student to the system"),
            ("Add Teacher", self.app.create_add_teacher_window, "Add a new teacher to the system"),
            ("Search Student", self.app.search_student, "Search for students by ID, name, or filters"),
            ("Search Teacher", self.app.search_teacher, "Search for teachers by ID or name"),
            ("Load Students Data From Excel", self.app.load_students_data, "Import student data from an Excel file(Student_ID, Name And Stream)"),
            ("Graduate Students", self.show_graduate_students_window, "Automatically graduate all students to the next form"),
            ("Update Student Info", self.show_update_student_info_window, "Manually update a student's stream, locker, or chair"),
            ("Display Students by Form", self.display_students_by_form_gui, "View all students grouped by form"),
            ("Students Without Books", self.app.show_students_without_borrowed_books, "View students who have not borrowed any books"),
        ]
        self.create_notebook_tab(self.notebook, "Membership Services", "MembershipFrame.TFrame", membership_buttons)

        # Delete Entities Tab
        delete_buttons = [
            ("Delete Student", lambda: self._delete_entity_gui("student", "Student ID"), "Remove a student and their borrowed books/reams"),
            ("Delete Book", lambda: self._delete_entity_gui("book", "Book ID"), "Remove a book and its borrowing records"),
            ("Delete Student Borrow", lambda: self._delete_borrow_gui("borrowed_book_student", "Student ID", "Book ID"), "Remove a specific book borrowed by a student"),
            ("Delete Teacher", lambda: self._delete_entity_gui("teacher", "Teacher ID"), "Remove a teacher and their borrowed books"),
            ("Delete Teacher Borrow", lambda: self._delete_borrow_gui("borrowed_book_teacher", "Teacher ID", "Book ID"), "Remove a specific book borrowed by a teacher"),
            ("Delete Ream Entry", lambda: self._delete_entity_gui("ream_entry", "Ream Entry ID"), "Remove a ream contribution entry"),
        ]
        self.create_notebook_tab(self.notebook, "Delete Entities", "DeleteFrame.TFrame", delete_buttons)

        # Resource Management Tab
        resource_tab = tk.Frame(self.notebook, bg="#DCEDC8")
        self.notebook.add(resource_tab, text="Resource Management")
        resource_notebook = ttk.Notebook(resource_tab)
        resource_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.logger.info("Resource Management tab and sub-notebook initialized")

        # Reams Management Sub-Tab
        reams_buttons = [
            ("Add Ream", self.app.open_add_ream_window, "Add reams for a student"),
            ("Total Reams", self.app.total_reams, "View total reams contributed by students"),
            ("Used Reams", self.app.used_reams, "Deduct used reams from student contributions"),
            ("View All Reams", self.display_all_reams_gui, "View all reams with student details and download as PDF"),
            ("Export Reams (Excel)", self.export_reams_gui, "Export ream entries to an Excel file"),
            ("Import Reams (Excel)", self.import_reams_gui, "Import ream entries from an Excel file"),
        ]
        reams_frame = tk.Frame(resource_notebook, bg="#FFF9C4")
        resource_notebook.add(reams_frame, text="Reams")
        self.create_button_grid(reams_frame, reams_buttons)
        self.logger.info("Reams sub-tab created")

        # Furniture Reports Sub-Tab
        furniture_report_buttons = [
            ("Search Locker", self.app.search_locker_gui, "Search for a locker by ID to view assigned student details"),
            ("Search Chair", self.app.search_chair_gui, "Search for a chair by ID to view assigned student details"),
            ("Display All Furniture", self.app.display_all_furniture_gui, "View total lockers and chairs by form with PDF export"),
            ("Display Furniture Details", self.app.display_furniture_details_gui, "View detailed list of all furniture with PDF export"),
            ("Add Furniture Category", self.app.add_furniture_category_gui, "Add or update a furniture category with counts"),
            ("Display Furniture Categories", self.app.display_furniture_categories_gui, "View all furniture categories with PDF export"),
            
        ]
        furniture_reports_frame = tk.Frame(resource_notebook, bg="#B3E5FC")
        resource_notebook.add(furniture_reports_frame, text="Furniture Reports")
        self.create_button_grid(furniture_reports_frame, furniture_report_buttons)
        self.logger.info("Furniture Reports sub-tab created")

        # Furniture Management Sub-Tab
        furniture_buttons = [
            ("Assign Locker", lambda: self.assign_furniture_gui("LKR"), "Assign lockers to students interactively or in batch"),
            ("Assign Chair", lambda: self.assign_furniture_gui("CHR"), "Assign chairs to students interactively or in batch"),
            ("View Locker Status", self.app.view_locker_status_gui, "View the status of all lockers and export to Excel"),
            ("View Chair Status", self.app.view_chair_status_gui, "View the status of all chairs and export to Excel"),
            ("Report Damaged Locker", self.app.report_damaged_locker_gui, "Mark a locker as damaged or needing repair"),
            ("Report Damaged Chair", self.app.report_damaged_chair_gui, "Mark a chair as damaged or needing repair"),
            ("Generate Furniture IDs", self.app.generate_furniture_ids_gui, "Generate and print IDs for lockers and chairs"),
            ("Load Chairs from Excel", self.load_chairs_gui, "Import chair assignments from an Excel file"),
            ("Load Lockers from Excel", self.load_lockers_gui, "Import locker assignments from an Excel file"),
        ]
        furniture_frame = tk.Frame(resource_notebook, bg="#C8E6C9")
        resource_notebook.add(furniture_frame, text="Furniture Management")
        self.create_button_grid(furniture_frame, furniture_buttons)
        self.logger.info("Furniture Management sub-tab created")

        # Logout and Register Frame
        logout_frame = tk.Frame(frame, bg="#f0f8ff")
        logout_frame.grid(row=3, column=0, sticky="ew")
        logout_frame.grid_columnconfigure(0, weight=1)
        logout_frame.grid_columnconfigure(1, weight=1)

        tk.Button(logout_frame, text="Register User", command=self.app.register_user, bg="#4CAF50", fg="white").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        tk.Button(logout_frame, text="Logout", command=self.app.logout, bg="#F44336", fg="white").grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        self.logger.info(f"Dashboard created with {len(self.notebook.tabs())} main tabs")
        return frame

    def button_click(self, command):
        command()

    def update_clock(self):
        try:
            if hasattr(self, 'clock_label') and self.clock_label.winfo_exists():  
                current_time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                self.clock_label.config(text=current_time)
                self.clock_update_id = self.root.after(1000, self.update_clock)  
        except tk.TclError:
            
            pass

    def show_notifications(self):
        current_user = getattr(self.app, 'current_user', None)
        if not current_user:
            self.logger.warning("No user ID available for notifications")
            messagebox.showerror("Error", "User ID not found. Please log in.")
            return

        reminder_text = self.app.check_reminders(current_user)
        if reminder_text:
            notification_window = tk.Toplevel(self.root)
            notification_window.title("Overdue Revision Books")
            notification_window.geometry("600x400")

            canvas = tk.Canvas(notification_window, bg="#f0f8ff")
            scrollbar = ttk.Scrollbar(notification_window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")

            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            tk.Label(
                scrollable_frame,
                text="Overdue Revision Books",
                font=('Arial', 14, "bold"),
                bg="#f0f8ff",
                fg="#333333"
            ).pack(pady=10)

            overdue_label = tk.Label(
                scrollable_frame,
                text=reminder_text,
                font=('Arial', 10),
                bg="#f0f8ff",
                fg="black",
                justify="left",
                wraplength=550
            )
            overdue_label.pack(padx=10, pady=5, anchor="w")

            self.root.update_idletasks()
            canvas.config(width=scrollable_frame.winfo_reqwidth())
        else:
            messagebox.showinfo("Notifications", "No overdue revision books at this time.")

    def show_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("300x200")
        tk.Label(settings_win, text="Theme:").pack(pady=5)
        theme_var = tk.StringVar(value="Light")
        tk.Radiobutton(settings_win, text="Light", variable=theme_var, value="Light").pack()
        tk.Radiobutton(settings_win, text="Dark", variable=theme_var, value="Dark").pack()
        tk.Radiobutton(settings_win, text="Blue", variable=theme_var, value="Blue").pack()
        tk.Radiobutton(settings_win, text="Green", variable=theme_var, value="Green").pack()
        tk.Button(settings_win, text="Apply", command=lambda: self.apply_theme(theme_var.get())).pack(pady=10)

    def apply_theme(self, theme):
        if theme == "Dark":
            self.root.configure(bg="#333333")
            foreground_color = "white"
            background_color = "#333333"
            button_bg = "#555555"
            button_fg = "white"
            notebook_bg = "#444444"
            notebook_fg = "white"
        elif theme == "Light":
            self.root.configure(bg="#f0f8ff")
            foreground_color = "black"
            background_color = "#f0f8ff"
            button_bg = "#D3D3D3"
            button_fg = "black"
            notebook_bg = ttk.Style().lookup('TNotebook.tab', 'background') # Get default notebook color
            notebook_fg = "black"
        elif theme == "Blue":
            self.root.configure(bg="#ADD8E6")  # Light Blue
            foreground_color = "black"
            background_color = "#ADD8E6"
            button_bg = "#87CEEB"  # Sky Blue
            button_fg = "black"
            notebook_bg = "#B0E0E6"  # Powder Blue
            notebook_fg = "black"
        elif theme == "Green":
            self.root.configure(bg="#90EE90")  # Light Green
            foreground_color = "black"
            background_color = "#90EE90"
            button_bg = "#3CB371"  # Medium Sea Green
            button_fg = "white"
            notebook_bg = "#8FBC8F"  # Dark Sea Green
            notebook_fg = "white"
        else:  # Default to Light if theme is not recognized
            self.root.configure(bg="#f0f8ff")
            foreground_color = "black"
            background_color = "#f0f8ff"
            button_bg = "#D3D3D3"
            button_fg = "black"
            notebook_bg = ttk.Style().lookup('TNotebook.tab', 'background')
            notebook_fg = "black"

        # Apply the theme colors to various widgets
        self.style.configure("TLabel", background=background_color, foreground=foreground_color)
        self.style.configure("TButton", background=button_bg, foreground=button_fg)
        self.style.configure("Clicked.TButton", background="#4CAF50", foreground="white") # Keep clicked style
        self.style.configure("TNotebook", background=notebook_bg, foreground=notebook_fg)
        self.style.configure("TNotebook.Tab", background=notebook_bg, foreground=notebook_fg)

        # Update background colors of existing frames 
        for frame in self.notebook_frames.values():
            frame.config(bg=background_color)
        for frame in self.button_frames.values():
            frame.config(bg=background_color)
        if hasattr(self, 'utility_frame'):
            self.utility_frame.config(bg=background_color)
        if hasattr(self, 'welcome_frame'):
            self.welcome_frame.config(bg="#FFD700") 

        # Update the clock label colors
        if hasattr(self, 'clock_label'):
            self.clock_label.config(bg=background_color, fg=foreground_color)


    def show_help(self):
        try:
            with open("help.txt", "r") as f:
                help_text = f.read()
            help_window = tk.Toplevel(self.root)
            help_window.title("Help")
            text_area = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, width=80, height=20)
            text_area.insert(tk.INSERT, help_text)
            text_area.config(state=tk.DISABLED)
            text_area.pack(expand=True, fill=tk.BOTH)
        except FileNotFoundError:
            messagebox.showinfo("Help", "Help file not found. Please create 'help.txt' with instructions.")

    def refresh_dashboard(self):
        messagebox.showinfo("Refresh", "Dashboard refreshed!")


    def create_login_window(self):
        """Create the login window with a manual backup button using grid layout."""
        try:
            self.login_frame = ttk.Frame(self.root, style="LoginFrame.TFrame")
            self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            ttk.Label(self.login_frame, text="Username:", style="LoginFrameLabel.TLabel").grid(row=0, column=0, padx=5, pady=5)
            self.username_entry = ttk.Entry(self.login_frame)
            self.username_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(self.login_frame, text="Password:", style="LoginFrameLabel.TLabel").grid(row=1, column=0, padx=5, pady=5)
            self.password_entry = tk.Entry(self.login_frame, show="*")
            self.password_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Button(self.login_frame, text="Login", command=self.app.login, style="LoginFrameButton.TButton").grid(row=2, column=0, columnspan=2, pady=10)
            tk.Button(self.login_frame, text="Manual Backup", command=self.app.manual_backup).grid(row=3, column=0, columnspan=2, pady=5)
            tk.Button(self.login_frame, text="Restore Database", command=self.app.restore_database).grid(row=4, column=0, columnspan=2, pady=5)
            return self.login_frame
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create login window: {tcl_err}")
            return None
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Invalid widget configuration: {attr_err}")
            return None

    def register_user(self):
        """Creates a window to register a new user with input validation."""
        try:
            register_window = tk.Toplevel(self.root)
            register_window.title("Register User")

            ttk.Label(register_window, text="Username:").grid(row=0, column=0, padx=5, pady=5)
            username_entry = ttk.Entry(register_window)
            username_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(register_window, text="Password:").grid(row=1, column=0, padx=5, pady=5)
            password_entry = ttk.Entry(register_window, show="*")
            password_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(register_window, text="Role:").grid(row=2, column=0, padx=5, pady=5)
            role_var = tk.StringVar(value="librarian")
            ttk.Combobox(register_window, textvariable=role_var, values=["librarian", "administrator"]).grid(row=2, column=1, padx=5, pady=5)

            def save_user_with_validation():
                username = username_entry.get().strip()
                password = password_entry.get().strip()
                role = role_var.get().strip()
                if not username:
                    messagebox.showerror("Input Error", "Username cannot be empty.")
                    return
                if len(username) > 50:
                    messagebox.showerror("Input Error", "Username must be 50 characters or less.")
                    return
                if not password:
                    messagebox.showerror("Input Error", "Password cannot be empty.")
                    return
                if len(password) < 6:
                    messagebox.showerror("Input Error", "Password must be at least 6 characters long.")
                    return
                if role not in ["librarian", "administrator"]:
                    messagebox.showerror("Input Error", "Role must be 'librarian' or 'administrator'.")
                    return
                self.app.save_user(username, password, role, register_window)

            ttk.Button(register_window, text="Save", command=save_user_with_validation).grid(row=3, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create register user window: {tcl_err}")
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Invalid widget setup for register user: {attr_err}")
    


    def add_student(self):
        """Creates a window to add a new student with input validation."""
        try:
            student_window = tk.Toplevel(self.root)
            student_window.title("Add Student")

            # Student Name
            ttk.Label(student_window, text="Student Name:").grid(row=0, column=0, padx=5, pady=5)
            name_entry = ttk.Entry(student_window)
            name_entry.grid(row=0, column=1, padx=5, pady=5)

            # Student ID
            ttk.Label(student_window, text="Student ID:").grid(row=1, column=0, padx=5, pady=5)
            student_id_entry = ttk.Entry(student_window)
            student_id_entry.grid(row=1, column=1, padx=5, pady=5)

            # Stream (optional)
            ttk.Label(student_window, text="Stream (optional):").grid(row=2, column=0, padx=5, pady=5)
            stream_entry = ttk.Entry(student_window)
            stream_entry.grid(row=2, column=1, padx=5, pady=5)

            def save_student_with_validation():
                student_id = student_id_entry.get().strip()
                name = name_entry.get().strip()
                stream = stream_entry.get().strip()

                # Validate all fields are provided
                if not all([student_id, name, stream]):
                    messagebox.showerror("Input Error", "All fields (Student ID, Name, Stream) are required.")
                    return

                # Additional validation (optional)
                if len(student_id) > 20 or not student_id.isalnum():
                    messagebox.showerror("Input Error", "Student ID must be 20 characters or less and alphanumeric.")
                    return
                if len(name) > 255:
                    messagebox.showerror("Input Error", "Name must be 255 characters or less.")
                    return
                if len(stream) > 50:
                    messagebox.showerror("Input Error", "Stream must be 50 characters or less.")
                    return

                # Call save_student with mandatory stream
                if self.app.save_student(student_id, name, stream, student_window):
                    self.logger.info(f"Student {student_id} added successfully")

            ttk.Button(student_window, text="Add", command=save_student_with_validation).grid(row=3, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to create add student window: {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to create add student window: {tcl_err}")


    def create_add_teacher_window(self):
        """Creates a window to add a new teacher with input validation."""
        try:
            teacher_window = tk.Toplevel(self.root)
            teacher_window.title("Add Teacher")

            tk.Label(teacher_window, text="Teacher Name:").grid(row=0, column=0, padx=5, pady=5)
            teacher_name_entry = tk.Entry(teacher_window)
            teacher_name_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(teacher_window, text="TSC Number:").grid(row=1, column=0, padx=5, pady=5)
            teacher_id_entry = tk.Entry(teacher_window)
            teacher_id_entry.grid(row=1, column=1, padx=5, pady=5)

            def add_teacher_with_validation():
                teacher_id = teacher_id_entry.get().strip()
                teacher_name = teacher_name_entry.get().strip()
                if not teacher_id:
                    messagebox.showerror("Input Error", "TSC Number cannot be empty.")
                    return
                if len(teacher_id) > 20 or not teacher_id.isalnum():
                    messagebox.showerror("Input Error", "TSC Number must be 20 characters or less and alphanumeric.")
                    return
                if not teacher_name:
                    messagebox.showerror("Input Error", "Teacher Name cannot be empty.")
                    return
                if len(teacher_name) > 255:
                    messagebox.showerror("Input Error", "Teacher Name must be 255 characters or less.")
                    return
                self.app.add_teacher(teacher_id, teacher_name, teacher_window)

            tk.Button(teacher_window, text="Add Teacher", command=add_teacher_with_validation).grid(row=2, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create add teacher window: {tcl_err}")
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Invalid widget setup for add teacher: {attr_err}")

    
    def borrow_book(self):
        """Creates a window for a teacher to borrow a book with input validation, confirmation, and condition selection."""
        try:
            borrow_book_window = tk.Toplevel(self.root)
            borrow_book_window.title("Book Borrowed")

            ttk.Label(borrow_book_window, text="Teacher ID:").grid(row=0, column=0, padx=5, pady=5)
            borrower_id_entry = ttk.Entry(borrow_book_window)
            borrower_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(borrow_book_window, text="Book ID:").grid(row=1, column=0, padx=5, pady=5)
            book_id_entry = ttk.Entry(borrow_book_window)
            book_id_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(borrow_book_window, text="Condition:").grid(row=2, column=0, padx=5, pady=5)
            condition_var = tk.StringVar(value="New")  # Default to "New"
            condition_dropdown = ttk.Combobox(borrow_book_window, textvariable=condition_var, values=["New", "Good", "Damaged"], state="readonly")
            condition_dropdown.grid(row=2, column=1, padx=5, pady=5)

            def borrow_with_validation_and_prompt():
                teacher_id = borrower_id_entry.get().strip()
                book_id = book_id_entry.get().strip()
                condition = condition_var.get()
                if not teacher_id:
                    messagebox.showerror("Input Error", "Teacher ID cannot be empty.")
                    return
                if len(teacher_id) > 20 or not teacher_id.isalnum():
                    messagebox.showerror("Input Error", "Teacher ID must be 20 characters or less and alphanumeric.")
                    return
                if not book_id:
                    messagebox.showerror("Input Error", "Book ID cannot be empty.")
                    return
                if len(book_id) > 255:
                    messagebox.showerror("Input Error", "Book ID must be 255 characters or less.")
                    return
                if messagebox.askyesno("Confirm Borrow", f"Are you sure you want to borrow Book ID '{book_id}' for Teacher ID '{teacher_id}' in '{condition}' condition?"):
                    self.app.borrow_book_teacher(teacher_id, book_id, borrow_book_window, condition)
                else:
                    messagebox.showinfo("Cancelled", "Borrowing operation cancelled.")

            ttk.Button(borrow_book_window, text="Borrow", command=borrow_with_validation_and_prompt).grid(row=3, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create borrow book window: {tcl_err}")
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Invalid widget setup for borrow book: {attr_err}")

    
    def return_book(self):
        """Creates a window for a teacher to return a book with input validation, confirmation, and condition selection."""
        try:
            return_book_window = tk.Toplevel(self.root)
            return_book_window.title("Return Book")

            ttk.Label(return_book_window, text="Teacher ID:").grid(row=0, column=0, padx=5, pady=5)
            borrower_id_entry = ttk.Entry(return_book_window)
            borrower_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(return_book_window, text="Book ID:").grid(row=1, column=0, padx=5, pady=5)
            book_id_entry = ttk.Entry(return_book_window)
            book_id_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(return_book_window, text="Condition on Return:").grid(row=2, column=0, padx=5, pady=5)
            condition_var = tk.StringVar(value="Good")
            condition_dropdown = ttk.Combobox(return_book_window, textvariable=condition_var, values=["New", "Good", "Damaged"], state="readonly")
            condition_dropdown.grid(row=2, column=1, padx=5, pady=5)

            # Display current condition
            current_condition_label = ttk.Label(return_book_window, text="Current Condition: N/A")
            current_condition_label.grid(row=3, column=0, columnspan=2, pady=5)

            def update_current_condition(event=None):
                teacher_id = borrower_id_entry.get().strip()
                book_id = book_id_entry.get().strip()
                if teacher_id and book_id:
                    name, borrowed_books = self.app.get_teacher_info(teacher_id)
                    if name:
                        for b_id, cond in borrowed_books:
                            if b_id == book_id:
                                current_condition_label.config(text=f"Current Condition: {cond}")
                                return
                    current_condition_label.config(text="Current Condition: Not Borrowed")
                else:
                    current_condition_label.config(text="Current Condition: N/A")

            borrower_id_entry.bind("<KeyRelease>", update_current_condition)
            book_id_entry.bind("<KeyRelease>", update_current_condition)

            def return_with_validation_and_prompt():
                teacher_id = borrower_id_entry.get().strip()
                book_id = book_id_entry.get().strip()
                condition = condition_var.get()
                if not teacher_id or not book_id:
                    messagebox.showerror("Input Error", "Teacher ID and Book ID cannot be empty.")
                    return
                if messagebox.askyesno("Confirm Return", f"Return Book ID '{book_id}' for Teacher ID '{teacher_id}' in '{condition}' condition?"):
                    self.app.return_book_teacher(teacher_id, book_id, return_book_window, condition)

            ttk.Button(return_book_window, text="Return", command=return_with_validation_and_prompt).grid(row=4, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create return book window: {tcl_err}")


    def add_new_book(self):
        try:
            add_book_window = tk.Toplevel(self.root)
            add_book_window.title("Add New Book")

            ttk.Label(add_book_window, text="Book ID:").grid(row=0, column=0, padx=5, pady=5)
            book_id_entry = ttk.Entry(add_book_window)
            book_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(add_book_window, text="Tags (comma-separated):").grid(row=1, column=0, padx=5, pady=5)
            tags_entry = ttk.Entry(add_book_window)
            tags_entry.grid(row=1, column=1, padx=5, pady=5)

            def save_with_validation():
                book_id = book_id_entry.get().strip()
                tags = tags_entry.get().strip()
                if not book_id:
                    messagebox.showerror("Input Error", "Book ID cannot be empty.")
                    return
                if messagebox.askyesno("Confirm", f"Add Book ID '{book_id}' with tags '{tags}'?"):
                    try:
                        result = self.app.add_book_with_tags(book_id, tags)
                        if result:  # Assuming add_book_with_tags returns True/False or similar
                            messagebox.showinfo("Success", f"Book '{book_id}' added successfully with tags '{tags}'.")
                            
                        else:
                            messagebox.showerror("Error", f"Failed to add book '{book_id}'. Please try again.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to add book '{book_id}': {e}")

            ttk.Button(add_book_window, text="Save", command=save_with_validation).grid(row=2, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create add new book window: {tcl_err}")



    def view_all_books(self, books):
        """Displays all books and offers a print option after preview."""
        try:
            # Create a message with all book IDs
            message = "BOOKS IN THE LIBRARY:\n\n" + "\n\n".join(f"ID: {book_id}" for book_id in books)
        
            # Show the books first without any print prompt
            preview_response = messagebox.showinfo("Books", message)
        
            # After the user closes the preview, ask if they want to print
            if messagebox.askyesno("Print Books", "Do you want to print the book list?"):
                self.app.print_books(books)
            
        except TypeError as type_err:
            messagebox.showerror("Display Error", f"Invalid book data format: {type_err}")

    def view_all_books_gui(self, books=None):
        try:
            # Fetch books if not provided
            if books is None:
                books = self.app.logic.get_all_books()
                if not books:
                    messagebox.showinfo("No Books", "No books available in the library.")
                    return

            books_window = tk.Toplevel(self.root)
            books_window.title("All Books")
            books_window.geometry("500x600")
            books_window.configure(bg="#f0f0f0")

            # Style configuration
            style = ttk.Style()
            style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=2)
            style.configure("CardLabel.TLabel", background="#ffffff", font=("Helvetica", 10))
            style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), background="#f0f0f0")
            style.configure("Search.TButton", font=("Helvetica", 10, "bold"))
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

            filter_frame = ttk.Frame(books_window, padding=10)
            filter_frame.pack(fill="x", pady=(0, 10))

            ttk.Label(filter_frame, text="Filter by Tag:", style="Header.TLabel").grid(row=0, column=0, padx=5, pady=5)
            tag_filter_entry = ttk.Entry(filter_frame)
            tag_filter_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            result_frame = ttk.Frame(books_window)
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            tree = ttk.Treeview(result_frame, columns=("Book ID",), show="headings", height=20)
            tree.heading("Book ID", text="Book ID")
            tree.column("Book ID", width=400)
            tree.configure(selectmode="browse")

            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)

            book_export_data = []

            def sort_books(book_list):
                def parse_book_id(book_id):
                    # Split the book ID into parts
                    parts = book_id.split('/')
                    parsed = []
                    for part in parts:
                        # If the part is numeric, pad it to a fixed width (e.g., 3 digits) for string comparison
                        if part.isdigit():
                            parsed.append(f"{int(part):03d}")  # e.g., "2" -> "002", "44" -> "044"
                        else:
                            parsed.append(part)  # Keep non-numeric parts as-is
                    # Pad with empty strings to ensure consistent length
                    while len(parsed) < 5:
                        parsed.append('')
                    return parsed
            
                # Sort based on parsed parts, all as strings
                return sorted(book_list, key=parse_book_id)

            def populate_tree(book_list):
                for item in tree.get_children():
                    tree.delete(item)
                book_export_data.clear()

                sorted_books = sort_books(book_list)
                tree.insert("", tk.END, values=(f"Total Books: {len(sorted_books)}",))
                for book in sorted_books:
                    tree.insert("", tk.END, values=(book,))
                    book_export_data.append({"Book ID": book})

            def apply_filter():
                tag_filter = tag_filter_entry.get().strip() or None
                filtered_books = self.app.logic.view_all_books(tag_filter)
                if filtered_books:
                    populate_tree(filtered_books)

            populate_tree(books)

            ttk.Button(filter_frame, text="Apply Filter", command=apply_filter, style="Search.TButton").grid(row=1, column=0, columnspan=2, pady=10)

            download_frame = ttk.Frame(books_window)
            download_frame.pack(pady=5)

            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                if not book_export_data:
                    messagebox.showinfo("No Data", "No book data available to export.", parent=books_window)
                    return
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")]
                )
                if not file_path:
                    return
                if file_format == "Excel":
                    df = pd.DataFrame(book_export_data)
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=books_window)
                elif file_format == "PDF":
                    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                    elements = []
                
                    def add_page_header_footer(canvas, doc):
                        canvas.saveState()
                        canvas.setFont("Helvetica-Bold", 12)
                        canvas.drawString(inch, letter[1] - 0.5*inch, "Books Inventory Report")
                        canvas.setFont("Helvetica", 10)
                        canvas.drawString(inch, letter[1] - 0.75*inch, f"Total Books: {len(book_export_data)}")
                        page_num = canvas.getPageNumber()
                        canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                        canvas.restoreState()

                    table_data = [["Book ID"]]
                    for book in book_export_data:
                        table_data.append([book["Book ID"]])

                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]))
                    elements.append(table)

                    doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=books_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            ttk.Button(books_window, text="Close", command=books_window.destroy, style="Action.TButton").pack(pady=5)

            books_window.grid_rowconfigure(1, weight=1)
            books_window.grid_columnconfigure(0, weight=1)

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display books: {tcl_err}")


    def search_student(self):
        """Creates a visually appealing window to search for a student with filters and download options."""
        try:
            search_window = tk.Toplevel(self.root)
            search_window.title("Search Student")
            search_window.geometry("500x600")
            search_window.configure(bg="#f0f0f0")

            # Style configuration for a modern look
            style = ttk.Style()
            style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=2)
            style.configure("CardLabel.TLabel", background="#ffffff", font=("Helvetica", 10))
            style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), background="#f0f0f0")
            style.configure("Search.TButton", font=("Helvetica", 10, "bold"))
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

            # Input frame at the top
            input_frame = ttk.Frame(search_window, padding=10)
            input_frame.pack(fill="x", pady=(0, 10))

            ttk.Label(input_frame, text="Student ID:", style="Header.TLabel").grid(row=0, column=0, padx=5, pady=5)
            student_id_entry = ttk.Entry(input_frame)
            student_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(input_frame, text="Name (partial):", style="Header.TLabel").grid(row=1, column=0, padx=5, pady=5)
            name_entry = ttk.Entry(input_frame)
            name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

            borrowed_var = tk.BooleanVar()
            ttk.Checkbutton(input_frame, text="Has Borrowed Books", variable=borrowed_var).grid(row=2, column=0, columnspan=2, pady=5)

            reams_var = tk.BooleanVar()
            ttk.Checkbutton(input_frame, text="Has Reams", variable=reams_var).grid(row=3, column=0, columnspan=2, pady=5)

            # Scrollable result area
            result_frame = ttk.Frame(search_window)
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            canvas = tk.Canvas(result_frame, bg="#f0f0f0")
            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # List to store student data for export
            student_export_data = []

            def search_with_validation():
                student_id = student_id_entry.get().strip()
                name_filter = name_entry.get().strip()
                if student_id and (len(student_id) > 20 or not student_id.isalnum()):
                    messagebox.showerror("Input Error", "Student ID must be 20 characters or less and alphanumeric.")
                    return
                if name_filter and len(name_filter) > 255:
                    messagebox.showerror("Input Error", "Name filter must be 255 characters or less.")
                    return

                # Clear previous results
                for widget in scrollable_frame.winfo_children():
                    widget.destroy()
                student_export_data.clear()  # Clear previous export data

                # Fetch students based on filters
                conn = self.app.db_manager._create_connection()
                if not conn:
                    no_result_label = ttk.Label(scrollable_frame, text="Database connection failed.", style="CardLabel.TLabel", foreground="#666666")
                    no_result_label.pack(pady=10)
                    return

                cursor = conn.cursor()
                query = "SELECT student_id, name FROM students WHERE 1=1"
                params = []
                if student_id:
                    query += " AND student_id = ?"
                    params.append(student_id)
                if name_filter:
                    query += " AND name LIKE ?"
                    params.append(f"%{name_filter}%")
                if borrowed_var.get():
                    query += " AND EXISTS (SELECT 1 FROM borrowed_books_student bbs WHERE bbs.student_id = students.student_id)"
                if reams_var.get():
                    query += " AND EXISTS (SELECT 1 FROM ream_entries r WHERE r.student_id = students.student_id AND r.reams_count > 0)"
                cursor.execute(query, params)
                students = cursor.fetchall()
                cursor.close()
                self.app.db_manager._close_connection(conn)

                if not students:
                    no_result_label = ttk.Label(scrollable_frame, text="No students found matching the criteria.", style="CardLabel.TLabel", foreground="#666666")
                    no_result_label.pack(pady=10)
                    return

                # Display each student in a card-like format and collect data for export
                for student_id, _ in students:
                    name, stream, borrowed_books, reams_count, locker_id, chair_id = self.app.db_manager.get_student_info(student_id)
                    if name is None:
                        continue

                    # Student card frame
                    card_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
                    card_frame.pack(fill="x", pady=5, padx=5)

                    # Header with student ID and name
                    ttk.Label(card_frame, text=f"{name} ({student_id})", style="Header.TLabel", background="#4CAF50", foreground="white").pack(fill="x", pady=(0, 5))

                    # Info grid
                    info_frame = ttk.Frame(card_frame)
                    info_frame.pack(fill="x", padx=5)

                    if stream:
                        ttk.Label(info_frame, text=f"Stream: {stream}", style="CardLabel.TLabel").pack(anchor="w")
                    ttk.Label(info_frame, text=f"Reams Brought: {reams_count}", style="CardLabel.TLabel").pack(anchor="w")
                    ttk.Label(info_frame, text=f"Locker: {locker_id if locker_id else 'Not assigned'}", style="CardLabel.TLabel").pack(anchor="w")
                    ttk.Label(info_frame, text=f"Chair: {chair_id if chair_id else 'Not assigned'}", style="CardLabel.TLabel").pack(anchor="w")

                    # Borrowed books section
                    books_frame = ttk.Frame(card_frame)
                    books_frame.pack(fill="x", padx=5, pady=(5, 0))
                    ttk.Label(books_frame, text="Borrowed Books:", style="CardLabel.TLabel", font=("Helvetica", 10, "bold")).pack(anchor="w")
                    if borrowed_books:
                        for book_id in borrowed_books:
                            ttk.Label(books_frame, text=f"• {book_id}", style="CardLabel.TLabel").pack(anchor="w")
                    else:
                        ttk.Label(books_frame, text="• None", style="CardLabel.TLabel", foreground="#666666").pack(anchor="w")

                    # Add student data to export list
                    student_export_data.append({
                        "Student ID": student_id,
                        "Name": name,
                        "Stream": stream if stream else "N/A",
                        "Reams Brought": reams_count,
                        "Locker": locker_id if locker_id else "Not assigned",
                        "Chair": chair_id if chair_id else "Not assigned",
                        "Borrowed Books": ", ".join(borrowed_books) if borrowed_books else "None"
                    })

            ttk.Button(input_frame, text="Search", command=search_with_validation, style="Search.TButton").grid(row=4, column=0, columnspan=2, pady=10)

            # Download frame
            download_frame = ttk.Frame(search_window)
            download_frame.pack(pady=5)

            # Download format dropdown
            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                if not student_export_data:
                    messagebox.showinfo("No Data", "No student data available to export. Please perform a search first.", parent=search_window)
                    return

                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")]
                )
                if not file_path:
                    return

                if file_format == "Excel":
                    # Prepare data for Excel
                    df = pd.DataFrame(student_export_data)
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=search_window)

                elif file_format == "PDF":
                    # Generate PDF
                    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                    elements = []
                    styles = getSampleStyleSheet()

                    ## Define page header and footer
                    def add_page_header_footer(canvas, doc):
                        canvas.saveState()
                        # Header
                        canvas.setFont("Helvetica-Bold", 12)
                        canvas.drawString(inch, letter[1] - 0.5*inch, "Books Inventory Report")
                        canvas.setFont("Helvetica", 10)
                        canvas.drawString(inch, letter[1] - 0.75*inch, f"Total Books in System: {total_books}")
                        # Footer (page number)
                        canvas.setFont("Helvetica", 8)
                        page_num = canvas.getPageNumber()
                        canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                        canvas.restoreState()

                     # Table data
                    table_data = [["Student ID", "Name", "Stream", "Reams Brought", "Locker", "Chair", "Borrowed Books"]]
                    for student in student_export_data:
                        table_data.append([
                            student["Student ID"],
                            student["Name"],
                            student["Stream"],
                            student["Reams Brought"],
                            student["Locker"],
                            student["Chair"],
                            student["Borrowed Books"]
                        ])

                    # Create table
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]))
                    elements.append(table)

                    # Build PDF with page header
                    doc.build(elements, onFirstPage=add_page_header, onLaterPages=add_page_header)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=search_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            #Close button
            ttk.Button(search_window, text="Close", command=search_window.destroy, style="Action.TButton").pack(pady=5)

            # Make window resizable
            search_window.grid_rowconfigure(1, weight=1)
            search_window.grid_columnconfigure(0, weight=1)

        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to create search student window: {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to create search student window: {tcl_err}")
        except AttributeError as attr_err:
            self.logger.error(f"Invalid widget setup for search student: {attr_err}")
            messagebox.showerror("GUI Error", f"Invalid widget setup for search student: {attr_err}")


    def search_teacher(self):
        """Creates a visually appealing window to search for a teacher with filters."""
        try:
            self.logger.info("Opening Search Teacher window")  # Log entry
            search_window = tk.Toplevel(self.root)
            search_window.title("Search Teacher")
            search_window.geometry("500x600")
            search_window.configure(bg="#f0f0f0")

            # Style configuration for a modern look
            style = ttk.Style()
            style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=2)
            style.configure("CardLabel.TLabel", background="#ffffff", font=("Helvetica", 10))
            style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), background="#f0f0f0")
            style.configure("Search.TButton", font=("Helvetica", 10, "bold"))

            # Input frame at the top
            input_frame = ttk.Frame(search_window, padding=10)
            input_frame.pack(fill="x", pady=(0, 10))

            ttk.Label(input_frame, text="Teacher ID:").grid(row=0, column=0, padx=5, pady=5)
            teacher_id_entry = ttk.Entry(input_frame)
            teacher_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(input_frame, text="Name (partial):").grid(row=1, column=0, padx=5, pady=5)
            name_entry = ttk.Entry(input_frame)
            name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

            borrowed_var = tk.BooleanVar()
            ttk.Checkbutton(input_frame, text="Has Borrowed Books", variable=borrowed_var).grid(row=2, column=0, columnspan=2, pady=5)

            # Scrollable result area
            result_frame = ttk.Frame(search_window)
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            canvas = tk.Canvas(result_frame, bg="#f0f0f0")
            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def search_with_validation():
                self.logger.info("Search button clicked")
                teacher_id = teacher_id_entry.get().strip()
                name_filter = name_entry.get().strip()
                has_borrowed = borrowed_var.get()

                self.logger.info(f"Search params: teacher_id={teacher_id}, name_filter={name_filter}, has_borrowed={has_borrowed}")

                if teacher_id and (len(teacher_id) > 20 or not teacher_id.isalnum()):
                    messagebox.showerror("Input Error", "Teacher ID must be 20 characters or less and alphanumeric.")
                    self.logger.warning("Invalid teacher_id format")
                    return
                if name_filter and len(name_filter) > 255:
                    messagebox.showerror("Input Error", "Name filter must be 255 characters or less.")
                    self.logger.warning("Invalid name_filter length")
                    return

                # Clear previous results
                for widget in scrollable_frame.winfo_children():
                    widget.destroy()
                self.logger.info("Cleared previous search results")

                conn = self.app.db_manager._create_connection()
                if not conn:
                    no_result_label = ttk.Label(scrollable_frame, text="Database connection failed.", style="CardLabel.TLabel", foreground="#666666")
                    no_result_label.pack(pady=10)
                    search_window.update()
                    self.logger.error("Database connection failed")
                    return

                cursor = conn.cursor()
                try:
                    query = "SELECT teacher_id, teacher_name FROM teachers WHERE 1=1"
                    params = []
                    if teacher_id:
                        query += " AND teacher_id = ?"
                        params.append(teacher_id)
                    if name_filter:
                        query += " AND teacher_name LIKE ?"
                        params.append(f"%{name_filter}%")
                    if has_borrowed:
                        query += " AND EXISTS (SELECT 1 FROM borrowed_books_teacher bbt WHERE bbt.teacher_id = teachers.teacher_id)"

                    self.logger.info(f"Executing query: {query} with params: {params}")
                    cursor.execute(query, params)
                    teachers = cursor.fetchall()
                    self.logger.info(f"Found {len(teachers)} teachers")
                except SQLiteError as e:
                    self.logger.error(f"Database query failed: {e}")
                    no_result_label = ttk.Label(scrollable_frame, text=f"Query failed: {e}", style="CardLabel.TLabel", foreground="#ff0000")
                    no_result_label.pack(pady=10)
                    search_window.update()
                    return
                finally:
                    cursor.close()
                    # Do not close conn here; it’s self.connection

                if not teachers:
                    no_result_label = ttk.Label(scrollable_frame, text="No teachers found matching the criteria.", style="CardLabel.TLabel", foreground="#666666")
                    no_result_label.pack(pady=10)
                    search_window.update()
                    self.logger.info("No teachers found")
                    return

                valid_results = False
                for teacher_id_result, teacher_name in teachers:
                    self.logger.info(f"Processing teacher: {teacher_id_result}")
                    teacher_info = self.app.db_manager.get_teacher_info(teacher_id_result)
                    if not teacher_info or teacher_info[0] is None:
                        self.logger.warning(f"No info for teacher {teacher_id_result}")
                        continue

                    name, borrowed_books = teacher_info[0], teacher_info[1]
                    locker_id = teacher_info[2] if len(teacher_info) > 2 else None
                    chair_id = teacher_info[3] if len(teacher_info) > 3 else None

                    card_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
                    card_frame.pack(fill="x", pady=5, padx=5)

                    ttk.Label(card_frame, text=f"{name} ({teacher_id_result})", style="Header.TLabel", background="#2196F3", foreground="white").pack(fill="x", pady=(0, 5))

                    info_frame = ttk.Frame(card_frame)
                    info_frame.pack(fill="x", padx=5)

                    if locker_id is not None:
                        ttk.Label(info_frame, text=f"Locker: {locker_id if locker_id else 'Not assigned'}", style="CardLabel.TLabel").pack(anchor="w")
                    if chair_id is not None:
                        ttk.Label(info_frame, text=f"Chair: {chair_id if chair_id else 'Not assigned'}", style="CardLabel.TLabel").pack(anchor="w")

                    books_frame = ttk.Frame(card_frame)
                    books_frame.pack(fill="x", padx=5, pady=(5, 0))
                    ttk.Label(books_frame, text="Borrowed Books:", style="CardLabel.TLabel", font=("Helvetica", 10, "bold")).pack(anchor="w")
                    if borrowed_books:
                        for book_id, condition in borrowed_books:
                            ttk.Label(books_frame, text=f"• {book_id} ({condition})", style="CardLabel.TLabel").pack(anchor="w")
                    else:
                        ttk.Label(books_frame, text="• None", style="CardLabel.TLabel", foreground="#666666").pack(anchor="w")

                    valid_results = True

                if not valid_results:
                    no_result_label = ttk.Label(scrollable_frame, text="No valid teacher information found.", style="CardLabel.TLabel", foreground="#666666")
                    no_result_label.pack(pady=10)
                    self.logger.info("No valid teacher info to display")

                search_window.update()
                self.logger.info("Search results displayed")

            ttk.Button(input_frame, text="Search", command=search_with_validation, style="Search.TButton").grid(row=3, column=0, columnspan=2, pady=10)

            # Make window resizable
            search_window.grid_rowconfigure(1, weight=1)
            search_window.grid_columnconfigure(0, weight=1)

        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to create search teacher window: {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to create search teacher window: {tcl_err}")
        except AttributeError as attr_err:
            self.logger.error(f"Invalid widget setup for search teacher: {attr_err}")
            messagebox.showerror("GUI Error", f"Invalid widget setup for search teacher: {attr_err}")
    

    def display_unreturned_books_gui(self, unreturned_books):
        """Displays unreturned books in a GUI window with Treeview and export options (Excel/PDF)."""
        try:
            # Check if unreturned_books is a dict and has data
            if not isinstance(unreturned_books, dict) or (not unreturned_books.get("students") and not unreturned_books.get("teachers")):
                messagebox.showinfo("Information", "No books are currently unreturned or invalid data format.")
                return

            display_window = tk.Toplevel(self.root)
            display_window.title("Unreturned Books")
            display_window.geometry("1000x600")
            display_window.configure(bg="#f0f0f0")

            # Treeview with scrollbars
            tree_frame = ttk.Frame(display_window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

            tree = ttk.Treeview(tree_frame, columns=(
                "Stream", "Total Students", "Total Books", "Student/Teacher ID", "Name", 
                "Stream Detail", "Book ID", "Borrowed On", "Condition"
            ), show="headings")
            tree.heading("Stream", text="Stream")
            tree.heading("Total Students", text="Total Students/Teachers")
            tree.heading("Total Books", text="Total Books")
            tree.heading("Student/Teacher ID", text="Student/Teacher ID")
            tree.heading("Name", text="Name")
            tree.heading("Stream Detail", text="Stream")
            tree.heading("Book ID", text="Book ID")
            tree.heading("Borrowed On", text="Borrowed On")
            tree.heading("Condition", text="Condition")
            tree.column("Stream", width=100)
            tree.column("Total Students", width=100)
            tree.column("Total Books", width=100)
            tree.column("Student/Teacher ID", width=100)
            tree.column("Name", width=150)
            tree.column("Stream Detail", width=100)
            tree.column("Book ID", width=100)
            tree.column("Borrowed On", width=100)
            tree.column("Condition", width=100)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            hsb.pack(side="bottom", fill="x")

            # Process student data by stream
            student_books = unreturned_books.get("students", [])
            streams = {}
            for book in student_books:
                stream = book["stream"] or "No Stream"
                if stream not in streams:
                    streams[stream] = {"students": set(), "books": []}
                streams[stream]["students"].add(book["student_id"])
                streams[stream]["books"].append(book)

            # Process teacher data
            teacher_books = unreturned_books.get("teachers", [])
            teacher_ids = set(book["teacher_id"] for book in teacher_books) if teacher_books else set()

            # Total unreturned books
            total_unreturned_books = len(student_books) + len(teacher_books)

            # Populate Treeview
            for stream, data in streams.items():
                total_students = len(data["students"])
                total_books = len(data["books"])
                parent = tree.insert("", "end", values=(stream, total_students, total_books, "", "", "", "", "", ""))
                for book in data["books"]:
                    tree.insert(parent, "end", values=(
                        "", "", "", 
                        book["student_id"], 
                        book["student_name"], 
                        book["stream"] or "N/A", 
                        book["book_id"], 
                        book["borrowed_on"], 
                        book["book_condition"]
                    ))

            # Add teachers as a separate "stream"
            if teacher_books:
                parent = tree.insert("", "end", values=("Teachers", len(teacher_ids), len(teacher_books), "", "", "", "", "", ""))
                for book in teacher_books:
                    tree.insert(parent, "end", values=(
                        "", "", "", 
                        book["teacher_id"], 
                        book["teacher_name"], 
                        "N/A", 
                        book["book_id"], 
                        book["borrowed_on"], 
                        book["book_condition"]
                    ))

            # Download frame
            download_frame = ttk.Frame(display_window)
            download_frame.pack(pady=5)

            # Download format dropdown
            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")]
                )
                if not file_path:
                    return

                try:
                    if file_format == "Excel":
                        # Prepare data for Excel
                        data = []
                        for stream, data_stream in streams.items():
                            for book in data_stream["books"]:
                                data.append({
                                    "Stream": stream,
                                    "Student/Teacher ID": book["student_id"],
                                    "Name": book["student_name"],
                                    "Stream Detail": book["stream"] or "N/A",
                                    "Book ID": book["book_id"],
                                    "Borrowed On": book["borrowed_on"],
                                    "Condition": book["book_condition"]
                                })
                        if teacher_books:
                            for book in teacher_books:
                                data.append({
                                    "Stream": "Teachers",
                                    "Student/Teacher ID": book["teacher_id"],
                                    "Name": book["teacher_name"],
                                    "Stream Detail": "N/A",
                                    "Book ID": book["book_id"],
                                    "Borrowed On": book["borrowed_on"],
                                    "Condition": book["book_condition"]
                                })
                        df = pd.DataFrame(data)
                        df.to_excel(file_path, index=False)
                        messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

                    elif file_format == "PDF":
                        # Generate PDF with repeating headers
                        doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                        elements = []
                        styles = getSampleStyleSheet()

                        # Define page header and footer
                        def add_page_header_footer(canvas, doc):
                            canvas.saveState()
                            # Header
                            canvas.setFont("Helvetica-Bold", 12)
                            canvas.drawString(inch, letter[1] - 0.5*inch, "Unreturned Books Report")
                            canvas.setFont("Helvetica", 10)
                            canvas.drawString(inch, letter[1] - 0.75*inch, f"Total Unreturned Books: {total_unreturned_books}")
                            # Footer (page number)
                            canvas.setFont("Helvetica", 8)
                            page_num = canvas.getPageNumber()
                            canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                            canvas.restoreState()

                        # Table data
                        table_data = [["Stream", "Student/Teacher ID", "Name", "Stream Detail", "Book ID", "Borrowed On", "Condition"]]
                        for stream, data_stream in streams.items():
                            for book in data_stream["books"]:
                                table_data.append([
                                    stream,
                                    book["student_id"],
                                    book["student_name"],
                                    book["stream"] or "N/A",
                                    book["book_id"],
                                    str(book["borrowed_on"]),
                                    book["book_condition"]
                                ])
                        if teacher_books:
                            for book in teacher_books:
                                table_data.append([
                                    "Teachers",
                                    book["teacher_id"],
                                    book["teacher_name"],
                                    "N/A",
                                    book["book_id"],
                                    str(book["borrowed_on"]),
                                    book["book_condition"]
                                ])

                        # Create table with repeating headers
                        table = LongTable(table_data)
                        table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),  # Consistent font size
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ]))
                        elements.append(table)

                        # Build PDF with page header and footer
                        doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                        messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export data: {e}", parent=display_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            # Close button
            ttk.Button(display_window, text="Close", command=display_window.destroy, style="Action.TButton").pack(pady=5)

            # Style for button
            style = ttk.Style()
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5, background="#4CAF50", foreground="white")

        except TypeError as type_err:
            messagebox.showerror("Display Error", f"Invalid unreturned books data: {type_err}")
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display unreturned books: {tcl_err}")
    

    def display_books_gui(self, books):
        """Displays all books in the inventory with Treeview, grouped by class, subject, and form, with download options."""
        try:
            if not books:
                messagebox.showinfo("Information", "No books in inventory.")
                return

            # Hardcoded mappings for class and subject short forms
            class_mapping = {
                "f1": "Class 1", "f2": "Class 2", "f3": "Class 3", "f4": "Class 4",
                "sbk": "Set Book Kiswahili", "sbe": "Set Book English",
            }

            subject_mapping = {
                "mat": "Mathematics", "eng": "English", "eg": "English", "ks": "Kiswahili",
                "kis": "Kiswahili", "g": "Geography", "geo": "Geography", "geog": "Geography",
                "hg": "History & Government", "hist": "History & Government", "bs": "Business Studies",
                "bst": "Business Studies", "hom": "Home Science", "hs": "Home Science",
                "agric": "Agriculture", "ag": "Agriculture", "agr": "Agriculture", "agri": "Agriculture",
                "cs": "Computer Studies", "cm": "Chemistry", "chem": "Chemistry", "bio": "Biology",
                "mm": "Mapambazuko ya Machweo",
            }

            # Load user-defined mappings (override hardcoded if exists)
            success, user_mappings = self.app.get_short_form_mappings()
            if success:
                class_mapping.update(user_mappings.get("class", {}))
                subject_mapping.update(user_mappings.get("subject", {}))

            display_window = tk.Toplevel(self.root)
            display_window.title("Display Books")
            display_window.geometry("900x600")
            display_window.configure(bg="#f0f0f0")

            # Parse book IDs and organize data
            book_data = {}
            for book in sorted(books):
                book_id = book if isinstance(book, str) else book[0] if isinstance(book, tuple) else str(book)
                try:
                    parts = book_id.split('/')
                    if len(parts) != 5:  # Expected format: class/subject/form/book_number/year
                        class_name, subject, form, book_number, year = "Ungrouped", "Unknown", "N/A", "N/A", "N/A"
                    else:
                        class_name, subject, form, book_number, year = parts
                        form = f"Form {form}"
                        year = f"20{year}" if len(year) == 2 else year

                    full_class = class_mapping.get(class_name.lower(), class_name)
                    full_subject = subject_mapping.get(subject.lower(), subject)

                    if full_class not in book_data:
                        book_data[full_class] = {}
                    if full_subject not in book_data[full_class]:
                        book_data[full_class][full_subject] = {}
                    if form not in book_data[full_class][full_subject]:
                        book_data[full_class][full_subject][form] = []

                    book_data[full_class][full_subject][form].append({
                        "book_id": book_id,
                        "book_number": book_number,
                        "year": year
                    })
                except Exception as e:
                    print(f"Error parsing book ID {book_id}: {e}")
                    class_name, subject, form = "Ungrouped", "Unknown", "N/A"
                    full_class = class_mapping.get(class_name.lower(), class_name)
                    full_subject = subject_mapping.get(subject.lower(), subject)
                    book_data.setdefault(full_class, {}).setdefault(full_subject, {}).setdefault(form, []).append({
                        "book_id": book_id,
                        "book_number": "N/A",
                        "year": "N/A"
                    })

            # Summary frame (just total books)
            summary_frame = ttk.Frame(display_window)
            summary_frame.pack(pady=5, fill="x")

            total_books = len(books)
            ttk.Label(summary_frame, text=f"Total Books in System: {total_books}", font=("Helvetica", 12, "bold"), background="#f0f0f0").pack()

            # Classes, Subjects, and Forms in a scrollable Text widget
            info_frame = ttk.LabelFrame(display_window, text="Classes, Subjects, and Forms")
            info_frame.pack(pady=5, fill="x")

            info_text = tk.Text(info_frame, height=5, width=80, wrap="word", font=("Helvetica", 10))
            info_scroll = ttk.Scrollbar(info_frame, orient="vertical", command=info_text.yview)
            info_text.configure(yscrollcommand=info_scroll.set)
            info_text.pack(side="left", fill="x", expand=True)
            info_scroll.pack(side="right", fill="y")

            info_content = ""
            for class_name in sorted(book_data.keys()):
                subjects = sorted(book_data[class_name].keys())
                forms = set()
                for subject in subjects:
                    forms.update(book_data[class_name][subject].keys())
                forms = sorted(forms)
                info_content += f"Class: {class_name}\n  Subjects: {', '.join(subjects)}\n  Forms: {', '.join(forms)}\n\n"
            info_text.insert("end", info_content.strip())
            info_text.config(state="disabled")  # Read-only

            # Treeview frame
            tree_frame = ttk.Frame(display_window)
            tree_frame.pack(pady=10, fill="both", expand=True)

            columns = ("Count", "Book Number", "Year", "Book ID")
            tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings")
            tree.heading("#0", text="Class / Subject / Form / Book")
            tree.heading("Count", text="Count")
            tree.heading("Book Number", text="Book Number")
            tree.heading("Year", text="Year")
            tree.heading("Book ID", text="Book ID")
            tree.column("#0", width=300)
            tree.column("Count", width=100, anchor="center")
            tree.column("Book Number", width=100, anchor="center")
            tree.column("Year", width=100, anchor="center")
            tree.column("Book ID", width=300, anchor="center")

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            hsb.pack(side="bottom", fill="x")

            # Populate Treeview
            for class_name in sorted(book_data.keys()):
                class_total = sum(len(books) for subjects in book_data[class_name].values() for books in subjects.values())
                class_node = tree.insert("", "end", text=f"Class: {class_name} (Total: {class_total})", open=False)
                for subject in sorted(book_data[class_name].keys()):
                    subject_total = sum(len(books) for books in book_data[class_name][subject].values())
                    subject_node = tree.insert(class_node, "end", text=f"Subject: {subject} (Total: {subject_total})", open=False)
                    for form in sorted(book_data[class_name][subject].keys()):
                        form_books = book_data[class_name][subject][form]
                        form_node = tree.insert(subject_node, "end", text=f"Form: {form} (Total: {len(form_books)})", open=False)
                        for book in sorted(form_books, key=lambda x: x["book_id"]):
                            tree.insert(form_node, "end", text="", values=(1, book["book_number"], book["year"], book["book_id"]))

            # Download frame
            download_frame = ttk.Frame(display_window)
            download_frame.pack(pady=5)

            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")]
                )   
                if not file_path:
                    return

                if file_format == "Excel":
                    data = []
                    for class_name in sorted(book_data.keys()):
                        for subject in sorted(book_data[class_name].keys()):
                            for form in sorted(book_data[class_name][subject].keys()):
                                for book in sorted(book_data[class_name][subject][form], key=lambda x: x["book_id"]):
                                    data.append({
                                        "Class": class_name,
                                        "Subject": subject,
                                        "Form": form,
                                        "Book Number": book["book_number"],
                                        "Year": book["year"],
                                        "Book ID": book["book_id"]
                                    })
                    df = pd.DataFrame(data)
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

                elif file_format == "PDF":
                    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                    elements = []
                    styles = getSampleStyleSheet()

                    def add_page_header(canvas, doc):
                        canvas.saveState()
                        canvas.setFont("Helvetica-Bold", 12)
                        canvas.drawString(inch, letter[1] - 0.5*inch, "Books Inventory Report")
                        canvas.setFont("Helvetica", 10)
                        canvas.drawString(inch, letter[1] - 0.75*inch, f"Total Books in System: {total_books}")
                        canvas.setFont("Helvetica", 8)
                        page_num = canvas.getPageNumber()
                        canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                        canvas.restoreState()

                    table_data = [["Class", "Subject", "Form", "Book Number", "Year", "Book ID"]]
                    for class_name in sorted(book_data.keys()):
                        for subject in sorted(book_data[class_name].keys()):
                            for form in sorted(book_data[class_name][subject].keys()):
                                for book in sorted(book_data[class_name][subject][form], key=lambda x: x["book_id"]):
                                    table_data.append([
                                        class_name, subject, form,
                                        book["book_number"], book["year"], book["book_id"]
                                    ])

                    table = LongTable(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]))
                    elements.append(table)

                    doc.build(elements, onFirstPage=add_page_header, onLaterPages=add_page_header)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)
            ttk.Button(display_window, text="Close", command=display_window.destroy, style="Action.TButton").pack(pady=5)

            style = ttk.Style()
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

        except TypeError as type_err:
            messagebox.showerror("Display Error", f"Invalid books data: {type_err}")
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display books: {tcl_err}")


    def open_add_ream_window(self):
        """Creates a window to add reams with input validation."""
        try:
            add_ream_window = tk.Toplevel(self.root)
            add_ream_window.title("Add Ream")

            tk.Label(add_ream_window, text="Student ID:").grid(row=0, column=0, padx=10, pady=10)
            student_id_entry = tk.Entry(add_ream_window)
            student_id_entry.grid(row=0, column=1, padx=10, pady=10)

            tk.Label(add_ream_window, text="Number of Reams:").grid(row=1, column=0, padx=10, pady=10)
            reams_entry = tk.Entry(add_ream_window)
            reams_entry.grid(row=1, column=1, padx=10, pady=10)

            def add_ream_with_validation():
                student_id = student_id_entry.get().strip()
                reams = reams_entry.get().strip()
                if not student_id:
                    messagebox.showerror("Input Error", "Student ID cannot be empty.")
                    return
                if len(student_id) > 20 or not student_id.isalnum():
                    messagebox.showerror("Input Error", "Student ID must be 20 characters or less and alphanumeric.")
                    return
                if not reams:
                    messagebox.showerror("Input Error", "Number of Reams cannot be empty.")
                    return
                try:
                    reams_count = int(reams)
                    if reams_count < 0:
                        messagebox.showerror("Input Error", "Number of Reams must be non-negative.")
                        return
                    if reams_count > 1000:  # Arbitrary upper limit
                        messagebox.showerror("Input Error", "Number of Reams must be less than 1000.")
                        return
                except ValueError:
                    messagebox.showerror("Input Error", "Number of Reams must be a valid integer.")
                    return
                self.app.add_ream(student_id, reams_count, add_ream_window)

            tk.Button(add_ream_window, text="Add Ream", command=add_ream_with_validation).grid(row=2, column=0, columnspan=2, pady=20)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create add ream window: {tcl_err}")
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Invalid widget setup for add ream: {attr_err}")



    def total_reams(self, total, form_reams, form_stream_students):
        """Displays total reams, form-wise reams, and per-student data grouped by form and stream with download option."""
        try:
            total_reams_window = tk.Toplevel(self.root)
            total_reams_window.title("Total Reams")
            total_reams_window.geometry("800x600")
            total_reams_window.configure(bg="#f0f0f0")

            # Summary frame
            summary_frame = ttk.Frame(total_reams_window)
            summary_frame.pack(pady=5, fill="x")

            # Total reams
            ttk.Label(summary_frame, text=f"Total Reams in System: {total}", font=("Helvetica", 12, "bold"), background="#f0f0f0").pack()

            # Forms and streams
            forms_streams_text = "Forms and Streams:\n"
            for form, streams in form_stream_students.items():
                if streams:
                    stream_list = ", ".join(sorted(streams.keys()))
                    forms_streams_text += f"{form}: {stream_list}\n"
            ttk.Label(summary_frame, text=forms_streams_text, font=("Helvetica", 10), background="#f0f0f0", justify="left").pack()

            # Treeview frame
            tree_frame = ttk.Frame(total_reams_window)
            tree_frame.pack(pady=10, fill="both", expand=True)

            # Treeview
            columns = ("Student ID", "Name", "Reams")
            tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings")
            tree.heading("#0", text="Form / Stream / Student")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Name", text="Name")
            tree.heading("Reams", text="Reams")
            tree.column("#0", width=300)
            tree.column("Student ID", width=150, anchor="center")
            tree.column("Name", width=200, anchor="center")
            tree.column("Reams", width=100, anchor="center")
            tree.pack(side="left", fill="both", expand=True)

            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)

            # Populate Treeview
            for form in sorted(form_reams.keys()):
                total_form_reams = form_reams[form]
                form_node = tree.insert("", "end", text=f"{form} (Total Reams: {total_form_reams})", open=False)
                streams = form_stream_students[form]
                for stream in sorted(streams.keys()):
                    stream_node = tree.insert(form_node, "end", text=stream, open=False)
                    students = streams[stream]
                    for student in sorted(students, key=lambda x: x["student_id"]):  # Sort by student_id
                        tree.insert(stream_node, "end", text="", values=(
                            student["student_id"],
                            student["name"],
                            student["reams"]
                        ))

            # Download frame
            download_frame = ttk.Frame(total_reams_window)
            download_frame.pack(pady=5)

            # Download format dropdown
            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                file_format = format_var.get()
                # Map file format to proper extension
                extension_map = {"Excel": ".xlsx", "PDF": ".pdf"}
                file_extension = extension_map.get(file_format, f".{file_format.lower()}")

                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=file_extension,  # Use .xlsx for Excel
                    filetypes=[(f"{file_format} files", f"*{file_extension}"), ("All files", "*.*")]
                )
                if not file_path:
                    return

                if file_format == "Excel":
                    # Prepare data for Excel
                    data = []
                    for form, streams in form_stream_students.items():
                        for stream, students in streams.items():
                            for student in sorted(students, key=lambda x: x["student_id"]):
                                data.append({
                                    "Form": form,
                                    "Stream": stream,
                                    "Student ID": student["student_id"],
                                    "Name": student["name"],
                                    "Reams": student["reams"]
                                })
                    df = pd.DataFrame(data)
                    df.to_excel(file_path, index=False, engine="openpyxl")  # Explicitly specify engine
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=total_reams_window)

                elif file_format == "PDF":
                    # Generate PDF
                    doc = SimpleDocTemplate(file_path, pagesize=letter)
                    elements = []
                    styles = getSampleStyleSheet()

                    # Title
                    elements.append(Paragraph("Total Reams Report", styles["Title"]))
                    elements.append(Spacer(1, 12))

                    # Summary
                    elements.append(Paragraph(f"Total Reams in System: {total}", styles["Normal"]))
                    elements.append(Spacer(1, 12))

                    # Table data
                    table_data = [["Form", "Stream", "Student ID", "Name", "Reams"]]
                    for form, streams in form_stream_students.items():
                        for stream, students in sorted(streams.items()):
                            for student in sorted(students, key=lambda x: x["student_id"]):
                                table_data.append([
                                    form,
                                    stream,
                                    student["student_id"],
                                    student["name"],
                                    student["reams"]
                                ])

                    # Create table
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    elements.append(table)

                    # Build PDF
                    doc.build(elements)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=total_reams_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            # Close button
            ttk.Button(total_reams_window, text="Close", command=total_reams_window.destroy, style="Action.TButton").pack(pady=5)

            # Style for button
            style = ttk.Style()
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

        except TypeError as type_err:
            messagebox.showerror("Display Error", f"Invalid reams data: {type_err}")
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display total reams: {tcl_err}")


    def used_reams(self):
        """Creates a window to deduct used reams with input validation."""
        try:
            used_reams_window = tk.Toplevel(self.root)
            used_reams_window.title("Deduct Used Reams")

            tk.Label(used_reams_window, text="Enter Number of Reams Used:").pack(pady=5)
            used_reams_entry = tk.Entry(used_reams_window)
            used_reams_entry.pack(pady=5)

            reams_remaining_label = tk.Label(used_reams_window, text="Reams Remaining: Loading...")
            reams_remaining_label.pack(pady=5)

            def deduct_with_validation():
                used_reams = used_reams_entry.get().strip()
                if not used_reams:
                    messagebox.showerror("Input Error", "Number of Reams Used cannot be empty.")
                    return
                try:
                    reams_count = int(used_reams)
                    if reams_count <= 0:
                        messagebox.showerror("Input Error", "Number of Reams Used must be positive.")
                        return
                    if reams_count > 10000:  # Arbitrary upper limit
                        messagebox.showerror("Input Error", "Number of Reams Used must be less than 10000.")
                        return
                except ValueError:
                    messagebox.showerror("Input Error", "Number of Reams Used must be a valid integer.")
                    return
                
                # Perform the deduction
                self.app.deduct_reams(reams_count, reams_remaining_label)
                # Update the label with the new remaining reams count
                self.app.update_reams_remaining(reams_remaining_label)

            tk.Button(used_reams_window, text="Deduct Reams", command=deduct_with_validation).pack(pady=10)
            # Initial update of remaining reams
            self.app.update_reams_remaining(reams_remaining_label)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create deduct reams window: {tcl_err}")
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Invalid widget setup for deduct reams: {attr_err}")


     
    def display_all_reams_gui(self):
        try:
            display_window = tk.Toplevel(self.root)
            display_window.title("All Reams Report")

            # Filter frame
            filter_frame = ttk.LabelFrame(display_window, text="Filters")
            filter_frame.pack(pady=10, padx=10, fill="x")

            ttk.Label(filter_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
            student_id_entry = ttk.Entry(filter_frame)
            student_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(filter_frame, text="Date Start (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
            date_start_entry = ttk.Entry(filter_frame)
            date_start_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(filter_frame, text="Date End (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
            date_end_entry = ttk.Entry(filter_frame)
            date_end_entry.grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(filter_frame, text="Minimum Reams:").grid(row=3, column=0, padx=5, pady=5)
            min_reams_entry = ttk.Entry(filter_frame)
            min_reams_entry.grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(filter_frame, text="View Mode:").grid(row=4, column=0, padx=5, pady=5)
            view_mode_var = tk.StringVar(value="detailed")
            ttk.Combobox(filter_frame, textvariable=view_mode_var, values=["detailed", "aggregated"], state="readonly").grid(row=4, column=1, padx=5, pady=5)

            # Treeview for display
            tree_frame = ttk.Frame(display_window)
            tree_frame.pack(pady=10, fill="both", expand=True)
            tree = ttk.Treeview(tree_frame, columns=("Student ID", "Name", "Reams", "Date Added"), show="headings")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Name", text="Name")
            tree.heading("Reams", text="Reams")
            tree.heading("Date Added", text="Date Added")
            tree.pack(side="left", fill="both", expand=True)
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)

            def apply_filters():
                student_id_filter = student_id_entry.get().strip() or None
                date_start = date_start_entry.get().strip() or None
                date_end = date_end_entry.get().strip() or None
                min_reams = min_reams_entry.get().strip() or None
                view_mode = view_mode_var.get()

                if date_start:
                    try:
                        date_start = datetime.strptime(date_start, "%Y-%m-%d").date()
                    except ValueError:
                        messagebox.showerror("Input Error", "Date Start must be in YYYY-MM-DD format.")
                        return
                if date_end:
                    try:
                        date_end = datetime.strptime(date_end, "%Y-%m-%d").date()
                    except ValueError:
                        messagebox.showerror("Input Error", "Date End must be in YYYY-MM-DD format.")
                        return
                if min_reams:
                    try:
                        min_reams = int(min_reams)
                        if min_reams < 0:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Input Error", "Minimum Reams must be a non-negative integer.")
                        return

                reams = self.app.get_all_reams_report(student_id_filter, date_start, date_end, min_reams, view_mode)
                for item in tree.get_children():
                    tree.delete(item)
                for student_id, name, reams_count, date_added in reams:
                    date_added = datetime.strptime(date_added, "%Y-%m-%d")
                    tree.insert("", "end", values=(student_id, name, reams_count, date_added.strftime("%Y-%m-%d")))

            ttk.Button(filter_frame, text="Apply Filters", command=apply_filters).grid(row=5, column=0, columnspan=2, pady=10)


            def download_pdf():
                output_dir = filedialog.askdirectory(title="Select Output Directory")
                if output_dir:
                    reams = self.app.get_all_reams_report(
                        student_id_entry.get().strip() or None,
                        datetime.strptime(date_start_entry.get().strip(), "%Y-%m-%d").date() if date_start_entry.get().strip() else None,
                        datetime.strptime(date_end_entry.get().strip(), "%Y-%m-%d").date() if date_end_entry.get().strip() else None,
                        int(min_reams_entry.get().strip()) if min_reams_entry.get().strip() else None,
                        view_mode_var.get()
                    )
                    pdf_filename = self.app.download_all_reams_report(reams, output_dir)
                    if pdf_filename:
                        messagebox.showinfo("Success", f"Reams report downloaded as '{pdf_filename}'.")

            button_frame = tk.Frame(display_window)
            button_frame.pack(pady=10)
            tk.Button(button_frame, text="Download PDF", command=download_pdf, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Close", command=display_window.destroy, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)

            apply_filters()  # Initial load
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display all reams: {tcl_err}")


    def export_reams_gui(self):
        """GUI for exporting ream entries to Excel with directory selection and progress bar."""
        try:
            export_window = tk.Toplevel(self.root)
            export_window.title("Export Reams to Excel")
            export_window.geometry("300x150")

            ttk.Label(export_window, text="Exporting Reams entries...").pack(pady=5)
            progress = ttk.Progressbar(export_window, length=200, mode="indeterminate")
            progress.pack(pady=10)
            status_label = ttk.Label(export_window, text="Select a directory to begin")
            status_label.pack(pady=5)

            def export_with_directory():
                output_dir = filedialog.askdirectory(title="Select Output Directory")
                if not output_dir:
                    messagebox.showinfo("Cancelled", "Export cancelled.")
                    return
                progress.start()
                export_window.update_idletasks()
                success = self.app.export_reams_to_excel(output_dir)  # Calls LibraryManagementSystem method
                progress.stop()
                if success:
                    export_window.destroy()

            ttk.Button(export_window, text="Select Directory and Export", command=export_with_directory).pack(pady=5)
            ttk.Button(export_window, text="Cancel", command=export_window.destroy).pack(pady=5)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create export reams window: {tcl_err}")

    def import_reams_gui(self):
        """GUI for importing ream entries from Excel with file selection and progress bar."""
        try:
            import_window = tk.Toplevel(self.root)
            import_window.title("Import Reams from Excel")
            import_window.geometry("300x150")

            ttk.Label(import_window, text="Importing Reams entries...").pack(pady=5)
            progress = ttk.Progressbar(import_window, length=200, mode="indeterminate")
            progress.pack(pady=10)
            status_label = ttk.Label(import_window, text="Select an Excel file to begin")
            status_label.pack(pady=5)

            def import_with_file():
                excel_file = filedialog.askopenfilename(
                    title="Select Excel File",
                    filetypes=[("Excel files", "*.xlsx *.xls")]
                )
                if not excel_file:
                    messagebox.showinfo("Cancelled", "Import cancelled.")
                    return
                progress.start()
                import_window.update_idletasks()
                success = self.app.import_reams_from_excel(excel_file)  # Calls the import method
                progress.stop()
                if success:
                    import_window.destroy()

            ttk.Button(import_window, text="Select File and Import", command=import_with_file).pack(pady=5)
            ttk.Button(import_window, text="Cancel", command=import_window.destroy).pack(pady=5)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create import reams window: {tcl_err}")



    def return_book_by_student(self):
        try:
            return_books_window = tk.Toplevel(self.root)
            return_books_window.title("Return Books by Student")
            return_books_window.geometry("400x600")

            tk.Label(return_books_window, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
            student_id_entry = tk.Entry(return_books_window)
            student_id_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(return_books_window, text="Condition on Return:").grid(row=1, column=0, padx=5, pady=5)
            condition_var = tk.StringVar(value="Good")
            condition_dropdown = ttk.Combobox(return_books_window, textvariable=condition_var, values=["New", "Good", "Damaged"], state="readonly")
            condition_dropdown.grid(row=1, column=1, padx=5, pady=5)

            student_name_label = tk.Label(return_books_window, text="")
            student_name_label.grid(row=2, column=0, columnspan=2, pady=5)

            # Add scrollbar to book_list_frame
            canvas = tk.Canvas(return_books_window)
            scrollbar = ttk.Scrollbar(return_books_window, orient="vertical", command=canvas.yview)
            book_list_frame = tk.Frame(canvas)
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            scrollbar.grid(row=3, column=2, sticky="ns")
            canvas.create_window((0, 0), window=book_list_frame, anchor="nw")
            book_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            def search_with_validation():
                student_id = student_id_entry.get().strip()
                if not student_id:
                    messagebox.showerror("Input Error", "Student ID cannot be empty.")
                    return
                self.app.search_student_for_return(student_id, student_name_label, book_list_frame, return_books_window)

            def return_with_confirmation():
                student_id = student_id_entry.get().strip()
                condition = condition_var.get()
                if not student_id:
                    messagebox.showerror("Input Error", "Student ID cannot be empty.")
                    return
                if messagebox.askyesno("Confirm Return", f"Return selected books for Student ID '{student_id}' in '{condition}' condition?"):
                    self.app.return_selected_books(student_id, book_list_frame, condition)
                else:
                    messagebox.showinfo("Cancelled", "Returning operation cancelled.")

            tk.Button(return_books_window, text="Search", command=search_with_validation).grid(row=4, column=0, padx=5, pady=5)
            tk.Button(return_books_window, text="Return Selected", command=return_with_confirmation).grid(row=4, column=1, padx=5, pady=5)

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create return books window: {tcl_err}")
    

    def borrow_books_by_student(self):
        try:
            search_window = tk.Toplevel(self.root)
            search_window.title("Search Student to Borrow")

            borrow_window = tk.Toplevel(self.root)
            borrow_window.title("Borrow Books")
            borrow_window.withdraw()
            borrow_window.geometry("400x500")

            # Search Window Setup
            ttk.Label(search_window, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
            student_id_entry = ttk.Entry(search_window)
            student_id_entry.grid(row=0, column=1, padx=5, pady=5)

            # Borrow Window Setup
            student_name_label = ttk.Label(borrow_window, text="")
            student_name_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))

            ttk.Label(borrow_window, text="Book ID:").grid(row=1, column=0, padx=5, pady=5)
            book_id_entry = ttk.Entry(borrow_window)
            book_id_entry.grid(row=1, column=1, padx=5, pady=5)

            book_frame = ttk.Frame(borrow_window)
            book_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            
            book_listbox = tk.Listbox(book_frame, height=20, width=40)
            book_listbox.pack(side=tk.LEFT, fill="both", expand=True)
            
            scrollbar = ttk.Scrollbar(book_frame, orient="vertical", command=book_listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill="y")
            book_listbox.config(yscrollcommand=scrollbar.set)

            # Ensure borrowed_books is initialized and cleared only once at start
            if not hasattr(self.app, 'borrowed_books'):
                self.app.borrowed_books = []
            #print(f"Initial state: {self.app.borrowed_books}")  # Debug
            self.app.borrowed_books.clear()
            self.app._update_borrow_list(book_listbox)

            def search_with_validation():
                student_id = student_id_entry.get().strip()
                if not student_id:
                    messagebox.showerror("Input Error", "Student ID cannot be empty.", parent=search_window)
                    return
                if len(student_id) > 20 or not student_id.isalnum():
                    messagebox.showerror("Input Error", "Student ID must be 20 characters or less and alphanumeric.", parent=search_window)
                    return
                self.app.search_student_for_borrow(student_id, borrow_window, search_window, book_listbox, student_name_label)

            ttk.Button(search_window, text="Search Student", command=search_with_validation).grid(row=1, column=0, columnspan=2, pady=10)

            def add_book_with_validation():
                book_id = book_id_entry.get().strip()
                if not book_id:
                    messagebox.showerror("Input Error", "Book ID cannot be empty.", parent=borrow_window)
                    return
                if len(book_id) > 255:
                    messagebox.showerror("Input Error", "Book ID must be 255 characters or less.", parent=borrow_window)
                    return
                self.app.add_book_to_borrow(book_id, book_listbox)
                book_id_entry.delete(0, tk.END)

            def remove_selected_book():
                try:
                    selected = book_listbox.curselection()
                    if not selected:
                        messagebox.showinfo("Selection Error", "Please select a book to remove.", parent=borrow_window)
                        return
                    selected_idx = selected[0]
                    if not self.app.borrowed_books:
                        messagebox.showinfo("Info", "No books in borrow list to remove.", parent=borrow_window)
                        if book_listbox.size() > 0:
                            messagebox.showwarning("Warning", "Listbox has items but borrowed list is empty. Resetting.", parent=borrow_window)
                            book_listbox.delete(0, tk.END)
                        return
                    if selected_idx >= len(self.app.borrowed_books):
                        messagebox.showerror("Error", "Selected index out of range. Resyncing list.", parent=borrow_window)
                        self.app._update_borrow_list(book_listbox)
                        return
                    #print(f"Before removal: {self.app.borrowed_books}")  # Debug
                    removed_book = self.app.borrowed_books.pop(selected_idx)
                    self.app._update_borrow_list(book_listbox)
                    #print(f"After removal: {self.app.borrowed_books}")  # Debug
                    messagebox.showinfo("Success", f"Removed Book ID: {removed_book} from the borrow list.", parent=borrow_window)
                except IndexError as e:
                    messagebox.showerror("Error", f"Index error removing book: {e}", parent=borrow_window)
                except AttributeError as e:
                    messagebox.showerror("Error", f"Failed to remove book: {e}", parent=borrow_window)

            def borrow_all_with_confirmation():
                if not book_listbox.size():
                    messagebox.showerror("Input Error", "No books added to borrow.", parent=borrow_window)
                    return
                book_ids = list(book_listbox.get(0, tk.END))
                book_ids = [entry.split("Book ID: ")[1] for entry in book_ids]
                #print(f"Confirming borrow: {self.app.borrowed_books}")  # Debug before confirmation
                if messagebox.askyesno("Confirm Borrow", f"Are you sure you want to borrow these books?\n{', '.join(book_ids)}", parent=borrow_window):
                    #print(f"Before borrow_all: {self.app.borrowed_books}")  # Debug
                    success = self.app.borrow_all_books(borrow_window, book_listbox)
                    if success:
                        borrow_window.destroy()
                else:
                    messagebox.showinfo("Cancelled", "Borrowing operation cancelled.", parent=borrow_window)

            # Buttons
            ttk.Button(borrow_window, text="Add Book", command=add_book_with_validation).grid(row=3, column=0, columnspan=2, pady=5)
            ttk.Button(borrow_window, text="Remove Selected", command=remove_selected_book).grid(row=4, column=0, columnspan=2, pady=5)
            ttk.Button(borrow_window, text="Borrow All Books", command=borrow_all_with_confirmation).grid(row=5, column=0, columnspan=2, pady=5)

            borrow_window.grid_rowconfigure(2, weight=1)
            borrow_window.grid_columnconfigure(0, weight=1)
            borrow_window.grid_columnconfigure(1, weight=1)

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create borrow books window: {tcl_err}")
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Invalid widget setup for borrow books: {attr_err}")


    def add_revision_book(self):
        try:
            add_window = tk.Toplevel(self.root)
            add_window.title("Add Revision Book")

            # Book ID input
            tk.Label(add_window, text="Book ID:").grid(row=0, column=0, padx=5, pady=5)
            book_id_entry = tk.Entry(add_window)
            book_id_entry.grid(row=0, column=1, padx=5, pady=5)

            # Tags input (optional)
            tk.Label(add_window, text="Tags (comma-separated, optional):").grid(row=1, column=0, padx=5, pady=5)
            tags_entry = tk.Entry(add_window)
            tags_entry.grid(row=1, column=1, padx=5, pady=5)

            def save_with_validation():
                book_id = book_id_entry.get().strip()
                tags_input = tags_entry.get().strip()

                if not book_id:
                    messagebox.showerror("Input Error", "Book ID cannot be empty.")
                    return
                if len(book_id) > 255:
                    messagebox.showerror("Input Error", "Book ID must be 255 characters or less.")
                    return

                # Convert tags string to list if provided, otherwise None
                tags = None
                if tags_input:
                    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

                try:
                    success = self.app.save_revision_book(book_id, tags)
                    if success:
                        messagebox.showinfo("Success", "Book added successfully!")
                        add_window.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to add book. Please check logs.")
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                    self.logger.error(f"Error saving revision book: {e}")

            tk.Button(add_window, text="Add", command=save_with_validation).grid(row=2, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create add revision book window: {tcl_err}")
            
    
    def borrow_revision_book_gui(self):
        try:
            borrow_window = tk.Toplevel(self.root)
            borrow_window.title("Borrow Revision Book")

            tk.Label(borrow_window, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
            student_id_entry = tk.Entry(borrow_window)
            student_id_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(borrow_window, text="Book ID:").grid(row=1, column=0, padx=5, pady=5)
            book_id_entry = tk.Entry(borrow_window)
            book_id_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(borrow_window, text="Reminder Days:").grid(row=2, column=0, padx=5, pady=5)
            reminder_entry = tk.Entry(borrow_window)
            reminder_entry.grid(row=2, column=1, padx=5, pady=5)

            tk.Label(borrow_window, text="Condition:").grid(row=3, column=0, padx=5, pady=5)
            condition_var = tk.StringVar(value="New")
            ttk.Combobox(borrow_window, textvariable=condition_var, values=["New", "Good", "Damaged"], state="readonly").grid(row=3, column=1, padx=5, pady=5)

            tk.Label(borrow_window, text="Tags (comma-separated):").grid(row=4, column=0, padx=5, pady=5)
            tags_entry = tk.Entry(borrow_window)
            tags_entry.grid(row=4, column=1, padx=5, pady=5)

            def borrow_with_validation():
                student_id = student_id_entry.get().strip()
                book_id = book_id_entry.get().strip()
                reminder_days = reminder_entry.get().strip()
                condition = condition_var.get()
                tags = tags_entry.get().strip()

                if not all([student_id, book_id, reminder_days]):
                    messagebox.showerror("Input Error", "All fields except tags are required.")
                    return
                try:
                    days = int(reminder_days)
                    if days <= 0:
                        messagebox.showerror("Input Error", "Reminder days must be positive.")
                        return
                except ValueError:
                    messagebox.showerror("Input Error", "Reminder days must be a valid integer.")
                    return

                if not messagebox.askyesno("Confirm", f"Borrow Book ID '{book_id}' for Student '{student_id}' with tags '{tags}'?"):
                    return

                # Save and borrow
                if not self.app.save_revision_book(book_id, tags):
                    messagebox.showerror("Error", f"Failed to save revision book {book_id}.")
                    return
                if self.app.borrow_revision_book(student_id, book_id, reminder_days, condition, borrow_window):
                    # Success message and window close handled in borrow_revision_book
                    pass
                else:
                    messagebox.showerror("Error", f"Failed to borrow book {book_id}. Check logs for details.")

            tk.Button(borrow_window, text="Borrow", command=borrow_with_validation).grid(row=5, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create borrow revision book window: {tcl_err}")
    
    def return_revision_book_gui(self):
        return_window = tk.Toplevel(self.root)
        return_window.title("Return Revision Book")

        tk.Label(return_window, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
        student_id_entry = tk.Entry(return_window)
        student_id_entry.grid(row=0, column=1, padx=5, pady=5)

        condition_var = tk.StringVar(value="Good")
        tk.Label(return_window, text="Condition on Return:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Combobox(return_window, textvariable=condition_var, values=["New", "Good", "Damaged"], state="readonly").grid(row=1, column=1, padx=5, pady=5)

        student_name_label = tk.Label(return_window, text="")
        student_name_label.grid(row=2, column=0, columnspan=2, pady=5)

        book_list_frame = tk.Frame(return_window)
        book_list_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.check_vars = {}

        def on_checkbutton_toggle(book_id):
            #print(f"Checkbutton {book_id} toggled to: {self.check_vars[book_id].get()}")
            return

        def search_revision_books():
            student_id = student_id_entry.get().strip()
            if not student_id:
                messagebox.showerror("Input Error", "Student ID cannot be empty.")
                return
            result = self.app.return_revision_book(student_id, book_list_frame)
            if result:
                student_name, books = result
                student_name_label.config(text=f"Student Name: {student_name}")
                for widget in book_list_frame.winfo_children():
                    widget.destroy()
                self.check_vars.clear()    
                if books:
                    for book_id in books:
                        var = tk.BooleanVar(value=False)
                        self.check_vars[book_id] = var
                        cb = tk.Checkbutton(book_list_frame, text=book_id, variable=var,
                                       command=lambda bid=book_id: on_checkbutton_toggle(bid))
                        cb.pack(anchor=tk.W)
                    book_list_frame.update()
    
                else:
                    tk.Label(book_list_frame, text="No books found.").pack()
            else:
                messagebox.showerror("Error", "Could not retrieve book information.")
            #print("After search, check_vars:", {k: v.get() for k, v in self.check_vars.items()})

        def return_selected():
            student_id = student_id_entry.get().strip()
            condition = condition_var.get()
            if not student_id:
                messagebox.showerror("Input Error", "Student ID cannot be empty.")
                return
            #print("Before selection, check_vars:", {k: v.get() for k, v in self.check_vars.items()})  # Debug
            selected_books = [book_id for book_id, var in self.check_vars.items() if var.get()]
            
            if not selected_books:
                messagebox.showerror("Error", "No books selected for return.")
                return
            if messagebox.askyesno("Confirm", f"Return {len(selected_books)} revision books for Student ID '{student_id}' in '{condition}' condition?"):
                self.app.return_selected_revision_books(student_id, selected_books, condition)  # Pass selected_books instead of book_list_frame
                messagebox.showinfo("Success", "Selected books returned successfully.")
                return_window.destroy()

        tk.Button(return_window, text="Search", command=search_revision_books).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(return_window, text="Return Selected", command=return_selected).grid(row=5, column=0, columnspan=2, pady=5)


    def view_revision_books_gui(self):
        try:
            # Fetch initial revision books
            books = self.app.view_revision_books()
            if not books:
                messagebox.showinfo("No Books", "No revision books available.")
                return

            display_window = tk.Toplevel(self.root)
            display_window.title("Revision Books")
            display_window.geometry("500x600")
            display_window.configure(bg="#f0f0f0")

            # Style configuration (same as view_all_books_gui)
            style = ttk.Style()
            style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=2)
            style.configure("CardLabel.TLabel", background="#ffffff", font=("Helvetica", 10))
            style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), background="#f0f0f0")
            style.configure("Search.TButton", font=("Helvetica", 10, "bold"))
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

            # Filter frame (same as view_all_books_gui)
            filter_frame = ttk.Frame(display_window, padding=10)
            filter_frame.pack(fill="x", pady=(0, 10))

            ttk.Label(filter_frame, text="Filter by Tag:", style="Header.TLabel").grid(row=0, column=0, padx=5, pady=5)
            tag_filter_entry = ttk.Entry(filter_frame)
            tag_filter_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            # Treeview frame
            result_frame = ttk.Frame(display_window)
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            tree = ttk.Treeview(result_frame, columns=("Book ID",), show="headings", height=20)
            tree.heading("Book ID", text="Book ID")
            tree.column("Book ID", width=400)
            tree.configure(selectmode="browse")  # Makes it uneditable

            # Add scrollbar
            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)

            # List to store book data for export (same as view_all_books_gui)
            book_export_data = []

            def sort_books(book_list):
                def parse_book_id(book_id):
                    # Split the book ID into parts
                    parts = book_id.split('/')
                    parsed = []
                    for part in parts:
                        # If the part is numeric, pad it to 3 digits for string comparison
                        if part.isdigit():
                            parsed.append(f"{int(part):03d}")  # e.g., "2" -> "002", "44" -> "044"
                        else:
                            parsed.append(part)  # Keep non-numeric parts as-is
                    # Pad with empty strings to ensure consistent length
                    while len(parsed) < 5:
                        parsed.append('')
                    return parsed
            
                # Sort based on parsed parts, all as strings
                return sorted(book_list, key=parse_book_id)

            def populate_tree(book_list):
                for item in tree.get_children():
                    tree.delete(item)
                book_export_data.clear()

                sorted_books = sort_books(book_list)
                tree.insert("", tk.END, values=(f"Total Books: {len(sorted_books)}",))
                for book in sorted_books:
                    tree.insert("", tk.END, values=(book,))
                    book_export_data.append({"Book ID": book})

            def apply_filter():
                tag_filter = tag_filter_entry.get().strip() or None
                # Assuming view_revision_books accepts a tag_filter (adjust if needed)
                filtered_books = self.app.view_revision_books(tag_filter)
                if filtered_books:
                    populate_tree(filtered_books)

            # Initial population
            populate_tree(books)

            ttk.Button(filter_frame, text="Apply Filter", command=apply_filter, style="Search.TButton").grid(row=1, column=0, columnspan=2, pady=10)

            # Download frame (same as view_all_books_gui)
            download_frame = ttk.Frame(display_window)
            download_frame.pack(pady=5)

            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                if not book_export_data:
                    messagebox.showinfo("No Data", "No book data available to export.", parent=display_window)
                    return
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")]
                )
                if not file_path:
                    return
                if file_format == "Excel":
                    df = pd.DataFrame(book_export_data)
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)
                elif file_format == "PDF":
                    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                    elements = []
                
                    def add_page_header_footer(canvas, doc):
                        canvas.saveState()
                        canvas.setFont("Helvetica-Bold", 12)
                        canvas.drawString(inch, letter[1] - 0.5*inch, "Revision Books Report")
                        canvas.setFont("Helvetica", 10)
                        canvas.drawString(inch, letter[1] - 0.75*inch, f"Total Books: {len(book_export_data)}")
                        page_num = canvas.getPageNumber()
                        canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                        canvas.restoreState()

                    table_data = [["Book ID"]]
                    for book in book_export_data:
                        table_data.append([book["Book ID"]])

                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]))
                    elements.append(table)

                    doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            # Close button
            ttk.Button(display_window, text="Close", command=display_window.destroy, style="Action.TButton").pack(pady=5)

            display_window.grid_rowconfigure(1, weight=1)
            display_window.grid_columnconfigure(0, weight=1)

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display revision books: {tcl_err}")

    def view_students_with_revision_books_gui(self):
        try:
            students = self.app.view_students_with_revision_books()
            if not students:
                messagebox.showinfo("No Data", "No students with revision books found.")
                return

            display_window = tk.Toplevel(self.root)
            display_window.title("Students with Revision Books")
            display_window.geometry("800x600")  # Wider to accommodate extra column
            display_window.configure(bg="#f0f0f0")

            # Style configuration
            style = ttk.Style()
            style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=2)
            style.configure("CardLabel.TLabel", background="#ffffff", font=("Helvetica", 10))
            style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), background="#f0f0f0")
            style.configure("Search.TButton", font=("Helvetica", 10, "bold"))
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

            # Filter frame
            filter_frame = ttk.Frame(display_window, padding=10)
            filter_frame.pack(fill="x", pady=(0, 10))

            ttk.Label(filter_frame, text="Filter by Student ID:", style="Header.TLabel").grid(row=0, column=0, padx=5, pady=5)
            student_id_filter_entry = ttk.Entry(filter_frame)
            student_id_filter_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(filter_frame, text="Filter by Name:", style="Header.TLabel").grid(row=1, column=0, padx=5, pady=5)
            name_filter_entry = ttk.Entry(filter_frame)
            name_filter_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

            # Treeview frame
            result_frame = ttk.Frame(display_window)
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Treeview frame
            result_frame = ttk.Frame(display_window)
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            tree = ttk.Treeview(result_frame, columns=("Student ID", "Name", "Stream", "Book ID", "Due Date"), show="headings", height=20)
            tree.heading("Student ID", text="Student ID")
            tree.heading("Name", text="Name")
            tree.heading("Stream", text="Stream")
            tree.heading("Book ID", text="Book ID")
            tree.heading("Due Date", text="Due Date")
            tree.column("Student ID", width=100)
            tree.column("Name", width=200)
            tree.column("Stream", width=150)
            tree.column("Book ID", width=200)
            tree.column("Due Date", width=150)
            tree.configure(selectmode="browse")

            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)

            student_export_data = []

            def sort_students(student_list):
                def parse_student_key(student):
                    student_id, name, stream, book_id, borrowed_on, reminder_days = student
                    # Parse book_id for sorting
                    book_parts = book_id.split('/')
                    parsed_book = []
                    for part in book_parts:
                        if part.isdigit():
                            parsed_book.append(f"{int(part):03d}")
                        else:
                            parsed_book.append(part)
                    while len(parsed_book) < 5:
                        parsed_book.append('')
                    # Sort by student_id, name, stream, then book_id
                    return (student_id, name, stream, tuple(parsed_book))
                
                return sorted(student_list, key=parse_student_key)

            def populate_tree(student_list):
                for item in tree.get_children():
                    tree.delete(item)
                student_export_data.clear()

                sorted_students = sort_students(student_list)
                tree.insert("", tk.END, values=(f"Total Students: {len(sorted_students)}", "", "", "", ""))
                for student_id, name, stream, book_id, borrowed_on, reminder_days in sorted_students:
                    # Calculate due_date from borrowed_on
                    if reminder_days is not None and borrowed_on:
                        try:
                            borrowed_date = datetime.strptime(borrowed_on, "%Y-%m-%d")  # Adjust format if different
                            due_date = borrowed_date + timedelta(days=reminder_days)
                            due_date_str = due_date.strftime("%Y-%m-%d")  # Format as string
                        except ValueError as e:
                            self.logger.error(f"Invalid date format for borrowed_on: {borrowed_on}, error: {e}")
                            due_date_str = "Invalid Date"
                    else:
                        due_date_str = "N/A"
                    
                    tree.insert("", tk.END, values=(student_id, name, stream, book_id, due_date_str))
                    student_export_data.append({
                        "Student ID": student_id,
                        "Name": name,
                        "Stream": stream,
                        "Book ID": book_id,
                        "Due Date": due_date_str
                    })

            def apply_filter():
                student_id_filter = student_id_filter_entry.get().strip() or None
                name_filter = name_filter_entry.get().strip() or None
                filtered_students = self.app.view_students_with_revision_books(student_id_filter=student_id_filter, name_filter=name_filter)
                if filtered_students:
                    populate_tree(filtered_students)

            populate_tree(students)

            ttk.Button(filter_frame, text="Apply Filter", command=apply_filter, style="Search.TButton").grid(row=2, column=0, columnspan=2, pady=10)

            # Download frame
            download_frame = ttk.Frame(display_window)
            download_frame.pack(pady=5)

            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                if not student_export_data:
                    messagebox.showinfo("No Data", "No student data available to export.", parent=display_window)
                    return
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")]
                )
                if not file_path:
                    return
                if file_format == "Excel":
                    df = pd.DataFrame(student_export_data)
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)
                elif file_format == "PDF":
                    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                    elements = []
                
                    def add_page_header_footer(canvas, doc):
                        canvas.saveState()
                        canvas.setFont("Helvetica-Bold", 12)
                        canvas.drawString(inch, letter[1] - 0.5*inch, "Students with Revision Books Report")
                        canvas.setFont("Helvetica", 10)
                        canvas.drawString(inch, letter[1] - 0.75*inch, f"Total Students: {len(student_export_data)}")
                        page_num = canvas.getPageNumber()
                        canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                        canvas.restoreState()

                    table_data = [["Student ID", "Name", "Stream", "Book ID", "Due Date"]]
                    for student in student_export_data:
                        table_data.append([student["Student ID"], student["Name"], student["Stream"], student["Book ID"], student["Due Date"]])

                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]))
                    elements.append(table)

                    doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            ttk.Button(display_window, text="Close", command=display_window.destroy, style="Action.TButton").pack(pady=5)

            display_window.grid_rowconfigure(1, weight=1)
            display_window.grid_columnconfigure(0, weight=1)

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display students with revision books: {tcl_err}")


    def display_books_by_condition_gui(self):
        """Displays a report of books grouped by condition with filter and download options."""
        try:
            books_by_condition = self.app.get_books_by_condition_report()
            if not any(books_by_condition.values()):
                messagebox.showinfo("No Data", "No books found in the library.")
                return

            display_window = tk.Toplevel(self.root)
            display_window.title("Books by Condition Report")
            display_window.geometry("600x600")
            display_window.configure(bg="#f0f0f0")

            # Style configuration
            style = ttk.Style()
            style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=2)
            style.configure("CardLabel.TLabel", background="#ffffff", font=("Helvetica", 10))
            style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), background="#f0f0f0")
            style.configure("Search.TButton", font=("Helvetica", 10, "bold"))
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

            # Filter frame
            filter_frame = ttk.Frame(display_window, padding=10)
            filter_frame.pack(fill="x", pady=(0, 10))

            ttk.Label(filter_frame, text="Filter by Condition:", style="Header.TLabel").grid(row=0, column=0, padx=5, pady=5)
            condition_var = tk.StringVar(value="All")
            condition_menu = ttk.OptionMenu(filter_frame, condition_var, "All", "All", "New", "Good", "Damaged")
            condition_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            # Treeview frame
            result_frame = ttk.Frame(display_window)
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            tree = ttk.Treeview(result_frame, columns=("Condition", "Book ID"), show="headings", height=20)
            tree.heading("Condition", text="Condition")
            tree.heading("Book ID", text="Book ID")
            tree.column("Condition", width=150)
            tree.column("Book ID", width=400)
            tree.configure(selectmode="browse")

            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)

            book_export_data = []

            def sort_books(book_list):
                def parse_book_id(book_id):
                    parts = book_id.split('/')
                    parsed = []
                    for part in parts:
                        if part.isdigit():
                            parsed.append(f"{int(part):03d}")
                        else:
                            parsed.append(part)
                    while len(parsed) < 5:
                        parsed.append('')
                    return parsed
                return sorted(book_list, key=parse_book_id)

            def populate_tree(books_by_condition):
                for item in tree.get_children():
                    tree.delete(item)
                book_export_data.clear()

                total_books = sum(len(books) for books in books_by_condition.values())
                tree.insert("", tk.END, values=(f"Total Books: {total_books}", ""))
                for condition, books in books_by_condition.items():
                    if books:  # Only show conditions with books
                        sorted_books = sort_books(books)
                        tree.insert("", tk.END, values=(f"{condition} ({len(sorted_books)})", ""))
                        for book_id in sorted_books:
                            tree.insert("", tk.END, values=("", book_id))
                            book_export_data.append({"Condition": condition, "Book ID": book_id})

            def apply_filter():
                condition_filter = condition_var.get()
                filtered_books = self.app.get_books_by_condition_report(condition_filter if condition_filter != "All" else None)
                if any(filtered_books.values()):
                    populate_tree(filtered_books)

            populate_tree(books_by_condition)

            ttk.Button(filter_frame, text="Apply Filter", command=apply_filter, style="Search.TButton").grid(row=1, column=0, columnspan=2, pady=10)

            # Download frame
            download_frame = ttk.Frame(display_window)
            download_frame.pack(pady=5)

            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                if not book_export_data:
                    messagebox.showinfo("No Data", "No book data available to export.", parent=display_window)
                    return
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")]
                )
                if not file_path:
                    return
                if file_format == "Excel":
                    df = pd.DataFrame(book_export_data)
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)
                elif file_format == "PDF":
                    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                    elements = []
                
                    def add_page_header_footer(canvas, doc):
                        canvas.saveState()
                        canvas.setFont("Helvetica-Bold", 12)
                        canvas.drawString(inch, letter[1] - 0.5*inch, "Books by Condition Report")
                        canvas.setFont("Helvetica", 10)
                        canvas.drawString(inch, letter[1] - 0.75*inch, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        canvas.drawString(inch, letter[1] - 1*inch, f"Total Books: {len(book_export_data)}")
                        page_num = canvas.getPageNumber()
                        canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                        canvas.restoreState()

                    table_data = [["Condition", "Book ID"]]
                    for book in book_export_data:
                        table_data.append([book["Condition"], book["Book ID"]])

                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]))
                    elements.append(table)

                    doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            ttk.Button(display_window, text="Close", command=display_window.destroy, style="Action.TButton").pack(pady=5)

            display_window.grid_rowconfigure(1, weight=1)
            display_window.grid_columnconfigure(0, weight=1)

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display books by condition: {tcl_err}")
        except TypeError as type_err:
            messagebox.showerror("Display Error", f"Invalid books data: {type_err}")



    def generate_qr_code_gui(self):
        """Prompts for single or bulk QR code generation with preview for bulk."""
        try:
            qr_window = tk.Toplevel(self.root)
            qr_window.title("Generate QR Code")

            # Single QR generation frame
            single_frame = ttk.LabelFrame(qr_window, text="Single QR Code")
            single_frame.pack(pady=10, padx=10, fill="x")

            tk.Label(single_frame, text="Select Type:").pack(pady=5)
            type_var = tk.StringVar(value="Book")
            type_dropdown = ttk.Combobox(single_frame, textvariable=type_var, values=["Book", "Student", "Teacher"], state="readonly")
            type_dropdown.pack(pady=5)

            tk.Label(single_frame, text="Enter ID:").pack(pady=5)
            id_entry = tk.Entry(single_frame)
            id_entry.pack(pady=5)

            def generate_single():
                entity_type = type_var.get()
                entity_id = id_entry.get().strip()
                if not entity_id:
                    messagebox.showerror("Input Error", f"{entity_type} ID cannot be empty.")
                    return

                filename, qr_image = self.app.generate_qr_code(entity_type, entity_id)
                if not filename:
                    return

                save_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png")],
                    initialfile=filename
                )
                if save_path:
                    qr_image.save(save_path)
                    qr_display = tk.PhotoImage(file=save_path)
                    qr_label = tk.Label(single_frame, image=qr_display)
                    qr_label.image = qr_display
                    qr_label.pack(pady=10)
                    tk.Label(single_frame, text=f"QR Code saved as: {save_path}").pack(pady=5)
                    messagebox.showinfo("Success", f"QR code generated and saved as '{save_path}'.")
                else:
                    messagebox.showinfo("Cancelled", "QR code generation cancelled.")

            tk.Button(single_frame, text="Generate Single QR", command=generate_single, bg="#FF9800", fg="white").pack(pady=10)

            # Bulk QR generation frame
            bulk_frame = ttk.LabelFrame(qr_window, text="Bulk QR Codes for Books")
            bulk_frame.pack(pady=10, padx=10, fill="x")

            tk.Label(bulk_frame, text="Class (e.g., KLB):").pack(pady=5)
            class_entry = tk.Entry(bulk_frame)
            class_entry.pack(pady=5)

            tk.Label(bulk_frame, text="Subject (e.g., CM):").pack(pady=5)
            subject_entry = tk.Entry(bulk_frame)
            subject_entry.pack(pady=5)

            tk.Label(bulk_frame, text="Form/Grade (e.g., 4):").pack(pady=5)
            form_entry = tk.Entry(bulk_frame)
            form_entry.pack(pady=5)

            tk.Label(bulk_frame, text="Number of Books:").pack(pady=5)
            number_entry = tk.Entry(bulk_frame)
            number_entry.pack(pady=5)

            tk.Label(bulk_frame, text="Year (e.g., 2026):").pack(pady=5)
            year_entry = tk.Entry(bulk_frame)
            year_entry.pack(pady=5)

            def generate_bulk_with_preview():  
                book_class = class_entry.get().strip()
                subject = subject_entry.get().strip()
                form = form_entry.get().strip()
                number_of_books = number_entry.get().strip()
                year = year_entry.get().strip()
                if not all([book_class, subject, form, number_of_books, year]):
                    messagebox.showerror("Input Error", "All fields are required for bulk generation.")
                    return

                # Generate preview images
                preview_images = self.app.generate_bulk_book_qrcodes_pdf(book_class, subject, form, number_of_books, year, ".", save_directly=False)
                if not preview_images:
                    return

                # Show preview window
                preview_window = tk.Toplevel(self.root)
                preview_window.title("Bulk QR Codes Preview")

                canvas = tk.Canvas(preview_window)  # Use tk.Canvas
                scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=canvas.yview)
                scrollable_frame = ttk.Frame(canvas)

                canvas.configure(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True)
                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

                 
                image_refs = []  # Keep references to avoid garbage collection
                y_pos = 0
                for img in preview_images:
                    tk_img = ImageTk.PhotoImage(img)  # Convert PIL Image to Tkinter PhotoImage
                    label = tk.Label(scrollable_frame, image=tk_img)
                    label.place(x=0, y=y_pos)
                    image_refs.append(tk_img)
                    y_pos += tk_img.height()

                canvas.config(scrollregion=(0, 0, tk_img.width(), y_pos))

                def save_bulk():
                    output_dir = filedialog.askdirectory(title="Select Output Directory")
                    if not output_dir:
                        messagebox.showinfo("Cancelled", "Bulk QR code generation cancelled.")
                        return
                    pdf_filename = self.app.generate_bulk_book_qrcodes_pdf(book_class, subject, form, number_of_books, year, output_dir, save_directly=True)
                    if pdf_filename:
                        messagebox.showinfo("Success", f"Bulk QR codes saved as '{pdf_filename}'.")
                        preview_window.destroy()
                        qr_window.destroy()  # Assumes qr_window is defined in outer scope

                button_frame = ttk.Frame(preview_window)
                button_frame.pack(pady=10)
                tk.Button(button_frame, text="Save", command=save_bulk, bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)
                tk.Button(button_frame, text="Cancel", command=preview_window.destroy, bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)
                # Clean up temporary file
                if os.path.exists("temp_preview.png"):
                    os.remove("temp_preview.png")

            tk.Button(bulk_frame, text="Preview Bulk QR Codes", command=generate_bulk_with_preview, bg="#FF9800", fg="white").pack(pady=10)
            tk.Button(qr_window, text="Close", command=qr_window.destroy, bg="#FF9800", fg="white").pack(pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to generate or display QR code: {tcl_err}")
        except FileNotFoundError as fnf_err:
            messagebox.showerror("File Error", f"Failed to load QR code image: {fnf_err}")


    def bulk_borrow_gui(self):
        bulk_window = tk.Toplevel(self.root)
        bulk_window.title("Bulk Borrow Books")

        method_var = tk.StringVar(value="Excel")
        ttk.Label(bulk_window, text="Choose Method:").pack(pady=5)
        ttk.Radiobutton(bulk_window, text="Upload Excel", variable=method_var, value="Excel").pack()
        ttk.Radiobutton(bulk_window, text="Manual Selection", variable=method_var, value="Manual").pack()

        excel_frame = ttk.Frame(bulk_window)
        excel_frame.pack(pady=10)
        def upload_excel():
            file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
            if file_path:
                results = self.app.bulk_borrow_books(file_path=file_path)
                show_borrow_results(results)
                bulk_window.destroy()

        ttk.Button(excel_frame, text="Upload Excel File", command=upload_excel).pack()

        manual_frame = ttk.Frame(bulk_window)
        manual_frame.pack(pady=10, fill="both", expand=True)

        ttk.Label(manual_frame, text="User ID:").pack(pady=5)
        user_id_entry = ttk.Entry(manual_frame)
        user_id_entry.pack(pady=5)

        ttk.Label(manual_frame, text="Entity Type:").pack(pady=5)
        entity_type_var = tk.StringVar(value="Student")
        ttk.Combobox(manual_frame, textvariable=entity_type_var, values=["Student", "Teacher"], state="readonly").pack(pady=5)

        # Treeview for book selection
        book_frame = ttk.Frame(manual_frame)
        book_frame.pack(pady=10, fill="both", expand=True)
        tree = ttk.Treeview(book_frame, columns=("Book ID", "Condition"), show="headings", selectmode="extended")
        tree.heading("Book ID", text="Book ID")
        tree.heading("Condition", text="Condition")
        tree.column("Book ID", width=150)
        tree.column("Condition", width=100)
        tree.pack(fill="both", expand=True)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(book_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Populate Treeview with books
        books = self.app.get_all_books()
        condition_vars = {}
        for book_id in books:
            cond_var = tk.StringVar(value="New")
            iid = tree.insert("", "end", values=(book_id, cond_var.get()))
            condition_vars[iid] = cond_var

        # Bind double-click to edit condition
        def update_condition(event):
            item = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            if not item or column != "#2":
                return

            cond_var = condition_vars.get(item)
            if not cond_var:
                return

            bbox = tree.bbox(item, column="Condition")
            if not bbox:
                return

            x, y, width, height = bbox
            edit_combo = ttk.Combobox(book_frame, textvariable=cond_var, values=["New", "Good", "Damaged"], state="readonly", width=10)
            edit_combo.place(x=x, y=y, width=width, height=height)
            edit_combo.focus_set()

            def save_and_destroy(event=None):
                tree.set(item, "Condition", cond_var.get())
                edit_combo.destroy()

            edit_combo.bind("<Return>", save_and_destroy)
            edit_combo.bind("<FocusOut>", save_and_destroy)

        tree.bind("<Double-1>", update_condition)

        def show_borrow_results(results):
            """Display feedback based on borrowing results."""
            msg = []
            if results["success"]:
                msg.append(f"Successfully borrowed {len(results['success'])} book(s): {', '.join(results['success'])}")
            if results["already_borrowed"]:
                msg.append(f"{len(results['already_borrowed'])} book(s) already borrowed: {', '.join(results['already_borrowed'])}")
            if results["errors"]:
                msg.append(f"Errors for {len(results['errors'])} book(s): {', '.join([f'{b} ({e})' for b, e in results['errors']])}")
            
            if msg:
                messagebox.showinfo("Borrowing Results", "\n".join(msg), parent=bulk_window)
            else:
                messagebox.showinfo("Borrowing Results", "No books processed.", parent=bulk_window)

        def process_manual():
            user_id = user_id_entry.get().strip()
            entity_type = entity_type_var.get()
            if not user_id:
                messagebox.showerror("Input Error", "User ID cannot be empty.", parent=bulk_window)
                return
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showerror("Input Error", "No books selected.", parent=bulk_window)
                return
            
            borrowings = [(user_id, tree.item(item, "values")[0], entity_type, tree.item(item, "values")[1])
                          for item in selected_items]
            results = self.app.bulk_borrow_books(borrowings=borrowings)
            show_borrow_results(results)
            bulk_window.destroy()

        ttk.Button(manual_frame, text="Borrow Selected", command=process_manual).pack(pady=10)
        ttk.Button(bulk_window, text="Close", command=bulk_window.destroy).pack(pady=10)

    def bulk_return_gui(self):
        """GUI for bulk returning via Excel upload or multi-select with Treeview."""
        try:
            bulk_window = tk.Toplevel(self.root)
            bulk_window.title("Bulk Return Books")

            ttk.Label(bulk_window, text="Choose Method:").pack(pady=5)
            method_var = tk.StringVar(value="Excel")
            ttk.Radiobutton(bulk_window, text="Upload Excel", variable=method_var, value="Excel").pack()
            ttk.Radiobutton(bulk_window, text="Manual Selection", variable=method_var, value="Manual").pack()

            # Excel upload frame
            excel_frame = ttk.Frame(bulk_window)
            excel_frame.pack(pady=10)

            def upload_excel():
                file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
                if file_path:
                    self.app.bulk_return_books(file_path=file_path)
                    bulk_window.destroy()

            ttk.Button(excel_frame, text="Upload Excel File", command=upload_excel).pack()

            # Manual selection frame
            manual_frame = ttk.Frame(bulk_window)
            manual_frame.pack(pady=10, fill="both", expand=True)

            ttk.Label(manual_frame, text="User ID:").pack(pady=5)
            user_id_entry = ttk.Entry(manual_frame)
            user_id_entry.pack(pady=5)

            ttk.Label(manual_frame, text="Entity Type:").pack(pady=5)
            entity_type_var = tk.StringVar(value="Student")
            ttk.Combobox(manual_frame, textvariable=entity_type_var, values=["Student", "Teacher"], state="readonly").pack(pady=5)

            # Treeview for book selection
            book_frame = ttk.Frame(manual_frame)
            book_frame.pack(pady=10, fill="both", expand=True)
            tree = ttk.Treeview(book_frame, columns=("Book ID", "Borrower", "Condition"), show="headings", selectmode="extended")
            tree.heading("Book ID", text="Book ID")
            tree.heading("Borrower", text="Borrower")
            tree.heading("Condition", text="Condition")
            tree.column("Book ID", width=100)
            tree.column("Borrower", width=150)
            tree.column("Condition", width=100)
            tree.pack(fill="both", expand=True)

            # Scrollbar for Treeview
            scrollbar = ttk.Scrollbar(book_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

            # Populate Treeview with unreturned books
            unreturned_books = self.app.get_unreturned_books()
            if unreturned_books is None:  # Defensive check, though now unnecessary with fixed get_unreturned_books
                unreturned_books = {"students": [], "teachers": []}

            condition_vars = {}  # Use Treeview item ID as key
            # Process students
            for student_book in unreturned_books.get("students", []):
                book_id = student_book["book_id"]
                borrower = f"Student: {student_book['student_name']} (Stream: {student_book.get('stream', 'N/A')})"
                condition = student_book.get("book_condition", "Good")
                cond_var = tk.StringVar(value=condition)
                iid = tree.insert("", "end", values=(book_id, borrower, cond_var.get()))
                condition_vars[iid] = cond_var

            # Process teachers
            for teacher_book in unreturned_books.get("teachers", []):
                book_id = teacher_book["book_id"]
                borrower = f"Teacher: {teacher_book['teacher_name']}"
                condition = teacher_book.get("book_condition", "Good")
                cond_var = tk.StringVar(value=condition)
                iid = tree.insert("", "end", values=(book_id, borrower, cond_var.get()))
                condition_vars[iid] = cond_var

            # Bind double-click to edit condition
            def update_condition(event):
                item = tree.identify_row(event.y)
                column = tree.identify_column(event.x)
                if not item or column != "#3":  # #3 is the "Condition" column
                    return

                cond_var = condition_vars.get(item)
                if not cond_var:  # Safety check
                    return

                bbox = tree.bbox(item, column="Condition")
                if not bbox:
                    return

                x, y, width, height = bbox
                edit_combo = ttk.Combobox(book_frame, textvariable=cond_var, values=["New", "Good", "Damaged"], state="readonly", width=10)
                edit_combo.place(x=x, y=y, width=width, height=height)
                edit_combo.focus_set()

                def save_and_destroy(event=None):
                    tree.set(item, "Condition", cond_var.get())
                    edit_combo.destroy()

                edit_combo.bind("<Return>", save_and_destroy)
                edit_combo.bind("<FocusOut>", save_and_destroy)

            tree.bind("<Double-1>", update_condition)

            def process_manual():
                user_id = user_id_entry.get().strip()
                entity_type = entity_type_var.get()
                if not user_id:
                    messagebox.showerror("Input Error", "User ID cannot be empty.")
                    return
                selected_items = tree.selection()
                returns = [(user_id, tree.item(item, "values")[0], entity_type, tree.item(item, "values")[2])
                            for item in selected_items]
                if not returns:
                    messagebox.showerror("Input Error", "No books selected.")
                    return
                self.app.bulk_return_books(returns=returns)
                bulk_window.destroy()

            ttk.Button(manual_frame, text="Return Selected", command=process_manual).pack(pady=10)
            ttk.Button(bulk_window, text="Close", command=bulk_window.destroy).pack(pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create bulk return window: {tcl_err}")



    def manage_categories_gui(self):
        """GUI to add tags to existing books with user feedback."""
        try:
            manage_window = tk.Toplevel(self.root)
            manage_window.title("Manage Book Categories")

            ttk.Label(manage_window, text="Book ID:").grid(row=0, column=0, padx=5, pady=5)
            book_id_entry = ttk.Entry(manage_window)
            book_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(manage_window, text="Tags (comma-separated):").grid(row=1, column=0, padx=5, pady=5)
            tags_entry = ttk.Entry(manage_window)
            tags_entry.grid(row=1, column=1, padx=5, pady=5)

            def add_tags():
                book_id = book_id_entry.get().strip()
                tags = tags_entry.get().strip()
                if not book_id:
                    messagebox.showerror("Input Error", "Book ID cannot be empty.", parent=manage_window)
                    return
                if not tags:
                    messagebox.showerror("Input Error", "Tags cannot be empty.", parent=manage_window)
                    return
                if messagebox.askyesno("Confirm", f"Add tags '{tags}' to Book ID '{book_id}'?", parent=manage_window):
                    try:
                        result = self.app.tag_book(book_id, tags)
                        if result:  # Assuming True indicates success
                            messagebox.showinfo("Success", f"Tags '{tags}' added to Book ID '{book_id}' successfully!", parent=manage_window)
                        else:
                            messagebox.showwarning("Warning", f"Failed to add tags to Book ID '{book_id}'. Book may not exist or tags unchanged.", parent=manage_window)
                        manage_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to add tags: {e}", parent=manage_window)

            ttk.Button(manage_window, text="Add Tags", command=add_tags).grid(row=2, column=0, columnspan=2, pady=10)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create manage categories window: {tcl_err}")



    def export_data_gui(self):
        """GUI for exporting library data with a progress bar."""
        try:
            export_window = tk.Toplevel(self.root)
            export_window.title("Export Library Data")
            export_window.geometry("300x200")

            ttk.Label(export_window, text="Select Format:").pack(pady=5)
            format_var = tk.StringVar(value="CSV")
            ttk.Radiobutton(export_window, text="CSV", variable=format_var, value="CSV").pack()
            ttk.Radiobutton(export_window, text="JSON", variable=format_var, value="JSON").pack()

            progress = ttk.Progressbar(export_window, length=200, mode="determinate")
            progress.pack(pady=10)
            status_label = ttk.Label(export_window, text="Ready to export")
            status_label.pack(pady=5)

            def update_progress(value):
                progress["value"] = value
                status_label.config(text=f"Exporting: {int(value)}%")
                export_window.update_idletasks()

            def export_with_prompt():
                output_dir = filedialog.askdirectory(title="Select Output Directory")
                if output_dir:
                    format = format_var.get().lower()
                    if self.app.export_library(output_dir, format, update_progress):
                        export_window.destroy()

            ttk.Button(export_window, text="Export", command=export_with_prompt).pack(pady=5)
            ttk.Button(export_window, text="Cancel", command=export_window.destroy).pack(pady=5)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create export data window: {tcl_err}")

    def import_data_gui(self):
        """GUI for importing library data with a progress bar and incremental option."""
        try:
            import_window = tk.Toplevel(self.root)
            import_window.title("Import Library Data")
            import_window.geometry("300x250")

            ttk.Label(import_window, text="Select Format:").pack(pady=5)
            format_var = tk.StringVar(value="CSV")
            ttk.Radiobutton(import_window, text="CSV (Directory)", variable=format_var, value="CSV").pack()
            ttk.Radiobutton(import_window, text="JSON (Single File)", variable=format_var, value="JSON").pack()

            incremental_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(import_window, text="Incremental Import (Merge with existing data)", variable=incremental_var).pack(pady=5)

            progress = ttk.Progressbar(import_window, length=200, mode="determinate")
            progress.pack(pady=10)
            status_label = ttk.Label(import_window, text="Ready to import")
            status_label.pack(pady=5)

            def update_progress(value):
                progress["value"] = value
                status_label.config(text=f"Importing: {int(value)}%")
                import_window.update_idletasks()

            def import_with_prompt():
                format = format_var.get().lower()
                incremental = incremental_var.get()
                if format == "csv":
                    directory = filedialog.askdirectory(title="Select Directory with CSV Files")
                    if directory and messagebox.askyesno("Confirm", f"This will {'merge with' if incremental else 'overwrite'} existing data. Proceed?"):
                        self.app.import_library(directory=directory, format="csv", incremental=incremental, progress_callback=update_progress)
                        import_window.destroy()
                elif format == "json":
                    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Select JSON File")
                    if file_path and messagebox.askyesno("Confirm", f"This will {'merge with' if incremental else 'overwrite'} existing data. Proceed?"):
                        self.app.import_library(file_path=file_path, format="json", incremental=incremental, progress_callback=update_progress)
                        import_window.destroy()

            ttk.Button(import_window, text="Import", command=import_with_prompt).pack(pady=5)
            ttk.Button(import_window, text="Cancel", command=import_window.destroy).pack(pady=5)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create import data window: {tcl_err}")



    def open_qr_add_book_gui(self):
        """Opens the QR code book adding GUI."""
        try:
            self.app.open_qr_add_book_gui()
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Failed to open QR add book GUI: {attr_err}")

    def open_qr_borrow_book_gui(self):
        """Opens the QR code borrowing GUI."""
        try:
            self.app.open_qr_borrow_book_gui()
        except AttributeError as attr_err:
            messagebox.showerror("GUI Error", f"Failed to open QR borrow book GUI: {attr_err}")

    
   
    def reminder_settings_gui(self):
        """GUI to customize reminder settings with a test option."""
        try:
            settings_window = tk.Toplevel(self.root)
            settings_window.title("Reminder Settings")

            ttk.Label(settings_window, text="Reminder Frequency:").grid(row=0, column=0, padx=5, pady=5)
            frequency_var = tk.StringVar(value="daily")
            ttk.Combobox(settings_window, textvariable=frequency_var, values=["daily", "weekly", "disabled"], state="readonly").grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(settings_window, text="Enable Sound:").grid(row=1, column=0, padx=5, pady=5)
            sound_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(settings_window, variable=sound_var, onvalue=True, offvalue=False).grid(row=1, column=1, padx=5, pady=5)

            # Load current settings
            current_user = self.app.current_user if hasattr(self.app, 'current_user') else "default_user"  # Fallback if not set
            current_freq, current_sound = self.app.get_reminder_settings(current_user)
            frequency_var.set(current_freq)
            sound_var.set(current_sound)

            def save_settings():
                if messagebox.askyesno("Confirm", "Save reminder settings?"):
                    try:
                        self.app.save_reminder_settings(current_user, frequency_var.get(), sound_var.get())
                        messagebox.showinfo("Success", "Reminder settings saved successfully!")
                        settings_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

            def test_reminder():
                # Temporarily save current settings to test them
                self.app.save_reminder_settings(current_user, frequency_var.get(), sound_var.get())
                reminder_result = self.app.check_reminders(current_user) 
                if reminder_result:
                    messagebox.showinfo("Test Reminder", reminder_result)
                else:
                    messagebox.showinfo("Test Reminder", "No overdue revision books found for this user.")

            button_frame = ttk.Frame(settings_window)
            button_frame.grid(row=2, column=0, columnspan=2, pady=10)
            ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Test Reminder", command=test_reminder).pack(side=tk.LEFT, padx=5)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to create reminder settings window: {tcl_err}")

     
    def _delete_entity_gui(self, entity_type, id_label):
        """Creates a GUI for deleting an entity with a single ID."""
        delete_window = tk.Toplevel(self.root)
        delete_window.title(f"Delete {entity_type.capitalize()}")
        delete_window.geometry("300x150")

        ttk.Label(delete_window, text=f"{id_label}:").pack(pady=5)
        id_entry = ttk.Entry(delete_window)
        id_entry.pack(pady=5)

        def confirm_delete():
            identifier = id_entry.get().strip()
            if not identifier:
                messagebox.showerror("Input Error", f"Please enter a {id_label}.")
                return
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete this {entity_type}?"):
                self.app.delete_from_system(entity_type, identifier)
                delete_window.destroy()

        ttk.Button(delete_window, text="Delete", command=confirm_delete).pack(pady=10)
        ttk.Button(delete_window, text="Cancel", command=delete_window.destroy).pack(pady=5)

    def _delete_borrow_gui(self, entity_type, id1_label, id2_label):
        """Creates a GUI for deleting a borrowed book with two IDs."""
        delete_window = tk.Toplevel(self.root)
        delete_window.title(f"Delete {entity_type.replace('_', ' ').capitalize()}")
        delete_window.geometry("300x200")

        ttk.Label(delete_window, text=f"{id1_label}:").pack(pady=5)
        id1_entry = ttk.Entry(delete_window)
        id1_entry.pack(pady=5)

        ttk.Label(delete_window, text=f"{id2_label}:").pack(pady=5)
        id2_entry = ttk.Entry(delete_window)
        id2_entry.pack(pady=5)

        def confirm_delete():
            id1 = id1_entry.get().strip()
            id2 = id2_entry.get().strip()
            if not id1 or not id2:
                messagebox.showerror("Input Error", f"Please enter both {id1_label} and {id2_label}.")
                return
            identifier = (id1, id2)
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete this {entity_type.replace('_', ' ')}?"):
                self.app.delete_from_system(entity_type, identifier)
                delete_window.destroy()

        ttk.Button(delete_window, text="Delete", command=confirm_delete).pack(pady=10)
        ttk.Button(delete_window, text="Cancel", command=delete_window.destroy).pack(pady=5)

    
    def search_book_borrow_gui(self):
        """Creates a GUI to search for book borrowing details."""
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Book Borrow Details")
        search_window.geometry("300x150")

        ttk.Label(search_window, text="Book ID:").pack(pady=5)
        book_id_entry = ttk.Entry(search_window)
        book_id_entry.pack(pady=5)

        def perform_search():
            book_id = book_id_entry.get().strip()
            if not book_id:
                messagebox.showerror("Input Error", "Please enter a Book ID.")
                return
            self.app.search_book_borrow_details(book_id)
            # Keep window open for multiple searches; close manually with Cancel

        ttk.Button(search_window, text="Search", command=perform_search).pack(pady=10)
        ttk.Button(search_window, text="Cancel", command=search_window.destroy).pack(pady=5)
    

    # New GUI methods for furniture management
    def assign_locker_gui(self):
        """GUI for assigning a locker to a student."""
        window = tk.Toplevel()
        window.title("Assign Locker")
        window.geometry("300x200")

        ttk.Label(window, text="Student ID:").pack(pady=5)
        student_id_entry = ttk.Entry(window)
        student_id_entry.pack(pady=5)

        ttk.Label(window, text="Locker ID:").pack(pady=5)
        locker_id_entry = ttk.Entry(window)
        locker_id_entry.pack(pady=5)

        def submit():
            student_id = student_id_entry.get()
            locker_id = locker_id_entry.get()
            if self.app.logic.assign_locker(student_id, locker_id):
                messagebox.showinfo("Success", f"Locker {locker_id} assigned to {student_id}")
                window.destroy()
            else:
                messagebox.showerror("Error", "Failed to assign locker")

        ttk.Button(window, text="Assign", command=submit).pack(pady=10)

    def assign_chair_gui(self):
        """GUI for assigning a chair to a student."""
        window = tk.Toplevel()
        window.title("Assign Chair")
        window.geometry("300x200")

        ttk.Label(window, text="Student ID:").pack(pady=5)
        student_id_entry = ttk.Entry(window)
        student_id_entry.pack(pady=5)

        ttk.Label(window, text="Chair ID:").pack(pady=5)
        chair_id_entry = ttk.Entry(window)
        chair_id_entry.pack(pady=5)

        def submit():
            student_id = student_id_entry.get()
            chair_id = chair_id_entry.get()
            if self.app.logic.assign_chair(student_id, chair_id):
                messagebox.showinfo("Success", f"Chair {chair_id} assigned to {student_id}")
                window.destroy()
            else:
                messagebox.showerror("Error", "Failed to assign chair")

        ttk.Button(window, text="Assign", command=submit).pack(pady=10)

    def _display_furniture_status_gui(self, furniture_type, title, output_filename):
        """Helper function to display furniture status (lockers or chairs) in a GUI with export options."""
        try:
            # Fetch the status data
            status = self.app.logic.get_furniture_status(furniture_type)
            if not status:
                messagebox.showerror("Error", f"Failed to fetch {furniture_type} status")
                return

            # Create the display window
            display_window = tk.Toplevel(self.root)
            display_window.title(title)
            display_window.geometry("800x600")
            display_window.configure(bg="#f0f0f0")

            # Treeview with scrollbars
            tree_frame = ttk.Frame(display_window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

            columns = ("ID", "Location", "Condition", "Assigned", "Student ID", "Name")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
            tree.heading("ID", text=f"{furniture_type.capitalize()} ID")
            tree.heading("Location", text="Location")
            tree.heading("Condition", text="Condition")
            tree.heading("Assigned", text="Assigned")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Name", text="Name")
            tree.column("ID", width=100, anchor="center")
            tree.column("Location", width=100, anchor="center")
            tree.column("Condition", width=100, anchor="center")
            tree.column("Assigned", width=100, anchor="center")
            tree.column("Student ID", width=100, anchor="center")
            tree.column("Name", width=150, anchor="center")

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            hsb.pack(side="bottom", fill="x")

            # Populate Treeview
            for item in status:
                tree.insert("", "end", values=(
                    item["locker_id"] if furniture_type == "lockers" else item["chair_id"],
                    item["location"],
                    item["cond"],
                    "Yes" if item["assigned"] else "No",
                    item["student_id"] if item["assigned"] else "N/A",
                    item["student_name"] if item["assigned"] else "N/A"  
                ))

            # Download frame
            download_frame = ttk.Frame(display_window)
            download_frame.pack(pady=5)

            # Download format dropdown
            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")],
                    initialfile=output_filename
                )
                if not file_path:
                    return

                try:
                    if file_format == "Excel":
                        # Prepare data for Excel
                        df = pd.DataFrame(status)
                        df = df.rename(columns={
                            "locker_id": "Locker ID" if furniture_type == "lockers" else "Chair ID",
                            "chair_id": "Chair ID" if furniture_type == "chairs" else "Locker ID",
                            "location": "Location",
                            "cond": "Condition",
                            "assigned": "Assigned",
                            "student_id": "Student ID",
                            "student_name": "Name"
                        })
                        # Adjust "Assigned" column for display
                        df["Assigned"] = df["Assigned"].apply(lambda x: "Yes" if x else "No")
                        df["Student ID"] = df.apply(lambda row: row["Student ID"] if row["Assigned"] == "Yes" else "N/A", axis=1)
                        df["Name"] = df.apply(lambda row: row["Name"] if row["Assigned"] == "Yes" else "N/A", axis=1)
                        df.to_excel(file_path, index=False)
                        messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

                    elif file_format == "PDF":
                        # Generate PDF with repeating headers
                        doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                        elements = []
                        styles = getSampleStyleSheet()

                        # Define page header and footer
                        def add_page_header_footer(canvas, doc):
                            canvas.saveState()
                            # Header
                            canvas.setFont("Helvetica-Bold", 12)
                            canvas.drawString(inch, letter[1] - 0.5*inch, f"{furniture_type.capitalize()} Status Report")
                            canvas.setFont("Helvetica", 10)
                            canvas.drawString(inch, letter[1] - 0.75*inch, f"Total {furniture_type.capitalize()}: {len(status)}")
                            # Footer (page number)
                            canvas.setFont("Helvetica", 8)
                            page_num = canvas.getPageNumber()
                            canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                            canvas.restoreState()

                        # Table data
                        table_data = [[
                            f"{furniture_type.capitalize()} ID", "Location", "Condition", 
                            "Assigned", "Student ID", "Name"
                        ]]
                        for item in status:
                            table_data.append([
                                item["locker_id"] if furniture_type == "lockers" else item["chair_id"],
                                item["location"],
                                item["cond"],
                                "Yes" if item["assigned"] else "No",
                                item["student_id"] if item["assigned"] else "N/A",
                                item["student_name"] if item["assigned"] else "N/A"
                            ])

                        # Create table with repeating headers
                        table = LongTable(table_data)
                        table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ]))
                        elements.append(table)

                        # Build PDF with page header and footer
                        doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                        messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export data: {e}", parent=display_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            # Close button
            ttk.Button(display_window, text="Close", command=display_window.destroy, style="Action.TButton").pack(pady=5)

            # Style for button
            style = ttk.Style()
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5, background="#4CAF50", foreground="white")

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display {furniture_type} status: {tcl_err}")


    def view_locker_status_gui(self):
        """GUI to view locker status with preview and export options."""
        self._display_furniture_status_gui("lockers", "Locker Status", "locker_status.xlsx")

    def view_chair_status_gui(self):
        """GUI to view chair status with preview and export options."""
        self._display_furniture_status_gui("chairs", "Chair Status", "chair_status.xlsx")


    def report_damaged_locker_gui(self):
        """GUI to report a damaged locker."""
        window = tk.Toplevel()
        window.title("Report Damaged Locker")
        window.geometry("300x200")

        ttk.Label(window, text="Locker ID:").pack(pady=5)
        locker_id_entry = ttk.Entry(window)
        locker_id_entry.pack(pady=5)

        condition_var = tk.StringVar(value="Damaged")
        ttk.Radiobutton(window, text="Damaged", variable=condition_var, value="Damaged").pack(pady=5)
        ttk.Radiobutton(window, text="Needs Repair", variable=condition_var, value="Needs Repair").pack(pady=5)

        def submit():
            locker_id = locker_id_entry.get().strip()
            condition = condition_var.get()
            if not locker_id:
                messagebox.showerror("Error", "Locker ID cannot be empty")
            elif self.app.logic.report_damaged_furniture("lockers", locker_id, condition):
                messagebox.showinfo("Success", f"Locker {locker_id} reported as {condition}")
                window.destroy()
            else:
                messagebox.showerror("Error", f"Failed to report locker {locker_id}. Check if it exists.")

        ttk.Button(window, text="Report", command=submit).pack(pady=10)

    def report_damaged_chair_gui(self):
        """GUI to report a damaged chair."""
        window = tk.Toplevel()
        window.title("Report Damaged Chair")
        window.geometry("300x200")

        ttk.Label(window, text="Chair ID:").pack(pady=5)
        chair_id_entry = ttk.Entry(window)
        chair_id_entry.pack(pady=5)

        condition_var = tk.StringVar(value="Damaged")
        ttk.Radiobutton(window, text="Damaged", variable=condition_var, value="Damaged").pack(pady=5)
        ttk.Radiobutton(window, text="Needs Repair", variable=condition_var, value="Needs Repair").pack(pady=5)

        def submit():
            chair_id = chair_id_entry.get().strip()
            condition = condition_var.get()
            if not chair_id:
                messagebox.showerror("Error", "Chair ID cannot be empty")
            elif self.app.logic.report_damaged_furniture("chairs", chair_id, condition):
                messagebox.showinfo("Success", f"Chair {chair_id} reported as {condition}")
                window.destroy()
            else:
                messagebox.showerror("Error", f"Failed to report chair {chair_id}. Check if it exists.")

        ttk.Button(window, text="Report", command=submit).pack(pady=10)

  
    def generate_furniture_ids_gui(self):
        """GUI to generate and print simple furniture IDs (e.g., LKR/R/001 or CHR/G/002)."""
        window = tk.Toplevel()
        window.title("Generate Furniture IDs")
        window.geometry("400x300")  # Adjusted size for fewer fields

        ttk.Label(window, text="Furniture Type:").pack(pady=5)
        type_var = tk.StringVar(value="LKR")
        ttk.Radiobutton(window, text="Locker (LKR)", variable=type_var, value="LKR").pack(pady=5)
        ttk.Radiobutton(window, text="Chair (CHR)", variable=type_var, value="CHR").pack(pady=5)

        ttk.Label(window, text="Color Code (e.g., R for Red, G for Green):").pack(pady=5)
        color_entry = ttk.Entry(window)
        color_entry.pack(pady=5)

        ttk.Label(window, text="Count (e.g., 3 for 001 to 003):").pack(pady=5)
        count_entry = ttk.Entry(window)
        count_entry.pack(pady=5)

        def submit():
            try:
                furniture_type = type_var.get()
                color = color_entry.get().strip().upper()
                count = int(count_entry.get() or 1)

                if not color:
                    messagebox.showerror("Input Error", "Color code cannot be empty.", parent=window)
                    return
                if len(color) > 1:
                    messagebox.showerror("Input Error", "Color code must be a single character (e.g., R or G).", parent=window)
                    return
                if count <= 0:
                    messagebox.showerror("Input Error", "Count must be a positive number.", parent=window)
                    return

                # Generate IDs and add to database
                success, result = self.app.logic.add_furniture(furniture_type, None, None, None, color, "Good", count)
                if success:
                    ids = result  # result is the list of IDs
                    if ids:
                        filename = f"{furniture_type}_ids.txt"
                        with open(filename, "w") as f:
                            f.write("\n".join(ids))
                        messagebox.showinfo("Success", f"Generated {len(ids)} IDs and saved to {filename}", parent=window)
                        window.destroy()
                    else:
                        messagebox.showwarning("Warning", "No IDs generated, but operation succeeded.", parent=window)
                else:
                    messagebox.showerror("Error", f"Failed to generate IDs: {result}", parent=window)
            except ValueError:
                messagebox.showerror("Input Error", "Count must be a valid number.", parent=window)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate IDs: {e}", parent=window)

        ttk.Button(window, text="Generate and Save", command=submit).pack(pady=10)

    def search_locker_gui(self):
        """GUI to search for a locker by ID and display student details."""
        window = tk.Toplevel()
        window.title("Search Locker")
        window.geometry("400x350")  # Increased height for extra field

        ttk.Label(window, text="Enter Locker ID:").pack(pady=5)
        locker_id_entry = ttk.Entry(window)
        locker_id_entry.pack(pady=5)

        result_frame = ttk.Frame(window)
        result_frame.pack(pady=10, fill="both", expand=True)

        def search():
            for widget in result_frame.winfo_children():
                widget.destroy()

            locker_id = locker_id_entry.get().strip()
            if not locker_id:
                messagebox.showerror("Error", "Locker ID cannot be empty")
                return

            details = self.app.logic.search_furniture_by_id("lockers", locker_id)
            if details:
                if details["assigned"] == 0 or details["student_id"] is None:
                    ttk.Label(result_frame, text=f"Locker {locker_id} is unassigned").pack(pady=5)
                else:
                    ttk.Label(result_frame, text=f"Locker ID: {details['locker_id']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Location: {details['location']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Form: {details['form']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Color: {details['color']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Condition: {details['cond']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Student ID: {details['student_id']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Student Name: {details['name']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Stream: {details['stream'] or 'N/A'}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Assigned Date: {details['assigned_date']}").pack(pady=5)
            else:
                ttk.Label(result_frame, text=f"No locker found with ID {locker_id}").pack(pady=5)

        ttk.Button(window, text="Search", command=search).pack(pady=10)

    def search_chair_gui(self):
        """GUI to search for a chair by ID and display student details."""
        window = tk.Toplevel()
        window.title("Search Chair")
        window.geometry("400x350")  # Increased height for extra field

        ttk.Label(window, text="Enter Chair ID:").pack(pady=5)
        chair_id_entry = ttk.Entry(window)
        chair_id_entry.pack(pady=5)

        result_frame = ttk.Frame(window)
        result_frame.pack(pady=10, fill="both", expand=True)

        def search():
            for widget in result_frame.winfo_children():
                widget.destroy()

            chair_id = chair_id_entry.get().strip()
            if not chair_id:
                messagebox.showerror("Error", "Chair ID cannot be empty")
                return

            details = self.app.logic.search_furniture_by_id("chairs", chair_id)
            if details:
                if details["assigned"] == 0 or details["student_id"] is None:
                    ttk.Label(result_frame, text=f"Chair {chair_id} is unassigned").pack(pady=5)
                else:
                    ttk.Label(result_frame, text=f"Chair ID: {details['chair_id']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Location: {details['location']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Form: {details['form']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Color: {details['color']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Condition: {details['cond']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Student ID: {details['student_id']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Student Name: {details['name']}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Stream: {details['stream'] or 'N/A'}").pack(pady=5)
                    ttk.Label(result_frame, text=f"Assigned Date: {details['assigned_date']}").pack(pady=5)
            else:
                ttk.Label(result_frame, text=f"No chair found with ID {chair_id}").pack(pady=5)

        ttk.Button(window, text="Search", command=search).pack(pady=10)
    

    

    def display_all_furniture_gui(self):
        """GUI to display total furniture by form and detailed contents with export options (Excel/PDF)."""
        try:
            # Create the display window
            window = tk.Toplevel(self.root)
            window.title("All Furniture Details")
            window.geometry("1000x600")
            window.configure(bg="#f0f0f0")

            # Treeview with scrollbar
            tree_frame = ttk.Frame(window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

            tree = ttk.Treeview(tree_frame, columns=(
                "Type", "Form/ID", "Count/Location", "Condition", "Assigned", "Student ID", "Name"
            ), show="headings")
            tree.heading("Type", text="Furniture Type")
            tree.heading("Form/ID", text="Form/ID")
            tree.heading("Count/Location", text="Count/Location")
            tree.heading("Condition", text="Condition")
            tree.heading("Assigned", text="Assigned")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Name", text="Name")
            tree.column("Type", width=150, anchor="center")
            tree.column("Form/ID", width=100, anchor="center")
            tree.column("Count/Location", width=100, anchor="center")
            tree.column("Condition", width=100, anchor="center")
            tree.column("Assigned", width=100, anchor="center")
            tree.column("Student ID", width=100, anchor="center")
            tree.column("Name", width=150, anchor="center")

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            hsb.pack(side="bottom", fill="x")

            # Fetch summary data (totals by form)
            summary_data = self.app.logic.get_furniture_totals_by_form()
            if not summary_data:
                ttk.Label(window, text="Failed to fetch furniture totals", foreground="#666666").pack(pady=10)
                return

            # Fetch detailed data for lockers and chairs
            lockers_data = self.app.logic.get_furniture_status("lockers")
            chairs_data = self.app.logic.get_furniture_status("chairs")
            if not lockers_data or not chairs_data:
                ttk.Label(window, text="Failed to fetch detailed furniture data", foreground="#666666").pack(pady=10)
                return

            # Calculate total furniture
            total_furniture = summary_data["total_lockers"] + summary_data["total_chairs"]

            # Populate Treeview with summary and details
            # Insert totals
            tree.insert("", "end", values=("Total Lockers", "", summary_data["total_lockers"], "", "", "", ""))
            tree.insert("", "end", values=("Total Chairs", "", summary_data["total_chairs"], "", "", "", ""))

            # Lockers by form (summary)
            lockers_node = tree.insert("", "end", values=("Lockers by Form", "", "", "", "", "", ""), open=True)
            for form, count in summary_data["lockers_by_form"].items():
                form_node = tree.insert(lockers_node, "end", values=("", form, count, "", "", "", ""), open=True)
                # Add detailed data for this form
                for locker in lockers_data:
                    if locker["form"] == form:
                        tree.insert(form_node, "end", values=(
                            "", locker["locker_id"], locker["location"], locker["cond"],
                            "Yes" if locker["assigned"] else "No",
                            locker["student_id"] if locker["assigned"] else "N/A",
                            locker["student_name"] if locker["assigned"] else "N/A"
                        ))

            # Chairs by form (summary)
            chairs_node = tree.insert("", "end", values=("Chairs by Form", "", "", "", "", "", ""), open=True)
            for form, count in summary_data["chairs_by_form"].items():
                form_node = tree.insert(chairs_node, "end", values=("", form, count, "", "", "", ""), open=True)
                # Add detailed data for this form
                for chair in chairs_data:
                    if chair["form"] == form:
                        tree.insert(form_node, "end", values=(
                            "", chair["chair_id"], chair["location"], chair["cond"],
                            "Yes" if chair["assigned"] else "No",
                            chair["student_id"] if chair["assigned"] else "N/A",
                            chair["student_name"] if chair["assigned"] else "N/A"
                        ))

            # Download frame
            download_frame = ttk.Frame(window)
            download_frame.pack(pady=5)

            # Download format dropdown
            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")],
                    initialfile="furniture_details.xlsx"
                )
                if not file_path:
                    return

                try:
                    if file_format == "Excel":
                        # Prepare summary data for Excel
                        export_data = [
                            {"Furniture Type": "Total Lockers", "Form/ID": "", "Count/Location": summary_data["total_lockers"], "Condition": "", "Assigned": "", "Student ID": "", "Name": ""},
                            {"Furniture Type": "Total Chairs", "Form/ID": "", "Count/Location": summary_data["total_chairs"], "Condition": "", "Assigned": "", "Student ID": "", "Name": ""}
                        ]
                        # Lockers by form (summary and details)
                        for form, count in summary_data["lockers_by_form"].items():
                            export_data.append({"Furniture Type": "Lockers by Form", "Form/ID": form, "Count/Location": count, "Condition": "", "Assigned": "", "Student ID": "", "Name": ""})
                            for locker in lockers_data:
                                if locker["form"] == form:
                                    export_data.append({
                                        "Furniture Type": "",
                                        "Form/ID": locker["locker_id"],
                                        "Count/Location": locker["location"],
                                        "Condition": locker["cond"],
                                        "Assigned": "Yes" if locker["assigned"] else "No",
                                        "Student ID": locker["student_id"] if locker["assigned"] else "N/A",
                                        "Name": locker["student_name"] if locker["assigned"] else "N/A"
                                    })
                        # Chairs by form (summary and details)
                        for form, count in summary_data["chairs_by_form"].items():
                            export_data.append({"Furniture Type": "Chairs by Form", "Form/ID": form, "Count/Location": count, "Condition": "", "Assigned": "", "Student ID": "", "Name": ""})
                            for chair in chairs_data:
                                if chair["form"] == form:
                                    export_data.append({
                                        "Furniture Type": "",
                                        "Form/ID": chair["chair_id"],
                                        "Count/Location": chair["location"],
                                        "Condition": chair["cond"],
                                        "Assigned": "Yes" if chair["assigned"] else "No",
                                        "Student ID": chair["student_id"] if chair["assigned"] else "N/A",
                                        "Name": chair["student_name"] if chair["assigned"] else "N/A"
                                    })
                        df = pd.DataFrame(export_data)
                        df.to_excel(file_path, index=False)
                        messagebox.showinfo("Success", f"Data exported to {file_path}", parent=window)

                    elif file_format == "PDF":
                        # Generate PDF with repeating headers
                        doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                        elements = []
                        styles = getSampleStyleSheet()

                        # Define page header and footer
                        def add_page_header_footer(canvas, doc):
                            canvas.saveState()
                            # Header
                            canvas.setFont("Helvetica-Bold", 12)
                            canvas.drawString(inch, letter[1] - 0.5*inch, "Furniture Details by Form")
                            canvas.setFont("Helvetica", 10)
                            canvas.drawString(inch, letter[1] - 0.75*inch, f"Total Furniture: {total_furniture}")
                            # Footer (page number)
                            canvas.setFont("Helvetica", 8)
                            page_num = canvas.getPageNumber()
                            canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                            canvas.restoreState()

                        # Summary table
                        elements.append(Paragraph("Summary: Furniture Totals by Form", styles["Heading2"]))
                        summary_table_data = [["Furniture Type", "Form", "Count"]]
                        summary_table_data.append(["Total Lockers", "", str(summary_data["total_lockers"])])
                        summary_table_data.append(["Total Chairs", "", str(summary_data["total_chairs"])])
                        for form, count in summary_data["lockers_by_form"].items():
                            summary_table_data.append(["Locker", form, str(count)])
                        for form, count in summary_data["chairs_by_form"].items():
                            summary_table_data.append(["Chair", form, str(count)])

                        summary_table = Table(summary_table_data)
                        summary_table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ]))
                        elements.append(summary_table)
                        elements.append(Spacer(1, 0.5*inch))

                        # Detailed table
                        elements.append(Paragraph("Details: Individual Furniture Items", styles["Heading2"]))
                        detail_table_data = [["Furniture Type", "Form/ID", "Location", "Condition", "Assigned", "Student ID", "Name"]]
                        # Lockers by form (details)
                        for form, count in summary_data["lockers_by_form"].items():
                            detail_table_data.append(["Lockers by Form", form, "", "", "", "", ""])
                            for locker in lockers_data:
                                if locker["form"] == form:
                                    detail_table_data.append([
                                        "",
                                        locker["locker_id"],
                                        locker["location"],
                                        locker["cond"],
                                        "Yes" if locker["assigned"] else "No",
                                        locker["student_id"] if locker["assigned"] else "N/A",
                                        locker["student_name"] if locker["assigned"] else "N/A"
                                    ])
                        # Chairs by form (details)
                        for form, count in summary_data["chairs_by_form"].items():
                            detail_table_data.append(["Chairs by Form", form, "", "", "", "", ""])
                            for chair in chairs_data:
                                if chair["form"] == form:
                                    detail_table_data.append([
                                        "",
                                        chair["chair_id"],
                                        chair["location"],
                                        chair["cond"],
                                        "Yes" if chair["assigned"] else "No",
                                        chair["student_id"] if chair["assigned"] else "N/A",
                                        chair["student_name"] if chair["assigned"] else "N/A"
                                    ])

                        detail_table = LongTable(detail_table_data)
                        detail_table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ]))
                        elements.append(detail_table)

                        # Build PDF with page header and footer
                        doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                        messagebox.showinfo("Success", f"Data exported to {file_path}", parent=window)

                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export data: {e}", parent=window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            # Close button
            ttk.Button(window, text="Close", command=window.destroy, style="Action.TButton").pack(pady=5)

            # Style for button
            style = ttk.Style()
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5, background="#4CAF50", foreground="white")

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display furniture details: {tcl_err}")

            
    def display_furniture_details_gui(self):
        """GUI to display detailed furniture list with Treeview and PDF export."""
        window = tk.Toplevel()
        window.title("All Furniture Details")
        window.geometry("800x400")

        # Treeview with scrollbar
        tree_frame = ttk.Frame(window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
        tree = ttk.Treeview(tree_frame, columns=("ID", "Student ID", "Name", "Form", "Condition"), show="headings")
        tree.heading("ID", text="Furniture ID")
        tree.heading("Student ID", text="Student ID")
        tree.heading("Name", text="Name")
        tree.heading("Form", text="Form")
        tree.heading("Condition", text="Condition")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Fetch and populate data
        data = self.app.logic.get_all_furniture_details()
        if data:
            # Lockers
            for locker in data["lockers"]:
                tree.insert("", "end", values=(
                    locker["locker_id"],
                    locker["student_id"] or "Unassigned",
                    locker["name"] or "N/A",
                    locker["form"],
                    locker["cond"]
                ))

            # Chairs
            for chair in data["chairs"]:
                tree.insert("", "end", values=(
                    chair["chair_id"],
                    chair["student_id"] or "Unassigned",
                    chair["name"] or "N/A",
                    chair["form"],
                    chair["cond"]
                ))

            # PDF export
            def export_to_pdf():
                doc = SimpleDocTemplate("furniture_details.pdf", pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()

                # Title
                elements.append(Paragraph("Furniture Details", styles["Heading1"]))

                # Table data
                table_data = [["Furniture ID", "Student ID", "Name", "Form", "Condition"]]
                for locker in data["lockers"]:
                    table_data.append([
                        locker["locker_id"],
                        locker["student_id"] or "Unassigned",
                        locker["name"] or "N/A",
                        locker["form"],
                        locker["cond"]
                    ])
                for chair in data["chairs"]:
                    table_data.append([
                        chair["chair_id"],
                        chair["student_id"] or "Unassigned",
                        chair["name"] or "N/A",
                        chair["form"],
                        chair["cond"]
                    ])

                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)

                doc.build(elements)
                messagebox.showinfo("Success", "Exported to furniture_details.pdf")

            ttk.Button(window, text="Export to PDF", command=export_to_pdf).pack(pady=10)
        else:
            ttk.Label(window, text="Failed to fetch furniture details").pack(pady=10)
        
    def add_furniture_category_gui(self):
        """GUI to add or update a furniture category."""
        window = tk.Toplevel()
        window.title("Add/Update Furniture Category")
        window.geometry("400x300")

        ttk.Label(window, text="Category Name:").pack(pady=5)
        category_entry = ttk.Entry(window)
        category_entry.pack(pady=5)

        ttk.Label(window, text="Total Count:").pack(pady=5)
        total_entry = ttk.Entry(window)
        total_entry.pack(pady=5)

        ttk.Label(window, text="Needs Repair (optional):").pack(pady=5)
        repair_entry = ttk.Entry(window)
        repair_entry.pack(pady=5)

        def submit():
            category_name = category_entry.get().strip()
            total_count = total_entry.get().strip()
            needs_repair = repair_entry.get().strip() or "0"

            if not category_name:
                messagebox.showerror("Error", "Category name cannot be empty")
                return
            try:
                total_count = int(total_count)
                needs_repair = int(needs_repair)
            except ValueError:
                messagebox.showerror("Error", "Total count and needs repair must be integers")
                return

            if self.app.logic.add_or_update_furniture_category(category_name, total_count, needs_repair):
                messagebox.showinfo("Success", f"Category '{category_name}' updated: {total_count} total, {needs_repair} need repair")
                window.destroy()
            else:
                messagebox.showerror("Error", "Failed to update category")

        ttk.Button(window, text="Submit", command=submit).pack(pady=10)

    def display_furniture_categories_gui(self):
        """GUI to display all furniture categories with Treeview and PDF export."""
        window = tk.Toplevel()
        window.title("All Furniture Categories")
        window.geometry("600x400")

        # Treeview with scrollbar
        tree_frame = ttk.Frame(window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
        tree = ttk.Treeview(tree_frame, columns=("Category", "Total", "Needs Repair"), show="headings")
        tree.heading("Category", text="Category Name")
        tree.heading("Total", text="Total Count")
        tree.heading("Needs Repair", text="Needs Repair")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Fetch and populate data
        categories = self.app.logic.get_all_furniture_categories()
        if categories:
            for category in categories:
                tree.insert("", "end", values=(
                    category["category_name"],
                    category["total_count"],
                    category["needs_repair"]
                ))

            # PDF export
            def export_to_pdf():
                doc = SimpleDocTemplate("furniture_categories.pdf", pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()

                elements.append(Paragraph("Furniture Categories", styles["Heading1"]))
                table_data = [["Category Name", "Total Count", "Needs Repair"]]
                for category in categories:
                    table_data.append([
                        category["category_name"],
                        str(category["total_count"]),
                        str(category["needs_repair"])
                    ])

                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)

                doc.build(elements)
                messagebox.showinfo("Success", "Exported to furniture_categories.pdf")

            ttk.Button(window, text="Export to PDF", command=export_to_pdf).pack(pady=10)
        else:
            ttk.Label(window, text="No furniture categories found").pack(pady=10)


    def show_graduate_students_window(self):
        try:
            self.logger.info("Opening graduate students window")
            grad_window = tk.Toplevel(self.root)
            grad_window.title("Manage Student Graduation")
            grad_window.geometry("450x300")
            grad_window.configure(bg="#e8f0f5")  # Light blue-gray background
            grad_window.resizable(False, False)  # Fixed size for consistency

            # Style configuration
            style = ttk.Style()
            style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#2c3e50", background="#e8f0f5")
            style.configure("Info.TLabel", font=("Segoe UI", 10), foreground="#34495e", background="#e8f0f5")
            style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)
            style.map("Action.TButton",
                    background=[("active", "#3498db"), ("!active", "#2980b9")],
                    foreground=[("active", "white"), ("!active", "white")])

            # Main frame with subtle border
            main_frame = ttk.Frame(grad_window, padding=20, relief="flat", style="Custom.TFrame")
            main_frame.pack(fill="both", expand=True)
            style.configure("Custom.TFrame", background="#e8f0f5")

            # Header
            ttk.Label(main_frame, text="Student Graduation Manager", style="Header.TLabel").pack(pady=(0, 10))

            # Info label with word wrap
            info_text = ("Manage student progression:\n- Graduate All: Advances students to the next form (e.g., 2B → 3B)\n"
                        "- Undo: Reverts students to the previous form (e.g., 3B → 2B)")
            ttk.Label(main_frame, text=info_text, style="Info.TLabel", wraplength=400, justify="center").pack(pady=(0, 20))

            # Button frame for alignment
            button_frame = ttk.Frame(main_frame, style="Custom.TFrame")
            button_frame.pack(expand=True)

            # Graduate button
            grad_button = ttk.Button(
                button_frame, text="Graduate All", command=lambda: perform_graduation(), style="Action.TButton"
            )
            grad_button.pack(pady=10)
            grad_button_tip = tk.Label(grad_window, text="Advance all students to the next form", font=("Segoe UI", 8),
                                    bg="#d5e8f5", fg="#2c3e50", bd=1, relief="solid", padx=5, pady=2)
            grad_button_tip.place_forget()  # Hidden by default
            def show_tip(event, tip=grad_button_tip, btn=grad_button):
                tip.place(x=btn.winfo_x() + btn.winfo_width() // 2 - tip.winfo_reqwidth() // 2, y=btn.winfo_y() - 30)
            def hide_tip(event, tip=grad_button_tip):
                tip.place_forget()
            grad_button.bind("<Enter>", show_tip)
            grad_button.bind("<Leave>", hide_tip)

            # Undo button
            undo_button = ttk.Button(
                button_frame, text="Undo Graduation", command=lambda: perform_undo_graduation(), style="Action.TButton"
            )
            undo_button.pack(pady=10)
            undo_tip = tk.Label(grad_window, text="Revert all students to the previous form", font=("Segoe UI", 8),
                            bg="#d5e8f5", fg="#2c3e50", bd=1, relief="solid", padx=5, pady=2)
            undo_tip.place_forget()
            def show_undo_tip(event, tip=undo_tip, btn=undo_button):
                tip.place(x=btn.winfo_x() + btn.winfo_width() // 2 - tip.winfo_reqwidth() // 2, y=btn.winfo_y() - 30)
            def hide_undo_tip(event, tip=undo_tip):
                tip.place_forget()
            undo_button.bind("<Enter>", show_undo_tip)
            undo_button.bind("<Leave>", hide_undo_tip)

            # Action functions
            def perform_graduation():
                if not messagebox.askyesno("Confirm Graduation", "Are you sure you want to graduate all students to the next form?",
                                        parent=grad_window):
                    return
                try:
                    self.logger.info("Attempting to graduate all students")
                    result = self.app.graduate_students()  # Assumes main.py calls self.logic
                    if result is None:
                        self.logger.error("graduate_students returned None unexpectedly")
                        messagebox.showerror("Error", "An unexpected error occurred during graduation.", parent=grad_window)
                        return
                    success, message = result
                    if success:
                        messagebox.showinfo("Success", message, parent=grad_window)
                        grad_window.destroy()
                    else:
                        messagebox.showerror("Error", f"Graduation failed: {message}", parent=grad_window)
                except Exception as e:
                    self.logger.error(f"Failed to graduate students: {e}")
                    messagebox.showerror("Error", f"Unexpected error: {e}", parent=grad_window)

            def perform_undo_graduation():
                if not messagebox.askyesno("Confirm Undo", "Are you sure you want to revert all students to their previous form?",
                                        parent=grad_window):
                    return
                try:
                    self.logger.info("Attempting to undo graduation for all students")
                    result = self.app.undo_graduate_students()  # Updated to match main.py
                    if result is None:
                        self.logger.error("undo_graduate_students returned None unexpectedly")
                        messagebox.showerror("Error", "An unexpected error occurred during undo.", parent=grad_window)
                        return
                    success, message = result
                    if success:
                        messagebox.showinfo("Success", message, parent=grad_window)
                        grad_window.destroy()
                    else:
                        messagebox.showerror("Error", f"Undo failed: {message}", parent=grad_window)
                except Exception as e:
                    self.logger.error(f"Failed to undo graduate students: {e}")
                    messagebox.showerror("Error", f"Unexpected error: {e}", parent=grad_window)

        except Exception as e:
            self.logger.error(f"Failed to create graduate window: {e}")
            messagebox.showerror("GUI Error", f"Failed to create window: {e}")


    def show_update_student_info_window(self):
        try:
            self.logger.info("Opening update student info window")
            update_window = tk.Toplevel(self.root)
            update_window.title("Update Student Info")
            update_window.geometry("400x400")
            update_window.configure(bg="#f0f0f0")

            style = ttk.Style()
            style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), background="#f0f0f0")
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"))

            main_frame = ttk.Frame(update_window, padding=10)
            main_frame.pack(fill="both", expand=True)

            ttk.Label(main_frame, text="Update Student Information", style="Header.TLabel").pack(pady=(0, 5))
            ttk.Label(main_frame, text="Enter Student ID and fields to update:").pack()

            ttk.Label(main_frame, text="Student ID:").pack(pady=(5, 0))
            student_id_entry = ttk.Entry(main_frame)
            student_id_entry.pack(pady=5)

            ttk.Label(main_frame, text="New Stream (e.g., 3 Blue):").pack(pady=(5, 0))
            stream_entry = ttk.Entry(main_frame)
            stream_entry.pack(pady=5)

            ttk.Label(main_frame, text="New Locker ID:").pack(pady=(5, 0))
            locker_entry = ttk.Entry(main_frame)
            locker_entry.pack(pady=5)

            ttk.Label(main_frame, text="New Chair ID:").pack(pady=(5, 0))
            chair_entry = ttk.Entry(main_frame)
            chair_entry.pack(pady=5)

            def perform_update():
                student_id = student_id_entry.get().strip()
                new_stream = stream_entry.get().strip() or None
                new_locker = locker_entry.get().strip() or None
                new_chair = chair_entry.get().strip() or None

                try:
                    self.logger.info(f"Attempting to update student {student_id} with stream={new_stream}, locker={new_locker}, chair={new_chair}")
                    result = self.app.update_student_info(student_id, new_stream, new_locker, new_chair)
                    if result is None:
                        self.logger.error(f"update_student_info returned None for student {student_id}")
                        messagebox.showerror("Error", "An unexpected error occurred during update.", parent=update_window)
                        return
                    success, message = result
                    if success:
                        messagebox.showinfo("Success", message, parent=update_window)
                        stream_entry.delete(0, tk.END)
                        locker_entry.delete(0, tk.END)
                        chair_entry.delete(0, tk.END)
                    else:
                        messagebox.showerror("Error", message, parent=update_window)
                except Exception as e:
                    self.logger.error(f"Failed to update student info: {e}")
                    messagebox.showerror("Error", f"Unexpected error: {e}", parent=update_window)

            ttk.Button(main_frame, text="Update Student", command=perform_update, style="Action.TButton").pack(pady=20)

        except Exception as e:
            self.logger.error(f"Failed to create update window: {e}")
            messagebox.showerror("GUI Error", f"Failed to create window: {e}")


    def load_chairs_gui(self):
        
        file_path = filedialog.askopenfilename(
            title="Select Chairs Excel File",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))  # Remove *.xls
        )
        if not file_path:
            return

        # Load Excel for preview
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            if not {'student_id', 'chair_id'}.issubset(df.columns):
                messagebox.showerror("Error", "Excel file must contain 'student_id' and 'chair_id' columns")
                return
        except Exception as e:
            self.logger.error(f"Failed to read Excel file: {e}")
            messagebox.showerror("Error", f"Failed to read Excel file: {e}")
            return

        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Chair Assignments")
        preview_window.geometry("600x400")
        preview_window.configure(bg="#f0f0f0")

        # Frame for Treeview and scrollbar
        tree_frame = ttk.Frame(preview_window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview for preview
        tree = ttk.Treeview(tree_frame, columns=list(df.columns), show="headings")
        tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Set column headings
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        # Insert all data
        for _, row in df.iterrows():
            tree.insert("", "end", values=[str(row[col]) for col in df.columns])

        # Button frame
        button_frame = ttk.Frame(preview_window)
        button_frame.pack(pady=10)

        def load_all_data():
            success, message = self.app.load_chairs_from_excel(file_path)
            if success:
                messagebox.showinfo("Success", message, parent=preview_window)
                preview_window.destroy()
            else:
                messagebox.showerror("Error", message, parent=preview_window)

        ttk.Button(button_frame, text="Load All", command=load_all_data, style="Action.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=preview_window.destroy, style="Action.TButton").pack(side="left", padx=5)

        # Style for buttons
        style = ttk.Style()
        style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)


    def load_lockers_gui(self):
        file_path = filedialog.askopenfilename(
            title="Select Lockers Excel File",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if not file_path:
            return

        # Load Excel for preview
        try:
            df = pd.read_excel(file_path)
            if not {'student_id', 'locker_id'}.issubset(df.columns):
                messagebox.showerror("Error", "Excel file must contain 'student_id' and 'locker_id' columns")
                return
        except Exception as e:
            self.logger.error(f"Failed to read Excel file: {e}")
            messagebox.showerror("Error", f"Failed to read Excel file: {e}")
            return

        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Locker Assignments")
        preview_window.geometry("600x400")
        preview_window.configure(bg="#f0f0f0")

        # Frame for Treeview and scrollbar
        tree_frame = ttk.Frame(preview_window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview for preview
        tree = ttk.Treeview(tree_frame, columns=list(df.columns), show="headings")
        tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Set column headings
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        # Insert all data
        for _, row in df.iterrows():
            tree.insert("", "end", values=[str(row[col]) for col in df.columns])

        # Button frame
        button_frame = ttk.Frame(preview_window)
        button_frame.pack(pady=10)

        def load_all_data():
            success, message = self.app.load_lockers_from_excel(file_path)
            if success:
                messagebox.showinfo("Success", message, parent=preview_window)
                preview_window.destroy()
            else:
                messagebox.showerror("Error", message, parent=preview_window)

        ttk.Button(button_frame, text="Load All", command=load_all_data, style="Action.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=preview_window.destroy, style="Action.TButton").pack(side="left", padx=5)

        # Style for buttons
        style = ttk.Style()
        style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)


    def display_students_by_form_gui(self):
        """Displays students grouped by form in a Treeview with collapsible nodes, total students, and download option."""
        try:
            self.logger.info("Opening display students by form window")
            success, result = self.app.display_students_by_form()
            if not success:
                messagebox.showerror("Error", result)
                return

            # Create window
            window = tk.Toplevel(self.root)
            window.title("Students by Form")
            window.geometry("800x550")  # Increased height for total label and download button
            window.configure(bg="#f0f0f0")

            # Calculate total students
            forms_data = result["forms"]
            total_students = sum(form_data["total"] for form_data in forms_data.values())

            # Total students label
            total_label = ttk.Label(window, text=f"Total Students: {total_students}", font=("Helvetica", 12, "bold"), background="#f0f0f0")
            total_label.pack(pady=5)

            # Frame for Treeview and scrollbar
            tree_frame = ttk.Frame(window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Treeview
            columns = ("Student ID", "Name", "Stream")
            tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings")
            tree.heading("#0", text="Form / Student Details")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Name", text="Name")
            tree.heading("Stream", text="Stream")
            tree.column("#0", width=300)
            tree.column("Student ID", width=150, anchor="center")
            tree.column("Name", width=200, anchor="center")
            tree.column("Stream", width=150, anchor="center")
            tree.pack(side="left", fill="both", expand=True)

            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)

            # Populate Treeview
            for form in sorted(forms_data.keys()):  # Sort forms: Form 1, Form 2, etc.
                total = forms_data[form]["total"]
                form_node = tree.insert("", "end", text=f"{form} (Total: {total})", open=False)
                for student in forms_data[form]["students"]:
                    tree.insert(form_node, "end", text="", values=(
                        student["student_id"],
                        student["name"],
                        student["stream"]
                    ))

            # Download frame
            download_frame = ttk.Frame(window)
            download_frame.pack(pady=5)

            # Download format dropdown
            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")]
                )
                if not file_path:
                    return

                if file_format == "Excel":
                    # Prepare data for Excel
                    data = []
                    for form in sorted(forms_data.keys()):
                        for student in forms_data[form]["students"]:
                            data.append({
                                "Form": form,
                                "Student ID": student["student_id"],
                                "Name": student["name"],
                                "Stream": student["stream"]
                            })
                    df = pd.DataFrame(data)
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=window)

                elif file_format == "PDF":
                    # Generate PDF
                    doc = SimpleDocTemplate(file_path, pagesize=letter)
                    elements = []
                    styles = getSampleStyleSheet()

                    # Title
                    elements.append(Paragraph("Students by Form", styles["Title"]))
                    elements.append(Spacer(1, 12))

                    # Table data
                    table_data = [["Form", "Student ID", "Name", "Stream"]]
                    for form in sorted(forms_data.keys()):
                        for student in forms_data[form]["students"]:
                            table_data.append([
                                form,
                                student["student_id"],
                                student["name"],
                                student["stream"]
                            ])

                    # Create table
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    elements.append(table)

                    # Build PDF
                    doc.build(elements)
                    messagebox.showinfo("Success", f"Data exported to {file_path}", parent=window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            # Close button
            ttk.Button(window, text="Close", command=window.destroy, style="Action.TButton").pack(pady=5)

            # Style for button
            style = ttk.Style()
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

        except Exception as e:
            self.logger.error(f"Failed to display students by form: {e}")
            messagebox.showerror("GUI Error", f"Failed to display students: {e}")


    def manage_short_form_mappings_gui(self):
        """GUI to manage short form to full name mappings for classes and subjects."""
        try:
            window = tk.Toplevel(self.root)
            window.title("Manage Short Form Mappings")
            window.geometry("400x400")
            window.configure(bg="#f0f0f0")

            # Entry frame
            entry_frame = ttk.Frame(window)
            entry_frame.pack(pady=10, padx=10, fill="x")

            ttk.Label(entry_frame, text="Short Form:").grid(row=0, column=0, padx=5, pady=5)
            short_form_entry = ttk.Entry(entry_frame)
            short_form_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(entry_frame, text="Full Name:").grid(row=1, column=0, padx=5, pady=5)
            full_name_entry = ttk.Entry(entry_frame)
            full_name_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(entry_frame, text="Type:").grid(row=2, column=0, padx=5, pady=5)
            type_var = tk.StringVar(value="subject")
            ttk.Combobox(entry_frame, textvariable=type_var, values=["class", "subject"], state="readonly").grid(row=2, column=1, padx=5, pady=5)

            def add_mapping():
                short_form = short_form_entry.get().strip()
                full_name = full_name_entry.get().strip()
                mapping_type = type_var.get()
                if not short_form or not full_name:
                    messagebox.showerror("Input Error", "Both short form and full name are required.", parent=window)
                    return

                success, message = self.app.add_short_form_mapping(short_form, full_name, mapping_type)
                if success:
                    messagebox.showinfo("Success", message, parent=window)
                    short_form_entry.delete(0, tk.END)
                    full_name_entry.delete(0, tk.END)
                    refresh_mappings()
                else:
                    messagebox.showerror("Error", message, parent=window)

            ttk.Button(entry_frame, text="Add Mapping", command=add_mapping).grid(row=3, column=0, columnspan=2, pady=10)

            # Treeview frame
            tree_frame = ttk.Frame(window)
            tree_frame.pack(pady=10, fill="both", expand=True)

            tree = ttk.Treeview(tree_frame, columns=("Short Form", "Full Name", "Type"), show="headings")
            tree.heading("Short Form", text="Short Form")
            tree.heading("Full Name", text="Full Name")
            tree.heading("Type", text="Type")
            tree.column("Short Form", width=100, anchor="center")
            tree.column("Full Name", width=150, anchor="center")
            tree.column("Type", width=100, anchor="center")
            tree.pack(side="left", fill="both", expand=True)

            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)

            def refresh_mappings():
                success, result = self.app.get_short_form_mappings()
                if not success:
                    messagebox.showerror("Error", result, parent=window)
                    return

                for item in tree.get_children():
                    tree.delete(item)
                for mapping_type, mappings in result.items():
                    for short_form, full_name in mappings.items():
                        tree.insert("", "end", values=(short_form, full_name, mapping_type))

            # Initial load
            refresh_mappings()

            # Close button
            ttk.Button(window, text="Close", command=window.destroy, style="Action.TButton").pack(pady=5)

            # Style for button
            style = ttk.Style()
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5)

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to manage short form mappings: {tcl_err}")


    def show_students_without_borrowed_books(self):
        """Displays students without borrowed books grouped by stream in a GUI with export options."""
        try:
            # Fetch the students data
            students = self.app.get_students_without_borrowed_books()
            if not students:
                messagebox.showinfo("No Students", "No students found without borrowed books.")
                return

            # Create the display window
            display_window = tk.Toplevel(self.root)
            display_window.title("Students Without Borrowed Books")
            display_window.geometry("600x500")
            display_window.configure(bg="#f0f0f0")

            # Treeview with scrollbars
            tree_frame = ttk.Frame(display_window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

            columns = ("Student ID", "Name", "Stream")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Name", text="Name")
            tree.heading("Stream", text="Stream")
            tree.column("Student ID", width=150, anchor="center")
            tree.column("Name", width=250, anchor="center")
            tree.column("Stream", width=100, anchor="center")

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            hsb.pack(side="bottom", fill="x")

            # Group students by stream
            stream_groups = {}
            for student_id, name, stream in students:
                stream_key = stream if stream else "No Stream"
                if stream_key not in stream_groups:
                    stream_groups[stream_key] = []
                stream_groups[stream_key].append((student_id, name, stream))

            # Populate Treeview with stream groups
            for stream, students_list in sorted(stream_groups.items()):
                stream_node = tree.insert("", "end", text=stream, open=True)
                for student_id, name, student_stream in students_list:
                    tree.insert(stream_node, "end", values=(student_id, name, student_stream or "N/A"))

            # Download frame
            download_frame = ttk.Frame(display_window)
            download_frame.pack(pady=5)

            # Download format dropdown
            format_var = tk.StringVar(value="Excel")
            format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
            format_menu.pack(side="left", padx=5)

            def download_data():
                file_format = format_var.get()
                file_path = filedialog.asksaveasfilename(
                    title=f"Save as {file_format}",
                    defaultextension=f".{file_format.lower()}",
                    filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")],
                    initialfile="students_without_books_by_stream"
                )
                if not file_path:
                    return

                try:
                    if file_format == "Excel":
                        # Prepare data for Excel with stream grouping
                        data = []
                        for stream, students_list in sorted(stream_groups.items()):
                            data.append(["Stream:", stream, ""])  # Stream header
                            for student_id, name, student_stream in students_list:
                                data.append([student_id, name, student_stream or "N/A"])
                            data.append(["", "", ""])  # Blank row between streams
                        df = pd.DataFrame(data, columns=["Student ID", "Name", "Stream"])
                        df.to_excel(file_path, index=False)
                        messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

                    elif file_format == "PDF":
                        # Generate PDF with stream-wise grouping
                        doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                        elements = []
                        styles = getSampleStyleSheet()

                        def add_page_header_footer(canvas, doc):
                            canvas.saveState()
                            canvas.setFont("Helvetica-Bold", 12)
                            canvas.drawString(inch, letter[1] - 0.5*inch, "Students Without Borrowed Books Report")
                            canvas.setFont("Helvetica", 10)
                            canvas.drawString(inch, letter[1] - 0.75*inch, f"Total Students: {len(students)}")
                            canvas.setFont("Helvetica", 8)
                            page_num = canvas.getPageNumber()
                            canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                            canvas.restoreState()

                        # Table data with stream headers
                        table_data = [["Student ID", "Name", "Stream"]]
                        for stream, students_list in sorted(stream_groups.items()):
                            table_data.append([f"Stream: {stream}", "", ""])  # Stream header row
                            for student_id, name, student_stream in students_list:
                                table_data.append([student_id, name, student_stream or "N/A"])
                            table_data.append(["", "", ""])  # Blank row between streams

                        table = LongTable(table_data)
                        table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),  # Bold stream headers
                        ]))
                        elements.append(table)

                        doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                        messagebox.showinfo("Success", f"Data exported to {file_path}", parent=display_window)

                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export data: {e}", parent=display_window)

            ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

            # Close button
            ttk.Button(display_window, text="Close", command=display_window.destroy, style="Action.TButton").pack(pady=5)

            # Style for button
            style = ttk.Style()
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5, background="#4CAF50", foreground="white")

        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display students without borrowed books: {tcl_err}")


    def open_view_all_books(self):
        self.view_all_books_gui()


    def assign_furniture_gui(self, furniture_type):
        """Opens a refined GUI for assigning lockers or chairs."""
        if furniture_type not in ["LKR", "CHR"]:
            self.logger.error(f"Invalid furniture type: {furniture_type}")
            return

        # Map "LKR" and "CHR" to "lockers" and "chairs"
        type_map = {"LKR": "lockers", "CHR": "chairs"}
        mapped_type = type_map[furniture_type]

        root = tk.Toplevel(self.root)
        app = FurnitureAssignmentGUI(root, self.app, furniture_type)  # Keep original for internal use
        app.furniture_list = self.app.get_furniture_status(mapped_type)  # Use mapped type for query
        root.mainloop()

class FurnitureAssignmentGUI:
    def __init__(self, root, app, furniture_type):
        self.root = root
        self.app = app
        self.furniture_type = furniture_type  # "LKR" or "CHR"
        self.assignments = {}
        self.table = "lockers" if furniture_type == "LKR" else "chairs"
        self.id_field = "locker_id" if furniture_type == "LKR" else "chair_id"
        self.assign_method = self.app.assign_locker if furniture_type == "LKR" else self.app.assign_chair
        self.undo_stack = []

        self.root.title(f"Assign {self.furniture_type.replace('LKR', 'Lockers').replace('CHR', 'Chairs')}")
        self.root.geometry("900x700")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.interactive_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.interactive_tab, text="Interactive Assignment")
        self.setup_interactive_mode()

        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text="Batch Assignment")
        self.setup_batch_mode()

    def setup_interactive_mode(self):
        control_frame = ttk.Frame(self.interactive_tab)
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(control_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.update_list())

        ttk.Label(control_frame, text="Condition:").pack(side="left", padx=5)
        self.cond_var = tk.StringVar(value="All")
        cond_menu = ttk.OptionMenu(control_frame, self.cond_var, "All", "All", "Good", "Damaged", "Needs Repair", command=lambda e: self.update_list())
        cond_menu.pack(side="left", padx=5)

        ttk.Label(control_frame, text="Sort by:").pack(side="left", padx=5)
        self.sort_var = tk.StringVar(value="ID")
        sort_menu = ttk.OptionMenu(control_frame, self.sort_var, "ID", "ID", "Location", "Status", command=lambda e: self.update_list())
        sort_menu.pack(side="left", padx=5)

        ttk.Button(control_frame, text="Export to CSV", command=self.export_to_csv).pack(side="right", padx=5)
        self.undo_btn = ttk.Button(control_frame, text="Undo Last", command=self.undo_last, state="disabled")
        self.undo_btn.pack(side="right", padx=5)

        list_frame = ttk.Frame(self.interactive_tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.furniture_list = self.app.get_furniture_status("lockers" if self.furniture_type == "LKR" else "chairs")
        self.update_list()

    def update_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        search_term = self.search_var.get().lower()
        cond_filter = self.cond_var.get()
        sort_key = self.sort_var.get()

        filtered_list = [
            item for item in self.furniture_list
            if (
                (search_term in str(item[self.id_field]).lower() or
                search_term in str(item["location"]).lower() or
                search_term in str(item["form"]).lower()) and
                (cond_filter == "All" or item["cond"] == cond_filter)
            )
        ]

        if sort_key == "ID":
            filtered_list.sort(key=lambda x: x[self.id_field])
        elif sort_key == "Location":
            filtered_list.sort(key=lambda x: x["location"])
        elif sort_key == "Status":
            filtered_list.sort(key=lambda x: x["assigned"], reverse=True)

        if not filtered_list:
            ttk.Label(self.scrollable_frame, text=f"No {self.furniture_type.replace('LKR', 'Lockers').replace('CHR', 'Chairs')} match the filters.").pack(pady=10)
            return

        for item in filtered_list:
            fid = item[self.id_field]
            assigned = item["assigned"]
            student_id = item["student_id"] if item["student_id"] else ""
            location = item["location"]
            form = item["form"]
            cond = item["cond"]

            #print(f"ID: {fid}, Assigned: {assigned}, Student ID: {student_id}")

            row_frame = ttk.Frame(self.scrollable_frame)
            row_frame.pack(fill="x", pady=5)

            status_text = f"{fid} ({'Assigned' if assigned else 'Available'})"
            status_label = ttk.Label(row_frame, text=status_text, width=30,
                                background="#ffcccc" if assigned else "#ccffcc")
            status_label.pack(side="left", padx=5)
            status_label.tooltip = tk.Toplevel(status_label, background="#ffffe0")
            status_label.tooltip.withdraw()
            ttk.Label(status_label.tooltip, text=f"Location: {location}\nForm: {form}\nCondition: {cond}").pack(padx=5, pady=5)
            status_label.bind("<Enter>", lambda e, l=status_label: l.tooltip.deiconify())
            status_label.bind("<Leave>", lambda e, l=status_label: l.tooltip.withdraw())

            student_entry = ttk.Entry(row_frame, width=20)
            student_entry.insert(0, student_id)  # Insert first
            student_entry.config(state="disabled" if assigned else "normal")  # Set state after
            student_entry.pack(side="left", padx=5)
            #print(f"Entry for {fid} set to: {student_entry.get()}")  # Check after packing

            save_btn = ttk.Button(row_frame, text="Save",
                                command=lambda f=fid, e=student_entry: self.save_individual(f, e),
                                state="disabled" if assigned else "normal")
            save_btn.pack(side="left", padx=5)

        self.root.update_idletasks()  # Force GUI refresh

    def save_individual(self, furniture_id, entry):
        student_id = entry.get().strip()
        if not student_id:
            messagebox.showerror("Error", "Student ID cannot be empty.")
            return

        success = self.assign_method(student_id, furniture_id)
        if success:
            messagebox.showinfo("Success", f"Assigned {furniture_id} to {student_id}.")
            entry.config(state="disabled")
            entry.master.children["!button"].config(state="disabled")
            self.undo_stack.append((furniture_id, student_id))
            self.undo_btn.config(state="normal")
            mapped_type = "lockers" if self.furniture_type == "LKR" else "chairs"
            self.furniture_list = self.app.get_furniture_status(mapped_type)
            #print("Refreshed furniture_list:", self.furniture_list[:5])  # Debug
            self.update_list()
        else:
            messagebox.showerror("Error", f"Failed to assign {furniture_id}. Check logs.")

    def undo_last(self):
        """Undo the last furniture assignment operation."""
        if not self.undo_stack:
            return

        furniture_id, student_id = self.undo_stack.pop()
        unassign_method = self.app.unassign_locker if self.furniture_type == "LKR" else lambda sid, fid: (
            self.app.db_manager.cursor.execute("DELETE FROM chair_assignments WHERE student_id = ? AND chair_id = ?", (sid, fid)) and
            self.app.db_manager.cursor.execute("UPDATE chairs SET assigned = 0 WHERE chair_id = ?", (fid,))
        )

        conn = self.db_manager._create_connection()
        if conn is None:
            self.app.logger.error("Failed to establish database connection for undo")
            messagebox.showerror("Error", "Cannot connect to database for undo operation")
            self.undo_stack.append((furniture_id, student_id))  # Revert pop if connection fails
            return

        try:
            cursor = conn.cursor()
            self.app.db_manager.cursor = cursor  # Maintain reference if needed elsewhere
            unassign_method(student_id, furniture_id)
            conn.commit()
            messagebox.showinfo("Undo", f"Reverted assignment of {furniture_id} from {student_id}.")
            self.furniture_list = self.app.get_furniture_status(self.furniture_type)
            self.update_list()
        except SQLiteError as e:
            if conn:  # Only rollback if conn exists
                conn.rollback()
            self.app.logger.error(f"Undo failed: {e}")
            messagebox.showerror("Error", f"Undo failed: {e}")
            self.undo_stack.append((furniture_id, student_id))  # Revert pop on failure
        finally:
            if conn:  # Only close if conn exists
                self.db_manager._close_connection(conn)

        if not self.undo_stack:
            self.undo_btn.config(state="disabled")

            
    def export_to_csv(self):
        filename = f"{self.furniture_type}_assignments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([self.id_field, "student_id", "location", "form", "condition", "status"])
            for item in self.furniture_list:
                writer.writerow([item[self.id_field], item["student_id"] or "Unassigned", 
                                item["location"], item["form"], item["cond"],
                                "Assigned" if item["assigned"] else "Available"])
        messagebox.showinfo("Export", f"Assignments exported to {filename}.")

    def setup_batch_mode(self):
        control_frame = ttk.Frame(self.batch_tab)
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(control_frame, text="Import CSV", command=self.import_batch_csv).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Clear All", command=self.clear_batch).pack(side="left", padx=5)

        input_frame = ttk.Frame(self.batch_tab)
        input_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(input_frame, text=f"{self.furniture_type.capitalize()} ID").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(input_frame, text="Student ID").grid(row=0, column=1, padx=5, pady=5)

        self.batch_entries = []
        for i in range(5):
            self.add_batch_row(input_frame, i + 1)

        button_frame = ttk.Frame(self.batch_tab)
        button_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(button_frame, text="Add Row", command=lambda: self.add_batch_row(input_frame, len(self.batch_entries) + 1)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save All", command=self.save_batch).pack(side="left", padx=5)

        self.progress = ttk.Progressbar(self.batch_tab, length=300, mode="determinate")
        self.progress.pack(pady=5)

    def add_batch_row(self, frame, row_num):
        fid_entry = ttk.Entry(frame, width=25)
        fid_entry.grid(row=row_num, column=0, padx=5, pady=5)

        sid_entry = ttk.Entry(frame, width=25)
        sid_entry.grid(row=row_num, column=1, padx=5, pady=5)

        self.batch_entries.append((fid_entry, sid_entry))

    def import_batch_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            if not {"furniture_id", "student_id"}.issubset(reader.fieldnames):
                messagebox.showerror("Error", "CSV must contain 'furniture_id' and 'student_id' columns.")
                return

            for i, row in enumerate(reader):
                if i >= len(self.batch_entries):
                    self.add_batch_row(self.batch_tab.winfo_children()[1], i + 1)
                fid_entry, sid_entry = self.batch_entries[i]
                fid_entry.delete(0, tk.END)
                sid_entry.delete(0, tk.END)
                fid_entry.insert(0, row["furniture_id"])
                sid_entry.insert(0, row["student_id"])
        messagebox.showinfo("Import", f"Loaded assignments from {file_path}.")

    def clear_batch(self):
        for fid_entry, sid_entry in self.batch_entries:
            fid_entry.delete(0, tk.END)
            sid_entry.delete(0, tk.END)
        messagebox.showinfo("Clear", "All batch entries cleared.")

    def save_batch(self):
        assignments = [(fid_entry.get().strip(), sid_entry.get().strip()) 
                       for fid_entry, sid_entry in self.batch_entries if fid_entry.get().strip() and sid_entry.get().strip()]
        
        if not assignments:
            messagebox.showerror("Error", "No valid assignments entered.")
            return

        self.progress["maximum"] = len(assignments)
        self.progress["value"] = 0

        success_count = 0
        error_messages = []
        for i, (fid, sid) in enumerate(assignments):
            if len(fid) > 20 or len(sid) > 20:
                error_messages.append(f"ID '{fid}' or '{sid}' exceeds 20 characters.")
                continue
            success = self.assign_method(sid, fid)
            if success:
                success_count += 1
            else:
                error_messages.append(f"Failed to assign {fid} to {sid}. Check logs.")
            self.progress["value"] = i + 1
            self.root.update_idletasks()

        if success_count > 0:
            messagebox.showinfo("Success", f"Successfully assigned {success_count} {self.furniture_type}.")
            for fid_entry, sid_entry in self.batch_entries:
                if not fid_entry.get().strip() in [f for f, _ in assignments if f not in [e.split()[2] for e in error_messages]]:
                    fid_entry.delete(0, tk.END)
                    sid_entry.delete(0, tk.END)
            self.furniture_list = self.app.get_furniture_status(self.furniture_type)
        if error_messages:
            messagebox.showerror("Errors", "\n".join(error_messages))