"""
Export Utilities

This module provides functionality for exporting data in various formats
such as CSV, Excel, PDF, and JSON for reporting and data exchange purposes.
"""

import csv
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime


class ExportUtils:
    """A utility class for exporting data in various formats."""

    @staticmethod
    def export_to_csv(
        data: List[Dict[str, Any]], 
        file_path: str,
        fieldnames: Optional[List[str]] = None,
        delimiter: str = ',',
        include_header: bool = True
    ) -> str:
        """
        Export data to a CSV file.

        Args:
            data: List of dictionaries containing data to export
            file_path: Path to the output CSV file
            fieldnames: List of field names (headers)
            delimiter: Delimiter to use in the CSV file
            include_header: Whether to include header row

        Returns:
            Path to the created CSV file

        Raises:
            IOError: If there's an error writing to the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)
            
            if include_header:
                writer.writeheader()
            
            writer.writerows(data)
        
        return file_path

    @staticmethod
    def export_to_json(
        data: Any, 
        file_path: str,
        indent: int = 4,
        sort_keys: bool = False
    ) -> str:
        """
        Export data to a JSON file.

        Args:
            data: Data to export as JSON
            file_path: Path to the output JSON file
            indent: Indentation level for pretty printing
            sort_keys: Whether to sort dictionary keys

        Returns:
            Path to the created JSON file

        Raises:
            IOError: If there's an error writing to the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=indent, ensure_ascii=False, sort_keys=sort_keys)
        
        return file_path

    @staticmethod
    def export_to_txt(
        data: List[str], 
        file_path: str,
        newline: str = '\n'
    ) -> str:
        """
        Export text data to a plain text file.

        Args:
            data: List of strings to export
            file_path: Path to the output text file
            newline: Newline character to use

        Returns:
            Path to the created text file

        Raises:
            IOError: If there's an error writing to the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(newline.join(data))
        
        return file_path

    @staticmethod
    def export_to_html(
        data: List[Dict[str, Any]], 
        file_path: str,
        title: str = "Export Data",
        table_id: str = "export-table"
    ) -> str:
        """
        Export data to an HTML file with a table.

        Args:
            data: List of dictionaries containing data to export
            file_path: Path to the output HTML file
            title: Title for the HTML page
            table_id: ID attribute for the HTML table

        Returns:
            Path to the created HTML file

        Raises:
            IOError: If there's an error writing to the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not data:
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .no-data {{ color: #666; font-style: italic; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="no-data">No data available</p>
</body>
</html>"""
        else:
            # Generate HTML table
            headers = list(data[0].keys())
            
            rows = []
            for item in data:
                row = "<tr>" + "".join(f"<td>{item.get(header, '')}</td>" for header in headers) + "</tr>"
                rows.append(row)
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f1f1f1; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <table id="{table_id}">
        <thead>
            <tr>{"".join(f"<th>{header}</th>" for header in headers)}</tr>
        </thead>
        <tbody>
            {"\n"
            .join(rows)}
        </tbody>
    </table>
    <p style="margin-top: 20px; color: #666; font-size: 0.9em;">
        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
</body>
</html>"""
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        
        return file_path

    @staticmethod
    def export_to_markdown(
        data: List[Dict[str, Any]], 
        file_path: str,
        title: str = "Export Data"
    ) -> str:
        """
        Export data to a Markdown file with a table.

        Args:
            data: List of dictionaries containing data to export
            file_path: Path to the output Markdown file
            title: Title for the Markdown document

        Returns:
            Path to the created Markdown file

        Raises:
            IOError: If there's an error writing to the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not data:
            markdown_content = f"# {title}\n\nNo data available\n"
        else:
            headers = list(data[0].keys())
            
            # Create table header
            header_row = " | ".join(headers)
            separator_row = " | ".join("---" for _ in headers)
            
            # Create data rows
            data_rows = []
            for item in data:
                row = " | ".join(str(item.get(header, '')) for header in headers)
                data_rows.append(row)
            
            markdown_content = f"# {title}\n\n{header_row}\n{separator_row}\n" + "\n".join(data_rows) + "\n"
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)
        
        return file_path

    @staticmethod
    def export_to_sql(
        data: List[Dict[str, Any]], 
        file_path: str,
        table_name: str
    ) -> str:
        """
        Export data to an SQL INSERT statements file.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not data:
            sql_content = f"-- SQL Export for {table_name}\n-- No data available\n"
        else:
            headers = list(data[0].keys())
            insert_statements = []

            for item in data:
                columns = ", ".join(headers)
                values_list = []

                for header in headers:
                    raw_value = item.get(header, "")
                    raw_value = "" if raw_value is None else str(raw_value)

                    # Escape single quotes for SQL
                    escaped_value = raw_value.replace("'", "''")
                    values_list.append(f"'{escaped_value}'")

                values = ", ".join(values_list)
                insert_statements.append(
                    f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                )

            sql_content = (
                f"-- SQL Export for {table_name}\n"
                f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                + "\n".join(insert_statements)
                + "\n"
            )
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(sql_content)
        
        return file_path
