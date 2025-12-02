# Conda Environment Setup

This project uses a custom conda environment with all required dependencies.

## Conda Installation

![Conda Setup Step](screenshots/conda_setup_2.png)

1. Download Miniconda from [here](https://www.anaconda.com/download/success)
2. Run the installer
3. When installing, check the option to "Add installation to my PATH environment variable"
4. Restart your code editor / terminal

![Conda Setup](screenshots/conda_setup.png)

## Environment Name

`emerald-youth-hack`

## Dependencies Included

- **Python 3.12**
- **pypdf** (>=6.0.0) - Modern PDF manipulation library (successor to PyPDF2)
- **reportlab** (>=4.0.0) - PDF generation library
- **pytest** (>=7.0.0) - Testing framework

## One-time setup

Paste these commands into your terminal. You will need to accept the terms of service when running `conda env create -f environment.yml`

```bash
conda init powershell
conda env create -f environment.yml
```

Restart your terminal

## Deactivating the Environment

```bash
conda deactivate
```

## Running Your Code

```bash
# Activate environment first (if a different environment has been activated since the one time setup)
conda activate emerald-youth-hack

# Then run the script
python generate_pdf_request.py <waiver_folder_path> <excel_file> <output_pdf_file_name>
```

Example usage: `python waivers KCSDataRequest_EYF2425SubmissionExample.xlsx output.pdf`

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
