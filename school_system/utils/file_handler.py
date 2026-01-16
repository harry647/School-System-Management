"""
File Handler Utility

This module provides functionality for handling file operations such as
reading, writing, copying, moving, and deleting files.
"""

import os
import shutil
import json
import csv
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class FileHandler:
    """A utility class for handling file operations."""

    @staticmethod
    def read_file(file_path: str) -> str:
        """
        Read the contents of a file.

        Args:
            file_path: Path to the file to read

        Returns:
            The content of the file as a string

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If there's an error reading the file
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def write_file(file_path: str, content: str, mode: str = 'w') -> None:
        """
        Write content to a file.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            mode: File opening mode ('w' for write, 'a' for append)

        Raises:
            IOError: If there's an error writing to the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, mode, encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """
        Read JSON data from a file.

        Args:
            file_path: Path to the JSON file

        Returns:
            The parsed JSON data as a dictionary

        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any], indent: int = 4) -> None:
        """
        Write JSON data to a file.

        Args:
            file_path: Path to the JSON file
            data: Data to write as JSON
            indent: Indentation level for pretty printing

        Raises:
            IOError: If there's an error writing to the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)

    @staticmethod
    def read_csv(file_path: str, delimiter: str = ',') -> List[Dict[str, Any]]:
        """
        Read CSV data from a file.

        Args:
            file_path: Path to the CSV file
            delimiter: Delimiter used in the CSV file

        Returns:
            List of dictionaries representing the CSV data

        Raises:
            FileNotFoundError: If the file does not exist
        """
        with open(file_path, 'r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            return list(reader)

    @staticmethod
    def write_csv(
        file_path: str, 
        data: List[Dict[str, Any]], 
        fieldnames: Optional[List[str]] = None,
        delimiter: str = ','
    ) -> None:
        """
        Write CSV data to a file.

        Args:
            file_path: Path to the CSV file
            data: Data to write as CSV
            fieldnames: List of field names (headers)
            delimiter: Delimiter to use in the CSV file

        Raises:
            IOError: If there's an error writing to the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def copy_file(source_path: str, destination_path: str) -> None:
        """
        Copy a file from source to destination.

        Args:
            source_path: Path to the source file
            destination_path: Path to the destination file

        Raises:
            FileNotFoundError: If the source file does not exist
            IOError: If there's an error copying the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        shutil.copy2(source_path, destination_path)

    @staticmethod
    def move_file(source_path: str, destination_path: str) -> None:
        """
        Move a file from source to destination.

        Args:
            source_path: Path to the source file
            destination_path: Path to the destination file

        Raises:
            FileNotFoundError: If the source file does not exist
            IOError: If there's an error moving the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        shutil.move(source_path, destination_path)

    @staticmethod
    def delete_file(file_path: str) -> None:
        """
        Delete a file.

        Args:
            file_path: Path to the file to delete

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If there's an error deleting the file
        """
        os.remove(file_path)

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file exists, False otherwise
        """
        return os.path.isfile(file_path)

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        Get the size of a file in bytes.

        Args:
            file_path: Path to the file

        Returns:
            Size of the file in bytes

        Raises:
            FileNotFoundError: If the file does not exist
        """
        return os.path.getsize(file_path)

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Get the extension of a file.

        Args:
            file_path: Path to the file

        Returns:
            The file extension (without the dot)
        """
        return Path(file_path).suffix.lstrip('.')

    @staticmethod
    def list_files_in_directory(directory_path: str, extension: Optional[str] = None) -> List[str]:
        """
        List files in a directory.

        Args:
            directory_path: Path to the directory
            extension: Optional file extension filter

        Returns:
            List of file paths in the directory

        Raises:
            FileNotFoundError: If the directory does not exist
        """
        files = []
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                if extension is None or file.endswith(f'.{extension}'):
                    files.append(file_path)
        return files
