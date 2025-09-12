import base64
import io
import fitz
from PIL import Image

def pdf_page_to_base64(file):
    print('pdf to image start')
    file_content = file.read()
    pdf_document = fitz.open(stream=file_content, filetype="pdf")
    page = pdf_document.load_page(0)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    print("pdf to image end")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
