#!/usr/bin/env python3
"""
Generate mock CSV file with student data for FERPA management system.
Includes students with and without FERPA documents.
"""

import csv
from datetime import datetime


def create_students_csv(filename='students.csv'):
    """
    Create a CSV file with mock student data.

    Includes:
    - 5 students WITH FERPA files (matching existing PDFs)
    - 7 students WITHOUT FERPA files
    - Total: 12 students
    """

    # Student data
    students = [
        # Students WITH FERPA files (these match our existing PDFs)
        {
            'student_id': 'STU001',
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@university.edu',
            'major': 'Computer Science',
            'gpa': 3.85,
            'enrollment_date': '2022-09-01',
            'has_ferpa': 'Yes'
        },
        {
            'student_id': 'STU002',
            'firstname': 'Jane',
            'lastname': 'Smith',
            'email': 'jane.smith@university.edu',
            'major': 'Business Administration',
            'gpa': 3.92,
            'enrollment_date': '2022-09-01',
            'has_ferpa': 'Yes'
        },
        {
            'student_id': 'STU003',
            'firstname': 'Michael',
            'lastname': 'Johnson',
            'email': 'michael.johnson@university.edu',
            'major': 'Mechanical Engineering',
            'gpa': 3.67,
            'enrollment_date': '2023-01-15',
            'has_ferpa': 'Yes'
        },
        {
            'student_id': 'STU004',
            'firstname': 'Emily',
            'lastname': 'Williams',
            'email': 'emily.williams@university.edu',
            'major': 'Psychology',
            'gpa': 3.78,
            'enrollment_date': '2022-09-01',
            'has_ferpa': 'Yes'
        },
        {
            'student_id': 'STU005',
            'firstname': 'David',
            'lastname': 'Brown',
            'email': 'david.brown@university.edu',
            'major': 'Biology',
            'gpa': 3.95,
            'enrollment_date': '2023-01-15',
            'has_ferpa': 'Yes'
        },

        # Students WITHOUT FERPA files (new students)
        {
            'student_id': 'STU006',
            'firstname': 'Sarah',
            'lastname': 'Martinez',
            'email': 'sarah.martinez@university.edu',
            'major': 'Chemistry',
            'gpa': 3.72,
            'enrollment_date': '2023-09-01',
            'has_ferpa': 'No'
        },
        {
            'student_id': 'STU007',
            'firstname': 'James',
            'lastname': 'Garcia',
            'email': 'james.garcia@university.edu',
            'major': 'Mathematics',
            'gpa': 3.88,
            'enrollment_date': '2023-09-01',
            'has_ferpa': 'No'
        },
        {
            'student_id': 'STU008',
            'firstname': 'Lisa',
            'lastname': 'Rodriguez',
            'email': 'lisa.rodriguez@university.edu',
            'major': 'English Literature',
            'gpa': 3.64,
            'enrollment_date': '2024-01-10',
            'has_ferpa': 'No'
        },
        {
            'student_id': 'STU009',
            'firstname': 'Robert',
            'lastname': 'Anderson',
            'email': 'robert.anderson@university.edu',
            'major': 'Physics',
            'gpa': 3.91,
            'enrollment_date': '2023-09-01',
            'has_ferpa': 'No'
        },
        {
            'student_id': 'STU010',
            'firstname': 'Amanda',
            'lastname': 'Taylor',
            'email': 'amanda.taylor@university.edu',
            'major': 'Sociology',
            'gpa': 3.55,
            'enrollment_date': '2024-01-10',
            'has_ferpa': 'No'
        },
        {
            'student_id': 'STU011',
            'firstname': 'Christopher',
            'lastname': 'Lee',
            'email': 'christopher.lee@university.edu',
            'major': 'Political Science',
            'gpa': 3.76,
            'enrollment_date': '2023-09-01',
            'has_ferpa': 'No'
        },
        {
            'student_id': 'STU012',
            'firstname': 'Rachel',
            'lastname': 'Davis',
            'email': 'rachel.davis@university.edu',
            'major': 'Art History',
            'gpa': 3.82,
            'enrollment_date': '2024-01-10',
            'has_ferpa': 'No'
        }
    ]

    # Define CSV columns
    fieldnames = [
        'student_id',
        'firstname',
        'lastname',
        'email',
        'major',
        'gpa',
        'enrollment_date',
        'has_ferpa'
    ]

    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(students)

    # Summary
    students_with_ferpa = sum(1 for s in students if s['has_ferpa'] == 'Yes')
    students_without_ferpa = sum(1 for s in students if s['has_ferpa'] == 'No')

    print(f"✓ Created '{filename}'")
    print(f"\nSummary:")
    print(f"  Total students: {len(students)}")
    print(f"  Students with FERPA: {students_with_ferpa}")
    print(f"  Students without FERPA: {students_without_ferpa}")
    print(f"\nStudents with FERPA files:")
    for student in students:
        if student['has_ferpa'] == 'Yes':
            print(f"  - {student['student_id']}: {student['firstname']} {student['lastname']}")

    return filename


def main():
    """Main function."""
    print("=" * 60)
    print("Student CSV Generator")
    print("=" * 60)
    print()

    create_students_csv()

    print("\n" + "=" * 60)
    print("Next step: Run 'python3 import_csv_to_db.py' to import into database")
    print("=" * 60)


if __name__ == "__main__":
    main()
