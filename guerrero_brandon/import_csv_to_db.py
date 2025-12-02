#!/usr/bin/env python3
"""
Import student CSV data into SQLite database and match to existing FERPA PDFs.
"""

import sqlite3
import csv
import os
import glob


def create_database(db_name='students.db'):
    """
    Create SQLite database with students table.

    Args:
        db_name: Name of the database file

    Returns:
        Connection object
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT,
            major TEXT,
            gpa REAL,
            enrollment_date TEXT,
            has_ferpa INTEGER,
            pdf_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    return conn


def find_ferpa_pdf(student_id, firstname, lastname, pdf_directory='student_pdfs'):
    """
    Find FERPA PDF file for a student based on naming convention.

    Looks for files matching: {student_id}_{lastname}-{firstname}-*.pdf

    Args:
        student_id: Student ID (e.g., STU001)
        firstname: Student first name
        lastname: Student last name
        pdf_directory: Directory containing FERPA PDFs

    Returns:
        Path to PDF file if found, None otherwise
    """
    if not os.path.exists(pdf_directory):
        return None

    # Pattern: STU001_Doe-John-*.pdf
    pattern = f"{student_id}_{lastname}-{firstname}-*.pdf"
    search_path = os.path.join(pdf_directory, pattern)

    matches = glob.glob(search_path)

    if matches:
        # Return the first match (should only be one)
        return matches[0]

    return None


def import_csv_to_database(csv_filename='students.csv', db_name='students.db'):
    """
    Import CSV data into SQLite database and match to FERPA PDFs.

    Args:
        csv_filename: Path to CSV file
        db_name: Name of database file
    """
    if not os.path.exists(csv_filename):
        print(f"Error: CSV file '{csv_filename}' not found!")
        print("Please run 'python3 create_student_csv.py' first.")
        return

    # Create/connect to database
    print(f"Creating database '{db_name}'...")
    conn = create_database(db_name)
    cursor = conn.cursor()

    # Clear existing data (for fresh import)
    cursor.execute('DELETE FROM students')

    # Read CSV and import
    print(f"\nImporting data from '{csv_filename}'...")
    imported_count = 0
    matched_count = 0

    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Convert has_ferpa to integer (1 or 0)
            has_ferpa = 1 if row['has_ferpa'].lower() in ['yes', 'y', '1', 'true'] else 0

            # Try to find FERPA PDF if student has_ferpa flag is set
            pdf_path = None
            if has_ferpa:
                pdf_path = find_ferpa_pdf(
                    row['student_id'],
                    row['firstname'],
                    row['lastname']
                )
                if pdf_path:
                    matched_count += 1
                    print(f"  ✓ Matched: {row['student_id']} - {row['firstname']} {row['lastname']} → {os.path.basename(pdf_path)}")
                else:
                    print(f"  ⚠ No PDF found for: {row['student_id']} - {row['firstname']} {row['lastname']}")

            # Insert into database
            cursor.execute('''
                INSERT INTO students (
                    student_id, firstname, lastname, email, major,
                    gpa, enrollment_date, has_ferpa, pdf_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['student_id'],
                row['firstname'],
                row['lastname'],
                row['email'],
                row['major'],
                float(row['gpa']),
                row['enrollment_date'],
                has_ferpa,
                pdf_path
            ))

            imported_count += 1

    conn.commit()

    # Display summary
    print(f"\n{'='*60}")
    print("Import Summary")
    print(f"{'='*60}")

    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM students WHERE has_ferpa = 1')
    students_with_ferpa_flag = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM students WHERE pdf_path IS NOT NULL')
    students_with_pdf = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM students WHERE has_ferpa = 1 AND pdf_path IS NULL')
    students_missing_pdf = cursor.fetchone()[0]

    print(f"Total students imported: {total_students}")
    print(f"Students marked as having FERPA: {students_with_ferpa_flag}")
    print(f"Students with matched PDF files: {students_with_pdf}")
    if students_missing_pdf > 0:
        print(f"Students missing PDF files: {students_missing_pdf} ⚠")

    # Show students with FERPA files
    print(f"\n{'='*60}")
    print("Students with FERPA Files (Alphabetically by Last Name)")
    print(f"{'='*60}")

    cursor.execute('''
        SELECT student_id, firstname, lastname, pdf_path
        FROM students
        WHERE pdf_path IS NOT NULL
        ORDER BY lastname, firstname
    ''')

    for row in cursor.fetchall():
        student_id, firstname, lastname, pdf_path = row
        print(f"  {student_id}: {firstname} {lastname}")
        print(f"    → {pdf_path}")

    conn.close()

    print(f"\n{'='*60}")
    print(f"✓ Database '{db_name}' created successfully!")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("  1. Verify data: sqlite3 students.db 'SELECT * FROM students;'")
    print("  2. Combine PDFs: python3 combine_student_pdfs.py")


def main():
    """Main function."""
    print("=" * 60)
    print("Student CSV to Database Importer")
    print("=" * 60)
    print()

    import_csv_to_database()


if __name__ == "__main__":
    main()
