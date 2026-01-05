"""
Import/Export service for handling data import and export operations.
"""

import csv
import json
import openpyxl
from typing import List, Dict
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import FileOperationException
from school_system.core.utils import ValidationUtils


class ImportExportService:
    """Service for handling data import and export operations."""

    def export_to_csv(self, data: List[Dict], filename: str) -> bool:
        """
        Export data to a CSV file.

        Args:
            data: The data to export.
            filename: The name of the CSV file.

        Returns:
            True if the export was successful, otherwise False.
        """
        logger.info(f"Exporting data to CSV file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"Data exported successfully to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    def import_from_csv(self, filename: str) -> List[Dict]:
        """
        Import data from a CSV file.

        Args:
            filename: The name of the CSV file.

        Returns:
            The imported data as a list of dictionaries.
        """
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return []

    def export_to_json(self, data: List[Dict], filename: str) -> bool:
        """
        Export data to a JSON file.

        Args:
            data: The data to export.
            filename: The name of the JSON file.

        Returns:
            True if the export was successful, otherwise False.
        """
        try:
            with open(filename, mode='w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False

    def import_from_json(self, filename: str) -> List[Dict]:
        """
        Import data from a JSON file.

        Args:
            filename: The name of the JSON file.

        Returns:
            The imported data as a list of dictionaries.
        """
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error importing from JSON: {e}")
            return []

    def export_to_excel(self, data: List[Dict], filename: str) -> bool:
        """
        Export data to an Excel file.

        Args:
            data: The data to export.
            filename: The name of the Excel file.

        Returns:
            True if the export was successful, otherwise False.
        """
        logger.info(f"Exporting data to Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            
            if data:
                headers = list(data[0].keys())
                sheet.append(headers)
                
                for row in data:
                    sheet.append([row.get(header, '') for header in headers])
            
            workbook.save(filename)
            logger.info(f"Data exported successfully to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False

    def import_from_excel(self, filename: str) -> List[Dict]:
        """
        Import data from an Excel file.

        Args:
            filename: The name of the Excel file.

        Returns:
            The imported data as a list of dictionaries.
        """
        try:
            workbook = openpyxl.load_workbook(filename)
            sheet = workbook.active
            
            headers = [cell.value for cell in sheet[1]]
            data = []
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row:
                    data.append(dict(zip(headers, row)))
            
            return data
        except Exception as e:
            print(f"Error importing from Excel: {e}")
            return []