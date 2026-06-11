import json
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

INPUT_DIR = Path("corpus/raw")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def extract_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_json(path: Path) -> str:
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
    html = path.read_text(encoding="utf-8", errors="ignore")
    if BeautifulSoup is None:
        return re.sub(r"<[^>]+>", " ", html)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def extract_pdf(path: Path) -> str:
    if PdfReader is None:
        raise ImportError("pypdf required")
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def extract_text(path: Path) -> str:
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


def collect_files(base_dir: Path):
    if not base_dir.exists():
        return []
    files = []
    for pattern in ("*.txt", "*.json", "*.html", "*.htm", "*.pdf"):
        files.extend(base_dir.rglob(pattern))
    return sorted(files)


def main():
    files = collect_files(INPUT_DIR)
    for path in files[:3]:
        text = clean_text(extract_text(path))
        print(f"FILE={path} LEN={len(text)}")
        print(text[:300])
        print("-" * 40)


if __name__ == "__main__":
    main()