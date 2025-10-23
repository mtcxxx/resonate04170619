import pymupdf  # PyMuPDF, install with: pip install pymupdf
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pandas as pd
import math

# DEBUG: Add missing import
import fitz  # This was missing! PyMuPDF's main module

def estimate_text_dimensions(text, fontsize=11, char_width_approx=7, char_height_factor=1.2, max_width=300):
    """
    Estimates the required width and height for the text box based on wording.
    Handles explicit line breaks from '\\' replaced with '\\n'.
    Assumes no further wrapping; sets width to max line length, capped at max_width.
    Returns (width, height) in points.
    """
    if not text.strip():
        return 100, fontsize * char_height_factor  # Min size for empty text
    
    # Preprocess: Replace '\' with '\n' for line breaks
    processed_text = text.replace('\\', '\n')
    lines = [line.strip() for line in processed_text.split('\n') if line.strip()]
    
    if not lines:
        return 100, fontsize * char_height_factor
    
    # Estimate max width based on longest line
    max_line_chars = max(len(line) for line in lines)
    estimated_width = min(max_width, max(100, max_line_chars * char_width_approx))
    
    # Height based on number of lines
    estimated_height = max(30, len(lines) * fontsize * char_height_factor)
    
    return estimated_width, estimated_height

def add_freetext_annotation(pdf_path, page_num, position, text):
    """
    Adds a FreeText annotation (visible text box) to the specified page and position in the PDF.
    Adjusts box size based on text length, handles '\\' as line break.
    Returns the output path and success status.
    """
    try:
        # DEBUG: Add error handling for file operations
        if not os.path.exists(pdf_path):
            print(f"DEBUG: PDF file not found: {pdf_path}")
            return None, False
            
        doc = pymupdf.open(pdf_path)
        print(f"DEBUG: Opened PDF with {len(doc)} pages")
        
        if page_num >= len(doc):
            print(f"DEBUG: Page {page_num} is out of range. PDF has {len(doc)} pages")
            doc.close()
            return None, False  # Invalid page
        
        page = doc[page_num]
        page_rect = page.rect
        width = page_rect.width
        height = page_rect.height
        print(f"DEBUG: Page dimensions: {width} x {height}")
        
        # Preprocess text: Replace '\' with '\n' for explicit line breaks
        processed_text = text.replace('\\', '\n')
        print(f"DEBUG: Original text: '{text[:50]}...'")
        print(f"DEBUG: Processed text: '{processed_text[:50]}...'")
        
        # Estimate dimensions based on processed text
        box_width, box_height = estimate_text_dimensions(text)  # Pass original for estimation, but uses processed internally
        print(f"DEBUG: Estimated box size: {box_width} x {box_height}")
        
        # Define margin
        margin = 50
        
        # Define rect based on position (adjust for dynamic size)
        if position == "top_left":
            rect = fitz.Rect(margin, margin, margin + box_width, margin + box_height)
        elif position == "top_right":
            rect = fitz.Rect(width - margin - box_width, margin, width - margin, margin + box_height)
        elif position == "bottom_left":
            rect = fitz.Rect(margin, height - margin - box_height, margin + box_width, height - margin)
        elif position == "bottom_right":
            rect = fitz.Rect(width - margin - box_width, height - margin - box_height, width - margin, height - margin)
        else:
            print(f"DEBUG: Invalid position: {position}")
            doc.close()
            return None, False  # Invalid position
        
        print(f"DEBUG: Initial rect: {rect}")
        
        # Ensure rect fits on page
        if rect.x1 > width or rect.y1 > height or rect.x0 < 0 or rect.y0 < 0:
            print(f"DEBUG: Rect overflows page, scaling down...")
            # Shrink if overflowing (simple adjustment)
            scale = min((width - 2*margin) / box_width, (height - 2*margin) / box_height) * 0.9
            if scale < 1:
                box_width *= scale
                box_height *= scale
                print(f"DEBUG: Scaled box size: {box_width} x {box_height}")
                # Redefine rect with scaled size
                if position == "top_left":
                    rect = fitz.Rect(margin, margin, margin + box_width, margin + box_height)
                elif position == "top_right":
                    rect = fitz.Rect(width - margin - box_width, margin, width - margin, margin + box_height)
                elif position == "bottom_left":
                    rect = fitz.Rect(margin, height - margin - box_height, margin + box_width, height - margin)
                elif position == "bottom_right":
                    rect = fitz.Rect(width - margin - box_width, height - margin - box_height, width - margin, height - margin)
        
        print(f"DEBUG: Final rect: {rect}")
        
        # Add FreeText annotation with processed text and dynamic rect
        annot = page.add_freetext_annot(rect, processed_text, fontsize=11, text_color=(0, 0, 0), align=0)
        annot.set_border(width=1, dashes=[2])  # Optional: Add a border
        print(f"DEBUG: Added annotation successfully")
        
        # Save the modified PDF
        base_name = os.path.splitext(pdf_path)[0]
        output_path = f"{base_name}_added.pdf"
        doc.save(output_path)
        doc.close()
        print(f"DEBUG: Saved to: {output_path}")
        
        return output_path, True
        
    except Exception as e:
        print(f"DEBUG: Error in add_freetext_annotation: {str(e)}")
        try:
            doc.close()
        except:
            pass
        return None, False

