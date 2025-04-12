# main.py

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import hashlib
import os
import json
import sys
import subprocess
from datetime import datetime, timedelta, date
from db_manager import DatabaseManager  
from gui_manager import GUIManager
from library_logic import LibraryLogic
from QRcode_Reader import QRCodeScannerGUI
from db_utils import create_db_connection, close_db_connection, initialize_database, backup_database, restore_database
import webbrowser
import platform
import requests
import openpyxl
import tempfile
import threading
import winsound

# Configure logging to a user-writable directory

log_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'HarLuFranInnoFluxSMS')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'school_management.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class WindowHandler:
    """Utility class to safely handle window closing."""
    @staticmethod
    def close_window(window):
        """Safely close a window if it’s a valid Tkinter object."""
        if isinstance(window, (tk.Tk, tk.Toplevel)):
            try:
                window.destroy()
                logging.getLogger('WindowHandler').info("Window closed successfully")
                return True
            except tk.TclError as e:
                logging.getLogger('WindowHandler').error(f"Failed to destroy window: {e}")
                return False
        elif window is None:
            logging.getLogger('WindowHandler').warning("No window provided to close")
            return False
        else:
            logging.getLogger('WindowHandler').error(f"Invalid window object: {type(window)} (expected Tk or Toplevel)")
            return False

class StartupWindow:
    def __init__(self, root, on_complete):
        self.root = root
        self.root.title("HarLuFran InnoFlux SMS - Starting")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.on_complete = on_complete
        self.connection = None

        
        self.label = tk.Label(root, text="Starting application...", font=("Arial", 12))
        self.label.pack(pady=20)
        
        self.progress = ttk.Progressbar(root, mode="indeterminate", length=300)
        self.progress.pack(pady=10)
        self.progress.start()
        
        self.status = tk.Label(root, text="", wraplength=380, justify="left")
        self.status.pack(pady=10)
        
        self.root.after(100, self.check_setup)

    def update_status(self, message):
        if self.root.winfo_exists():
            self.status.config(text=message)
            self.root.update_idletasks()

    def check_setup(self):
        self.update_status("Initializing SQLite database...")
        result = initialize_database()  # Returns connection or False
        if result and not isinstance(result, bool):  # Check if result is a connection object
            self.connection = result
            self.update_status("Database initialized successfully...")
            self.root.after(500, self.finish)
        else:
            self.update_status("Database setup failed. Check logs for details.")
            logging.error("Failed to initialize database during startup")
            self.root.after(1000, self.root.destroy)  # Exit if initialization fails

    def finish(self):
        if self.root.winfo_exists():
            self.progress.stop()
            if self.connection:
                self.on_complete(self.connection)
            else:
                logging.error("No valid connection to pass to main app")
                self.root.destroy()

