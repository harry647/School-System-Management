"""
QR service for managing QR code-related operations.
"""

from typing import Optional, List, Dict
import datetime
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.models.book import QRBook, QRBorrowLog
from school_system.database.repositories.book_repo import QRBookRepository, QRBorrowLogRepository


class QRService:
    """Service for managing QR code-related operations."""
 
    def __init__(self):
        self.qr_book_repository = QRBookRepository()

    def generate_qr_code(self, data: str) -> str:
        """
        Generate a QR code for the given data.

        Args:
            data: The data to encode in the QR code.

        Returns:
            The generated QR code as a string.
        """
        logger.info(f"Generating QR code for data: {data}")
        ValidationUtils.validate_input(data, "Data for QR code cannot be empty")
        
        # Logic to generate QR code
        qr_code = self._generate_qr(data)
        logger.info(f"QR code generated successfully: {qr_code}")
        return qr_code

    def _generate_qr(self, data: str) -> str:
        """
        Internal method to generate QR code.

        Args:
            data: The data to encode.

        Returns:
            The generated QR code.
        """
        # Placeholder for QR generation logic
        return f"QR_CODE_{data}"

    def save_qr_book(self, qr_book: str, metadata: dict) -> QRBook:
        """
        Save a QR book to the database.

        Args:
            qr_book: The QR book to save.
            metadata: Additional metadata for the QR book.

        Returns:
            The saved QRBook object.
        """
        qr = QRBook(qr_book=qr_book, **metadata)
        return self.qr_book_repository.create(qr)
 
    def get_qr_book_by_id(self, qr_id: int) -> Optional[QRBook]:
        """
        Retrieve a QR book by its ID.

        Args:
            qr_id: The ID of the QR book.

        Returns:
            The QRBook object if found, otherwise None.
        """
        return self.qr_book_repository.get_by_id(qr_id)

    def get_all_qr_books(self) -> List[QRBook]:
        """
        Retrieve all QR books.

        Returns:
            A list of all QRBook objects.
        """
        return self.qr_book_repository.get_all()

    def create_qr_book(self, qr_book_data: dict) -> QRBook:
        """
        Create a new QR book.

        Args:
            qr_book_data: A dictionary containing QR book data.

        Returns:
            The created QRBook object.
        """
        logger.info(f"Creating a new QR book with data: {qr_book_data}")
        ValidationUtils.validate_input(qr_book_data.get('book_number'), "Book number cannot be empty")

        qr_book = QRBook(**qr_book_data)
        created_qr_book = self.qr_book_repository.create(qr_book)
        logger.info(f"QR book created successfully with ID: {created_qr_book.book_number}")
        return created_qr_book

    def update_qr_book(self, book_number: int, qr_book_data: dict) -> Optional[QRBook]:
        """
        Update an existing QR book.

        Args:
            book_number: The book number of the QR book to update.
            qr_book_data: A dictionary containing updated QR book data.

        Returns:
            The updated QRBook object if successful, otherwise None.
        """
        qr_book = self.qr_book_repository.get_by_id(book_number)
        if not qr_book:
            return None

        for key, value in qr_book_data.items():
            setattr(qr_book, key, value)

        return self.qr_book_repository.update(qr_book)

    def delete_qr_book(self, book_number: int) -> bool:
        """
        Delete a QR book.

        Args:
            book_number: The book number of the QR book to delete.

        Returns:
            True if the QR book was deleted, otherwise False.
        """
        qr_book = self.qr_book_repository.get_by_id(book_number)
        if not qr_book:
            return False

        self.qr_book_repository.delete(qr_book)
        return True

    def get_all_qr_borrow_logs(self) -> List[QRBorrowLog]:
        """
        Retrieve all QR borrow logs.

        Returns:
            A list of all QRBorrowLog objects.
        """
        qr_borrow_log_repository = QRBorrowLogRepository()
        return qr_borrow_log_repository.get_all()

    def get_qr_borrow_log_by_id(self, book_number: int) -> Optional[QRBorrowLog]:
        """
        Retrieve a QR borrow log by book number.

        Args:
            book_number: The book number of the QR borrow log.

        Returns:
            The QRBorrowLog object if found, otherwise None.
        """
        qr_borrow_log_repository = QRBorrowLogRepository()
        return qr_borrow_log_repository.get_by_id(book_number)

    def create_qr_borrow_log(self, borrow_log_data: dict) -> QRBorrowLog:
        """
        Create a new QR borrow log.

        Args:
            borrow_log_data: A dictionary containing QR borrow log data.

        Returns:
            The created QRBorrowLog object.
        """
        logger.info(f"Creating a new QR borrow log with data: {borrow_log_data}")
        ValidationUtils.validate_input(borrow_log_data.get('book_number'), "Book number cannot be empty")
        ValidationUtils.validate_input(borrow_log_data.get('student_id'), "Student ID cannot be empty")

        qr_borrow_log = QRBorrowLog(**borrow_log_data)
        qr_borrow_log_repository = QRBorrowLogRepository()
        created_log = qr_borrow_log_repository.create(qr_borrow_log)
        logger.info(f"QR borrow log created successfully for book number: {created_log.book_number}")
        return created_log

    def update_qr_borrow_log(self, book_number: int, borrow_log_data: dict) -> Optional[QRBorrowLog]:
        """
        Update an existing QR borrow log.

        Args:
            book_number: The book number of the QR borrow log to update.
            borrow_log_data: A dictionary containing updated QR borrow log data.

        Returns:
            The updated QRBorrowLog object if successful, otherwise None.
        """
        qr_borrow_log_repository = QRBorrowLogRepository()
        qr_borrow_log = qr_borrow_log_repository.get_by_id(book_number)
        if not qr_borrow_log:
            return None

        for key, value in borrow_log_data.items():
            setattr(qr_borrow_log, key, value)

        return qr_borrow_log_repository.update(qr_borrow_log)

    def delete_qr_borrow_log(self, book_number: int) -> bool:
        """
        Delete a QR borrow log.

        Args:
            book_number: The book number of the QR borrow log to delete.

        Returns:
            True if the QR borrow log was deleted, otherwise False.
        """
        qr_borrow_log_repository = QRBorrowLogRepository()
        qr_borrow_log = qr_borrow_log_repository.get_by_id(book_number)
        if not qr_borrow_log:
            return False

        qr_borrow_log_repository.delete(qr_borrow_log)
        return True

    def generate_qr_code_with_options(self, data: str, size: int = 200, format: str = 'png') -> dict:
        """
        Generate QR code with customizable options.

        Args:
            data: The data to encode in the QR code.
            size: The size of the QR code in pixels.
            format: The output format (png, svg, etc.).

        Returns:
            A dictionary containing the QR code and metadata.
        """
        logger.info(f"Generating QR code with options for data: {data}")
        ValidationUtils.validate_input(data, "Data for QR code cannot be empty")
        
        try:
            # Enhanced QR generation with options
            qr_code = self._generate_qr_with_options(data, size, format)
            logger.info(f"QR code generated successfully with options: {qr_code}")
            return {
                'qr_code': qr_code,
                'data': data,
                'size': size,
                'format': format,
                'generated_at': datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating QR code with options: {e}")
            return {}

    def _generate_qr_with_options(self, data: str, size: int, format: str) -> str:
        """
        Internal method to generate QR code with options.

        Args:
            data: The data to encode.
            size: The size of the QR code.
            format: The output format.

        Returns:
            The generated QR code.
        """
        # Placeholder for enhanced QR generation logic
        return f"QR_CODE_{format}_{size}_{data}"

    def validate_qr_code(self, qr_code: str) -> bool:
        """
        Validate QR code format and content.

        Args:
            qr_code: The QR code to validate.

        Returns:
            True if the QR code is valid, otherwise False.
        """
        logger.info(f"Validating QR code: {qr_code}")
        
        try:
            # Basic validation - in a real implementation, this would be more comprehensive
            if not qr_code or len(qr_code) < 10:
                return False
            
            # Check if QR code follows expected pattern
            if not qr_code.startswith("QR_CODE_"):
                return False
            
            logger.info(f"QR code validation successful: {qr_code}")
            return True
        except Exception as e:
            logger.error(f"Error validating QR code: {e}")
            return False

    def generate_batch_qr_codes(self, data_list: List[str]) -> List[dict]:
        """
        Generate multiple QR codes in batch.

        Args:
            data_list: A list of data strings to encode.

        Returns:
            A list of dictionaries containing generated QR codes and metadata.
        """
        logger.info(f"Generating batch QR codes for {len(data_list)} items")
        
        if not data_list or len(data_list) == 0:
            return []
        
        batch_results = []
        for data in data_list:
            try:
                ValidationUtils.validate_input(data, "Data for QR code cannot be empty")
                qr_result = self.generate_qr_code_with_options(data)
                batch_results.append(qr_result)
            except Exception as e:
                logger.error(f"Error generating QR code for data {data}: {e}")
                continue
        
        logger.info(f"Successfully generated {len(batch_results)} QR codes in batch")
        return batch_results

    def search_qr_books(self, query: str) -> List[QRBook]:
        """
        Search QR books by various criteria.

        Args:
            query: The search query.

        Returns:
            A list of QRBook objects matching the criteria.
        """
        logger.info(f"Searching QR books with query: {query}")
        
        try:
            all_qr_books = self.qr_book_repository.get_all()
            results = []
            
            for qr_book in all_qr_books:
                # Search by book number or details
                if (query.lower() in str(qr_book.book_number).lower() or
                    (qr_book.details and query.lower() in qr_book.details.lower())):
                    results.append(qr_book)
            
            logger.info(f"Found {len(results)} QR books matching query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching QR books: {e}")
            return []

    def get_qr_book_statistics(self, book_number: int) -> dict:
        """
        Get statistics for a specific QR book.

        Args:
            book_number: The book number of the QR book.

        Returns:
            A dictionary containing QR book statistics.
        """
        logger.info(f"Getting statistics for QR book: {book_number}")
        
        try:
            qr_book = self.qr_book_repository.get_by_id(book_number)
            if not qr_book:
                return {}
            
            # Get borrow logs for this book
            qr_borrow_log_repository = QRBorrowLogRepository()
            borrow_logs = qr_borrow_log_repository.get_all()
            book_borrow_logs = [log for log in borrow_logs if log.book_number == book_number]
            
            stats = {
                'book_number': qr_book.book_number,
                'details': qr_book.details,
                'added_date': qr_book.added_date,
                'total_borrows': len(book_borrow_logs),
                'currently_borrowed': len([log for log in book_borrow_logs if not log.return_date]),
                'last_borrow_date': max([log.borrow_date for log in book_borrow_logs], default=None) if book_borrow_logs else None
            }
            
            logger.info(f"QR book statistics: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting QR book statistics: {e}")
            return {}

    def get_qr_borrow_analytics(self) -> dict:
        """
        Get analytics on QR book borrowing patterns.

        Returns:
            A dictionary containing QR borrow analytics.
        """
        logger.info("Generating QR borrow analytics")
        
        try:
            qr_borrow_log_repository = QRBorrowLogRepository()
            all_borrow_logs = qr_borrow_log_repository.get_all()
            
            if not all_borrow_logs:
                return {}
            
            # Calculate analytics
            total_borrows = len(all_borrow_logs)
            currently_borrowed = len([log for log in all_borrow_logs if not log.return_date])
            returned_borrows = len([log for log in all_borrow_logs if log.return_date])
            
            # Get most borrowed books
            book_borrow_counts = {}
            for log in all_borrow_logs:
                book_num = log.book_number
                book_borrow_counts[book_num] = book_borrow_counts.get(book_num, 0) + 1
            
            most_borrowed = max(book_borrow_counts.items(), key=lambda x: x[1]) if book_borrow_counts else (None, 0)
            
            analytics = {
                'total_borrows': total_borrows,
                'currently_borrowed': currently_borrowed,
                'returned_borrows': returned_borrows,
                'most_borrowed_book': most_borrowed[0],
                'most_borrowed_count': most_borrowed[1],
                'borrow_rate': currently_borrowed / total_borrows if total_borrows > 0 else 0
            }
            
            logger.info(f"QR borrow analytics: {analytics}")
            return analytics
        except Exception as e:
            logger.error(f"Error generating QR borrow analytics: {e}")
            return {}

    def export_qr_codes_to_file(self, qr_codes: List[str], format: str = 'pdf') -> bool:
        """
        Export QR codes to a file.

        Args:
            qr_codes: A list of QR codes to export.
            format: The output format.

        Returns:
            True if the export was successful, otherwise False.
        """
        logger.info(f"Exporting {len(qr_codes)} QR codes to {format} file")
        
        try:
            # Placeholder for export logic
            # In a real implementation, this would generate a file with all QR codes
            filename = f"qr_codes_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            
            # Simulate export process
            with open(filename, 'w') as f:
                for i, qr_code in enumerate(qr_codes):
                    f.write(f"QR Code {i+1}: {qr_code}\n")
            
            logger.info(f"Successfully exported QR codes to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting QR codes to file: {e}")
            return False

    def import_qr_codes_from_file(self, filename: str) -> List[str]:
        """
        Import QR codes from a file.

        Args:
            filename: The name of the file to import from.

        Returns:
            A list of imported QR codes.
        """
        logger.info(f"Importing QR codes from file: {filename}")
        
        try:
            # Placeholder for import logic
            # In a real implementation, this would read QR codes from a file
            imported_codes = []
            
            with open(filename, 'r') as f:
                for line in f:
                    if line.strip().startswith("QR Code"):
                        qr_code = line.strip().split(": ")[1]
                        imported_codes.append(qr_code)
            
            logger.info(f"Successfully imported {len(imported_codes)} QR codes from {filename}")
            return imported_codes
        except Exception as e:
            logger.error(f"Error importing QR codes from file: {e}")
            return []

    def track_qr_book_availability(self, book_number: int, status: str) -> bool:
        """
        Track availability status of QR books.

        Args:
            book_number: The book number of the QR book.
            status: The availability status.

        Returns:
            True if the tracking was successful, otherwise False.
        """
        logger.info(f"Tracking availability for QR book {book_number}: {status}")
        
        try:
            qr_book = self.qr_book_repository.get_by_id(book_number)
            if not qr_book:
                return False
            
            # Store availability status
            if not hasattr(qr_book, 'availability_history'):
                qr_book.availability_history = []
            
            qr_book.availability_history.append({
                'status': status,
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            self.qr_book_repository.update(qr_book)
            logger.info(f"Successfully tracked availability for QR book {book_number}")
            return True
        except Exception as e:
            logger.error(f"Error tracking QR book availability: {e}")
            return False

    def get_qr_code_usage_history(self, book_number: int) -> List[dict]:
        """
        Get usage history for a QR code.

        Args:
            book_number: The book number of the QR book.

        Returns:
            A list of dictionaries containing usage history.
        """
        logger.info(f"Getting usage history for QR book: {book_number}")
        
        try:
            qr_borrow_log_repository = QRBorrowLogRepository()
            all_borrow_logs = qr_borrow_log_repository.get_all()
            
            # Filter logs for this specific book
            book_logs = [log for log in all_borrow_logs if log.book_number == book_number]
            
            usage_history = []
            for log in book_logs:
                usage_entry = {
                    'book_number': log.book_number,
                    'student_id': log.student_id,
                    'borrow_date': log.borrow_date,
                    'return_date': log.return_date,
                    'duration': self._calculate_borrow_duration(log.borrow_date, log.return_date)
                }
                usage_history.append(usage_entry)
            
            logger.info(f"Retrieved {len(usage_history)} usage records for QR book {book_number}")
            return usage_history
        except Exception as e:
            logger.error(f"Error getting QR code usage history: {e}")
            return []

    def _calculate_borrow_duration(self, borrow_date: str, return_date: str = None) -> str:
        """
        Calculate the duration of a borrow period.

        Args:
            borrow_date: The borrow date.
            return_date: The return date (optional).

        Returns:
            A string representing the duration.
        """
        try:
            if return_date:
                borrow_dt = datetime.datetime.fromisoformat(borrow_date)
                return_dt = datetime.datetime.fromisoformat(return_date)
                duration = return_dt - borrow_dt
                return str(duration)
            else:
                return "Not returned yet"
        except Exception as e:
            logger.error(f"Error calculating borrow duration: {e}")
            return "Unknown"