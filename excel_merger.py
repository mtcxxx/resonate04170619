import pandas as pd
import os
from tkinter import Tk, filedialog, messagebox
import tkinter as tk
import tempfile
import shutil
from openpyxl import load_workbook
import contextlib

# Context manager to create a temporary file without filters
@contextlib.contextmanager
def temp_file_without_filters(file_path):
    """Creates a temporary copy of an Excel file with all filters removed."""
    try:
        # Create a temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(temp_fd)

        # Copy the original file to the temporary file
        shutil.copy(file_path, temp_path)

        # Load the temporary workbook and remove filters
        wb = load_workbook(temp_path)
        for sheet in wb:
            if sheet.auto_filter:  # Check if the sheet has an auto-filter
                sheet.auto_filter.ref = None  # Remove the filter
        wb.save(temp_path)

        yield temp_path  # Provide the temporary file path to the caller
    finally:
        # Clean up the temporary file
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"Failed to delete temporary file {temp_path}: {e}")

def select_files():
    """Prompt the user to select Excel files."""
    root = Tk()
    root.withdraw()  # Hide the main window
    files = filedialog.askopenfilenames(
        title="Select Excel Files to Merge",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    return list(files)

def select_destination_folder():
    """Prompt the user to select a destination folder."""
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Destination Folder")
    return folder

def ask_merge_all_sheets():
    """Ask the user whether to merge all sheets or just the first sheet."""
    root = Tk()
    root.withdraw()
    response = messagebox.askyesno(
        title="Merge Sheets",
        message="Do you want to merge all sheets? (Yes: Merge all sheets, No: Merge only the first sheet)"
    )
    return response

def merge_excel_files():
    """Merge selected Excel files into a single file."""
    # Select Excel files
    excel_files = select_files()
    if not excel_files:
        messagebox.showerror("Error", "No files selected!")
        return

    # Select destination folder
    dest_folder = select_destination_folder()
    if not dest_folder:
        messagebox.showerror("Error", "No destination folder selected!")
        return

    # Ask whether to merge all sheets
    merge_all = ask_merge_all_sheets()

    if merge_all:
        # Merge all sheets, grouping by sheet name
        sheet_data = {}
        for file in excel_files:
            with temp_file_without_filters(file) as temp_file:
                workbook_name = os.path.splitext(os.path.basename(file))[0]
                try:
                    xls = pd.ExcelFile(temp_file)
                    for sheet_name in xls.sheet_names:
                        try:
                            # Read sheet with dtype=object to avoid type conversion errors
                            df = pd.read_excel(temp_file, sheet_name=sheet_name, dtype=object)
                            # Add workbook name as a column
                            df['Workbook_Name'] = workbook_name
                            if sheet_name not in sheet_data:
                                sheet_data[sheet_name] = []
                            sheet_data[sheet_name].append(df)
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to read sheet '{sheet_name}' in file '{file}': {str(e)}")
                            return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process file '{file}': {str(e)}")
                    return

        # Combine sheets with the same name and save
        output_file = os.path.join(dest_folder, "merged_excel.xlsx")
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for sheet_name, dfs in sheet_data.items():
                    # Concatenate all DataFrames for this sheet name
                    combined_df = pd.concat(dfs, ignore_index=True)
                    # Ensure Workbook_Name is the first column
                    if 'Workbook_Name' in combined_df.columns:
                        cols = combined_df.columns.tolist()
                        cols.remove('Workbook_Name')
                        combined_df = combined_df[['Workbook_Name'] + cols]
                    combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save merged file: {str(e)}")
            return
    else:
        # Merge only the first sheet of each file
        dfs = []
        for file in excel_files:
            with temp_file_without_filters(file) as temp_file:
                workbook_name = os.path.splitext(os.path.basename(file))[0]
                try:
                    xls = pd.ExcelFile(temp_file)
                    if xls.sheet_names:  # Check if there are any sheets
                        try:
                            # Read first sheet with dtype=object
                            df = pd.read_excel(temp_file, sheet_name=xls.sheet_names[0], dtype=object)
                            # Add workbook name as a column
                            df['Workbook_Name'] = workbook_name
                            dfs.append(df)
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to read first sheet in file '{file}': {str(e)}")
                            return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process file '{file}': {str(e)}")
                    return

        # Combine first sheets and save
        output_file = os.path.join(dest_folder, "merged_excel.xlsx")
        try:
            combined_df = pd.concat(dfs, ignore_index=True)
            # Ensure Workbook_Name is the first column
            if 'Workbook_Name' in combined_df.columns:
                cols = combined_df.columns.tolist()
                cols.remove('Workbook_Name')
                combined_df = combined_df[['Workbook_Name'] + cols]
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                combined_df.to_excel(writer, sheet_name="MergedSheet", index=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save merged file: {str(e)}")
            return

    messagebox.showinfo("Success", f"Merged file saved to {output_file}")

if __name__ == "__main__":
    merge_excel_files()