# Student FERPA Management System

A comprehensive student data management system using SQLite database and CSV for tracking and combining FERPA (Family Educational Rights and Privacy Act) documents. This system simulates a realistic non-profit scenario where not all students have submitted their FERPA documents.

## Overview

This system manages student records and their associated FERPA PDF documents, allowing organizations to:
- Maintain a database of student information
- Track which students have submitted FERPA documents
- Automatically match student records to PDF files
- Generate combined FERPA reports with only students who have submitted documentation
- Organize everything alphabetically by last name

## System Architecture

```
CSV File (students.csv) - 12 students
    ↓
SQLite Database (students.db)
    ├── 5 students WITH FERPA files
    └── 7 students WITHOUT FERPA files (pending)
    ↓
Match to existing PDFs in student_pdfs/
    ↓
Combined Report (combined_students.pdf)
    - Professional cover page
    - Only students with FERPA files
    - Alphabetically sorted
```

## Features

- **CSV as Source of Truth**: Easy to edit by non-technical staff
- **SQLite Database**: Efficient querying and data management
- **Automatic PDF Matching**: Intelligently matches CSV records to existing FERPA PDFs
- **Realistic Scenario**: Handles incomplete FERPA submissions (common in non-profits)
- **Alphabetical Sorting**: Always organized by last name
- **Professional Cover Page**: Shows statistics and student roster
- **Scalable**: Easy to add more students and re-import
- **Audit Trail**: Database tracks creation and update timestamps

## Project Structure

```
/hackathon/
├── README.md                       # This file
├── students.csv                    # CSV source of truth (12 students)
├── students.db                     # SQLite database
├── create_student_csv.py          # Generate mock CSV file
├── import_csv_to_db.py            # Import CSV to database
├── generate_student_pdfs.py       # Generate individual FERPA PDFs
├── combine_student_pdfs.py        # Combine PDFs from database
├── student_pdfs/                   # Directory containing FERPA PDFs
│   ├── STU001_Doe-John-*.pdf
│   ├── STU002_Smith-Jane-*.pdf
│   ├── STU003_Johnson-Michael-*.pdf
│   ├── STU004_Williams-Emily-*.pdf
│   └── STU005_Brown-David-*.pdf
└── combined_students.pdf          # Final combined output
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Required Python Packages

```bash
pip install pypdf reportlab
```

### Built-in Packages (no installation needed)
- `sqlite3`
- `csv`
- `os`
- `glob`
- `datetime`

## Quick Start

### 1. Generate Mock Student Data

```bash
python3 create_student_csv.py
```

**Output:**
- Creates `students.csv` with 12 mock students
- 5 students marked as having FERPA documents
- 7 students without FERPA documents (pending)

### 2. Import CSV to Database

```bash
python3 import_csv_to_db.py
```

**Output:**
- Creates `students.db` SQLite database
- Imports all 12 students
- Automatically matches 5 students to existing FERPA PDFs in `student_pdfs/`
- Displays summary of matched and pending students

### 3. Generate Combined FERPA Report

```bash
python3 combine_student_pdfs.py
```

**Output:**
- Creates `combined_students.pdf`
- Includes professional cover page with statistics
- Contains only students with FERPA files (5 students)
- Organized alphabetically by last name

## Student Data

### Students WITH FERPA Files (5)

| ID | Name | Major | GPA | FERPA Status |
|----|------|-------|-----|--------------|
| STU001 | John Doe | Computer Science | 3.85 | ✓ Available |
| STU002 | Jane Smith | Business Administration | 3.92 | ✓ Available |
| STU003 | Michael Johnson | Mechanical Engineering | 3.67 | ✓ Available |
| STU004 | Emily Williams | Psychology | 3.78 | ✓ Available |
| STU005 | David Brown | Biology | 3.95 | ✓ Available |

### Students WITHOUT FERPA Files (7)

| ID | Name | Major | GPA | FERPA Status |
|----|------|-------|-----|--------------|
| STU006 | Sarah Martinez | Chemistry | 3.72 | ⚠ Pending |
| STU007 | James Garcia | Mathematics | 3.88 | ⚠ Pending |
| STU008 | Lisa Rodriguez | English Literature | 3.64 | ⚠ Pending |
| STU009 | Robert Anderson | Physics | 3.91 | ⚠ Pending |
| STU010 | Amanda Taylor | Sociology | 3.55 | ⚠ Pending |
| STU011 | Christopher Lee | Political Science | 3.76 | ⚠ Pending |
| STU012 | Rachel Davis | Art History | 3.82 | ⚠ Pending |

## Database Schema

### `students` Table

```sql
CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT,
    major TEXT,
    gpa REAL,
    enrollment_date TEXT,
    has_ferpa INTEGER,              -- 1 = Yes, 0 = No
    pdf_path TEXT,                  -- Path to FERPA PDF (NULL if pending)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## File Naming Convention

FERPA PDF files follow this naming pattern:
```
{student_id}_{lastname}-{firstname}-{timestamp}.pdf
```

