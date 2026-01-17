# Borrowing Analytics System

## Overview

The Borrowing Analytics System provides comprehensive insights into library borrowing patterns, inventory status, and student participation across different classes, streams, and subjects. This system generates detailed reports that help librarians understand borrowing trends and identify areas needing attention.

## Features

### 📊 Comprehensive Analytics Reports

1. **Borrowing Summary by Subject/Stream/Form**
   - Detailed breakdown of borrowing activity by subject within each stream and form
   - Individual student borrowing records
   - Total borrowing counts and unique student counts

2. **Borrowing Percentage by Class**
   - Percentage of students who have borrowed books in each class
   - Comparison against total class enrollment
   - Average borrowings per student

3. **Inventory Summary**
   - Total number of books in the system
   - Current availability status
   - Borrowing utilization percentage

4. **Books Categorized by Subject and Form**
   - Distribution of books across subjects and class levels
   - Availability status within each category
   - Borrowing rates by category

5. **Students Not Borrowed by Stream/Subject**
   - Identification of students who haven't borrowed from specific subjects
   - Stream-wise breakdown of non-participants
   - Detailed student lists for targeted outreach

6. **Students Not Borrowed Any Books**
   - Complete list of students with zero borrowing activity
   - Stream-wise organization
   - Total count of inactive borrowers

## User Interface

### Access
Navigate to **Reports** → **Book Reports** → Select **"Borrowing Analytics"** from the report type dropdown.

### Report Display

#### Summary Panel
- **Inventory Overview**: Total books, availability, utilization
- **Inactive Students**: Count and stream breakdown
- **Key Metrics**: Borrowing percentages and averages

#### Data Tables
- **Class Borrowing Percentages**: Tabular view with sortable columns
- **Book Categorization**: Subject-wise book distribution
- **Detailed Lists**: Student names and borrowing gaps

### Export Options
- **Excel Export**: Structured spreadsheet with all analytics data
- **PDF Export**: Formatted report for printing and sharing

## Technical Implementation

### ReportService Analytics Methods

#### `get_borrowing_analytics_report()`
Main method that orchestrates all analytics calculations and returns comprehensive report data.

#### `_get_borrowing_summary_by_subject_stream_form()`
```python
# Analyzes borrowing patterns by subject within each stream/form combination
# Returns detailed breakdown with student lists and borrowing counts
```

#### `_get_borrowing_percentage_by_class()`
```python
# Calculates borrowing participation rates for each class
# Compares active borrowers against total enrollment
```

#### `_get_inventory_summary()`
```python
# Aggregates book inventory statistics
# Calculates availability and utilization metrics
```

#### `_get_books_categorized_by_subject_form()`
```python
# Groups books by subject and class level
# Tracks availability within each category
```

#### `_get_students_not_borrowed_by_stream_subject()`
```python
# Identifies students without borrowing activity in specific subjects
# Organizes by stream and subject combinations
```

#### `_get_students_not_borrowed_any_books()`
```python
# Finds students with zero borrowing activity across all subjects
# Groups by stream for organizational insights
```

### Data Sources

#### Student Data
- **Source**: `students` table via StudentService
- **Fields**: admission_number, name, stream, class associations
- **Processing**: Stream validation and class grouping

#### Book Data
- **Source**: `books` table via BookService
- **Fields**: subject, class_name, availability status
- **Processing**: Subject categorization and availability tracking

#### Borrowing Data
- **Source**: `borrowed_books_student` table via BorrowedBookStudentRepository
- **Fields**: student_id, book_id, borrowing dates
- **Processing**: Activity tracking and pattern analysis

### Analytics Calculations

#### Borrowing Percentage
```python
student_borrowing_percentage = (students_borrowed / total_students) * 100
```

#### Book Utilization
```python
borrowed_percentage = (borrowed_books / total_books) * 100
```

#### Category-wise Availability
```python
availability_rate = (available_books / total_books) * 100
```

## Report Structure

### JSON Response Format
```json
{
  "borrowing_summary_by_subject_stream_form": [...],
  "borrowing_percentage_by_class": [...],
  "inventory_summary": {...},
  "books_categorized_by_subject_form": [...],
  "students_not_borrowed_by_stream_subject": [...],
  "students_not_borrowed_any_books": {...}
}
```

