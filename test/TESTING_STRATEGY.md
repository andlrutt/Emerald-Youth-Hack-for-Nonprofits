# Testing Strategy for PDF Merger

## Overview

This document explains the testing strategy for verifying that `merge_pdfs()` correctly creates a merged PDF file with pages in the exact order specified by the `pdf_files` parameter.

## Testing Approach

### 1. Unit Tests
**Purpose**: Test individual behaviors and edge cases in isolation.

**What to Test**:
- ✅ File existence checks (overwrite parameter)
- ✅ Error handling (missing files, invalid PDFs)
- ✅ Edge cases (empty list, all files invalid)
- ✅ Return value behavior

**Why Unit Tests First?**
- Fast execution
- Isolate specific behaviors
- Catch regressions early
- Don't require PDF creation/reading

### 2. Integration Tests
**Purpose**: Test the complete workflow end-to-end, including order verification.

**What to Test**:
- ✅ Output file is created
- ✅ Output file is a valid PDF
- ✅ Pages are in the correct order
- ✅ Works with single-page PDFs
- ✅ Works with multi-page PDFs
- ✅ Handles mixed valid/invalid files

## Key Challenge: Verifying Page Order

### The Problem
We need to verify that pages in the merged PDF appear in the same order as the input `pdf_files` list.

### The Solution: Content-Based Verification

**Strategy**:
1. **Create test PDFs with unique identifiers**
   - Each test PDF contains unique, extractable text (e.g., "PDF_FIRST", "PDF_SECOND")
   - This allows us to identify which source PDF each page came from

2. **Merge PDFs in a known order**
   - Call `merge_pdfs()` with PDFs in a specific sequence
   - Example: `[pdf1, pdf2, pdf3]` where pdf1 contains "FIRST", pdf2 contains "SECOND", etc.

3. **Extract and verify page content**
   - Use PyPDF2's `PdfReader` to read the merged PDF
   - Extract text from each page using `page.extract_text()`
   - Verify that page 0 contains "FIRST", page 1 contains "SECOND", etc.

### Why This Approach Works

✅ **Direct verification**: Tests the actual requirement (order preservation)  
✅ **Real-world testing**: Uses actual PDFs, not mocks  
✅ **Reliable**: Text extraction is deterministic  
✅ **Fast**: No need for manual inspection  
✅ **Automated**: Can run in CI/CD pipelines  

### Alternative Approaches (and why they're less ideal)

❌ **Manual inspection**: Not automated, slow, error-prone  
❌ **File size comparison**: Doesn't verify order  
❌ **Metadata comparison**: May not be reliable across PDF libraries  
❌ **Page count only**: Doesn't verify order  

## Test Implementation Details

### Creating Test PDFs

We use `reportlab` to programmatically create test PDFs:

```python
def _create_test_pdf(filepath, text_content):
    """Create a single-page PDF with unique text."""
    c = canvas.Canvas(filepath, pagesize=letter)
    c.drawString(100, 700, text_content)  # Add unique identifier
    c.save()
```

### Verifying Order

```python
# After merging
reader = PdfReader(merged_output_path)

# Verify each page contains expected identifier
for page_num, expected_id in enumerate(["FIRST", "SECOND", "THIRD"]):
    page_text = reader.pages[page_num].extract_text()
    assert expected_id in page_text, f"Page {page_num} order incorrect"
```

## Test Structure

```
test_pdf_merger.py
├── TestPDFMergerUnit (Unit tests)
│   ├── test_overwrite_false_skips_when_file_exists
│   ├── test_overwrite_true_replaces_existing_file
│   ├── test_empty_pdf_list_creates_no_output
│   ├── test_nonexistent_file_is_skipped
│   └── test_invalid_pdf_is_skipped
│
└── TestPDFMergerIntegration (Integration tests)
    ├── test_merge_creates_output_file
    ├── test_merge_preserves_order_single_page_pdfs  ⭐ KEY TEST
    ├── test_merge_preserves_order_multi_page_pdfs   ⭐ KEY TEST
    └── test_merge_with_mixed_valid_invalid_files
```

## Running the Tests

```bash
# Install dependencies
pip install pytest reportlab PyPDF2

# Run all tests
pytest test_pdf_merger.py -v

# Run only integration tests
pytest test_pdf_merger.py::TestPDFMergerIntegration -v

# Run only unit tests
pytest test_pdf_merger.py::TestPDFMergerUnit -v
```

## Expected Test Coverage

- **Unit Tests**: ~80% of edge cases and error paths
- **Integration Tests**: 100% of happy path + order verification
- **Overall Coverage**: Critical paths for order preservation

## Why This Strategy is Reasonable for a Hackathon

1. **Fast to implement**: Uses existing libraries (pytest, reportlab, PyPDF2)
2. **Comprehensive**: Tests both unit and integration levels
3. **Maintainable**: Clear test structure, easy to extend
4. **Reliable**: Automated verification eliminates human error
5. **Practical**: Tests real-world scenarios (single/multi-page PDFs, invalid files)

## Future Enhancements

- Performance tests for large PDFs
- Memory leak detection
- Concurrent merge testing
- Different PDF format compatibility (encrypted, corrupted, etc.)

