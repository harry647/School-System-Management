"""
Report service for generating and managing reports.
"""

from typing import Dict, List
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.database.repositories.book_repo import BookRepository
from school_system.database.repositories.student_repo import StudentRepository


class ReportService:
    """Service for generating and managing reports."""

    def __init__(self):
        self.book_repository = BookRepository()
        self.student_repository = StudentRepository()

    def generate_report(self, report_type: str, parameters: Dict) -> Report:
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