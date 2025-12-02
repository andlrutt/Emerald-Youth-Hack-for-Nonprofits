"""
FERPA Waiver PDF Merger - Streamlit UI
A simple web interface for merging student FERPA waiver PDFs.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from pypdf import PdfWriter, PdfReader
from pypdf.errors import PdfReadError
from datetime import datetime


def read_eyf_ids_from_excel(excel_file, column_name="EYFID"):
    """
    Reads a list of EYF IDs from an Excel file.
    """
    # Try reading with default header (row 0)
    df = pd.read_excel(excel_file)

    # If column not found, try reading with header in row 1
    if column_name not in df.columns:
        excel_file.seek(0)  # Reset file pointer
        df = pd.read_excel(excel_file, header=1)

    if column_name not in df.columns:
        raise ValueError(f"Could not find '{column_name}' column in your Excel file. "
                        "Please make sure the column is named exactly 'EYFID'.")

    eyf_ids = df[column_name].dropna().astype(int).astype(str).tolist()

    # Check for duplicates
    duplicates = [id for id in set(eyf_ids) if eyf_ids.count(id) > 1]
    if duplicates:
        raise ValueError(f"Duplicate student IDs found in Excel file: {', '.join(duplicates)}")

    return eyf_ids


def match_uploaded_pdfs_to_eyf_ids(uploaded_files, eyf_ids):
    """
    Match uploaded PDF files to EYF IDs based on filename prefix.

    Args:
        uploaded_files: Dict of {filename: bytes_data}
        eyf_ids: List of EYF ID strings

    Returns:
        dict with 'matched', 'missing', 'duplicates' lists
    """
    results = {'matched': [], 'missing': [], 'duplicates': []}

    for eyf_id in eyf_ids:
        matching_files = [
            (fname, data) for fname, data in uploaded_files.items()
            if fname.startswith(f"{eyf_id}_")
        ]

        if len(matching_files) == 0:
            results['missing'].append(eyf_id)
        elif len(matching_files) > 1:
            results['duplicates'].append((eyf_id, [f[0] for f in matching_files]))
        else:
            fname, data = matching_files[0]
            results['matched'].append((eyf_id, fname, data))

    return results


def merge_pdfs_in_memory(pdf_items):
    """
    Merge PDFs from in-memory bytes data.

    Args:
        pdf_items: List of (eyf_id, filename, bytes_data) tuples

    Returns:
        tuple: (merged PDF as bytes or None, list of errors)
    """
    writer = PdfWriter()
    successful = 0
    errors = []

    for eyf_id, filename, pdf_bytes in pdf_items:
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)
            successful += 1
        except PdfReadError:
            errors.append(f"{filename}: Invalid or corrupted PDF file")
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")

    if successful == 0:
        return None, errors

    output = BytesIO()
    writer.write(output)
    return output.getvalue(), errors


def generate_missing_report(missing_ids, duplicates):
    """Generate a text report of missing waivers and duplicates."""
    report = "FERPA Waiver Status Report\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "=" * 50 + "\n\n"

    if missing_ids:
        report += f"MISSING WAIVERS ({len(missing_ids)} students)\n"
        report += "-" * 30 + "\n"
        for eyf_id in missing_ids:
            report += f"  - EYF ID: {eyf_id}\n"
        report += "\n"

    if duplicates:
        report += f"DUPLICATE FILES ({len(duplicates)} students)\n"
        report += "-" * 30 + "\n"
        for eyf_id, files in duplicates:
            report += f"  - EYF ID {eyf_id}:\n"
            for f in files:
                report += f"      {f}\n"
        report += "\n"

    if not missing_ids and not duplicates:
        report += "All students have exactly one waiver on file.\n"

    return report


# Page config
st.set_page_config(
    page_title="FERPA Waiver Merger",
    page_icon="📋",
    layout="centered"
)

st.title("FERPA Waiver PDF Merger")
st.markdown("Upload student IDs and waiver PDFs to create a merged document.")

# Initialize session state
if 'eyf_ids' not in st.session_state:
    st.session_state.eyf_ids = []
if 'uploaded_pdfs' not in st.session_state:
    st.session_state.uploaded_pdfs = {}
if 'match_results' not in st.session_state:
    st.session_state.match_results = None
if 'merged_pdf' not in st.session_state:
    st.session_state.merged_pdf = None

# Step 1: Excel Upload
st.header("Step 1: Upload Student List")
st.markdown("Upload an Excel file with a column named **EYFID** containing student IDs.")

excel_file = st.file_uploader(
    "Choose Excel file",
    type=['xlsx', 'xls'],
    key="excel_uploader"
)

if excel_file is not None:
    try:
        eyf_ids = read_eyf_ids_from_excel(excel_file)
        st.session_state.eyf_ids = eyf_ids
        st.success(f"Loaded **{len(eyf_ids)}** student IDs from the file")
    except ValueError as e:
        st.error(str(e))
        st.session_state.eyf_ids = []
    except Exception as e:
        st.error(f"Could not read the Excel file. Please check that it's a valid .xlsx or .xls file.")
        st.session_state.eyf_ids = []

st.divider()

# Step 2: PDF Upload
st.header("Step 2: Upload Waiver PDFs")
st.markdown("Upload the FERPA waiver PDF files. Filenames should start with the student's EYF ID.")
st.caption("Expected format: `EYFID_Name_KCS Records Consent_....pdf`")

pdf_files = st.file_uploader(
    "Choose PDF files",
    type=['pdf'],
    accept_multiple_files=True,
    key="pdf_uploader"
)

if pdf_files:
    st.session_state.uploaded_pdfs = {f.name: f.read() for f in pdf_files}
    st.success(f"Uploaded **{len(pdf_files)}** PDF files")

st.divider()

# Step 3: Match Results
st.header("Step 3: Review Matches")

if st.session_state.eyf_ids and st.session_state.uploaded_pdfs:
    results = match_uploaded_pdfs_to_eyf_ids(
        st.session_state.uploaded_pdfs,
        st.session_state.eyf_ids
    )
    st.session_state.match_results = results

    # Summary metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Matched", len(results['matched']))
    with col2:
        if results['missing']:
            st.metric("Missing", len(results['missing']), delta="needs attention", delta_color="inverse")
        else:
            st.metric("Missing", 0)
    with col3:
        if results['duplicates']:
            st.metric("Duplicates", len(results['duplicates']), delta="will be skipped", delta_color="inverse")
        else:
            st.metric("Duplicates", 0)

    # Expandable details
    if results['missing']:
        with st.expander(f"View {len(results['missing'])} Missing Waivers"):
            for eyf_id in results['missing']:
                st.write(f"- EYF ID: **{eyf_id}**")

    if results['duplicates']:
        with st.expander(f"View {len(results['duplicates'])} Duplicates (will be skipped)"):
            for eyf_id, files in results['duplicates']:
                st.write(f"- EYF ID **{eyf_id}**: {len(files)} files found")
                for f in files:
                    st.caption(f"    {f}")

elif st.session_state.eyf_ids and not st.session_state.uploaded_pdfs:
    st.info("Upload PDF files to see match results.")
elif st.session_state.uploaded_pdfs and not st.session_state.eyf_ids:
    st.info("Upload an Excel file with student IDs to see match results.")
else:
    st.info("Upload both files to see match results.")

st.divider()

# Step 4: Download
st.header("Step 4: Download")

if st.session_state.match_results and st.session_state.match_results['matched']:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Merged PDF", type="primary", use_container_width=True):
            with st.spinner("Merging PDFs..."):
                merged_bytes, errors = merge_pdfs_in_memory(
                    st.session_state.match_results['matched']
                )
                if merged_bytes:
                    st.session_state.merged_pdf = merged_bytes
                    if errors:
                        st.warning(f"Merged with {len(errors)} skipped files")
                        for err in errors:
                            st.caption(f"- {err}")
                else:
                    st.error("Could not merge PDFs. All files may be invalid.")

        if st.session_state.merged_pdf:
            st.download_button(
                label="Download Merged PDF",
                data=st.session_state.merged_pdf,
                file_name=f"merged_ferpa_waivers_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    with col2:
        # Missing report download
        if st.session_state.match_results['missing'] or st.session_state.match_results['duplicates']:
            report = generate_missing_report(
                st.session_state.match_results['missing'],
                st.session_state.match_results['duplicates']
            )
            st.download_button(
                label="Download Status Report",
                data=report,
                file_name=f"waiver_status_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.success("All students matched!")

elif st.session_state.match_results and not st.session_state.match_results['matched']:
    st.warning("No matching waivers found. Please check that PDF filenames start with the correct EYF ID.")
else:
    st.info("Complete steps 1-3 to generate downloads.")

# Footer
st.divider()
st.caption("FERPA Waiver Merger - Emerald Youth Foundation")
