#!/usr/bin/env python3
"""
Generate mock PDF files with student data.
File naming convention: ID_lastname-firstname-timestamp.pdf
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def create_student_pdf(student_data, output_dir):
    """
    Create a PDF file with student information.

    Args:
        student_data: Dictionary containing student information
        output_dir: Directory to save the PDF file
    """
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Create filename: ID_lastname-firstname-timestamp.pdf
    filename = f"{student_data['id']}_{student_data['lastname']}-{student_data['firstname']}-{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    # Create PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1 * inch, height - 1 * inch, "Student Information")

    # Draw a line
    c.line(1 * inch, height - 1.2 * inch, width - 1 * inch, height - 1.2 * inch)

    # Student details
    c.setFont("Helvetica-Bold", 14)
    y_position = height - 2 * inch

    c.drawString(1 * inch, y_position, "Student Name:")
    c.setFont("Helvetica", 14)
    c.drawString(3 * inch, y_position, f"{student_data['firstname']} {student_data['lastname']}")

    y_position -= 0.5 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y_position, "Student ID:")
    c.setFont("Helvetica", 14)
    c.drawString(3 * inch, y_position, student_data['id'])

    y_position -= 0.5 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y_position, "Email:")
    c.setFont("Helvetica", 14)
    c.drawString(3 * inch, y_position, student_data['email'])

    y_position -= 0.5 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y_position, "Major:")
    c.setFont("Helvetica", 14)
    c.drawString(3 * inch, y_position, student_data['major'])

    y_position -= 0.5 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y_position, "GPA:")
    c.setFont("Helvetica", 14)
    c.drawString(3 * inch, y_position, str(student_data['gpa']))

    y_position -= 0.5 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y_position, "Enrollment Date:")
    c.setFont("Helvetica", 14)
    c.drawString(3 * inch, y_position, student_data['enrollment_date'])

    # Footer with generation timestamp
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(1 * inch, 0.5 * inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save PDF
    c.save()
    print(f"Created: {filename}")
    return filename


def main():
    """Main function to generate mock student PDFs."""
    # Create output directory
    output_dir = "student_pdfs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}/")

    # Mock student data
    students = [
        {
            "id": "STU001",
            "firstname": "John",
            "lastname": "Doe",
            "email": "john.doe@university.edu",
            "major": "Computer Science",
            "gpa": 3.85,
            "enrollment_date": "2022-09-01"
        },
        {
            "id": "STU002",
            "firstname": "Jane",
            "lastname": "Smith",
            "email": "jane.smith@university.edu",
            "major": "Business Administration",
            "gpa": 3.92,
            "enrollment_date": "2022-09-01"
        },
        {
            "id": "STU003",
            "firstname": "Michael",
            "lastname": "Johnson",
            "email": "michael.johnson@university.edu",
            "major": "Mechanical Engineering",
            "gpa": 3.67,
            "enrollment_date": "2023-01-15"
        },
        {
            "id": "STU004",
            "firstname": "Emily",
            "lastname": "Williams",
            "email": "emily.williams@university.edu",
            "major": "Psychology",
            "gpa": 3.78,
            "enrollment_date": "2022-09-01"
        },
        {
            "id": "STU005",
            "firstname": "David",
            "lastname": "Brown",
            "email": "david.brown@university.edu",
            "major": "Biology",
            "gpa": 3.95,
            "enrollment_date": "2023-01-15"
        }
    ]

    # Generate PDFs for each student
    print(f"\nGenerating {len(students)} student PDF files...\n")
    for student in students:
        create_student_pdf(student, output_dir)

    print(f"\nAll PDFs generated successfully in '{output_dir}/' directory!")


if __name__ == "__main__":
    main()
