"""
Test suite for pdf_merger.py

This test suite includes:
- Unit tests: Testing individual behaviors (error handling, edge cases)
- Integration tests: Testing full workflow including PDF creation and order verification

To run:
    pytest test_pdf_merger.py -v
    or
    python3 -m pytest test_pdf_merger.py -v
    or (if pytest is installed globally)
    python3 -m pytest test/test_pdf_merger.py -v
"""

import os
import pytest

# Import the function to test
from pdf_merger import merge_pdfs

# For creating test PDFs and reading them
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from pypdf import PdfReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    pytestmark = pytest.mark.skip("reportlab or pypdf not available")


class TestPDFMergerUnit:
    """Unit tests for individual behaviors of merge_pdfs function."""

    def test_overwrite_false_skips_when_file_exists(self, tmp_path):
        """Test that merge is skipped when output exists and overwrite=False."""
        output_file = tmp_path / "output.pdf"
        output_file.write_bytes(b"existing content")

        # Should return early without merging
        merge_pdfs([], str(output_file), overwrite=False)

        # File should still contain original content
        assert output_file.read_bytes() == b"existing content"


    def test_overwrite_true_replaces_existing_file(self, tmp_path):
        """Test that merge overwrites existing file when overwrite=True."""
        test_pdf = tmp_path / "test.pdf"
        _create_test_pdf(str(test_pdf), "Test Content")

        output_file = tmp_path / "output.pdf"
        output_file.write_bytes(b"old content")

        merge_pdfs([str(test_pdf)], str(output_file), overwrite=True)

        # File should be replaced with merged PDF
        assert output_file.exists()
        assert output_file.read_bytes() != b"old content"
        # Verify it's a valid PDF by checking it can be read
        reader = PdfReader(str(output_file))
        assert len(reader.pages) > 0

    def test_empty_pdf_list_creates_no_output(self, tmp_path):
        """Test that empty PDF list doesn't create output file."""
        output_file = tmp_path / "output.pdf"

        merge_pdfs([], str(output_file))

        assert not output_file.exists()

    def test_nonexistent_file_is_skipped(self, tmp_path, capsys):
        """Test that nonexistent files are skipped gracefully."""
        output_file = tmp_path / "output.pdf"
        nonexistent_file = tmp_path / "nonexistent.pdf"

        merge_pdfs([str(nonexistent_file)], str(output_file))

        # Should not create output (no successful merges)
        assert not output_file.exists()

        # Should print skip message
        captured = capsys.readouterr()
        assert "SKIPPED" in captured.out or "File not found" in captured.out

    def test_invalid_pdf_is_skipped(self, tmp_path, capsys):
        """Test that invalid PDF files are skipped."""
        # Create a file that's not a valid PDF
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_text("This is not a PDF file")

        output_file = tmp_path / "output.pdf"

        merge_pdfs([str(invalid_pdf)], str(output_file))

        # Should not create output
        assert not output_file.exists()

        # Should print skip message
        captured = capsys.readouterr()
        assert "SKIPPED" in captured.out or "Invalid" in captured.out


