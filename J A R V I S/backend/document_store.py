import asyncio
import csv
import json
import logging
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from livekit.agents.llm import function_tool


logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".csv", ".docx", ".pdf"}
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "for", "from", "how",
    "i", "in", "is", "it", "me", "of", "on", "or", "our", "please", "that", "the",
    "this", "to", "what", "when", "where", "which", "who", "why", "with", "you",
    "your", "ka", "ke", "ki", "kya", "mai", "main", "mujhe", "se", "toh",
}


@dataclass
class DocumentChunk:
    document_name: str
    chunk_index: int
    text: str


class DocumentKnowledgeBase:
    """Simple local document grounding over a folder of user-provided files."""

    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir).expanduser().resolve()
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    def _iter_documents(self) -> List[Path]:
        files = [
            path
            for path in self.documents_dir.rglob("*")
            if (
                path.is_file()
                and path.suffix.lower() in SUPPORTED_EXTENSIONS
                and not path.name.startswith(".")
                and path.name.lower() != "readme.md"
            )
        ]
        return sorted(files)

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _tokenize(self, text: str) -> List[str]:
        return [
            token
            for token in re.findall(r"[a-zA-Z0-9]{2,}", text.lower())
            if token not in STOP_WORDS
        ]

    def _chunk_text(self, text: str, max_chars: int = 900) -> List[str]:
        clean = self._normalize_whitespace(text)
        if not clean:
            return []

        sentences = re.split(r"(?<=[.!?])\s+", clean)
        chunks: List[str] = []
        current = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= max_chars:
                current = candidate
                continue

            if current:
                chunks.append(current)
            if len(sentence) <= max_chars:
                current = sentence
            else:
                for idx in range(0, len(sentence), max_chars):
                    chunks.append(sentence[idx: idx + max_chars].strip())
                current = ""

        if current:
            chunks.append(current)
        return chunks

    def _read_txt_like(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")

    def _read_json(self, path: Path) -> str:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _read_csv(self, path: Path) -> str:
        rows: List[str] = []
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                rows.append(", ".join(cell.strip() for cell in row if cell is not None))
        return "\n".join(rows)

    def _read_docx(self, path: Path) -> str:
        try:
            with zipfile.ZipFile(path) as archive:
                xml_bytes = archive.read("word/document.xml")
            xml_text = xml_bytes.decode("utf-8", errors="ignore")
            return " ".join(re.findall(r">([^<>]+)<", xml_text))
        except Exception as exc:
            logger.warning("Failed to parse DOCX %s: %s", path.name, exc)
            return ""

    def _read_pdf(self, path: Path) -> str:
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            logger.warning("PDF parsing skipped for %s because pypdf is not installed.", path.name)
            return ""

        try:
            reader = PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        except Exception as exc:
            logger.warning("Failed to parse PDF %s: %s", path.name, exc)
            return ""

    def _read_document(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            return self._read_txt_like(path)
        if suffix == ".json":
            return self._read_json(path)
        if suffix == ".csv":
            return self._read_csv(path)
        if suffix == ".docx":
            return self._read_docx(path)
        if suffix == ".pdf":
            return self._read_pdf(path)
        return ""

    def _load_chunks_sync(self) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        for path in self._iter_documents():
            text = self._read_document(path)
            for idx, chunk in enumerate(self._chunk_text(text)):
                chunks.append(
                    DocumentChunk(
                        document_name=path.name,
                        chunk_index=idx,
                        text=chunk,
                    )
                )
        return chunks

    async def load_chunks(self) -> List[DocumentChunk]:
        return await asyncio.to_thread(self._load_chunks_sync)

    async def get_status(self) -> Dict[str, Any]:
        files = await asyncio.to_thread(self._iter_documents)
        return {
            "documents_dir": str(self.documents_dir),
            "document_count": len(files),
            "document_names": [path.name for path in files[:10]],
            "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
        }

    async def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        chunks = await self.load_chunks()
        query_terms = set(self._tokenize(query))
        if not query_terms:
            return []

        scored: List[tuple[int, int, DocumentChunk]] = []
        for chunk in chunks:
            chunk_terms = set(self._tokenize(chunk.text))
            overlap = len(query_terms & chunk_terms)
            if overlap == 0:
                continue
            scored.append((overlap, len(chunk.text), chunk))

        ranked = sorted(scored, key=lambda item: (item[0], min(item[1], 900)), reverse=True)
        results: List[Dict[str, Any]] = []
        for overlap, _, chunk in ranked[:limit]:
            results.append(
                {
                    "document_name": chunk.document_name,
                    "chunk_index": chunk.chunk_index,
                    "score": overlap,
                    "text": chunk.text,
                }
            )
        return results

    async def build_prompt_context(self, limit: int = 5) -> str:
        status = await self.get_status()
        if status["document_count"] == 0:
            return "\nDOCUMENT KNOWLEDGE BASE:\n(No local documents available.)"

        names = ", ".join(status["document_names"][:limit])
        more = ""
        if status["document_count"] > limit:
            more = f" and {status['document_count'] - limit} more"
        return (
            "\nDOCUMENT KNOWLEDGE BASE:\n"
            f"- Folder: {status['documents_dir']}\n"
            f"- Loaded documents: {status['document_count']}\n"
            f"- Available files: {names}{more}\n"
            "- Use the local document tools whenever the user asks about uploaded files, notes, PDFs, or documents.\n"
        )


def create_document_tools(knowledge_base: DocumentKnowledgeBase) -> Sequence[Any]:
    @function_tool()
    async def list_local_documents() -> str:
        """List user-provided local documents available for grounded answers."""
        status = await knowledge_base.get_status()
        if status["document_count"] == 0:
            return (
                "No local documents found. Ask the user to place files in "
                f"{status['documents_dir']}."
            )
        return json.dumps(
            {
                "documents_dir": status["documents_dir"],
                "document_count": status["document_count"],
                "document_names": status["document_names"],
            },
            ensure_ascii=False,
        )

    @function_tool()
    async def search_local_documents(query: str) -> str:
        """Search the local document folder for passages relevant to the user's question."""
        results = await knowledge_base.search(query=query, limit=3)
        if not results:
            return (
                "No relevant local document passages found. Try a more specific query "
                "or add documents to the knowledge base folder."
            )
        return json.dumps(results, ensure_ascii=False)

    return [list_local_documents, search_local_documents]
