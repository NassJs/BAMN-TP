import json
import os
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from langdetect import detect
except ImportError:
    detect = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None

# Raw corpus input folder
INPUT_DIR = Path("corpus/raw")

# Final output required by R1
OUTPUT_FILE = Path("corpus/chunks.jsonl")

# Default chunk parameters required by the project
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))

# Skip extremely small fragments
MIN_CHUNK_LEN = 80


def clean_text(text: str) -> str:
    """Normalize whitespace and remove noisy characters."""
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def detect_language(text: str):
    """Detect language if langdetect is available."""
    if detect is None or not text:
        return None
    try:
        return detect(text[:1000])
    except Exception:
        return None


def extract_txt(path: Path) -> str:
    """Extract text from plain text files."""
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_json(path: Path) -> str:
    """Extract text recursively from JSON values."""
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)

    texts = []

    def walk(obj):
        if isinstance(obj, dict):
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
        elif isinstance(obj, str):
            s = obj.strip()
            if s:
                texts.append(s)

    walk(data)
    return "\n".join(texts)


def extract_html(path: Path) -> str:
    """Extract readable text from HTML files."""
    html = path.read_text(encoding="utf-8", errors="ignore")

    if BeautifulSoup is None:
        return re.sub(r"<[^>]+>", " ", html)

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def extract_pdf(path: Path) -> str:
    """Extract text from a PDF file."""
    if PdfReader is None:
        raise ImportError("pypdf is required for PDF extraction")

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def extract_text(path: Path) -> str:
    """Dispatch extraction according to file extension."""
    ext = path.suffix.lower()

    if ext == ".txt":
        return extract_txt(path)
    if ext == ".json":
        return extract_json(path)
    if ext in {".html", ".htm"}:
        return extract_html(path)
    if ext == ".pdf":
        return extract_pdf(path)

    return ""


def split_text(text: str):
    """Split text into overlapping chunks."""
    text = clean_text(text)
    if len(text) < MIN_CHUNK_LEN:
        return []

    if RecursiveCharacterTextSplitter is not None:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_text(text)

        result = []
        cursor = 0
        for chunk in chunks:
            chunk = clean_text(chunk)
            idx = text.find(chunk, cursor)
            if idx == -1:
                idx = cursor
            if len(chunk) >= MIN_CHUNK_LEN:
                result.append((idx, chunk))
            cursor = idx + max(1, len(chunk) - CHUNK_OVERLAP)

        return result

    # Fallback if langchain_text_splitters is not installed
    step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
    result = []

    for start in range(0, len(text), step):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = clean_text(text[start:end])
        if len(chunk) >= MIN_CHUNK_LEN:
            result.append((start, chunk))
        if end >= len(text):
            break

    return result


def collect_files(base_dir: Path):
    """Collect supported files from corpus/raw."""
    if not base_dir.exists():
        return []

    files = []
    for pattern in ("*.txt", "*.json", "*.html", "*.htm", "*.pdf"):
        files.extend(base_dir.rglob(pattern))

    return sorted(files)


def process_file(path: Path):
    """Extract, chunk, and attach metadata to a single file."""
    raw_text = extract_text(path)
    text = clean_text(raw_text)

    if len(text) < MIN_CHUNK_LEN:
        return []

    lang = detect_language(text)
    file_type = path.suffix.lower().lstrip(".")
    records = []

    for i, (position, chunk) in enumerate(split_text(text)):
        records.append(
            {
                "source": str(path.as_posix()),
                "type": file_type,
                "chunk_id": f"{path.stem}_{i}",
                "position": position,
                "language": lang,
                "text": chunk,
            }
        )

    return records


def main():
    """Run ingestion and write the JSONL output."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    files = collect_files(INPUT_DIR)
    all_chunks = []

    for path in files:
        try:
            all_chunks.extend(process_file(path))
        except Exception as e:
            print(f"[ingest] skip {path}: {e}")

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for item in all_chunks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[ingest] {len(files)} documents -> {len(all_chunks)} chunks dans {OUTPUT_FILE}")


if __name__ == "__main__":
    main()