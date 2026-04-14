from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_file):
    pdf_file.seek(0)
    reader = PdfReader(pdf_file)
    extracted_pages = []

    for page in reader.pages:
        extracted_pages.append(page.extract_text() or "")

    text = "\n".join(extracted_pages).strip()
    pdf_file.seek(0)
    return text
