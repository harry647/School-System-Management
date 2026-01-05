"""
Book service for managing book-related operations.
"""

from typing import List, Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import validate_input
from school_system.models.book import Book
from school_system.database.repositories.book_repository import BookRepository


class BookService:
    """Service for managing book-related operations."""

    def __init__(self):
        self.book_repository = BookRepository()

    def get_all_books(self) -> List[Book]:
        """
        Retrieve all books.

        Returns:
            A list of all Book objects.
        """
        return self.book_repository.get_all()

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Retrieve a book by its ID.

        Args:
            book_id: The ID of the book.

        Returns:
            The Book object if found, otherwise None.
        """
        return self.book_repository.get_by_id(book_id)

    def create_book(self, book_data: dict) -> Book:
        """
        Create a new book.

        Args:
            book_data: A dictionary containing book data.

        Returns:
            The created Book object.
        """
        logger.info(f"Creating a new book with data: {book_data}")
        validate_input(book_data.get('title'), "Book title cannot be empty")
        
        book = Book(**book_data)
        created_book = self.book_repository.create(book)
        logger.info(f"Book created successfully with ID: {created_book.id}")
        return created_book

    def update_book(self, book_id: int, book_data: dict) -> Optional[Book]:
        """
        Update an existing book.

        Args:
            book_id: The ID of the book to update.
            book_data: A dictionary containing updated book data.

        Returns:
            The updated Book object if successful, otherwise None.
        """
        book = self.book_repository.get_by_id(book_id)
        if not book:
            return None

        for key, value in book_data.items():
            setattr(book, key, value)

        return self.book_repository.update(book)

    def delete_book(self, book_id: int) -> bool:
        """
        Delete a book.

        Args:
            book_id: The ID of the book to delete.

        Returns:
            True if the book was deleted, otherwise False.
        """
        book = self.book_repository.get_by_id(book_id)
        if not book:
            return False

        self.book_repository.delete(book)
        return True