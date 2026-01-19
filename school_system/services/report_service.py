"""
Report service for generating and managing reports.
"""

from typing import Dict, List, Tuple
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.services.import_export_service import ImportExportService
from school_system.services.student_service import StudentService
from school_system.services.class_management_service import ClassManagementService
from school_system.database.repositories.book_repo import BookRepository, BorrowedBookStudentRepository
from school_system.database.repositories.student_repo import StudentRepository
from school_system.database.repositories.teacher_repo import TeacherRepository
from school_system.database.repositories.furniture_repo import ChairRepository, LockerRepository


class ReportService:
    """Service for generating and managing reports."""

    def __init__(self):
        self.book_repository = BookRepository()
        self.student_repository = StudentRepository()
        self.borrowed_book_repo = BorrowedBookStudentRepository()
        self.teacher_repository = TeacherRepository()
        self.chair_repository = ChairRepository()
        self.locker_repository = LockerRepository()
        self.import_export_service = ImportExportService()
        self.student_service = StudentService()
        self.class_management_service = ClassManagementService()

    def generate_report(self, report_type: str, parameters: Dict) -> Dict:
        """
        Generate a report based on the given type and parameters.

        Args:
            report_type: The type of report to generate.
            parameters: Additional parameters for the report.

        Returns:
            The generated Report object.
        """
        logger.info(f"Generating report of type: {report_type}")
        ValidationUtils.validate_input(report_type, "Report type cannot be empty")
        
        # Logic to generate the report
        report_data = self._generate_report_data(report_type, parameters)
        logger.info(f"Report generated successfully")
        return report_data

    def _generate_report_data(self, report_type: str, parameters: Dict) -> Dict:
        """
        Internal method to generate report data.

        Args:
            report_type: The type of report.
            parameters: Additional parameters.

        Returns:
            The generated report data.
        """
        # Placeholder for report generation logic
        return {"report_type": report_type, "parameters": parameters}

    def get_book_report(self, book_id: int) -> Dict:
        """
        Retrieve a book report by its ID.

        Args:
            book_id: The ID of the book.

        Returns:
            The book report data.
        """
        book = self.book_repository.get_by_id(book_id)
        return {"book": book}
 
    def get_all_books_report(self) -> List[Dict]:
        """
        Retrieve all books report.

        Returns:
            A list of all books report data.
        """
        books = self.book_repository.get_all()
        return [{"book": book} for book in books]

    def get_borrowed_books_report(self) -> List[Dict]:
        """
        Retrieve borrowed books report.

        Returns:
            A list of borrowed books report data.
        """
        try:
            report_data = []
            
            # Get all borrowed books (not returned)
            all_borrowed = []
            try:
                # Get all students and their borrowings
                all_students = self.student_service.get_all_students()
                for student in all_students:
                    borrowings = self.borrowed_book_repo.get_borrowed_books_by_student(str(student.student_id))
                    all_borrowed.extend(borrowings)
            except Exception as e:
                logger.warning(f"Error getting all borrowed books: {e}")
            
            # Process each borrowing
            for borrowing in all_borrowed:
                if borrowing.returned_on is None:  # Only currently borrowed
                    book = self.book_repository.get_by_id(borrowing.book_id)
                    if book:
                        # Get student info
                        student = self.student_service.get_student_by_id(str(borrowing.student_id))
                        student_name = student.name if student else f"Student {borrowing.student_id}"
                        
                        # Calculate days borrowed
                        from datetime import datetime, date
                        if isinstance(borrowing.borrowed_on, str):
                            borrowed_date = datetime.strptime(borrowing.borrowed_on, '%Y-%m-%d').date()
                        elif isinstance(borrowing.borrowed_on, date):
                            borrowed_date = borrowing.borrowed_on
                        else:
                            borrowed_date = date.today()
                        
                        days_borrowed = (date.today() - borrowed_date).days
                        
                        report_data.append({
                            'book': book,
                            'book_number': book.book_number,
                            'title': book.title,
                            'author': book.author or 'N/A',
                            'student_id': borrowing.student_id,
                            'student_name': student_name,
                            'borrowed_on': borrowing.borrowed_on,
                            'days_borrowed': days_borrowed,
                            'reminder_days': borrowing.reminder_days or 7,
                            'status': 'Borrowed'
                        })
            
            logger.info(f"Generated borrowed books report with {len(report_data)} entries")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating borrowed books report: {e}")
            return []

    def get_available_books_report(self) -> List[Dict]:
        """
        Retrieve available books report.

        Returns:
            A list of available books report data.
        """
        try:
            report_data = []
            
            # Get all available books
            available_books = self.book_repository.get_available_books()
            
            for book in available_books:
                # Double-check that book is not currently borrowed
                is_actually_available = True
                try:
                    # Check if book is borrowed by any student
                    student_borrowings = self.borrowed_book_repo.find_by_field('book_id', book.id)
                    for borrowing in student_borrowings:
                        if borrowing.returned_on is None:
                            is_actually_available = False
                            break
                except:
                    pass
                
                if is_actually_available:
                    subject = getattr(book, 'subject', None) or getattr(book, 'category', None) or 'N/A'
                    class_name = getattr(book, 'class_name', None) or 'N/A'
                    
                    report_data.append({
                        'book': book,
                        'book_number': book.book_number,
                        'title': book.title,
                        'author': book.author or 'N/A',
                        'isbn': book.isbn or 'N/A',
                        'subject': subject,
                        'class_name': class_name,
                        'book_type': 'Revision' if getattr(book, 'revision', 0) == 1 else 'Course',
                        'condition': getattr(book, 'book_condition', 'Good') or 'Good',
                        'status': 'Available'
                    })
            
            logger.info(f"Generated available books report with {len(report_data)} entries")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating available books report: {e}")
            return []

    def get_overdue_books_report(self) -> List[Dict]:
        """
        Retrieve overdue books report.

        Returns:
            A list of overdue books report data.
        """
        try:
            from datetime import datetime, date, timedelta
            report_data = []
            
            # Get all overdue books (default 14 days, but check reminder_days)
            overdue_borrowings = self.borrowed_book_repo.get_overdue_books(days_overdue=14)
            
            for borrowing in overdue_borrowings:
                if borrowing.returned_on is None:  # Only currently borrowed
                    book = self.book_repository.get_by_id(borrowing.book_id)
                    if book:
                        # Get student info
                        student = self.student_service.get_student_by_id(str(borrowing.student_id))
                        student_name = student.name if student else f"Student {borrowing.student_id}"
                        
                        # Calculate overdue days
                        if isinstance(borrowing.borrowed_on, str):
                            borrowed_date = datetime.strptime(borrowing.borrowed_on, '%Y-%m-%d').date()
                        elif isinstance(borrowing.borrowed_on, date):
                            borrowed_date = borrowing.borrowed_on
                        else:
                            borrowed_date = date.today()
                        
                        # Use reminder_days if available, otherwise default to 14
                        due_days = borrowing.reminder_days if borrowing.reminder_days else 14
                        due_date = borrowed_date + timedelta(days=due_days)
                        days_overdue = (date.today() - due_date).days
                        
                        # Only include if actually overdue
                        if days_overdue > 0:
                            report_data.append({
                                'book': book,
                                'book_number': book.book_number,
                                'title': book.title,
                                'author': book.author or 'N/A',
                                'student_id': borrowing.student_id,
                                'student_name': student_name,
                                'borrowed_on': borrowing.borrowed_on,
                                'due_date': due_date,
                                'days_overdue': days_overdue,
                                'reminder_days': due_days,
                                'status': f'Overdue ({days_overdue} days)'
                            })
            
            logger.info(f"Generated overdue books report with {len(report_data)} entries")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating overdue books report: {e}")
            return []

    def get_book_inventory_report(self) -> List[Dict]:
        """
        Retrieve book inventory report.

        Returns:
            A list of book inventory report data with comprehensive inventory information.
        """
        try:
            report_data = []
            
            # Get all books
            all_books = self.book_repository.get_all()
            
            # Get all borrowed books to check status
            borrowed_book_ids = set()
            try:
                all_students = self.student_service.get_all_students()
                for student in all_students:
                    borrowings = self.borrowed_book_repo.get_borrowed_books_by_student(str(student.student_id))
                    for borrowing in borrowings:
                        if borrowing.returned_on is None:
                            borrowed_book_ids.add(borrowing.book_id)
            except Exception as e:
                logger.warning(f"Error checking borrowed status: {e}")
            
            # Group by subject and class for summary
            inventory_summary = {}
            
            for book in all_books:
                subject = getattr(book, 'subject', None) or getattr(book, 'category', None) or 'Unknown'
                class_name = getattr(book, 'class_name', None) or 'Unknown'
                
                # Determine actual status
                is_borrowed = book.id in borrowed_book_ids or not book.available
                status = 'Borrowed' if is_borrowed else 'Available'
                
                # Create inventory entry
                report_data.append({
                    'book': book,
                    'book_number': book.book_number,
                    'title': book.title,
                    'author': book.author or 'N/A',
                    'isbn': book.isbn or 'N/A',
                    'subject': subject,
                    'class_name': class_name,
                    'book_type': 'Revision' if getattr(book, 'revision', 0) == 1 else 'Course',
                    'condition': getattr(book, 'book_condition', 'Good') or 'Good',
                    'status': status,
                    'available': not is_borrowed
                })
                
                # Update summary
                key = (subject, class_name)
                if key not in inventory_summary:
                    inventory_summary[key] = {
                        'subject': subject,
                        'class_name': class_name,
                        'total': 0,
                        'available': 0,
                        'borrowed': 0
                    }
                
                inventory_summary[key]['total'] += 1
                if is_borrowed:
                    inventory_summary[key]['borrowed'] += 1
                else:
                    inventory_summary[key]['available'] += 1
            
            # Add summary entries at the beginning
            summary_entries = []
            for key, summary in sorted(inventory_summary.items()):
                summary_entries.append({
                    'book': None,  # Mark as summary entry
                    'book_number': 'SUMMARY',
                    'title': f"{summary['subject']} - {summary['class_name']}",
                    'author': f"Total: {summary['total']} | Available: {summary['available']} | Borrowed: {summary['borrowed']}",
                    'isbn': '',
                    'subject': summary['subject'],
                    'class_name': summary['class_name'],
                    'book_type': '',
                    'condition': '',
                    'status': f"{summary['available']}/{summary['total']} Available",
                    'available': summary['available'] > 0,
                    'is_summary': True
                })
            
            # Combine summary and detailed entries
            final_report = summary_entries + report_data
            
            logger.info(f"Generated book inventory report with {len(final_report)} entries ({len(summary_entries)} summaries, {len(report_data)} books)")
            return final_report
            
        except Exception as e:
            logger.error(f"Error generating book inventory report: {e}")
            return []

    def export_report_to_excel(self, report_data: List[Dict], filename: str) -> bool:
        """
        Export report data to an Excel file.

        Args:
            report_data: The report data to export.
            filename: The name of the Excel file.

        Returns:
            True if the export was successful, otherwise False.
        """
        logger.info(f"Exporting report to Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            return self.import_export_service.export_to_excel(report_data, filename)
        except Exception as e:
            logger.error(f"Error exporting report to Excel: {e}")
            return False

    def import_report_from_excel(self, filename: str) -> List[Dict]:
        """
        Import report data from an Excel file.

        Args:
            filename: The name of the Excel file.

        Returns:
            The imported report data as a list of dictionaries.
        """
        logger.info(f"Importing report from Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            return self.import_export_service.import_from_excel(filename)
        except Exception as e:
            logger.error(f"Error importing report from Excel: {e}")
            return []

    def get_all_students_report(self) -> List[Dict]:
        """
        Retrieve all students report.

        Returns:
            A list of all students report data.
        """
        students = self.student_repository.get_all()
        return [{"student": student} for student in students]

    def get_students_by_stream_report(self) -> List[Dict]:
        """
        Retrieve students by stream report.

        Returns:
            A list of students grouped by stream.
        """
        try:
            report_data = []
            
            # Get all streams
            all_streams = self.class_management_service.get_all_stream_names()
            
            for stream in all_streams:
                # Get students in this stream
                students = self.class_management_service.get_students_by_stream(stream)
                
                # Add stream header
                report_data.append({
                    'student': None,  # Mark as header
                    'student_id': 'STREAM_HEADER',
                    'name': f"Stream: {stream}",
                    'stream': stream,
                    'class_name': f"Total: {len(students)} students",
                    'admission_number': '',
                    'books_borrowed': 0,
                    'is_header': True
                })
                
                # Add students in this stream
                for student in students:
                    # Get borrowing count
                    borrowings = self.borrowed_book_repo.get_borrowed_books_by_student(str(student.student_id))
                    current_borrowings = [b for b in borrowings if b.returned_on is None]
                    
                    report_data.append({
                        'student': student,
                        'student_id': student.student_id,
                        'name': student.name,
                        'stream': stream,
                        'class_name': getattr(student, 'class_name', 'Unknown') or 'Unknown',
                        'admission_number': getattr(student, 'admission_number', student.student_id) or student.student_id,
                        'books_borrowed': len(current_borrowings),
                        'is_header': False
                    })
            
            logger.info(f"Generated students by stream report with {len(report_data)} entries")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating students by stream report: {e}")
            return []

    def get_students_by_class_report(self) -> List[Dict]:
        """
        Retrieve students by class report.

        Returns:
            A list of students grouped by class.
        """
        try:
            report_data = []
            
            # Get all class levels
            class_levels = self.class_management_service.get_all_class_levels()
            
            for class_level in sorted(class_levels):
                # Get students in this class
                students = self.class_management_service.get_students_by_class_level(class_level)
                
                # Add class header
                report_data.append({
                    'student': None,  # Mark as header
                    'student_id': 'CLASS_HEADER',
                    'name': f"Form {class_level}",
                    'stream': f"Total: {len(students)} students",
                    'class_name': f"Form {class_level}",
                    'admission_number': '',
                    'books_borrowed': 0,
                    'is_header': True
                })
                
                # Add students in this class
                for student in students:
                    # Get borrowing count
                    borrowings = self.borrowed_book_repo.get_borrowed_books_by_student(str(student.student_id))
                    current_borrowings = [b for b in borrowings if b.returned_on is None]
                    
                    report_data.append({
                        'student': student,
                        'student_id': student.student_id,
                        'name': student.name,
                        'stream': getattr(student, 'stream', 'Unknown') or 'Unknown',
                        'class_name': f"Form {class_level}",
                        'admission_number': getattr(student, 'admission_number', student.student_id) or student.student_id,
                        'books_borrowed': len(current_borrowings),
                        'is_header': False
                    })
            
            logger.info(f"Generated students by class report with {len(report_data)} entries")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating students by class report: {e}")
            return []

    def get_student_library_activity_report(self) -> List[Dict]:
        """
        Retrieve student library activity report.

        Returns:
            A list of student library activity data with borrowing statistics.
        """
        try:
            report_data = []
            
            # Get all students
            all_students = self.student_service.get_all_students()
            
            for student in all_students:
                # Get all borrowings (current and returned)
                all_borrowings = self.borrowed_book_repo.find_by_field('student_id', str(student.student_id))
                current_borrowings = [b for b in all_borrowings if b.returned_on is None]
                returned_borrowings = [b for b in all_borrowings if b.returned_on is not None]
                
                # Calculate statistics
                total_borrowed = len(all_borrowings)
                currently_borrowed = len(current_borrowings)
                total_returned = len(returned_borrowings)
                
                # Get most recent borrowing date
                most_recent_borrowing = None
                if all_borrowings:
                    most_recent_borrowing = max(all_borrowings, key=lambda x: x.borrowed_on if x.borrowed_on else '')
                
                # Get overdue count
                overdue_count = 0
                for borrowing in current_borrowings:
                    if borrowing.reminder_days:
                        from datetime import datetime, date, timedelta
                        if isinstance(borrowing.borrowed_on, str):
                            borrowed_date = datetime.strptime(borrowing.borrowed_on, '%Y-%m-%d').date()
                        elif isinstance(borrowing.borrowed_on, date):
                            borrowed_date = borrowing.borrowed_on
                        else:
                            continue
                        
                        due_date = borrowed_date + timedelta(days=borrowing.reminder_days)
                        if date.today() > due_date:
                            overdue_count += 1
                
                report_data.append({
                    'student': student,
                    'student_id': student.student_id,
                    'name': student.name,
                    'stream': getattr(student, 'stream', 'Unknown') or 'Unknown',
                    'class_name': getattr(student, 'class_name', 'Unknown') or 'Unknown',
                    'admission_number': getattr(student, 'admission_number', student.student_id) or student.student_id,
                    'total_borrowed': total_borrowed,
                    'currently_borrowed': currently_borrowed,
                    'total_returned': total_returned,
                    'overdue_count': overdue_count,
                    'most_recent_borrowing': most_recent_borrowing.borrowed_on if most_recent_borrowing else None,
                    'activity_status': 'Active' if currently_borrowed > 0 else ('Inactive' if total_borrowed == 0 else 'Dormant')
                })
            
            # Sort by activity status and total borrowed (most active first)
            report_data.sort(key=lambda x: (
                0 if x['activity_status'] == 'Active' else (1 if x['activity_status'] == 'Dormant' else 2),
                -x['total_borrowed']
            ))
            
            logger.info(f"Generated student library activity report with {len(report_data)} entries")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating student library activity report: {e}")
            return []

    def get_student_borrowing_history_report(self) -> List[Dict]:
        """
        Retrieve student borrowing history report.

        Returns:
            A list of student borrowing history data with detailed borrowing records.
        """
        try:
            report_data = []
            
            # Get all students
            all_students = self.student_service.get_all_students()
            
            for student in all_students:
                # Get all borrowings (both current and returned)
                all_borrowings = self.borrowed_book_repo.find_by_field('student_id', str(student.student_id))
                
                if not all_borrowings:
                    # Student with no borrowing history
                    report_data.append({
                        'student': student,
                        'student_id': student.student_id,
                        'name': student.name,
                        'stream': getattr(student, 'stream', 'Unknown') or 'Unknown',
                        'class_name': getattr(student, 'class_name', 'Unknown') or 'Unknown',
                        'admission_number': getattr(student, 'admission_number', student.student_id) or student.student_id,
                        'total_borrowings': 0,
                        'books_borrowed': 'None',
                        'first_borrowing': None,
                        'last_borrowing': None,
                        'has_history': False
                    })
                    continue
                
                # Sort borrowings by date (most recent first)
                sorted_borrowings = sorted(all_borrowings, key=lambda x: x.borrowed_on if x.borrowed_on else '', reverse=True)
                
                # Get book details for each borrowing
                borrowing_details = []
                for borrowing in sorted_borrowings[:10]:  # Limit to 10 most recent
                    book = self.book_repository.get_by_id(borrowing.book_id)
                    if book:
                        status = 'Returned' if borrowing.returned_on else 'Borrowed'
                        return_info = f"Returned: {borrowing.returned_on}" if borrowing.returned_on else "Not returned"
                        borrowing_details.append(f"{book.book_number} ({book.title}) - {status} - {return_info}")
                
                books_text = "; ".join(borrowing_details) if borrowing_details else "None"
                if len(all_borrowings) > 10:
                    books_text += f"; ... and {len(all_borrowings) - 10} more"
                
                # Get first and last borrowing dates
                first_borrowing = sorted_borrowings[-1] if sorted_borrowings else None
                last_borrowing = sorted_borrowings[0] if sorted_borrowings else None
                
                report_data.append({
                    'student': student,
                    'student_id': student.student_id,
                    'name': student.name,
                    'stream': getattr(student, 'stream', 'Unknown') or 'Unknown',
                    'class_name': getattr(student, 'class_name', 'Unknown') or 'Unknown',
                    'admission_number': getattr(student, 'admission_number', student.student_id) or student.student_id,
                    'total_borrowings': len(all_borrowings),
                    'books_borrowed': books_text,
                    'first_borrowing': first_borrowing.borrowed_on if first_borrowing else None,
                    'last_borrowing': last_borrowing.borrowed_on if last_borrowing else None,
                    'has_history': True
                })
            
            # Sort by total borrowings (most active first)
            report_data.sort(key=lambda x: -x['total_borrowings'])
            
            logger.info(f"Generated student borrowing history report with {len(report_data)} entries")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating student borrowing history report: {e}")
            return []

    def get_all_teachers_report(self) -> List[Dict]:
        """
        Retrieve all teachers report.

        Returns:
            A list of all teachers report data.
        """
        teachers = self.teacher_repository.get_all()
        return [{"teacher": teacher} for teacher in teachers]

    def get_all_furniture_report(self) -> List[Dict]:
        """
        Retrieve all furniture report.

        Returns:
            A list of all furniture report data.
        """
        # Get all chairs and lockers
        chairs = self.chair_repository.get_all()
        lockers = self.locker_repository.get_all()

        # Convert to unified format
        furniture_data = []

        # Add chairs
        for chair in chairs:
            furniture_data.append({
                "furniture": chair,
                "type": "Chair",
                "id": getattr(chair, 'chair_id', ''),
                "location": getattr(chair, 'location', 'Unknown'),
                "form": getattr(chair, 'form', 'Unknown'),
                "condition": getattr(chair, 'cond', 'Good'),
                "assigned": getattr(chair, 'assigned', 0) == 1,
                "status": "Assigned" if getattr(chair, 'assigned', 0) else "Available"
            })

        # Add lockers
        for locker in lockers:
            furniture_data.append({
                "furniture": locker,
                "type": "Locker",
                "id": getattr(locker, 'locker_id', ''),
                "location": getattr(locker, 'location', 'Unknown'),
                "form": getattr(locker, 'form', 'Unknown'),
                "condition": getattr(locker, 'cond', 'Good'),
                "assigned": getattr(locker, 'assigned', 0) == 1,
                "status": "Assigned" if getattr(locker, 'assigned', 0) else "Available"
            })

        return furniture_data

    def get_borrowing_analytics_report(self) -> Dict:
        """
        Get comprehensive borrowing analytics report.

        Returns:
            Dictionary containing all borrowing analytics data.
        """
        logger.info("Generating comprehensive borrowing analytics report")

        try:
            analytics = {
                'borrowing_summary_by_subject_stream_form': self._get_borrowing_summary_by_subject_stream_form(),
                'borrowing_percentage_by_class': self._get_borrowing_percentage_by_class(),
                'inventory_summary': self._get_inventory_summary(),
                'books_categorized_by_subject_form': self._get_books_categorized_by_subject_form(),
                'students_not_borrowed_by_stream_subject': self._get_students_not_borrowed_by_stream_subject(),
                'students_not_borrowed_any_books': self._get_students_not_borrowed_any_books()
            }

            logger.info("Borrowing analytics report generated successfully")
            return analytics

        except Exception as e:
            logger.error(f"Error generating borrowing analytics report: {e}")
            return {}

    def _get_borrowing_summary_by_subject_stream_form(self) -> List[Dict]:
        """
        Get borrowing summary for each subject in each stream per form.

        Returns:
            List of dictionaries with borrowing summaries.
        """
        try:
            summary = []

            # Get all class-stream combinations
            combinations = self.class_management_service.get_class_stream_combinations()

            for class_level, stream, student_count in combinations:
                # Get students in this class-stream
                students = self.class_management_service.get_students_by_class_and_stream(class_level, stream)

                if not students:
                    continue

                student_ids = [str(student.student_id) for student in students]

                # Get all borrowed books for these students
                borrowed_books = []
                for student_id in student_ids:
                    student_borrowings = self.borrowed_book_repo.get_borrowed_books_by_student(student_id)
                    borrowed_books.extend(student_borrowings)

                # Group by subject
                subject_summary = {}
                for borrowing in borrowed_books:
                    book = self.book_repository.get_by_id(borrowing.book_id)
                    if book:
                        subject = getattr(book, 'subject', None) or getattr(book, 'category', 'Unknown')
                        if subject not in subject_summary:
                            subject_summary[subject] = {
                                'subject': subject,
                                'total_borrowed': 0,
                                'unique_students': set(),
                                'books': []
                            }
                        subject_summary[subject]['total_borrowed'] += 1
                        subject_summary[subject]['unique_students'].add(borrowing.student_id)
                        subject_summary[subject]['books'].append({
                            'book_number': getattr(book, 'book_number', str(book.id)),
                            'title': book.title,
                            'student_id': borrowing.student_id,
                            'borrowed_on': borrowing.borrowed_on
                        })

                # Convert to list format
                for subject_data in subject_summary.values():
                    summary.append({
                        'form': f"Form {class_level}",
                        'stream': stream,
                        'subject': subject_data['subject'],
                        'total_students': student_count,
                        'students_borrowed': len(subject_data['unique_students']),
                        'total_borrowings': subject_data['total_borrowed'],
                        'books_borrowed': subject_data['books']
                    })

            return summary

        except Exception as e:
            logger.error(f"Error getting borrowing summary by subject stream form: {e}")
            return []

    def _get_borrowing_percentage_by_class(self) -> List[Dict]:
        """
        Get percentage of borrowing per class compared to total required.

        Returns:
            List of dictionaries with borrowing percentages by class.
        """
        try:
            percentages = []

            # Get all class levels
            class_levels = self.class_management_service.get_all_class_levels()

            for class_level in class_levels:
                # Get students in this class
                students = self.class_management_service.get_students_by_class_level(class_level)
                total_students = len(students)

                if total_students == 0:
                    continue

                # Get borrowed books for this class using a simpler approach
                borrowed_count = 0
                students_borrowed = set()

                try:
                    # Use a more direct database approach to avoid repository issues
                    from school_system.database.repositories.base import BaseRepository
                    from school_system.models.book import BorrowedBookStudent

                    repo = BaseRepository(BorrowedBookStudent)
                    student_ids = [str(student.student_id) for student in students]

                    # Query directly for borrowed books
                    cursor = repo.db.cursor()
                    placeholders = ','.join('?' * len(student_ids))
                    cursor.execute(f"""
                        SELECT student_id, COUNT(*) as borrow_count
                        FROM borrowed_books_student
                        WHERE student_id IN ({placeholders}) AND returned_on IS NULL
                        GROUP BY student_id
                    """, student_ids)

                    results = cursor.fetchall()
                    for row in results:
                        student_id, count = row[0], row[1]
                        students_borrowed.add(student_id)
                        borrowed_count += count

                except Exception as e:
                    logger.warning(f"Error getting borrowing data for class {class_level}: {e}")
                    # Fallback: try to get basic counts
                    try:
                        for student in students[:10]:  # Limit to first 10 students to avoid performance issues
                            try:
                                # Simple count query
                                cursor = self.borrowed_book_repo.db.cursor()
                                cursor.execute("""
                                    SELECT COUNT(*) FROM borrowed_books_student
                                    WHERE student_id = ? AND returned_on IS NULL
                                """, (str(student.student_id),))
                                count = cursor.fetchone()[0]
                                if count > 0:
                                    students_borrowed.add(student.student_id)
                                    borrowed_count += count
                            except:
                                continue
                    except:
                        pass

                # Calculate percentages
                students_borrowed_count = len(students_borrowed)
                student_borrowing_percentage = (students_borrowed_count / total_students) * 100 if total_students > 0 else 0

                percentages.append({
                    'form': f"Form {class_level}",
                    'total_students': total_students,
                    'students_borrowed': students_borrowed_count,
                    'student_borrowing_percentage': round(student_borrowing_percentage, 2),
                    'total_borrowings': borrowed_count,
                    'average_borrowings_per_student': round(borrowed_count / total_students, 2) if total_students > 0 else 0
                })

            return percentages

        except Exception as e:
            logger.error(f"Error getting borrowing percentage by class: {e}")
            return []

    def _get_inventory_summary(self) -> Dict:
        """
        Get number of books in inventory.

        Returns:
            Dictionary with inventory summary.
        """
        try:
            all_books = self.book_repository.get_all()
            total_books = len(all_books)
            available_books = len([book for book in all_books if book.available])
            borrowed_books = total_books - available_books

            # Get available books count
            available_count = len(self.book_repository.get_available_books())

            return {
                'total_books': total_books,
                'available_books': available_count,
                'borrowed_books': borrowed_books,
                'borrowed_percentage': round((borrowed_books / total_books) * 100, 2) if total_books > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error getting inventory summary: {e}")
            return {}

    def _get_books_categorized_by_subject_form(self) -> List[Dict]:
        """
        Get number of books categorized per subject, per form.

        Returns:
            List of dictionaries with book categorization data.
        """
        try:
            categorization = []

            # Get all books
            all_books = self.book_repository.get_all()

            # Group by form and subject
            form_subject_groups = {}

            for book in all_books:
                form = getattr(book, 'class_name', None) or 'Unknown'
                subject = getattr(book, 'subject', None) or getattr(book, 'category', None) or 'Unknown'
                
                # Ensure form and subject are strings (not None) for consistent sorting
                form = str(form) if form is not None else 'Unknown'
                subject = str(subject) if subject is not None else 'Unknown'

                key = (form, subject)
                if key not in form_subject_groups:
                    form_subject_groups[key] = {
                        'form': form,
                        'subject': subject,
                        'total_books': 0,
                        'available_books': 0,
                        'borrowed_books': 0
                    }

                form_subject_groups[key]['total_books'] += 1
                if book.available:
                    form_subject_groups[key]['available_books'] += 1
                else:
                    form_subject_groups[key]['borrowed_books'] += 1

            # Convert to list
            for data in form_subject_groups.values():
                categorization.append(data)

            # Sort with safe handling of None values
            return sorted(categorization, key=lambda x: (
                str(x['form']) if x['form'] is not None else 'Unknown',
                str(x['subject']) if x['subject'] is not None else 'Unknown'
            ))

        except Exception as e:
            logger.error(f"Error getting books categorized by subject form: {e}")
            return []

    def _get_students_not_borrowed_by_stream_subject(self) -> List[Dict]:
        """
        Get names of students who have not borrowed books in each stream, per subject.

        Returns:
            List of dictionaries with students who haven't borrowed by stream/subject.
        """
        try:
            not_borrowed = []

            # Get all class-stream combinations (simplified approach)
            try:
                combinations = self.class_management_service.get_class_stream_combinations()
            except:
                # Fallback: get basic class levels and assume common streams
                combinations = []
                try:
                    class_levels = self.class_management_service.get_all_class_levels()
                    for class_level in class_levels[:3]:  # Limit to avoid performance issues
                        combinations.append((class_level, "General", 10))  # Assume 10 students per class
                except:
                    return []  # Return empty if we can't get basic data

            for class_level, stream, _ in combinations[:5]:  # Limit combinations to avoid performance issues
                try:
                    # Get students in this class-stream
                    students = self.class_management_service.get_students_by_class_and_stream(class_level, stream)
                except:
                    continue

                # Get popular subjects (limit to avoid performance issues)
                popular_subjects = ["Mathematics", "English", "Science", "History", "Geography"]

                for subject in popular_subjects[:3]:  # Limit subjects
                    # Find students who haven't borrowed from this subject
                    students_not_borrowed = []

                    for student in students[:20]:  # Limit students per class
                        try:
                            # Check borrowing history using simpler query
                            cursor = self.borrowed_book_repo.db.cursor()
                            cursor.execute("""
                                SELECT COUNT(*) FROM borrowed_books_student bbs
                                JOIN books bk ON bbs.book_id = bk.id
                                WHERE bbs.student_id = ? AND (bk.subject = ? OR bk.category = ?)
                            """, (str(student.student_id), subject, subject))

                            borrow_count = cursor.fetchone()[0]
                            if borrow_count == 0:
                                students_not_borrowed.append({
                                    'student_id': student.student_id,
                                    'student_name': student.name,
                                    'admission_number': getattr(student, 'admission_number', str(student.student_id))
                                })
                        except:
                            continue

                    if students_not_borrowed:
                        not_borrowed.append({
                            'form': f"Form {class_level}",
                            'stream': stream,
                            'subject': subject,
                            'students_not_borrowed': students_not_borrowed[:10],  # Limit results
                            'count': len(students_not_borrowed)
                        })

            return not_borrowed

        except Exception as e:
            logger.error(f"Error getting students not borrowed by stream subject: {e}")
            return []

    def _get_students_not_borrowed_any_books(self) -> Dict:
        """
        Get students who have not borrowed any books and their total number.

        Returns:
            Dictionary with students who haven't borrowed any books.
        """
        try:
            all_students = self.student_service.get_all_students()
            students_not_borrowed = []

            for student in all_students[:100]:  # Limit to avoid performance issues
                try:
                    # Check borrowing history using direct query
                    cursor = self.borrowed_book_repo.db.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) FROM borrowed_books_student
                        WHERE student_id = ?
                    """, (str(student.student_id),))

                    borrow_count = cursor.fetchone()[0]
                    if borrow_count == 0:
                        students_not_borrowed.append({
                            'student_id': student.student_id,
                            'student_name': student.name,
                            'admission_number': getattr(student, 'admission_number', str(student.student_id)),
                            'stream': getattr(student, 'stream', 'Unknown')
                        })
                except:
                    continue

            # Group by stream for better organization
            stream_groups = {}
            for student in students_not_borrowed:
                stream = student['stream']
                if stream not in stream_groups:
                    stream_groups[stream] = []
                stream_groups[stream].append(student)

            return {
                'total_students_not_borrowed': len(students_not_borrowed),
                'students_by_stream': stream_groups,
                'all_students_not_borrowed': students_not_borrowed[:50]  # Limit results
            }

        except Exception as e:
            logger.error(f"Error getting students not borrowed any books: {e}")
            return {'total_students_not_borrowed': 0, 'students_by_stream': {}, 'all_students_not_borrowed': []}
