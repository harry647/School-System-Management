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


class ReportService:
    """Service for generating and managing reports."""

    def __init__(self):
        self.book_repository = BookRepository()
        self.student_repository = StudentRepository()
        self.borrowed_book_repo = BorrowedBookStudentRepository()
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
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"book": {"id": "N/A", "title": "Feature not implemented", "status": "N/A", "author": "N/A"}}]

    def get_available_books_report(self) -> List[Dict]:
        """
        Retrieve available books report.

        Returns:
            A list of available books report data.
        """
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"book": {"id": "N/A", "title": "Feature not implemented", "status": "N/A", "author": "N/A"}}]

    def get_overdue_books_report(self) -> List[Dict]:
        """
        Retrieve overdue books report.

        Returns:
            A list of overdue books report data.
        """
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"book": {"id": "N/A", "title": "Feature not implemented", "status": "N/A", "author": "N/A"}}]

    def get_book_inventory_report(self) -> List[Dict]:
        """
        Retrieve book inventory report.

        Returns:
            A list of book inventory report data.
        """
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"book": {"id": "N/A", "title": "Feature not implemented", "status": "N/A", "author": "N/A"}}]

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
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"student": {"id": "N/A", "name": "Feature not implemented", "stream": "N/A", "class": "N/A"}}]

    def get_students_by_class_report(self) -> List[Dict]:
        """
        Retrieve students by class report.

        Returns:
            A list of students grouped by class.
        """
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"student": {"id": "N/A", "name": "Feature not implemented", "stream": "N/A", "class": "N/A"}}]

    def get_student_library_activity_report(self) -> List[Dict]:
        """
        Retrieve student library activity report.

        Returns:
            A list of student library activity data.
        """
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"student": {"id": "N/A", "name": "Feature not implemented", "stream": "N/A", "class": "N/A"}}]

    def get_student_borrowing_history_report(self) -> List[Dict]:
        """
        Retrieve student borrowing history report.

        Returns:
            A list of student borrowing history data.
        """
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"student": {"id": "N/A", "name": "Feature not implemented", "stream": "N/A", "class": "N/A"}}]

    def get_all_teachers_report(self) -> List[Dict]:
        """
        Retrieve all teachers report.

        Returns:
            A list of all teachers report data.
        """
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"teacher": {"id": "N/A", "name": "Feature not implemented", "subject": "N/A", "status": "N/A"}}]

    def get_all_furniture_report(self) -> List[Dict]:
        """
        Retrieve all furniture report.

        Returns:
            A list of all furniture report data.
        """
        # This would need to be implemented based on your data model
        # For now, return a placeholder
        return [{"furniture": {"id": "N/A", "name": "Feature not implemented", "type": "N/A", "status": "N/A"}}]

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

                # Get borrowed books for this class
                borrowed_count = 0
                students_borrowed = set()

                for student in students:
                    student_borrowings = self.borrowed_book_repo.get_borrowed_books_by_student(str(student.student_id))
                    if student_borrowings:
                        borrowed_count += len(student_borrowings)
                        students_borrowed.add(student.student_id)

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
                form = getattr(book, 'class_name', 'Unknown')
                subject = getattr(book, 'subject', None) or getattr(book, 'category', 'Unknown')

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

            return sorted(categorization, key=lambda x: (x['form'], x['subject']))

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

            # Get all class-stream combinations
            combinations = self.class_management_service.get_class_stream_combinations()

            for class_level, stream, _ in combinations:
                # Get students in this class-stream
                students = self.class_management_service.get_students_by_class_and_stream(class_level, stream)

                # Get all subjects from books
                all_books = self.book_repository.get_all()
                all_subjects = set()
                for book in all_books:
                    subject = getattr(book, 'subject', None) or getattr(book, 'category', None)
                    if subject:
                        all_subjects.add(subject)

                for subject in all_subjects:
                    # Find students who haven't borrowed from this subject
                    students_not_borrowed = []

                    for student in students:
                        # Check if student has borrowed any book from this subject
                        student_borrowings = self.borrowed_book_repo.get_borrowed_books_by_student(str(student.student_id))
                        has_borrowed_subject = False

                        for borrowing in student_borrowings:
                            book = self.book_repository.get_by_id(borrowing.book_id)
                            if book:
                                book_subject = getattr(book, 'subject', None) or getattr(book, 'category', None)
                                if book_subject == subject:
                                    has_borrowed_subject = True
                                    break

                        if not has_borrowed_subject:
                            students_not_borrowed.append({
                                'student_id': student.student_id,
                                'student_name': student.name,
                                'admission_number': getattr(student, 'admission_number', str(student.student_id))
                            })

                    if students_not_borrowed:
                        not_borrowed.append({
                            'form': f"Form {class_level}",
                            'stream': stream,
                            'subject': subject,
                            'students_not_borrowed': students_not_borrowed,
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

            for student in all_students:
                # Check if student has any borrowings
                student_borrowings = self.borrowed_book_repo.get_borrowed_books_by_student(str(student.student_id))
                if not student_borrowings:
                    students_not_borrowed.append({
                        'student_id': student.student_id,
                        'student_name': student.name,
                        'admission_number': getattr(student, 'admission_number', str(student.student_id)),
                        'stream': getattr(student, 'stream', 'Unknown')
                    })

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
                'all_students_not_borrowed': students_not_borrowed
            }

        except Exception as e:
            logger.error(f"Error getting students not borrowed any books: {e}")
            return {'total_students_not_borrowed': 0, 'students_by_stream': {}, 'all_students_not_borrowed': []}