# Main script
if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Step 1: Let user choose one or more PDFs
        pdf_paths = filedialog.askopenfilenames(
            title="Select one or more PDF files",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not pdf_paths:
            messagebox.showinfo("Cancelled", "No PDFs selected. Exiting.")
            exit()
        
        print(f"Selected {len(pdf_paths)} PDF(s):")
        for path in pdf_paths:
            print(f"  - {os.path.basename(path)}")
        
        # Step 2: Let user choose the Excel file
        excel_path = filedialog.askopenfilename(
            title="Select the Excel file with PDF names and texts",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if not excel_path:
            messagebox.showinfo("Cancelled", "No Excel file selected. Exiting.")
            exit()
        
        # Read Excel
        try:
            df = pd.read_excel(excel_path, header=None)  # No header, first col PDF name, second text
            if df.shape[1] < 2:
                raise ValueError("Excel must have at least 2 columns: PDF name and text.")
            print(f"Loaded Excel with {len(df)} rows.")
            print(f"DEBUG: Excel columns: {df.shape[1]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read Excel: {str(e)}")
            exit()
        
        # Create a dict for quick lookup: {pdf_basename: text}
        text_map = {}
        for _, row in df.iterrows():
            pdf_name = str(row.iloc[0]).strip().lower()  # Normalize to lowercase for matching
            text = str(row.iloc[1]).strip()
            if pdf_name and text:
                text_map[pdf_name] = text
        
        print(f"DEBUG: Created text map with {len(text_map)} entries")
        for key, value in list(text_map.items())[:3]:  # Show first 3 entries
            print(f"  '{key}' -> '{value[:30]}...'")
        
        # Step 3: Let user choose page and position
        try:
            page_input = input("Enter the page number to insert on (1-based, e.g., 1): ").strip()
            page_num = int(page_input) - 1  # Convert to 0-based
            if page_num < 0:
                raise ValueError("Page number must be 1 or higher.")
            print(f"DEBUG: Using page {page_num} (0-based)")
        except ValueError as e:
            print(f"DEBUG: Invalid page input: {e}")
            messagebox.showerror("Error", "Invalid page number. Exiting.")
            exit()
        
        print("\nPosition options:")
        print("1. Top Left")
        print("2. Top Right")
        print("3. Bottom Left")
        print("4. Bottom Right")
        
        try:
            pos_choice = input("Enter your choice (1-4): ").strip()
            position_map = {"1": "top_left", "2": "top_right", "3": "bottom_left", "4": "bottom_right"}
            position = position_map.get(pos_choice)
            if not position:
                raise ValueError("Invalid choice.")
            print(f"DEBUG: Selected position: {position}")
        except ValueError as e:
            print(f"DEBUG: Invalid position choice: {e}")
            messagebox.showerror("Error", "Invalid position choice. Exiting.")
            exit()
        
        print(f"Will add text box to page {page_input} at {position.replace('_', ' ').title()} corner.")
        print("Text box size will be automatically adjusted based on text length.")
        print("Note: Any '\\' in text will be treated as a line break and split to the next row.")
        
        # Process each PDF
        successful = 0
        skipped = 0
        output_paths = []
        
        try:
            for i, pdf_path in enumerate(pdf_paths, 1):
                pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0].lower()  # Match without extension
                print(f"\nProcessing PDF {i}/{len(pdf_paths)}: {os.path.basename(pdf_path)}")
                print(f"DEBUG: Looking for basename: '{pdf_basename}'")
                
                if pdf_basename in text_map:
                    text = text_map[pdf_basename]
                    print(f"  Text: '{text[:50]}...'")  # Preview short text
                    # Estimate and print dimensions for logging (processes internally)
                    est_width, est_height = estimate_text_dimensions(text)
                    print(f"  Estimated box size: {est_width:.1f} x {est_height:.1f} pt")
                    output_path, success = add_freetext_annotation(pdf_path, page_num, position, text)
                    if success:
                        successful += 1
                        output_paths.append(output_path)
                        print(f"  Success! Output: {os.path.basename(output_path)}")
                    else:
                        skipped += 1
                        print(f"  Skipped: Invalid page or position.")
                else:
                    print(f"  Skipped: No matching text found in Excel for '{os.path.basename(pdf_path)}'")
                    print(f"DEBUG: Available keys: {list(text_map.keys())[:5]}...")  # Show first 5 keys
                    skipped += 1
            
            # Summary
            summary_msg = f"Processed {len(pdf_paths)} PDFs.\n"
            summary_msg += f"Successful additions: {successful}\n"
            summary_msg += f"Skipped: {skipped}\n"
            if output_paths:
                summary_msg += "Output files:\n" + "\n".join([f"  - {os.path.basename(p)}" for p in output_paths])
            
            if successful > 0:
                messagebox.showinfo("Success", summary_msg)
            else:
                messagebox.showinfo("No Changes", "No PDFs had matching texts in Excel.")
            
            print(f"\nSummary: {successful} successful additions, {skipped} skipped.")
            if output_paths:
                print("Output files:")
                for p in output_paths:
                    print(f"  - {p}")
        
        except Exception as e:
            print(f"DEBUG: Error during processing: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")
            print(f"Error: {str(e)}")
    
    except Exception as e:
        print(f"DEBUG: Fatal error: {str(e)}")
        messagebox.showerror("Fatal Error", f"A fatal error occurred: {str(e)}")
    
    input("Press Enter to exit...")  # Pause to see output