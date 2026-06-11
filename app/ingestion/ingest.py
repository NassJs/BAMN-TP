import json
import re
import os
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

INPUT_DIR = Path("corpus/raw")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
MIN_CHUNK_LEN = 80


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def detect_language(text: str):
    if detect is None or not text:
        return None
    try:
        return detect(text[:1000])
    except Exception:
        return None


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


def split_text(text: str):
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
        res = []
        pos = 0
        for chunk in chunks:
            idx = text.find(chunk, pos)
            if idx == -1:
                idx = pos
            chunk = clean_text(chunk)
            if len(chunk) >= MIN_CHUNK_LEN:
                res.append((idx, chunk))
            pos = idx + len(chunk)
        return res

    step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
    res = []
    for start in range(0, len(text), step):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = clean_text(text[start:end])
        if len(chunk) >= MIN_CHUNK_LEN:
            res.append((start, chunk))
        if end >= len(text):
            break
    return res