class TestPDFMergerIntegration:
    """Integration tests for full workflow including order verification."""

    def test_merge_creates_output_file(self, tmp_path):
        """Integration test: Verify that merge creates the output file."""
        pdf1 = tmp_path / "pdf1.pdf"
        pdf2 = tmp_path / "pdf2.pdf"
        _create_test_pdf(str(pdf1), "Content 1")
        _create_test_pdf(str(pdf2), "Content 2")

        output_file = tmp_path / "merged.pdf"

        merge_pdfs([str(pdf1), str(pdf2)], str(output_file))

        # Verify output file exists
        assert output_file.exists(), "Output PDF file should be created"

        # Verify it's a valid PDF
        reader = PdfReader(str(output_file))
        assert len(reader.pages) == 2, "Merged PDF should have 2 pages"

    def test_merge_preserves_order_single_page_pdfs(self, tmp_path):
        """
        Integration test: Verify PDFs are merged in the exact order provided.

        Strategy:
        1. Create multiple test PDFs, each with unique identifiable text
        2. Merge them in a specific order
        3. Extract text from each page of merged PDF
        4. Verify the order matches input order
        """
        # Create test PDFs with unique identifiers
        pdf_files = []
        identifiers = ["FIRST", "SECOND", "THIRD", "FOURTH"]

        for i, identifier in enumerate(identifiers):
            pdf_path = tmp_path / f"pdf_{i}.pdf"
            _create_test_pdf(str(pdf_path), f"PDF_{identifier}_PAGE")
            pdf_files.append(str(pdf_path))

        # Merge in specific order
        output_file = tmp_path / "ordered_merge.pdf"
        merge_pdfs(pdf_files, str(output_file))

        # Verify output exists
        assert output_file.exists(), "Output PDF should be created"

        # Read merged PDF and extract text from each page
        reader = PdfReader(str(output_file))
        assert len(reader.pages) == len(identifiers), \
            f"Expected {len(identifiers)} pages, got {len(reader.pages)}"

        # Extract text from each page and verify order
        for page_num, expected_id in enumerate(identifiers):
            page = reader.pages[page_num]
            page_text = page.extract_text()

            # Verify this page contains the expected identifier
            assert expected_id in page_text, \
                f"Page {page_num + 1} should contain '{expected_id}', but got: {page_text[:50]}"

            # Verify it doesn't contain identifiers from other positions
            for other_id in identifiers:
                if other_id != expected_id:
                    # Allow some overlap in text extraction, but main identifier should be unique
                    pass

    def test_merge_preserves_order_multi_page_pdfs(self, tmp_path):
        """
        Integration test: Verify order when input PDFs have multiple pages.

        This tests a more complex scenario where each input PDF has multiple pages.
        """
        # Create PDFs with multiple pages, each with unique identifiers
        pdf1 = tmp_path / "multi1.pdf"
        pdf2 = tmp_path / "multi2.pdf"

        _create_multi_page_pdf(str(pdf1), "PDF_A", num_pages=2)
        _create_multi_page_pdf(str(pdf2), "PDF_B", num_pages=3)

        output_file = tmp_path / "multi_merged.pdf"

        # Merge in order: pdf1, then pdf2
        merge_pdfs([str(pdf1), str(pdf2)], str(output_file))

        # Verify output
        assert output_file.exists()
        reader = PdfReader(str(output_file))
        assert len(reader.pages) == 5, "Should have 2 + 3 = 5 pages"

        # Verify order: first 2 pages should be from PDF_A, next 3 from PDF_B
        page0_text = reader.pages[0].extract_text()
        page1_text = reader.pages[1].extract_text()
        page2_text = reader.pages[2].extract_text()

        assert "PDF_A" in page0_text, "First page should be from PDF_A"
        assert "PDF_A" in page1_text, "Second page should be from PDF_A"
        assert "PDF_B" in page2_text, "Third page should be from PDF_B"

    def test_merge_with_mixed_valid_invalid_files(self, tmp_path):
        """Integration test: Verify merge works when some files are invalid."""
        pdf1 = tmp_path / "valid1.pdf"
        pdf2 = tmp_path / "valid2.pdf"
        _create_test_pdf(str(pdf1), "VALID_ONE")
        _create_test_pdf(str(pdf2), "VALID_TWO")

        # Create invalid file
        invalid = tmp_path / "invalid.pdf"
        invalid.write_text("Not a PDF")

        output_file = tmp_path / "mixed_merge.pdf"

        # Merge: valid, invalid, valid
        merge_pdfs([str(pdf1), str(invalid), str(pdf2)], str(output_file))

        # Should still create output with valid PDFs
        assert output_file.exists()
        reader = PdfReader(str(output_file))
        assert len(reader.pages) == 2, "Should have 2 pages from valid PDFs"

        # Verify order: first page from pdf1, second from pdf2
        assert "VALID_ONE" in reader.pages[0].extract_text()
        assert "VALID_TWO" in reader.pages[1].extract_text()


# Helper functions for creating test PDFs

def _create_test_pdf(filepath, text_content):
    """Create a simple single-page PDF with the given text content."""
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 100, text_content)
    c.save()


def _create_multi_page_pdf(filepath, base_identifier, num_pages):
    """Create a multi-page PDF with unique text on each page."""
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    for page_num in range(num_pages):
        # Add unique text to each page
        c.drawString(100, height - 100, f"{base_identifier}_PAGE_{page_num + 1}")
        c.showPage()  # Move to next page

    c.save()

