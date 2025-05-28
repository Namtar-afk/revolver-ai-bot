# PyPDF2.py


class PdfWriter:
    """Stub minimal pour tests : écrit un PDF vide."""

    def __init__(self):
        pass

    def write(self, path: str) -> None:
        # Écrit un en-tête PDF et une marque de fin
        with open(path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")
