import pymupdf  # PyMuPDF, install with: pip install pymupdf
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

def replace_text_in_annotations(pdf_path, old_text, new_text):
    """
    Replaces old_text with new_text in all annotation contents across the PDF.
    Handles both Text (sticky notes) and FreeText annotations.
    Returns the number of modifications made and the output path.
    """
    doc = pymupdf.open(pdf_path)
    modified_count = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        for annot in page.annots():
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
    
    # Save the modified PDF
    base_name = os.path.splitext(pdf_path)[0]
    output_path = f"{base_name}_modified.pdf"
    doc.save(output_path)
    doc.close()
    
    return modified_count, output_path

# Main script
if __name__ == "__main__":
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
        print(f"  - {path}")
    
    # Step 2: Let user type the text to replace (applied to all PDFs)
    old_text = simpledialog.askstring("Text to Find", "Enter the text to find and replace:", parent=root).strip()
    if not old_text:
        messagebox.showerror("Error", "No search text provided. Exiting.")
        exit()
    
    # Step 3: Let user type the replacement text (applied to all PDFs)
    new_text = simpledialog.askstring("Replacement Text", "Enter the replacement text:", parent=root).strip()
    
    # Process each PDF
    total_modified = 0
    output_paths = []
    
    try:
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"\nProcessing PDF {i}/{len(pdf_paths)}: {os.path.basename(pdf_path)}")
            modified_count, output_path = replace_text_in_annotations(pdf_path, old_text, new_text)
            total_modified += modified_count
            output_paths.append(output_path)
            print(f"Completed: {modified_count} annotations modified. Output: {output_path}")
        
        # Summary
        if total_modified > 0:
            summary_msg = f"Successfully replaced text in {total_modified} annotations across {len(pdf_paths)} PDFs.\n"
            summary_msg += "Output files:\n" + "\n".join([f"  - {os.path.basename(p)}" for p in output_paths])
            messagebox.showinfo("Success", summary_msg)
        else:
            messagebox.showinfo("No Changes", "No matching text found in any annotations across the selected PDFs.")
        
        print(f"\nSummary: {total_modified} total annotations modified across {len(pdf_paths)} PDFs.")
        print("Output files:")
        for p in output_paths:
            print(f"  - {p}")
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")
        print(f"Error: {str(e)}")
    
    messagebox.showinfo("Complete", "Processing complete! Check the console for details.")