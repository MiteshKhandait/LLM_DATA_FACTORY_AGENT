from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.models import Document, DocumentSegment


def load_txt(path: Path) -> Document:
    """
    Load a plain text file and return a Document object.
    """

    text = path.read_text(encoding="utf-8")

    lines = text.splitlines()

    segments = []

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        segments.append(
            DocumentSegment(
                segment_id=f"line_{line_number}",
                text=line,
                location={
                    "type": "line",
                    "line": line_number,
                },
            )
        )

    return Document(
        text=text,
        source=str(path),
        file_type="txt",
        metadata={
            "character_count": len(text),
            "line_count": len(lines),
        },
        segments=segments,
    )


def load_pdf(path: Path) -> Document:
    """
    Load a PDF file and extract text from each page.
    """

    reader = PdfReader(str(path))

    pages = []
    segments = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        pages.append(page_text)

        if page_text.strip():
            segments.append(
                DocumentSegment(
                    segment_id=f"page_{page_number}",
                    text=page_text,
                    location={
                        "type": "page",
                        "page": page_number,
                    },
                )
            )

    text = "\n".join(pages)

    return Document(
        text=text,
        source=str(path),
        file_type="pdf",
        metadata={
            "page_count": len(reader.pages),
            "character_count": len(text),
        },
        segments=segments,
    )


def load_docx(path: Path) -> Document:
    """
    Load a DOCX file and extract paragraph text.
    """

    doc = DocxDocument(str(path))

    paragraphs = []
    segments = []

    for paragraph_number, paragraph in enumerate(
        doc.paragraphs,
        start=1,
    ):
        paragraph_text = paragraph.text

        if not paragraph_text.strip():
            continue

        paragraphs.append(paragraph_text)

        segments.append(
            DocumentSegment(
                segment_id=f"paragraph_{paragraph_number}",
                text=paragraph_text,
                location={
                    "type": "paragraph",
                    "paragraph": paragraph_number,
                },
            )
        )

    text = "\n".join(paragraphs)

    return Document(
        text=text,
        source=str(path),
        file_type="docx",
        metadata={
            "paragraph_count": len(paragraphs),
            "character_count": len(text),
        },
        segments=segments,
    )


def load_document(file_path: str | Path) -> Document:
    """
    Detect the file type and use the appropriate loader.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    extension = path.suffix.lower()

    if extension == ".txt":
        return load_txt(path)

    if extension == ".pdf":
        return load_pdf(path)

    if extension == ".docx":
        return load_docx(path)

    raise ValueError(
        f"Unsupported file type: {extension}. "
        "Supported formats: .txt, .pdf, .docx"
    )