class LibraryManagementSystem:
    def __init__(self, root, conn):
        self.root = root
        self.connection = conn  # Store the connection
        self.current_user = None
        self.logger = logging.getLogger('LibraryManagementSystem')
        self.logger.info("Initializing LibraryManagementSystem")
        self.window_handler = WindowHandler()

        if not self.connection:
            self.logger.error("No valid database connection provided")
            raise RuntimeError("Database connection is required")

        def start_main_app(conn):
            self.root.deiconify()
            self.root.title("HarLuFran InnoFlux SMS")
            self.root.geometry("800x600")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.backup_timer = None
            self.dashboard_frame = None
            self.reminder_after_id = None
            self.borrowed_books = []

            self.db_manager = DatabaseManager(self.connection)  # Pass the connection
            self.logic = LibraryLogic(self.db_manager)
            self.gui = GUIManager(root, self)
            self.password = self.db_manager.load_password() or self._initialize_password()
            self.gui.login_frame = self.gui.create_login_window()
            self.logger.info("Login window launched successfully")

        try:
            with open("renewal.json", 'r') as renewal_file:
                data = json.load(renewal_file)
                self.renewal_key = data.get("renewal_key", None)
            self.logger.info("Renewal key loaded successfully")
        except FileNotFoundError as fnf_err:
            self.logger.error(f"Renewal file not found: {fnf_err}")
            messagebox.showerror("File Error", f"Renewal file not found: {fnf_err}")
            self.renewal_key = None
        except json.JSONDecodeError as json_err:
            self.logger.error(f"Invalid JSON in renewal file: {json_err}")
            messagebox.showerror("File Error", f"Invalid JSON in renewal file: {json_err}")
            self.renewal_key = None
        except Exception as e:
            self.logger.critical(f"Initialization failed: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {e}")
            raise

        try:
            self.check_license()
            self.schedule_backup(interval=24*60*60)
            self.logger.info("Application initialized successfully")
            start_main_app(self.connection)
        except (FileNotFoundError, ValueError) as lic_err:
            self.logger.error(f"License check failed: {lic_err}")
            messagebox.showerror("License Error", f"Failed to check license: {lic_err}")
            raise

        

    def backup_database(self):
        """Handle database backup using db_utils."""
        try:
            self.logger.info("Initiating database backup")
            if backup_database():
                self.logger.info("Backup action completed")
            else:
                self.logger.error("Backup action failed")
        except Exception as e:
            self.logger.error(f"Failed to perform database backup: {e}")
            messagebox.showerror("Backup Error", f"Failed to perform database backup: {e}")

    

    def restore_database(self):
        """Handle database restore using db_utils."""
        try:
            self.logger.info("Initiating database restore")
            backup_file = filedialog.askopenfilename(
                title="Select Backup File",
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
            )
            if not backup_file:
                self.logger.info("Restore cancelled by user")
                return

            if not messagebox.askyesno("Confirm Restore", "This will overwrite the current database. Continue?"):
                self.logger.info("Restore cancelled by user confirmation")
                return

            if restore_database(backup_file):
                self.logger.info("Restore action completed successfully")
                messagebox.showinfo("Restore Success", f"Data restored from '{backup_file}'.")
            else:
                self.logger.warning("Restore action failed")
        except Exception as e:
            self.logger.error(f"Failed to perform database restore: {e}")
            messagebox.showerror("Restore Error", f"Failed to perform database restore: {e}")

    def schedule_backup(self, interval):
        """Schedule automatic backups using db_utils."""
        def run_backup():
            self.logger.info("Running scheduled backup")
            backup_database()
            self.backup_timer = threading.Timer(interval, run_backup)
            self.backup_timer.start()

        self.backup_timer = threading.Timer(interval, run_backup)
        self.backup_timer.start()
        self.logger.info(f"Scheduled backups every {interval/3600} hours")

    def _initialize_password(self):
        """Initializes the admin password if not found in the database."""
        try:
            self.logger.info("Initializing default admin password")
            default_password = hashlib.sha256("harry123".encode()).hexdigest()
            self.db_manager.save_password(default_password)
            self.logger.info("Default admin password initialized")
            return default_password
        except (ProgrammingError, IntegrityError) as db_err:
            self.logger.error(f"Failed to initialize password: {db_err}")
            messagebox.showerror("Database Error", f"Failed to initialize password: {db_err}")
            return None

    def check_license(self):
        """Checks the license status and prompts for renewal if expired."""
        try:
            self.logger.info("Checking license status")
            with open("licence.json", "r") as f:
                license_data = json.load(f)
                expiration_date = datetime.strptime(license_data["expiration_date"], "%Y-%m-%d")
                grace_period = expiration_date + timedelta(days=7)
                current_date = datetime.now()

                if current_date > grace_period:
                    self.show_license_expired_message()
                    sys.exit()
                elif current_date > expiration_date:
                    self.show_license_expired_message()
                    self.prompt_for_license_renewal()
            self.logger.info("License check completed")
        except FileNotFoundError as fnf_err:
            self.logger.warning("License file not found, prompting for renewal")
            messagebox.showerror("License Error", "License file not found! Please renew the license.")
            self.prompt_for_license_renewal()
        except json.JSONDecodeError as json_err:
            self.logger.error(f"Invalid JSON in license file: {json_err}")
            messagebox.showerror("License Error", f"Invalid JSON in license file: {json_err}")
            raise
        except KeyError as key_err:
            self.logger.error(f"Missing expiration_date in license file: {key_err}")
            messagebox.showerror("License Error", f"Missing expiration_date in license file: {key_err}")
            raise
        except ValueError as val_err:
            self.logger.error(f"Invalid date format in license file: {val_err}")
            messagebox.showerror("License Error", f"Invalid date format in license file: {val_err}")
            raise

    def show_license_expired_message(self):
        """Displays a license expired message."""
        try:
            self.logger.warning("License expired, showing message")
            messagebox.showerror("License Expired", "Your application license has expired. Please renew.")
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to show license expired message: {tcl_err}")
            print(f"Failed to show license expired message: {tcl_err}")  # Fallback to console if GUI fails

    def prompt_for_license_renewal(self):
        """Prompts the user for a renewal key and updates the license."""
        try:
            self.logger.info("Prompting for license renewal")
            while True:
                renewal_key = simpledialog.askstring("License Expired", "Please enter the renewal key to continue:")
                if renewal_key == self.renewal_key:
                    new_expiration_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
                    self.renew_license(new_expiration_date)
                    break
                else:
                    self.logger.warning("Invalid renewal key entered")
                    messagebox.showerror("Invalid Key", "The renewal key you entered is incorrect. Try again.")
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to prompt for renewal key: {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to prompt for renewal key: {tcl_err}")
        except AttributeError as attr_err:
            self.logger.error(f"Invalid state for renewal prompt: {attr_err}")
            messagebox.showerror("Error", f"Invalid state for renewal prompt: {attr_err}")

    def renew_license(self, new_expiration_date):
        """Renews the license and restarts the application."""
        try:
            self.logger.info(f"Renewing license until {new_expiration_date}")
            with open("licence.json", "w") as f:
                json.dump({"expiration_date": new_expiration_date}, f, indent=4)
            messagebox.showinfo("License Renewed", f"Your license has been renewed until {new_expiration_date}.")
            python = sys.executable
            subprocess.Popen([python, sys.argv[0]])
            sys.exit()
            self.logger.info("License renewed and application restarted")
        except FileNotFoundError as fnf_err:
            self.logger.error(f"Failed to access license file: {fnf_err}")
            messagebox.showerror("File Error", f"Failed to access license file: {fnf_err}")
        except PermissionError as perm_err:
            self.logger.error(f"Permission denied while writing license file: {perm_err}")
            messagebox.showerror("File Error", f"Permission denied while writing license file: {perm_err}")
        except json.JSONEncodeError as json_err:
            self.logger.error(f"Failed to encode license data: {json_err}")
            messagebox.showerror("File Error", f"Failed to encode license data: {json_err}")
        except subprocess.SubprocessError as sub_err:
            self.logger.error(f"Failed to restart application: {sub_err}")
            messagebox.showerror("Error", f"Failed to restart application: {sub_err}")

    def login(self):
        try:
            self.logger.info("Attempting user login")
            username = self.gui.username_entry.get()
            if self.logic.login(username, self.gui.password_entry.get()):
                self.current_user = username
                self.gui.login_frame.destroy()
                self.dashboard_frame = tk.Frame(self.root)  # Create a new frame for dashboard
                self.dashboard_frame.pack(fill="both", expand=True)
                self.gui.create_dashboard(self.dashboard_frame)  # Pass the frame to populate
                self.logger.info("Login successful, dashboard created")
            else:
                messagebox.showerror("Login Failed", "Invalid credentials")
        except AttributeError as attr_err:
            self.logger.error(f"Failed to access login fields: {attr_err}")
            messagebox.showerror("GUI Error", f"Failed to access login fields: {attr_err}")

    def logout(self):
        """Log out the current user and return to login screen."""
        try:
            if self.current_user:
                self.logger.info(f"User {self.current_user} logging out")
                self.current_user = None
                if self.dashboard_frame:
                    self.dashboard_frame.destroy()  # Destroy only the dashboard frame
                    self.dashboard_frame = None
                self.gui.login_frame = self.gui.create_login_window()
                self.logger.info("Logout successful, returned to login screen")
            else:
                self.logger.warning("Logout attempted with no active user")
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to log out: {tcl_err}")
            messagebox.showerror("Logout Error", f"Failed to log out: {tcl_err}")

    def register_user(self):
        """Opens the user registration window."""
        try:
            self.logger.info("Opening register user window")
            self.gui.register_user()
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to open register user window: {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to open register user window: {tcl_err}")

    def save_user(self, username, password, role, window):
        """Saves a new user and closes the registration window on success."""
        try:
            self.logger.info(f"Saving new user: {username}, role: {role}")
            if self.logic.save_user(username, password, role):
                messagebox.showinfo("Success", "User registered successfully!")
                self.window_handler.close_window(window)
                self.logger.info(f"User {username} saved successfully")
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to close register window: {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to close register window: {tcl_err}")
        except TypeError as type_err:
            self.logger.error(f"Invalid input type for user: {type_err}")
            messagebox.showerror("Error", f"Invalid input type for user: {type_err}")

    def load_students_data(self):
        """Loads student data from an Excel file."""
        try:
            self.logger.info("Opening file dialog to load student data")
            file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
            if file_path and self.logic.load_students_data(file_path):
                self.logger.info(f"Loading students from file: {file_path}")
                messagebox.showinfo("Success", "Student data loaded successfully!")
                self.logger.info("Student data loaded successfully")
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to open file dialog: {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to open file dialog: {tcl_err}")
        except FileNotFoundError as fnf_err:
            self.logger.warning(f"File selection cancelled or not found: {fnf_err}")
            messagebox.showerror("File Error", f"File selection cancelled or not found: {fnf_err}")

    def load_books_from_excel(self):
        """Loads books from an Excel file."""
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
            if file_path and self.logic.load_books_from_excel(file_path):
                pass  # Success message handled in logic
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open file dialog: {tcl_err}")
        except FileNotFoundError as fnf_err:
            messagebox.showerror("File Error", f"File selection cancelled or not found: {fnf_err}")

    def add_student(self):
        """Opens the add student window."""
        try:
            self.gui.add_student()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open add student window: {tcl_err}")

    def save_student(self, student_id, name, stream, window=None):
        """Saves a new student with mandatory stream and closes the window on success."""
        self.logger.info(f"Saving student: {student_id}, name: {name}, stream: {stream}")
        try:
            # Basic validation in this layer (optional, since db_manager checks it)
            if not all([student_id, name, stream]):
                messagebox.showerror("Error", "Student ID, Name, and Stream are all required.")
                return False
            
            if self.logic.save_student(student_id, name, stream):
                messagebox.showinfo("Success", "Student added successfully!")
                self.window_handler.close_window(window)
                return True
            else:
                messagebox.showerror("Error", "Failed to save student")
                return False
        except Exception as e:
            self.logger.error(f"Failed to save student: {e}")
            messagebox.showerror("Error", f"Failed to save student: {e}")
            return False

    def add_teacher(self, teacher_id, teacher_name, window):
        """Adds a new teacher and closes the window on success."""
        try:
            if self.logic.add_teacher(teacher_id, teacher_name):
                messagebox.showinfo("Success", "Teacher added successfully!")
                self.window_handler.close_window(window)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to close teacher window: {tcl_err}")
        except TypeError as type_err:
            messagebox.showerror("Error", f"Invalid input type for teacher: {type_err}")

    def create_add_teacher_window(self):
        """Opens the add teacher window."""
        try:
            self.gui.create_add_teacher_window()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open add teacher window: {tcl_err}")

    def add_new_book(self):
        """Opens the add new book window."""
        try:
            self.gui.add_new_book()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open add new book window: {tcl_err}")

    def save_new_book(self, book_id, window):
        """Saves a new book (window can be None for QR code)."""
        try:
            if self.logic.add_new_book(book_id):
                messagebox.showinfo("Success", "Book added successfully!")
                if window:
                    self.window_handler.close_window(window)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to close book window: {tcl_err}")
        except TypeError as type_err:
            messagebox.showerror("Error", f"Invalid input type for book: {type_err}")

    def add_book_with_tags(self, book_id, tags=None):
        """Delegates adding a book with tags to LibraryLogic."""
        try:
            return self.logic.add_book_with_tags(book_id, tags)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add book with tags: {e}")
            return False


    def tag_book(self, book_id, tags):
        """Delegates adding tags to a book to LibraryLogic."""
        try:
            return self.logic.tag_book(book_id, tags)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to tag book: {e}")
            return False


    def view_all_books(self, tag_filter=None):
        """Delegates fetching all books with tag filter to LibraryLogic."""
        try:
            books = self.logic.view_all_books(tag_filter)
            self.gui.view_all_books(books)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view all books: {e}")


    def print_books(self, books):
        """Prints the book list to a file."""
        try:
            self.logic.print_books(books)
        except (FileNotFoundError, PermissionError, IOError) as file_err:
            messagebox.showerror("File Error", f"Failed to print books: {file_err}")

    def display_books_gui(self):
        """Displays all books in the inventory."""
        try:
            books = self.logic.get_all_books()
            self.gui.display_books_gui(books)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display books inventory: {tcl_err}")

    def borrow_book(self):
        """Opens the borrow book window for teachers."""
        try:
            self.gui.borrow_book()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open borrow book window: {tcl_err}")

    def borrow_book_teacher(self, teacher_id, book_id, window, condition="New"):
        """Handles a teacher borrowing a book with condition (window can be None for QR code)."""
        try:
            if self.logic.borrow_book_teacher(teacher_id, book_id, condition):
                messagebox.showinfo("Success", "Book borrowed successfully!")
                if window:
                    self.window_handler.close_window(window)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to close borrow window: {tcl_err}")
        except TypeError as type_err:
            messagebox.showerror("Error", f"Invalid input type for borrowing: {type_err}")

    def return_book(self):
        """Opens the return book window for teachers."""
        try:
            self.gui.return_book()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open return book window: {tcl_err}")

    def return_book_teacher(self, teacher_id, book_id, window, condition=None):
        """Handles a teacher returning a book with updated condition (window can be None for QR code)."""
        try:
            if self.logic.return_book_teacher(teacher_id, book_id, condition):
                messagebox.showinfo("Success", "Book returned successfully!")
                if window:
                    self.window_handler.close_window(window)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to close return window: {tcl_err}")
        except TypeError as type_err:
            messagebox.showerror("Error", f"Invalid input type for returning: {type_err}")

    def borrow_books_by_student(self):
        """Opens the student borrowing window."""
        try:
            self.gui.borrow_books_by_student()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open borrow books window: {tcl_err}")


    def save_revision_book(self, book_id, tags):
        """Save a revision book with tags."""
        try:
            if not self.logic.save_revision_book(book_id, tags):
                messagebox.showerror("Error", "Failed to save revision book.")
                return False
            self.logger.info(f"Revision book {book_id} saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving revision book: {e}")
            messagebox.showerror("Error", f"Error saving revision book: {e}")
            return False

    def borrow_revision_book(self, student_id, book_id, reminder_days, condition, window=None):
        success = self.logic.borrow_revision_book(student_id, book_id, reminder_days, condition)
        if success:
            messagebox.showinfo("Success", f"Revision book {book_id} borrowed successfully by {student_id}!")
            if window:
                self.window_handler.close_window(window)
            return True
        else:
            self.logger.error(f"Failed to borrow revision book {book_id} for student {student_id}")
            return False
            
    def return_revision_book(self, student_id, book_list_frame):
        student_name = self.db_manager.get_student_name(student_id)
        if not student_name:
            return None
        books = self.db_manager.get_student_borrowed_revision_books(student_id)
        return student_name, [book[0] for book in books]

    def view_revision_books(self, tag_filter=None):
        """Fetches revision books with an optional tag filter."""
        try:
            # Assuming revision books are fetched via LibraryLogic or DBManager
            books = self.logic.view_revision_books(tag_filter)  # Update logic method if needed
            return books
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch revision books: {e}")
            return []

    def view_students_with_revision_books(self, student_id_filter=None, name_filter=None):
        """Fetches students with revision books with optional filters."""
        try:
            students = self.logic.view_students_with_revision_books(student_id_filter, name_filter)
            return students  # Returns list of (student_id, name, stream, book_id, borrowed_on, reminder_days)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch students with revision books: {e}")
            return []


    def search_student_for_borrow(self, student_id, borrow_window, search_window, book_listbox, student_name_label):
        """Searches a student for borrowing."""
        try:
            self.logic.search_student_for_borrow(student_id, borrow_window, search_window, book_listbox, student_name_label)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to search student for borrowing: {tcl_err}")

    def add_book_to_borrow(self, book_id, book_listbox):
        """Adds a book to the borrowing list."""
        try:
            self.logic.add_book_to_borrow(book_id, book_listbox)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to add book to borrow list: {tcl_err}")

    def borrow_all_books(self, borrow_window, book_listbox):
        """Borrows all books for the student and hides the window on success."""
        try:
            if self.logic.borrow_all_books(borrow_window, book_listbox):
                borrow_window.withdraw()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to close borrow window: {tcl_err}")

    def _update_borrow_list(self, book_listbox):
        """Updates the borrowing listbox."""
        try:
            if not isinstance(book_listbox, tk.Listbox):
                raise AttributeError(f"Expected Listbox, got {type(book_listbox)}")
            book_listbox.delete(0, tk.END)
            for i, book_id in enumerate(self.borrowed_books):
                book_listbox.insert(tk.END, f"{i + 1}) Book ID: {book_id}")
        except AttributeError as attr_err:
            messagebox.showerror("Error", f"Failed to update borrow list: {attr_err}")


    def return_book_by_student(self):
        """Opens the student return book window."""
        try:
            self.gui.return_book_by_student()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open return books window: {tcl_err}")

    def search_student_for_return(self, student_id, student_name_label, book_list_frame, search_window=None):
        """Searches a student for returning books."""
        try:
            self.logic.search_student_for_return(student_id, student_name_label, book_list_frame, search_window)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to search student for return: {tcl_err}")

    def return_selected_books(self, student_id, frame, condition=None):
        try:
            self.logic.return_selected_books(student_id, frame, condition)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to return selected books: {tcl_err}")


    
    def return_selected_revision_books(self, student_id, selected_books, condition):
        self.logger.debug(f"Returning books for student {student_id}: {selected_books}")
        for book_id in selected_books:
            success = self.db_manager.return_book_student(student_id, book_id, condition)
            if not success:
                self.logger.warning(f"Failed to return book {book_id} for student {student_id}")
                messagebox.showerror("Error", f"Failed to return book {book_id}.")
                return False
        self.logger.info(f"Successfully returned {len(selected_books)} books for student {student_id}")
        return True

    def search_student(self):
        """Opens the student search window."""
        try:
            self.gui.search_student()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open search student window: {tcl_err}")

    def display_student_info(self, student_id, name_filter, filter_by_borrowed, filter_by_reams, result_label):
        """Displays student info with filters."""
        try:
            self.logger.info("Displaying student info with filters")
            self.logic.display_student_info(student_id, name_filter, filter_by_borrowed, filter_by_reams, result_label)
        except Exception as e:
            self.logger.error(f"Failed to display student info: {e}")
            result_label.config(text=f"Error displaying student info: {e}")


    def search_teacher(self):
        """Opens the teacher search window."""
        try:
            self.gui.search_teacher()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open search teacher window: {tcl_err}")



    def get_teacher_info(self, teacher_id):
        """Fetches teacher info for displaying current condition."""
        return self.logic.db_manager.get_teacher_info(teacher_id)  


    def display_teacher_info(self, teacher_id, name_filter, filter_by_borrowed, result_label):
        """Displays teacher info with filters."""
        try:
            self.logger.info("Displaying teacher info with filters")
            self.logic.display_teacher_info(teacher_id, name_filter, filter_by_borrowed, result_label)
        except Exception as e:
            self.logger.error(f"Failed to display teacher info: {e}")
            result_label.config(text=f"Error displaying teacher info: {e}")

    def graduate_students(self):
        try:
            self.logger.info("Graduating students to next class")
            return self.logic.graduate_students()  # Return the tuple (success, message)
        except Exception as e:
            self.logger.error(f"Failed to graduate students: {e}")
            return False, f"Error graduating students to next class: {e}"  # Return a fallback tuple

    def update_student_info(self, student_id, new_stream=None, new_locker=None, new_chair=None):
        self.logger.debug(f"Calling update_student_info with: student_id={student_id}, new_stream={new_stream}, new_locker={new_locker}, new_chair={new_chair}")
        try:
            self.logger.info("Updating students info")
            return self.logic.update_student_info(student_id, new_stream, new_locker, new_chair)
        except Exception as e:
            self.logger.error(f"Failed to update student info: {e}")
            return False, f"Error updating student info: {e}"

    def undo_graduate_students(self):
        try:
            self.logger.info("Undoing graduation of students")
            return self.logic.undo_graduate_students()
        except Exception as e:
            self.logger.error(f"Failed to undo graduate students: {e}")
            return False, f"Error undoing graduation: {e}"


    def display_unreturned_books_gui(self):
        """Displays unreturned books."""
        try:
            unreturned_books = self.logic.get_unreturned_books()
            self.gui.display_unreturned_books_gui(unreturned_books)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display unreturned books: {tcl_err}")


    def download_unreturned_info(self, unreturned_books):
        """Downloads unreturned books info."""
        try:
            self.logic.download_unreturned_info(unreturned_books)
        except (FileNotFoundError, PermissionError, IOError) as file_err:
            messagebox.showerror("File Error", f"Failed to download unreturned info: {file_err}")


    def open_add_ream_window(self):
        """Opens the add ream window."""
        try:
            self.gui.open_add_ream_window()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open add ream window: {tcl_err}")
            

    def add_ream(self, student_id, reams_brought, window):
        """Adds reams for a student and closes the window on success."""
        try:
            if self.logic.add_ream(student_id, reams_brought):
                self.window_handler.close_window(window)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to close ream window: {tcl_err}")
        except TypeError as type_err:
            messagebox.showerror("Error", f"Invalid input type for reams: {type_err}")

    def total_reams(self):
        """Displays total reams with form and stream breakdown."""
        try:
            total, student_reams, form_reams, form_stream_students, exported = self.logic.get_total_reams()
            self.gui.total_reams(total, form_reams, form_stream_students)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to display total reams: {tcl_err}")

    def used_reams(self):
        """Opens the used reams window."""
        try:
            self.gui.used_reams()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to open used reams window: {tcl_err}")

    def deduct_reams(self, used_reams, label):
        """Deducts reams and updates the label."""
        try:
            self.logic.deduct_reams(used_reams, label)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to update reams label: {tcl_err}")

    def update_reams_remaining(self, label):
        """Updates the reams remaining label."""
        try:
            self.logic.update_reams_remaining(label)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to update reams remaining: {tcl_err}")


    
    def get_all_reams_report(self, student_id_filter=None, date_start=None, date_end=None, min_reams=None, view_mode="detailed"):
        """Fetches the all reams report with filters and view mode."""
        try:
            return self.logic.get_all_reams_report(student_id_filter, date_start, date_end, min_reams, view_mode)
        except Exception as e:
            self.logger.error(f"Failed to fetch all reams report: {e}")
            messagebox.showerror("Error", f"Failed to fetch all reams report: {e}")
            return []


    def download_all_reams_report(self, reams, output_dir):
        """Downloads the all reams report as a PDF."""
        try:
            return self.logic.download_all_reams_report(reams, output_dir)
        except Exception as e:
            self.logger.error(f"Failed to download all reams report: {e}")
            messagebox.showerror("Error", f"Failed to download all reams report: {e}")
            return None


    def export_reams_to_excel(self, output_dir):
        """Delegates exporting reams to LibraryLogic."""
        try:
            return self.logic.export_reams_to_excel(output_dir)
        except Exception as e:
            self.logger.error(f"Failed to export reams: {e}")
            messagebox.showerror("Error", f"Failed to export reams: {e}")
            return False

    def import_reams_from_excel(self, excel_file_path):
        """Delegates importing reams from Excel to LibraryLogic."""
        try:
            return self.logic.import_reams_from_excel(excel_file_path)
        except Exception as e:
            self.logger.error(f"Failed to import reams: {e}")
            messagebox.showerror("Error", f"Failed to import reams: {e}")
            return False


    
    def get_books_by_condition_report(self, condition_filter=None):
        """Fetches the books by condition report with an optional filter."""
        try:
            return self.logic.get_books_by_condition_report(condition_filter)
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to fetch books by condition report: {tcl_err}")
            return {"New": [], "Good": [], "Damaged": []}



    def open_qr_scanner(self, mode="general" ):
        """Open the QR Code Scanner GUI in a separate window."""
        self.logger.info(f"Opening QR Code Scanner GUI in {mode} mode")
        try:
            qr_window = tk.Toplevel(self.root)
            qr_window.title("QR Code Scanner - Borrow Mode")
            qr_window.geometry("800x600")
            qr_app = QRCodeScannerGUI(qr_window, self.db_manager)
            qr_window.protocol("WM_DELETE_WINDOW", qr_window.destroy)  
            qr_window.transient(self.root)  
            qr_window.grab_set()  
        except Exception as e:
            self.logger.error(f"Failed to open QR scanner: {e}")
            messagebox.showerror("QR Scanner Error", f"Failed to open QR scanner: {e}")


    def generate_qr_code(self, entity_type, entity_id):
        """Generates a QR code for a specified entity type and ID."""
        try:
            return self.logic.generate_qr_code(entity_type, entity_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code in management system: {e}")
            return None, None


    def generate_bulk_book_qrcodes_pdf(self, book_class, subject, form, number_of_books, year, output_dir, save_directly=True):
        """Generates QR codes for multiple books in a PDF, with option for preview."""
        try:
            return self.logic.generate_bulk_book_qrcodes_pdf(book_class, subject, form, number_of_books, year, output_dir, save_directly)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bulk QR codes: {e}")
            return None

            
    def get_all_books(self, tag_filter=None):
        """Delegates fetching all books with tag filter to LibraryLogic."""
        try:
            return self.logic.get_all_books(tag_filter)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch all books: {e}")
            return []


    def get_unreturned_books(self):
        """Fetches all unreturned books."""
        try:
            return self.logic.get_unreturned_books()
        except Exception as e:
            self.logger.error(f"Failed to fetch unreturned books: {e}")
            messagebox.showerror("Error", f"Failed to fetch unreturned books: {e}")
            return []



    def bulk_borrow_books(self, file_path=None, borrowings=None):
        """Delegates bulk borrowing to LibraryLogic."""
        try:
            return self.logic.bulk_borrow_books(file_path, borrowings)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to perform bulk borrow: {e}")
            return 0, []

    def bulk_return_books(self, file_path=None, returns=None):
        """Delegates bulk returning to LibraryLogic."""
        try:
            return self.logic.bulk_return_books(file_path, returns)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to perform bulk return: {e}")
            return 0, []

    

    def export_library(self, output_dir=".", format="csv", progress_callback=None):
        """Delegates library export to LibraryLogic with progress callback."""
        try:
            return self.logic.export_library(output_dir, format, progress_callback)
        except Exception as e:
            self.logger.error(f"Failed to export library data: {e}")
            messagebox.showerror("Error", f"Failed to export library data: {e}")
            return False

    def import_library(self, file_path=None, directory=None, format="csv", incremental=False, progress_callback=None):
        """Delegates library import to LibraryLogic with incremental option and progress callback."""
        try:
            return self.logic.import_library(file_path, directory, format, incremental, progress_callback)
        except Exception as e:
            self.logger.error(f"Failed to import library data: {e}")
            messagebox.showerror("Error", f"Failed to import library data: {e}")
            return False


    def manual_backup(self):
        """Trigger a manual backup from the GUI."""
        success = backup_database(encrypt=True)
        if success:
            self.logger.info("Manual backup completed successfully")
        else:
            self.logger.error("Manual backup failed")


    
    def check_reminders(self, user_id):
        """Checks for overdue revision books based on user-specific reminder settings and returns a detailed message."""
        try:
            if not user_id:
                self.logger.warning("No user ID provided for checking reminders")
                return None

            frequency, sound_enabled = self.get_reminder_settings(user_id)  
            if frequency == "disabled":
                self.logger.debug(f"Reminders disabled for user {user_id}")
                return None

            overdue_books = self.db_manager.check_overdue_revision_books()
            if not overdue_books:
                self.logger.debug(f"No overdue revision books found for user {user_id}")
                return None

            today = datetime.now().date()
            filtered_overdue = []
            for student_id, name, book_id, borrowed_on, reminder_days in overdue_books:
                due_date = borrowed_on + timedelta(days=reminder_days)
                days_overdue = (today - due_date).days
                if days_overdue > 0:
                    check_frequency = 1 if frequency == "daily" else 7
                    if days_overdue % check_frequency == 0:
                        filtered_overdue.append((student_id, name, book_id, due_date, days_overdue))

            if filtered_overdue:
                reminder_text = "Overdue Revision Books:\n"
                reminder_text += "\n".join(
                    f"Student: {name} (ID: {student_id}), Book: {book_id}, Due: {due_date.strftime('%Y-%m-%d')}, Overdue: {days} days"
                    for student_id, name, book_id, due_date, days in filtered_overdue
                )
                self.logger.info(f"Overdue revision books found for user {user_id}: {reminder_text}")
                if sound_enabled:
                    try:
                        import winsound
                        winsound.Beep(1000, 500)
                    except ImportError:
                        self.logger.warning("Sound not available; winsound not installed.")
                return reminder_text
            self.logger.debug(f"No overdue revision books found for user {user_id} after frequency filter")
            return None
        except AttributeError as attr_err:
            self.logger.error(f"Failed to check reminders due to invalid state: {attr_err}")
            messagebox.showerror("Error", f"Failed to check reminders due to invalid state: {attr_err}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in check_reminders: {e}")
            messagebox.showerror("Error", f"Unexpected error in check_reminders: {e}")
            return None

    


    def save_reminder_settings(self, user_id, reminder_frequency, sound_enabled):
        """Delegates saving reminder settings to LibraryLogic."""
        try:
            return self.logic.save_reminder_settings(user_id, reminder_frequency, sound_enabled)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save reminder settings: {e}")
            return False

    def get_reminder_settings(self, user_id):
        """Delegates fetching reminder settings to LibraryLogic."""
        try:
            return self.logic.get_reminder_settings(user_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch reminder settings: {e}")
            return "daily", True

    
    def start_reminder_check(self, reminder_label):
        """Starts the reminder check loop and updates the GUI label."""
        def check_and_update():
            try:
                if not self.current_user:
                    self.logger.warning("No current user set for reminder check")
                    self.gui.update_reminder_label(reminder_label, "No user logged in for reminders")
                else:
                    user_id = self.current_user 
                    reminder_text = self.logic.check_reminders(user_id)
                    if reminder_text:
                        self.gui.update_reminder_label(reminder_label, reminder_text)
                        winsound.Beep(1000, 1000)  # 1000 Hz, 1 second beep
                        self.logger.info("Reminder triggered for overdue revision books")
                    else:
                        self.gui.update_reminder_label(reminder_label, "No overdue revision books")
            except Exception as e:
                self.logger.error(f"Failed to check reminders: {e}")
                self.gui.update_reminder_label(reminder_label, f"Reminder check failed: {e}")
            # Schedule the next check (60 seconds)
            self.reminder_after_id = self.root.after(60000, check_and_update)

        # Start the loop
        self.reminder_after_id = self.root.after(0, check_and_update)  # Start immediately

     

    def delete_from_system(self, entity_type, identifier):
        """Delegates deletion to LibraryLogic."""
        try:
            success = self.logic.delete_from_system(entity_type, identifier)
            if success:
                messagebox.showinfo("Success", f"Deleted {entity_type} successfully!")
            else:
                messagebox.showerror("Error", f"Failed to delete {entity_type}.")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete {entity_type}: {e}")
            messagebox.showerror("Error", f"Failed to delete {entity_type}: {e}")
            return False


    def search_book_borrow_details(self, book_id):
        """Searches for book borrowing details and displays results."""
        try:
            result = self.logic.search_book_borrow_details(book_id)
            if result is None:
                messagebox.showerror("Error", f"Book ID {book_id} not found in the system.")
            elif result["borrower_type"] == "none":
                messagebox.showinfo("Book Status", f"Book ID: {book_id}\nStatus: {result['message']}")
            else:
                messagebox.showinfo(
                    "Book Borrow Details",
                    f"Book ID: {result['book_id']}\n"
                    f"Borrower Type: {result['borrower_type'].capitalize()}\n"
                    f"Borrower ID: {result['borrower_id']}\n"
                    f"Borrower Name: {result['borrower_name']}\n"
                    f"Borrowed On: {result['borrowed_on']}"
                )
        except Exception as e:
            self.logger.error(f"Failed to search book {book_id}: {e}")
            messagebox.showerror("Error", f"Failed to search book: {e}")


    def assign_locker(self, student_id, locker_id):
        try:
            self.logger.info(f"Assigning locker {locker_id} to student {student_id}")
            return self.logic.assign_locker(student_id, locker_id)
        except Exception as e:
            self.logger.error(f"Failed to assign locker: {e}")
            return False

    def assign_chair(self, student_id, chair_id):
        try:
            self.logger.info(f"Assigning chair {chair_id} to student {student_id}")
            return self.logic.assign_chair(student_id, chair_id)
        except Exception as e:
            self.logger.error(f"Failed to assign chair: {e}")
            return False

    def get_furniture_status(self, furniture_type):
        try:
            self.logger.info(f"Fetching furniture status for {furniture_type}")
            return self.logic.get_furniture_status(furniture_type)
        except Exception as e:
            self.logger.error(f"Failed to get furniture status: {e}")
            return []

    def unassign_locker(self, student_id, locker_id):
        try:
            self.logger.info(f"Unassigning locker {locker_id} from student {student_id}")
            return self.logic.unassign_locker(student_id, locker_id)
        except Exception as e:
            self.logger.error(f"Failed to unassign locker: {e}")
            return False

    # Methods from _populate_furniture_tab
    def view_locker_status_gui(self):
        try:
            self.logger.info("Opening locker status GUI")
            self.gui.view_locker_status_gui()
        except Exception as e:
            self.logger.error(f"Failed to open locker status GUI: {e}")
            tk.messagebox.showerror("Error", f"Failed to view locker status: {e}")

    def view_chair_status_gui(self):
        try:
            self.logger.info("Opening chair status GUI")
            self.gui.view_chair_status_gui()
        except Exception as e:
            self.logger.error(f"Failed to open chair status GUI: {e}")
            tk.messagebox.showerror("Error", f"Failed to view chair status: {e}")

    def report_damaged_locker_gui(self):
        try:
            self.logger.info("Opening report damaged locker GUI")
            self.gui.report_damaged_locker_gui()
        except Exception as e:
            self.logger.error(f"Failed to report damaged locker: {e}")
            tk.messagebox.showerror("Error", f"Failed to report damaged locker: {e}")

    def report_damaged_chair_gui(self):
        try:
            self.logger.info("Opening report damaged chair GUI")
            self.gui.report_damaged_chair_gui()
        except Exception as e:
            self.logger.error(f"Failed to report damaged chair: {e}")
            tk.messagebox.showerror("Error", f"Failed to report damaged chair: {e}")

    def generate_furniture_ids_gui(self):
        try:
            self.logger.info("Opening generate furniture IDs GUI")
            self.gui.generate_furniture_ids_gui()
        except Exception as e:
            self.logger.error(f"Failed to generate furniture IDs: {e}")
            tk.messagebox.showerror("Error", f"Failed to generate furniture IDs: {e}")

    def search_locker_gui(self):
        try:
            self.logger.info("Opening search locker GUI")
            self.gui.search_locker_gui()
        except Exception as e:
            self.logger.error(f"Failed to search locker: {e}")
            tk.messagebox.showerror("Error", f"Failed to search locker: {e}")

    def search_chair_gui(self):
        try:
            self.logger.info("Opening search chair GUI")
            self.gui.search_chair_gui()
        except Exception as e:
            self.logger.error(f"Failed to search chair: {e}")
            tk.messagebox.showerror("Error", f"Failed to search chair: {e}")

    def display_all_furniture_gui(self):
        try:
            self.logger.info("Opening display all furniture GUI")
            self.gui.display_all_furniture_gui()
        except Exception as e:
            self.logger.error(f"Failed to display all furniture: {e}")
            tk.messagebox.showerror("Error", f"Failed to display all furniture: {e}")

    def display_furniture_details_gui(self):
        try:
            self.logger.info("Opening display furniture details GUI")
            self.gui.display_furniture_details_gui()
        except Exception as e:
            self.logger.error(f"Failed to display furniture details: {e}")
            tk.messagebox.showerror("Error", f"Failed to display furniture details: {e}")

    def add_furniture_category_gui(self):
        try:
            self.logger.info("Opening add furniture category GUI")
            self.gui.add_furniture_category_gui()
        except Exception as e:
            self.logger.error(f"Failed to add furniture category: {e}")
            tk.messagebox.showerror("Error", f"Failed to add furniture category: {e}")

    def display_furniture_categories_gui(self):
        try:
            self.logger.info("Opening display furniture categories GUI")
            self.gui.display_furniture_categories_gui()
        except Exception as e:
            self.logger.error(f"Failed to display furniture categories: {e}")
            tk.messagebox.showerror("Error", f"Failed to display furniture categories: {e}")

    def load_chairs_from_excel(self, file_path):
        try:
            self.logger.info(f"Calling load_chairs_from_excel with file: {file_path}")
            return self.logic.load_chairs_from_excel(file_path)
        except Exception as e:
            self.logger.error(f"Failed to load chairs from Excel: {e}")
            return False, f"Error loading chairs: {e}"

    def load_lockers_from_excel(self, file_path):
        try:
            self.logger.info(f"Calling load_lockers_from_excel with file: {file_path}")
            return self.logic.load_lockers_from_excel(file_path)
        except Exception as e:
            self.logger.error(f"Failed to load lockers from Excel: {e}")
            return False, f"Error loading lockers: {e}"
    

    def display_students_by_form(self):
        try:
            self.logger.info("Calling display_students_by_form")
            return self.logic.display_students_by_form()
        except Exception as e:
            self.logger.error(f"Failed to display students by form: {e}")
            return False, f"Error displaying students by form: {e}"
    

    def add_short_form_mapping(self, short_form, full_name, mapping_type):
        try:
            self.logger.info(f"Adding short form mapping: {short_form} -> {full_name} ({mapping_type})")
            return self.logic.add_short_form_mapping(short_form, full_name, mapping_type)
        except Exception as e:
            self.logger.error(f"Failed to add short form mapping: {e}")
            return False, f"Error adding short form mapping: {e}"

    def get_short_form_mappings(self):
        try:
            self.logger.info("Fetching short form mappings")
            return self.logic.get_short_form_mappings()
        except Exception as e:
            self.logger.error(f"Failed to fetch short form mappings: {e}")
            return False, f"Error fetching short form mappings: {e}"


    def get_students_without_borrowed_books(self):
        """Fetches students without borrowed books from the logic layer."""
        try:
            return self.logic.get_students_without_borrowed_books()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to get students without borrowed books: {tcl_err}")
            return []

    def show_students_without_borrowed_books(self):
        """Displays students without borrowed books."""
        try:
            self.gui.show_students_without_borrowed_books()
        except tk.TclError as tcl_err:
            messagebox.showerror("GUI Error", f"Failed to show students without borrowed books: {tcl_err}")

    def on_closing(self):
        """Close the database connection and exit."""
        if self.connection:
            close_db_connection(self.connection)
            self.logger.info("Database connection closed")
        
        if self.backup_timer is not None:
            self.root.after_cancel(self.backup_timer)

        if self.reminder_after_id:
            self.root.after_cancel(self.reminder_after_id)

        self.root.quit()
        self.root.destroy()
    

def main():
    root = tk.Tk()
    root.withdraw()  
    conn = initialize_database()  
    if not conn or isinstance(conn, bool):
        logging.error("Failed to initialize database, exiting")
        messagebox.showerror("Startup Error", "Failed to initialize database. Check logs.")
        root.destroy()
        return
    try:
        app = LibraryManagementSystem(root, conn)
        root.mainloop()
    except RuntimeError as e:
        logging.error(f"Application startup failed: {e}")
        messagebox.showerror("Startup Error", str(e))
        root.destroy()

if __name__ == "__main__":
    main()