**Examples:**
- `STU001_Doe-John-20251202113959.pdf`
- `STU002_Smith-Jane-20251202113959.pdf`

## Usage Examples

### Query Students with FERPA Files

```bash
sqlite3 students.db "SELECT student_id, firstname, lastname, major FROM students WHERE has_ferpa = 1 AND pdf_path IS NOT NULL ORDER BY lastname;"
```

### Query Students Pending FERPA

```bash
sqlite3 students.db "SELECT student_id, firstname, lastname, email FROM students WHERE has_ferpa = 0 OR pdf_path IS NULL ORDER BY lastname;"
```

### Get Database Statistics

```bash
sqlite3 students.db "
SELECT
    COUNT(*) as total_students,
    SUM(CASE WHEN has_ferpa = 1 AND pdf_path IS NOT NULL THEN 1 ELSE 0 END) as with_ferpa,
    SUM(CASE WHEN has_ferpa = 0 OR pdf_path IS NULL THEN 1 ELSE 0 END) as pending_ferpa
FROM students;"
```

### Export All Data to CSV

```bash
sqlite3 -header -csv students.db "SELECT * FROM students;" > export.csv
```

## Adding New Students

### Option 1: Edit CSV and Re-import

1. Edit `students.csv` with new student records
2. Run: `python3 import_csv_to_db.py`
3. The database will be refreshed with new data

### Option 2: Direct Database Insert

```bash
sqlite3 students.db "
INSERT INTO students (student_id, firstname, lastname, email, major, gpa, enrollment_date, has_ferpa)
VALUES ('STU013', 'Alex', 'Thompson', 'alex.thompson@university.edu', 'Engineering', 3.70, '2024-09-01', 0);
"
```

## Generating New FERPA PDFs

To generate a FERPA PDF for a student in the database:

1. Modify `generate_student_pdfs.py` to read from database
2. Or manually create PDF and name it following the convention
3. Run `python3 import_csv_to_db.py` to refresh matches

## Troubleshooting

### "No module named 'pypdf'" or "No module named 'reportlab'"

**Solution:**
```bash
pip3 install pypdf reportlab
```

### "Database not found" when running combine script

**Solution:**
```bash
python3 import_csv_to_db.py
```

### PDFs not matching to students

**Issue:** PDF filename doesn't match the expected pattern.

**Solution:** Ensure PDF files follow the naming convention:
```
{student_id}_{lastname}-{firstname}-{timestamp}.pdf
```

Example: `STU001_Doe-John-20251202113959.pdf`

### "Students missing PDF files" error

**Issue:** Database has `pdf_path` set but file doesn't exist.

**Solution:**
1. Check if PDF files are in `student_pdfs/` directory
2. Re-run `python3 import_csv_to_db.py` to refresh matches

## Scripts Reference

### `create_student_csv.py`
Generates a mock CSV file with 12 students (5 with FERPA, 7 without).

**Usage:** `python3 create_student_csv.py`

### `import_csv_to_db.py`
Imports CSV data into SQLite database and matches students to existing FERPA PDFs.

**Usage:** `python3 import_csv_to_db.py`

**Features:**
- Creates database if it doesn't exist
- Matches students to PDFs by filename pattern
- Displays detailed import summary

### `generate_student_pdfs.py`
Generates individual FERPA PDF files from hardcoded student data.

**Usage:** `python3 generate_student_pdfs.py`

**Note:** This was the original script. For new PDFs, consider modifying it to read from database.

### `combine_student_pdfs.py`
Reads from database and combines FERPA PDFs into a single document.

**Usage:** `python3 combine_student_pdfs.py`

**Features:**
- Queries database for students with FERPA files
- Verifies PDF files exist
- Creates professional cover page
- Combines PDFs alphabetically by last name
- Shows statistics (total students vs. students with FERPA)

## Use Cases

### Non-Profit Organization
Track student FERPA submissions and generate compliance reports showing which students have and haven't submitted documents.

### Educational Institution
Manage student records and generate combined FERPA packages for administrative purposes.

### Hackathon / Demo
Demonstrate a realistic data management system with partial data availability (common in real-world scenarios).

## Future Enhancements

- **Web Interface**: Build a Flask/Django web app for easier management
- **Email Notifications**: Automatically email students who haven't submitted FERPA
- **PDF Validation**: Check PDF content to ensure it's a valid FERPA document
- **Export Reports**: Generate Excel reports of FERPA submission status
- **Audit Logging**: Track when PDFs are added/removed
- **Bulk Upload**: Handle multiple PDF uploads at once

## Contributing

This is a hackathon project for educational purposes. Feel free to:
- Add new features
- Improve the database schema
- Enhance the PDF generation
- Add data validation
- Create a web interface

## License

This project is created for educational and hackathon purposes. Feel free to use and modify as needed.

## Contact

For questions or issues, please refer to the project repository or contact the development team.

---

**Generated for Non-Profit Hackathon** | Student FERPA Management System v1.0
