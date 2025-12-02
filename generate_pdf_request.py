import pandas as pd
import os
import re
from pathlib import Path
import sys
from pypdf import PdfWriter, PdfReader
from pypdf.errors import PdfReadError

# TODO verify that there are no duplicate EYF IDs in the list
# TODO verify what to do if there is a duplicate EYF ID or we cannot find one?
# TODO create dependency list/setup
# pandas, openpyxl

def read_eyf_ids_from_excel(excel_file, column_name="EYFID"):
    """
    Reads a list of EYF IDs from an Excel file.

    Args:
        excel_file (str): Path to the Excel file containing EYF IDs.
        column_name (str): Name of the column containing EYF IDs.

    Returns:
        list: A list of EYF IDs.
    """
    # Try reading with default header (row 0)
    df = pd.read_excel(excel_file)
    
    # If column not found, try reading with header in row 1
    if column_name not in df.columns:
        df = pd.read_excel(excel_file, header=1)
    
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in Excel file")
    
    eyf_ids = df[column_name].dropna().astype(int).astype(str).tolist()
    
    # Check for duplicates
    duplicates = [id for id in set(eyf_ids) if eyf_ids.count(id) > 1]
    if duplicates:
        raise ValueError(f"Duplicate EYF IDs found in Excel file: {', '.join(duplicates)}")
    
    return eyf_ids


def validate_file_formats(folder_path, regex_pattern):
    """
    Iterate over all files in a folder and validate filenames against a regex pattern.
    
    Args:
        folder_path (str): Path to the folder containing files to validate
        regex_pattern (str): Regular expression pattern to match against filenames
        
    Returns:
        tuple: (valid_files list, invalid_files list)
    """
    valid_files = []
    invalid_files = []
    
    pattern = re.compile(regex_pattern)
    
    folder = Path(folder_path)
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder_path}")
    
    for file_path in folder.iterdir():
        if file_path.is_file():
            filename = file_path.name
            
            if pattern.match(filename):
                valid_files.append(filename)
            else:
                invalid_files.append(filename)
    
    return valid_files, invalid_files

def get_files_for_eyf_ids(folder_path, eyf_ids):
    """
    Validate the existence of expected files in a folder.
    
    Args:
        folder_path (str): Path to the folder containing files
        eyf_ids (list): List of EYF IDs to grab FERPA waivers for
        
    Returns:
        tuple: (eyf_id, list of matching file paths) for each EYF ID
    """
    result = []
        
    folder = Path(folder_path)
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder_path}")
    
    for eyf_id in eyf_ids:
        matching_files = list(folder.glob(f"{eyf_id}_*.pdf"))
        result.append((eyf_id, matching_files))
    
    return result

def read_eyf_ids_from_file(ids_file):
    """
    Reads a list of EYF IDs from a text file.

    Args:
        ids_file (str): Path to the text file containing EYF IDs (one per line).

    Returns:
        list: A list of EYF IDs.
    """
    with open(ids_file, 'r') as f:
        return [line.strip() for line in f]

def process_waiver_matches(eyf_ids_with_filepaths):
    """
    Processes the matched waiver files, identifying errors and successful matches.

    Args:
        eyf_ids_with_filepaths (list): A list of tuples, each containing an EYF ID and a list of file paths.

    Returns:
        list: A list of file paths for the PDFs that are ready to be combined.
    """
    pdfs_to_combine = []
    for eyf_id, filepaths in eyf_ids_with_filepaths:
        if len(filepaths) == 0:
            print(f"ERROR: No waiver found for EYF ID {eyf_id}")
        elif len(filepaths) > 1:
            print(f"ERROR: Multiple waivers found for EYF ID {eyf_id}:")
            for filepath in filepaths:
                print(f"  {filepath}")
        else:  # exactly one file found
            pdfs_to_combine.append(filepaths[0])
    return pdfs_to_combine

