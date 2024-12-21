import os
from PyPDF2 import PdfReader

# Folder containing PDF files
pdf_folder = "path_to_your_folder"  # Replace with your folder path
output_txt = "output.txt"          # Output text file

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()  # Remove extra whitespace
    except Exception as e:
        return f"Error reading {pdf_path}: {str(e)}"

# Main script to process PDFs and save results to a text file
def process_pdfs_to_text(pdf_folder, output_txt):
    with open(output_txt, "w", encoding="utf-8") as txt_file:
        for file_name in os.listdir(pdf_folder):
            if file_name.endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, file_name)
                print(f"Processing: {pdf_path}")
                text = extract_text_from_pdf(pdf_path)
                # Write PDF content to the text file
                txt_file.write(f"File: {file_name}\n{text}\n\n\n\n")  # 4-line gap
    print(f"Text content saved to {output_txt}")

# Run the script
process_pdfs_to_text(pdf_folder, output_txt)