### Borrowing Summary Item
```json
{
  "form": "Form 4",
  "stream": "Red",
  "subject": "Mathematics",
  "total_students": 25,
  "students_borrowed": 18,
  "total_borrowings": 32,
  "books_borrowed": [...]
}
```

### Class Percentage Item
```json
{
  "form": "Form 4",
  "total_students": 25,
  "students_borrowed": 18,
  "student_borrowing_percentage": 72.0,
  "total_borrowings": 32,
  "average_borrowings_per_student": 1.28
}
```

### Inventory Summary
```json
{
  "total_books": 150,
  "available_books": 120,
  "borrowed_books": 30,
  "borrowed_percentage": 20.0
}
```

## Usage Examples

### Generating Analytics Report
```python
from school_system.services.report_service import ReportService

report_service = ReportService()
analytics = report_service.get_borrowing_analytics_report()

# Access different analytics
inventory = analytics['inventory_summary']
percentages = analytics['borrowing_percentage_by_class']
not_borrowed = analytics['students_not_borrowed_any_books']
```

### Displaying in UI
```python
def _display_borrowing_analytics(self, analytics_data):
    # Update summary text
    summary = self._generate_analytics_summary(analytics_data)
    self.summary_text.setPlainText(summary)

    # Update data tables
    self._populate_percentage_table(analytics_data['borrowing_percentage_by_class'])
    self._populate_categorization_table(analytics_data['books_categorized_by_subject_form'])
```

## Performance Considerations

### Data Processing Optimization
- **Lazy Loading**: Analytics calculated only when requested
- **Caching**: Heavy computations cached where possible
- **Pagination**: Large student lists handled efficiently

### Database Query Efficiency
- **Indexed Queries**: Uses indexed fields for fast retrieval
- **Batch Processing**: Large datasets processed in chunks
- **Connection Pooling**: Efficient database connection management

## Error Handling

### Data Validation
- **Stream Format Validation**: Handles invalid stream formats gracefully
- **Missing Data**: Continues processing with available data
- **Division by Zero**: Protected against empty datasets

### Exception Management
- **Try-Catch Blocks**: Comprehensive error catching
- **Graceful Degradation**: Continues with partial data when possible
- **User Feedback**: Clear error messages for UI display

## Integration Points

### UI Components
- **BookReportsWindow**: Main interface for analytics display
- **Dynamic Tables**: Adapts to different analytics data structures
- **Export Functions**: Supports Excel and PDF output formats

### Service Dependencies
- **StudentService**: Student data and stream management
- **BookService**: Book inventory and categorization
- **ClassManagementService**: Class and stream organization

### Database Dependencies
- **students**: Student enrollment and stream data
- **books**: Book inventory with subject/class categorization
- **borrowed_books_student**: Borrowing transaction history

## Future Enhancements

### Planned Features
- **Real-time Analytics**: Live updating dashboard
- **Trend Analysis**: Historical borrowing pattern tracking
- **Predictive Insights**: Forecasting borrowing needs
- **Custom Reports**: User-defined analytics combinations
- **Email Notifications**: Automated report distribution

### API Endpoints
```python
GET /api/analytics/borrowing-summary
GET /api/analytics/class-percentages
GET /api/analytics/inventory-status
POST /api/analytics/export/{format}
```

## Troubleshooting

### Common Issues

#### No Data in Reports
- **Cause**: Empty database or missing borrowing records
- **Solution**: Verify data exists and run sample transactions

#### Performance Issues
- **Cause**: Large datasets causing slow queries
- **Solution**: Implement pagination or data sampling

#### Invalid Stream Formats
- **Cause**: Students with non-standard stream names
- **Solution**: Standardize stream naming conventions

### Debug Information
Enable detailed logging for analytics generation:
```python
import logging
logging.getLogger('school_system.services.report_service').setLevel(logging.DEBUG)
```

## Security Considerations

### Data Privacy
- **Student Information**: Only displays necessary identification data
- **Access Control**: Analytics restricted to authorized librarian roles
- **Audit Logging**: All report generation activities logged

### Data Integrity
- **Transaction Safety**: Analytics calculations don't modify data
- **Read-Only Operations**: No database writes during report generation
- **Validation**: Input parameters validated before processing

## Support

For technical support or feature requests related to the Borrowing Analytics System, refer to the main application documentation or contact the development team.