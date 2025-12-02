import os
from pypdf import PdfWriter, PdfReader
from pypdf.errors import PdfReadError

def merge_pdfs(pdf_files, output_file_name, overwrite=False):
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
