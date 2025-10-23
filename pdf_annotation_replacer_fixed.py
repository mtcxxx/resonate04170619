import pymupdf  # PyMuPDF, install with: pip install pymupdf
import os
import sys

# Try to import tkinter, but handle the case where it's not available or no display
def check_gui_availability():
    """Check if GUI is available by testing tkinter creation."""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, simpledialog
        
        # Try to create a root window to test if display is available
        root = tk.Tk()
        root.withdraw()  # Hide it immediately
        root.destroy()
        return True, tk, filedialog, messagebox, simpledialog
    except ImportError:
        return False, None, None, None, None
    except Exception as e:
        return False, None, None, None, None

GUI_AVAILABLE, tk, filedialog, messagebox, simpledialog = check_gui_availability()

if not GUI_AVAILABLE:
    print("Warning: GUI not available. Falling back to command-line mode.")

def replace_text_in_annotations(pdf_path, old_text, new_text):
    """
    Replaces old_text with new_text in all annotation contents across the PDF.
    Handles both Text (sticky notes) and FreeText annotations.
    Returns the number of modifications made and the path to the updated PDF.
    """
    try:
        doc = pymupdf.open(pdf_path)
        modified_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            for annot in page.annots():
                try:
                    info = annot.info
                    current_content = info.get("content", "")
                    
                    if old_text in current_content:
                        # For Text annotations (e.g., sticky notes), update the popup content
                        if annot.type[1] == "Text":
                            info["content"] = current_content.replace(old_text, new_text)
                            annot.set_info(info)
                            modified_count += 1
                            print(f"Modified Text annotation on page {page_num + 1} of {os.path.basename(pdf_path)}")
                        
                        # For FreeText annotations (editable text boxes), update the displayed text
                        elif annot.type[1] == "FreeText":
                            new_full_content = current_content.replace(old_text, new_text)
                            # Update the content in the annotation info
                            info["content"] = new_full_content
                            annot.set_info(info)
                            # For FreeText annotations, we need to update the appearance stream
                            # This recreates the visual representation of the text
                            annot.update()
                            modified_count += 1
                            print(f"Modified FreeText annotation on page {page_num + 1} of {os.path.basename(pdf_path)}")
                except Exception as e:
                    print(f"Warning: Could not process annotation on page {page_num + 1}: {e}")
                    continue
        
        # Try to save incrementally first, fall back to new file if that fails
        try:
            doc.save(pdf_path, incremental=True)
            output_path = pdf_path
        except Exception as e:
            print(f"Warning: Could not save incrementally ({e}). Saving to new file.")
            output_path = pdf_path.replace('.pdf', '_modified.pdf')
            doc.save(output_path)
        
        doc.close()
        
        return modified_count, output_path
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return 0, pdf_path

