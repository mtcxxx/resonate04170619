# PDF Annotation Text Replacer

A Python script that replaces text in PDF annotations (both Text and FreeText annotations) across multiple PDF files.

## Features

- **Multiple PDF Support**: Process one or more PDF files at once
- **Annotation Types**: Handles both Text (sticky notes) and FreeText (editable text boxes) annotations
- **Dual Interface**: Works with both GUI (tkinter) and command-line interfaces
- **Error Handling**: Robust error handling with fallback options
- **Backup Safety**: Creates backups when possible and falls back to new files when needed

## Installation

### Prerequisites

1. **Python 3.6+** (tested with Python 3.13)
2. **PyMuPDF library**:
   ```bash
   pip install pymupdf
   ```

3. **tkinter** (for GUI mode - usually included with Python):
   ```bash
   # On Ubuntu/Debian:
   sudo apt-get install python3-tk
   
   # On macOS (usually pre-installed):
   # No additional installation needed
   
   # On Windows (usually pre-installed):
   # No additional installation needed
   ```

## Usage

### GUI Mode (Interactive)

Run the script without arguments to use the GUI interface:

```bash
python3 pdf_annotation_replacer_fixed.py
```

This will:
1. Open a file dialog to select PDF files
2. Show input dialogs for text to find and replace
3. Process the files and show results

### Command Line Mode

#### With PDF files as arguments:
```bash
python3 pdf_annotation_replacer_fixed.py file1.pdf file2.pdf
```

#### Interactive command line:
```bash
python3 pdf_annotation_replacer_fixed.py
# Then follow the prompts
```

### Test Mode

To test the functionality without user input:

```bash
python3 test_pdf_replacer_working.py
```

## Files

- `pdf_annotation_replacer.py` - Original script (has GUI issues in headless environments)
- `pdf_annotation_replacer_fixed.py` - **Main script** with improved error handling
- `test_pdf_replacer_working.py` - Test script that demonstrates functionality
- `requirements.txt` - Python dependencies

## Debugging Issues Found

### 1. Missing Dependencies
**Problem**: `ModuleNotFoundError: No module named 'pymupdf'`
**Solution**: Install PyMuPDF with `pip install pymupdf`

### 2. Missing tkinter
**Problem**: `ModuleNotFoundError: No module named 'tkinter'`
**Solution**: Install tkinter package (varies by OS)

### 3. GUI Display Issues
**Problem**: `_tkinter.TclError: no display name and no $DISPLAY environment variable`
**Solution**: Added GUI availability detection and fallback to command-line mode

### 4. PDF Save Issues
**Problem**: `Can't do incremental writes when changing encryption`
**Solution**: Added fallback to save as new file when incremental save fails

## How It Works

1. **PDF Loading**: Opens PDF files using PyMuPDF
2. **Annotation Processing**: Iterates through all pages and annotations
3. **Text Replacement**: 
   - For Text annotations: Updates the popup content
   - For FreeText annotations: Updates both content and appearance stream
4. **Saving**: Attempts incremental save first, falls back to new file if needed

## Supported Annotation Types

- **Text Annotations**: Sticky notes, comments, popup annotations
- **FreeText Annotations**: Editable text boxes, callouts

## Error Handling

The script includes comprehensive error handling:
- Individual annotation processing errors don't stop the entire process
- PDF save errors are handled gracefully with fallback options
- GUI unavailability automatically falls back to command-line mode
- File validation ensures only valid PDF files are processed

## Example Output

```
PDF Annotation Text Replacer
========================================
Selected 1 PDF(s):
  - document.pdf
Enter the text to find and replace: old text
Enter the replacement text: NEW TEXT

Processing PDF 1/1: document.pdf
Modified Text annotation on page 1 of document.pdf
Modified FreeText annotation on page 2 of document.pdf
Completed: 2 annotations modified. Updated: document.pdf

Summary: 2 total annotations modified across 1 PDFs.
Modified files:
  - document.pdf

Processing complete.
```

## Troubleshooting

### GUI Not Working
If you see "Warning: GUI not available. Falling back to command-line mode.", the script will still work but will use command-line input instead of dialogs.

### Permission Errors
Make sure you have write permissions to the PDF files or the directory where new files will be created.

### Large Files
For very large PDF files, processing may take some time. The script provides progress feedback.

## License

This script is provided as-is for educational and practical use.