def merge_pdfs(pdf_files, output_file_name, overwrite=True):
    """
    Merges a list of PDF files into a single output file in the order specified.
    Includes checks for file existence and robust error handling.

    Args:
        pdf_files (list): A list of strings, where each string is the
                          full path to a PDF file to be merged.
        output_file_name (str): The name and path for the final merged PDF file.
        overwrite (bool): If True, overwrites the output file if it already exists.
                          If False and the file exists, the merge is skipped.
    """

    if os.path.exists(output_file_name) and not overwrite:
        print(f"Output file already exists: {output_file_name}")
        print("Set 'overwrite=True' to force merging and replacement.")
        return

    writer = PdfWriter()
    successful_merges = 0

    # 2. Iterate through the list of PDF file paths and append each one
    print(f"Starting PDF merge process for {len(pdf_files)} files...")
    for pdf_path in pdf_files:
        try:
            # Check if the file path is valid before attempting to open it
            if not os.path.isfile(pdf_path):
                 raise FileNotFoundError(f"File not found at path: {pdf_path}")

            # Read the PDF and append all its pages to the writer
            reader = PdfReader(pdf_path)
            writer.append_pages_from_reader(reader)
            print(f"  [SUCCESS] Appended: {os.path.basename(pdf_path)}")
            successful_merges += 1

        except FileNotFoundError as e:
            print(f"  [SKIPPED] File not found: {e}")
        except PdfReadError:
            # Handles cases where the file exists but is not a valid PDF
            print(f"  [SKIPPED] Invalid or corrupted PDF file: {os.path.basename(pdf_path)}")
        except Exception as e:
            # Catch all other unexpected errors
            print(f"  [ERROR] Failed to append {os.path.basename(pdf_path)}: {e}")

    # 3. Write the final merged PDF to the output file
    if successful_merges > 0:
        try:
            with open(output_file_name, 'wb') as output_file:
                writer.write(output_file)
            print(f"\n--- Successfully merged {successful_merges} files into: {output_file_name} ---")
        except Exception as e:
            print(f"\n[CRITICAL ERROR] Failed to write output file: {e}")
        finally:
            writer.close()
    else:
        print("\n--- No valid PDF files were successfully appended. Merge skipped. ---")
        writer.close()

def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_pdf_request.py <waiver_folder_path> <excel_file> <output_file>")
        print("  <waiver_folder_path>: Path to the folder containing the FERPA waivers")
        print("  <excel_file>: Path to Excel file containing EYF IDs")
        print("  <output_file>: Path for the merged PDF output file")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    excel_file = sys.argv[2]
    output_file = sys.argv[3]
    
    folder_path = sys.argv[1]
    excel_file = sys.argv[2]
    
    eyf_ids = read_eyf_ids_from_excel(excel_file)
    
    file_pattern = "[EYF ID]_[Client name]_KCS Records Consent_[previous file name]_[date].pdf"
    regex_pattern = r"^[0-9]+_[A-Za-z ]+_KCS Records Consent_.*\.pdf$"
    
    try:
        valid_files, invalid_files = validate_file_formats(folder_path, regex_pattern)
        
        if (len(invalid_files) > 0):
            print(f"ERROR: Some files do not match the expected format: {file_pattern}")
            for file in invalid_files:
                print(f"{file}")
            sys.exit(1)

        eyf_ids_with_filepaths = get_files_for_eyf_ids(folder_path, eyf_ids)
        pdfs_to_combine = process_waiver_matches(eyf_ids_with_filepaths)

        fully_matched_count = len(pdfs_to_combine)
        eyf_id_count = len(eyf_ids)

        print(f"Successfully 1:1 matched waivers for {fully_matched_count} out of {eyf_id_count} EYF IDs. Proceed with PDF generation?")
        user_input = input("Enter 'y' to continue or 'n' to cancel: ").strip().lower()
        if user_input != 'y':
            print("Operation cancelled.")
            sys.exit(0)

        merge_pdfs(pdfs_to_combine, output_file)
            
    except Exception as e:
        print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
