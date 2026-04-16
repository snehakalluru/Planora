MAX_PDF_TEXT_LENGTH = 2000


def extract_text_from_pdf(pdf_file):
    try:
        from PyPDF2 import PdfReader
    except ImportError as exc:
        raise RuntimeError("PyPDF2 is not installed. PDF uploads are unavailable.") from exc

    pdf_file.seek(0)
    reader = PdfReader(pdf_file)
    extracted_pages = []

    for page in reader.pages:
        extracted_pages.append(page.extract_text() or "")

    text = "\n".join(extracted_pages).strip()
    pdf_file.seek(0)

    if len(text) > MAX_PDF_TEXT_LENGTH:
        return text[:MAX_PDF_TEXT_LENGTH].rstrip() + "\n\n[...truncated for model safety]"

    return text
