# Conda Environment Setup

This project uses a custom conda environment with all required dependencies.

## Environment Name
`emerald-youth-hack`

## Dependencies Included
- **Python 3.12**
- **pypdf** (>=6.0.0) - Modern PDF manipulation library (successor to PyPDF2)
- **reportlab** (>=4.0.0) - PDF generation library
- **pytest** (>=7.0.0) - Testing framework

## Activating the Environment

```bash
conda activate emerald-youth-hack
```

## Deactivating the Environment

```bash
conda deactivate
```

## Running Tests

Once the environment is activated:

```bash
# From project root
python -m pytest test/test_pdf_merger.py -v

# Or just
pytest test/test_pdf_merger.py -v
```

## Running Your Code

```bash
# Activate environment first
conda activate emerald-youth-hack

# Then run your scripts
python pdf_merger.py
```

## Recreating the Environment

If you need to recreate the environment (e.g., on a new machine):

```bash
conda env create -f environment.yml
```

## Updating the Environment

If you add new dependencies, update `environment.yml` and then:

```bash
conda env update -f environment.yml --prune
```

## Verifying Installation

To verify all packages are installed correctly:

```bash
conda activate emerald-youth-hack
python -c "import pypdf; import reportlab; import pytest; print('All dependencies OK!')"
```

