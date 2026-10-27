import re

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
PDF_PATH = "ai_document_intelligence_poc_sample.pdf"
HEADING_PATTERN = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$")
PAGE_NUMBER_PATTERN = re.compile(r"\bPage\s+\d+\s+of\s+\d+\b")


def embed_chunk(chunks: list[dict]) -> list[dict]:
    for chunk in chunks:
        chunk["embedding"] = model.encode(chunk["text"]).tolist()
    return chunks

def extract_paragraph_chunks(pdf_path: str) -> list[dict[str, str | int | None]]:
    reader = PdfReader(pdf_path)
    first_page_text = reader.pages[0].extract_text() or ""
    document_id_match = re.search(
        r"\bDocument ID:\s*([A-Za-z0-9_-]+)", first_page_text
    )
    title_id = document_id_match.group(1) if document_id_match else "document"

    chunks: list[dict[str, str | int | None]] = []
    current_heading_id: str | None = None
    current_heading: str | None = None

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text(extraction_mode="layout") or ""
        paragraph_lines: list[str] = []

        def save_paragraph() -> None:
            if not paragraph_lines:
                return

            paragraph_id = len(chunks) + 1
            chunks.append(
                {
                    "title_id": title_id,
                    "heading_id": current_heading_id,
                    "heading": current_heading,
                    "paragraph_id": f"{title_id}-paragraph-{paragraph_id:04d}",
                    "chunk_id": f"{title_id}-chunk-{paragraph_id:04d}",
                    "page_number": page_number,
                    "text": " ".join(paragraph_lines),
                }
            )
            paragraph_lines.clear()

        for raw_line in page_text.splitlines():
            line = raw_line.strip()

            if PAGE_NUMBER_PATTERN.search(line):
                continue

            if not line:
                save_paragraph()
                continue

            heading_match = HEADING_PATTERN.match(line)
            if heading_match:
                save_paragraph()
                current_heading_id = heading_match.group(1).rstrip(".")
                current_heading = line
                continue

            paragraph_lines.append(line)

        save_paragraph()

    return chunks


if __name__ == "__main__":
    chunks = extract_paragraph_chunks(PDF_PATH)
    print(f"Created {len(chunks)} paragraph chunks.")
    chunks = embed_chunk(chunks)
    for chunk in chunks[:4]:
        print(
            f"\n{chunk['chunk_id']} | page {chunk['page_number']} "
            f"| heading: {chunk['heading'] or 'none'}"
        )
        
