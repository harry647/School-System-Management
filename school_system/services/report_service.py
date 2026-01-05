"""
Report service for generating and managing reports.
"""

from typing import Dict, List
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import validate_input
from school_system.models.report import Report
from school_system.database.repositories.report_repository import ReportRepository


class ReportService:
    """Service for generating and managing reports."""

    def __init__(self):
        self.report_repository = ReportRepository()

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
        validate_input(report_type, "Report type cannot be empty")
        
        # Logic to generate the report
        report_data = self._generate_report_data(report_type, parameters)
        report = Report(report_type=report_type, data=report_data, **parameters)
        created_report = self.report_repository.create(report)
        logger.info(f"Report generated successfully with ID: {created_report.id}")
        return created_report

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

    def get_report_by_id(self, report_id: int) -> Report:
        """
        Retrieve a report by its ID.

        Args:
            report_id: The ID of the report.

        Returns:
            The Report object if found, otherwise None.
        """
        return self.report_repository.get_by_id(report_id)

    def get_all_reports(self) -> List[Report]:
        """
        Retrieve all reports.

        Returns:
            A list of all Report objects.
        """
        return self.report_repository.get_all()