def get_pdf_files_gui():
    """Get PDF files using GUI file dialog."""
    if not GUI_AVAILABLE:
        return []
    
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    pdf_paths = filedialog.askopenfilenames(
        title="Select one or more PDF files",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    root.destroy()
    return list(pdf_paths)

def get_pdf_files_cli():
    """Get PDF files using command line input."""
    print("Enter PDF file paths (one per line, empty line to finish):")
    pdf_paths = []
    while True:
        path = input("PDF path: ").strip()
        if not path:
            break
        if os.path.exists(path) and path.lower().endswith('.pdf'):
            pdf_paths.append(path)
        else:
            print(f"Warning: {path} is not a valid PDF file or doesn't exist.")
    
    return pdf_paths

def get_text_input_gui(prompt, title):
    """Get text input using GUI dialog."""
    if not GUI_AVAILABLE:
        return None
    
    root = tk.Tk()
    root.withdraw()
    
    result = simpledialog.askstring(title, prompt)
    root.destroy()
    return result

def get_text_input_cli(prompt):
    """Get text input using command line."""
    return input(f"{prompt}: ").strip()

def show_message_gui(title, message, msg_type="info"):
    """Show message using GUI dialog."""
    if not GUI_AVAILABLE:
        return
    
    root = tk.Tk()
    root.withdraw()
    
    if msg_type == "error":
        messagebox.showerror(title, message)
    elif msg_type == "warning":
        messagebox.showwarning(title, message)
    else:
        messagebox.showinfo(title, message)
    
    root.destroy()

def main():
    """Main function that handles both GUI and CLI modes."""
    print("PDF Annotation Text Replacer")
    print("=" * 40)
    
    # Step 1: Get PDF files
    if GUI_AVAILABLE and len(sys.argv) == 1:
        print("GUI mode available. Opening file dialog...")
        pdf_paths = get_pdf_files_gui()
        if not pdf_paths:
            show_message_gui("Cancelled", "No PDFs selected. Exiting.")
            return
    else:
        if len(sys.argv) > 1:
            # PDF files provided as command line arguments
            pdf_paths = [arg for arg in sys.argv[1:] if arg.lower().endswith('.pdf') and os.path.exists(arg)]
            if not pdf_paths:
                print("Error: No valid PDF files found in command line arguments.")
                return
        else:
            # Use CLI input
            pdf_paths = get_pdf_files_cli()
            if not pdf_paths:
                print("No PDF files provided. Exiting.")
                return
    
    print(f"Selected {len(pdf_paths)} PDF(s):")
    for path in pdf_paths:
        print(f"  - {path}")
    
    # Step 2: Get text to replace
    if GUI_AVAILABLE and len(sys.argv) == 1:
        old_text = get_text_input_gui("Enter the text to find and replace:", "Find Text")
        if old_text is None:
            show_message_gui("Cancelled", "Operation cancelled. Exiting.")
            return
    else:
        old_text = get_text_input_cli("Enter the text to find and replace")
        if not old_text:
            print("Error: No search text provided. Exiting.")
            return
    
    old_text = old_text.strip()
    if not old_text:
        if GUI_AVAILABLE and len(sys.argv) == 1:
            show_message_gui("Error", "No search text provided. Exiting.")
        else:
            print("Error: No search text provided. Exiting.")
        return
    
    # Step 3: Get replacement text
    if GUI_AVAILABLE and len(sys.argv) == 1:
        new_text = get_text_input_gui("Enter the replacement text:", "Replace Text")
        if new_text is None:
            show_message_gui("Cancelled", "Operation cancelled. Exiting.")
            return
    else:
        new_text = get_text_input_cli("Enter the replacement text")
    
    new_text = new_text.strip()
    
    # Process each PDF
    total_modified = 0
    modified_paths = []
    
    try:
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"\nProcessing PDF {i}/{len(pdf_paths)}: {os.path.basename(pdf_path)}")
            modified_count, updated_path = replace_text_in_annotations(pdf_path, old_text, new_text)
            total_modified += modified_count
            modified_paths.append(updated_path)
            print(f"Completed: {modified_count} annotations modified. Updated: {updated_path}")
        
        # Summary
        if total_modified > 0:
            summary_msg = f"Successfully replaced text in {total_modified} annotations across {len(pdf_paths)} PDFs.\n"
            summary_msg += "Modified files:\n" + "\n".join([f"  - {os.path.basename(p)}" for p in modified_paths])
            
            if GUI_AVAILABLE and len(sys.argv) == 1:
                show_message_gui("Success", summary_msg)
            else:
                print(f"\n{summary_msg}")
        else:
            no_changes_msg = "No matching text found in any annotations across the selected PDFs."
            if GUI_AVAILABLE and len(sys.argv) == 1:
                show_message_gui("No Changes", no_changes_msg)
            else:
                print(f"\n{no_changes_msg}")
        
        print(f"\nSummary: {total_modified} total annotations modified across {len(pdf_paths)} PDFs.")
        print("Modified files:")
        for p in modified_paths:
            print(f"  - {p}")
    
    except Exception as e:
        error_msg = f"An error occurred during processing: {str(e)}"
        if GUI_AVAILABLE and len(sys.argv) == 1:
            show_message_gui("Error", error_msg)
        else:
            print(f"Error: {error_msg}")
    
    if GUI_AVAILABLE and len(sys.argv) == 1:
        show_message_gui("Done", "Processing complete. Press OK to exit.")
    else:
        print("\nProcessing complete.")

if __name__ == "__main__":
    main()
