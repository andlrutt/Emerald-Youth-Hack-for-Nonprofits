#!/usr/bin/env python3
"""
Combine multiple student FERPA PDF files into a single PDF document.
Reads student data from SQLite database and only includes students with FERPA files.
Students are organized alphabetically by last name.
"""

import os
import sqlite3
from datetime import datetime
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io


def get_students_with_ferpa(db_name='students.db'):
    """
    Query database for students with FERPA files.

    Args:
        db_name: Name of the SQLite database

    Returns:
        List of student dictionaries, sorted alphabetically by last name
    """
    if not os.path.exists(db_name):
        print(f"Error: Database '{db_name}' not found!")
        print("Please run 'python3 import_csv_to_db.py' first.")
        return None, None

    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    # Get total student count
    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0]

    # Get students with FERPA files, sorted alphabetically
    cursor.execute('''
        SELECT student_id, firstname, lastname, email, major, gpa,
               enrollment_date, pdf_path
        FROM students
        WHERE has_ferpa = 1 AND pdf_path IS NOT NULL
        ORDER BY lastname, firstname
    ''')

    students = []
    for row in cursor.fetchall():
        students.append({
            'id': row['student_id'],
            'firstname': row['firstname'],
            'lastname': row['lastname'],
            'email': row['email'],
            'major': row['major'],
            'gpa': row['gpa'],
            'enrollment_date': row['enrollment_date'],
            'pdf_path': row['pdf_path'],
            'display_name': f"{row['firstname']} {row['lastname']}"
        })

    conn.close()

    return students, total_students


def create_cover_page(students, total_students, output_stream):
    """
    Create a professional cover page for the combined PDF.

    Args:
        students: List of student dictionaries with FERPA files
        total_students: Total number of students in database
        output_stream: BytesIO stream to write the PDF to
    """
    c = canvas.Canvas(output_stream, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 28)
    title = "Student FERPA Records"
    title_width = c.stringWidth(title, "Helvetica-Bold", 28)
    c.drawString((width - title_width) / 2, height - 1.5 * inch, title)

    c.setFont("Helvetica-Bold", 18)
    subtitle = "Combined Report"
    subtitle_width = c.stringWidth(subtitle, "Helvetica-Bold", 18)
    c.drawString((width - subtitle_width) / 2, height - 2 * inch, subtitle)

    # Draw a line
    c.setLineWidth(2)
    c.line(1 * inch, height - 2.3 * inch, width - 1 * inch, height - 2.3 * inch)

    # Summary information
    c.setFont("Helvetica", 12)
    y_position = height - 3 * inch

    c.drawString(1 * inch, y_position, f"Total Students in Database: {total_students}")
    y_position -= 0.3 * inch

    c.drawString(1 * inch, y_position, f"Students with FERPA Files: {len(students)}")
    y_position -= 0.3 * inch

    missing_ferpa = total_students - len(students)
    if missing_ferpa > 0:
        c.drawString(1 * inch, y_position, f"Students Pending FERPA: {missing_ferpa}")
        y_position -= 0.3 * inch

    c.drawString(1 * inch, y_position, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    y_position -= 0.5 * inch

    # Student list header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y_position, "Students with FERPA Files (Alphabetically Sorted):")
    y_position -= 0.4 * inch

    # List all students with FERPA
    c.setFont("Helvetica", 11)
    for idx, student in enumerate(students, 1):
        if y_position < 1 * inch:  # Start new page if running out of space
            c.showPage()
            c.setFont("Helvetica", 11)
            y_position = height - 1 * inch

        student_line = f"{idx}. {student['display_name']} (ID: {student['id']}) - {student['major']}"
        c.drawString(1.5 * inch, y_position, student_line)
        y_position -= 0.25 * inch

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(1 * inch, 0.5 * inch, "This document contains FERPA records for students organized alphabetically by last name.")

    c.save()
    output_stream.seek(0)


def combine_pdfs_from_database(db_name='students.db', output_filename='combined_students.pdf'):
    """
    Combine PDF files for students from database.
    Only includes students with FERPA files, sorted alphabetically by last name.

    Args:
        db_name: Name of the SQLite database
        output_filename: Name of the combined output PDF file
    """
    # Get students from database
    print("\nQuerying database for students with FERPA files...")
    students, total_students = get_students_with_ferpa(db_name)

    if students is None:
        return

    if not students:
        print("No students with FERPA files found in database.")
        return

    print(f"\nDatabase Summary:")
    print(f"  Total students: {total_students}")
    print(f"  Students with FERPA: {len(students)}")
    print(f"  Students pending FERPA: {total_students - len(students)}")

    print("\nStudents with FERPA files (alphabetically by last name):")
    for idx, student in enumerate(students, 1):
        print(f"  {idx}. {student['display_name']} ({student['id']}) - {student['major']}")

    # Verify PDF files exist
    print("\nVerifying PDF files...")
    missing_files = []
    for student in students:
        if not os.path.exists(student['pdf_path']):
            missing_files.append(student)
            print(f"  ⚠ Missing: {student['pdf_path']}")
        else:
            print(f"  ✓ Found: {os.path.basename(student['pdf_path'])}")

    if missing_files:
        print(f"\nError: {len(missing_files)} PDF file(s) are missing!")
        print("Please ensure all FERPA PDFs are in the 'student_pdfs/' directory.")
        return

    # Create PDF writer
    pdf_writer = PdfWriter()

    # Create and add cover page
    print("\nCreating cover page...")
    cover_stream = io.BytesIO()
    create_cover_page(students, total_students, cover_stream)
    cover_reader = PdfReader(cover_stream)
    for page in cover_reader.pages:
        pdf_writer.add_page(page)

    # Add each student's PDF in alphabetical order
    print("\nCombining PDFs...")
    for student in students:
        try:
            pdf_reader = PdfReader(student['pdf_path'])
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            print(f"  ✓ Added: {student['display_name']}")
        except Exception as e:
            print(f"  ✗ Error adding {student['display_name']}: {str(e)}")

    # Write the combined PDF to file
    with open(output_filename, 'wb') as output_file:
        pdf_writer.write(output_file)

    print(f"\n✓ Successfully created '{output_filename}'")
    print(f"  Total pages: {len(pdf_writer.pages)}")
    print(f"  Students included: {len(students)}")


def main():
    """Main function to combine student FERPA PDFs from database."""
    db_name = "students.db"
    output_filename = "combined_students.pdf"

    print("=" * 60)
    print("Student FERPA PDF Combiner (Database-Driven)")
    print("=" * 60)

    combine_pdfs_from_database(db_name, output_filename)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
