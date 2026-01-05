# School-System-Management

A Python-based application for managing school operations, including student records, library resources, and administrative tasks. Features include a graphical user interface (GUI), QR code scanning for data entry, and a database for persistent storage.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Student Management**: Add, update, and view student information.
- **Library System**: Manage books, track borrowing, and handle returns.
- **Library Reports**: Gives detailed reports about revision books, borrowing and returning records and total books in the library per category.
- **QR Code Scanning**: Use QR codes for quick student or resource identification, borrowing and returning.
- **Resource Management**: They include Ream and Furniture Management. 
- **Graphical Interface**: User-friendly GUI for administrators.
- **Database Storage**: Store data securely with a local database.

## Requirements
- Python 3.8 or higher
- Dependencies listed in `requirements.txt`
- A compatible database system (e.g., SQLite, configured separately)
- Git (for cloning the repository)
- A webcam or QR code scanner (for QR code functionality, if applicable)

## Installation
Follow these steps to set up the School System Management application on your local machine.

1. **Clone the repository**:
   Clone the project from GitHub to your local machine:
   ```bash
   git clone https://github.com/harry647/School-System-Management.git
   cd School-System-Management

2. **Set up a virtual environment**:
   - Create a virtual environment to isolate dependencies (recommended):
   ```bash
   python -m venv venv
   ```
   - Activate the virtual environment
   ```bash
   venv\Scripts\activate
   ```
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**: 
   Install the required Python packages listed in requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note**: If you encounter issues with the `fitz` package, make sure to install PyMuPDF instead:
   ```bash
   pip uninstall fitz -y
   pip install PyMuPDF
   ```

4. **Prepare for configuration**: The application requires configuration files, which are not included in the repository for security reasons. Proceed to the Configuration section below.

## Configuration
The application requires specific configuration files that are not included in the repository for security reasons. Follow these steps to set up the necessary files:

1. **Copy example configuration files**:
   ```bash
   cp renewal.json.example renewal.json
   cp licence.json.example licence.json
   ```

2. **Configure renewal.json**:
   Edit `renewal.json` and replace `YOUR_RENEWAL_KEY_HERE` with your actual renewal key:
   ```json
   {
       "renewal_key": "YOUR_ACTUAL_RENEWAL_KEY"
   }
   ```

3. **Configure licence.json**:
   Edit `licence.json` and set the expiration date in YYYY-MM-DD format:
   ```json
   {
       "expiration_date": "2025-12-31"
   }
   ```

4. **Default Login Credentials**:
   - Default Password: `harry123`
   - You can change this after first login by creating a new user account

**Note**: The database will be created automatically when you first run the application.

## Usage

1. **Activate the virtual environment (if not already active)**:
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Use the GUI to**:
   - Add or update student records.
   - Manage library books and borrowing.
   - Deal with resource management
   - Scan QR codes for attendance or resource tracking.
   - Generate reports or view data.
   - Refer to help.txt for detailed instructions, shortcuts, or troubleshooting tips.

## Project Structure
```
School-System-Management/
├── QRcode_Reader.py         # Handles QR code scanning
├── db_manager.py            # Manages database operations
├── db_utils.py              # Database utility functions
├── gui_manager.py           # Manages the graphical interface
├── library_logic.py         # Library system logic
├── main.py                  # Application entry point
├── setup_school.py          # Initializes the database
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── renewal.json.example     # Example renewal configuration
├── licence.json.example     # Example license configuration
├── .gitignore               # Git ignore rules
├── help.txt                 # User guide
├── school_icon.ico          # Application icon
```

**Note**: Configuration files (`renewal.json`, `licence.json`) and the database are not included in the repository. Create them as described in the Configuration section above.

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'frontend'**
   - This occurs when the wrong `fitz` package is installed
   - Solution: `pip uninstall fitz -y && pip install PyMuPDF`

2. **Missing renewal.json or licence.json files**
   - Copy from example files: `cp renewal.json.example renewal.json`
   - Copy from example files: `cp licence.json.example licence.json`

3. **Database connection issues**
   - The database is created automatically on first run
   - Ensure you have write permissions in the application directory

## Contributing
Contributions are welcome! To contribute:

1. Fork the repository.
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Commit your changes**:
   ```bash
   git commit -m "Add your feature"
   ```

4. **Push to your branch**:
   ```bash
   git push origin feature/your-feature
   ```

5. **Open a pull request on GitHub**.
   - Please include tests and follow the project's coding style.

## License
This project is licensed under the MIT License (pending addition of a LICENSE file). See the repository for details.
