# Excel File Merger

A Python script that merges multiple Excel files into a single file with a graphical user interface.

## Features

- **Multiple File Selection**: Select multiple Excel files (.xlsx, .xls) to merge
- **Flexible Sheet Merging**: Choose to merge all sheets or just the first sheet from each file
- **Sheet Grouping**: When merging all sheets, sheets with the same name are combined together
- **Source Tracking**: Adds a "Workbook_Name" column to track which file each row came from
- **Filter Removal**: Automatically removes Excel filters to prevent reading issues
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas openpyxl
```

## Usage

1. Run the script:

```bash
python excel_merger.py
```

2. The script will open a file dialog to select Excel files to merge
3. Choose a destination folder for the merged file
4. Select whether to merge all sheets or just the first sheet:
   - **Yes**: Merges all sheets, grouping by sheet name
   - **No**: Merges only the first sheet from each file

## Output

The merged file will be saved as `merged_excel.xlsx` in the selected destination folder.

### When merging all sheets:
- Each sheet name becomes a separate worksheet in the output file
- Data from sheets with the same name across different files are combined
- The "Workbook_Name" column shows which source file each row came from

### When merging first sheets only:
- All first sheets are combined into a single "MergedSheet" worksheet
- The "Workbook_Name" column shows which source file each row came from

## Requirements

- Python 3.7+
- pandas >= 1.5.0
- openpyxl >= 3.0.0
- tkinter (usually included with Python)

## Notes

- The script uses `dtype=object` when reading Excel files to avoid type conversion errors
- Temporary files are created and cleaned up automatically to handle Excel filters
- The "Workbook_Name" column is always placed as the first column in the output