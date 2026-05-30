from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import os

from utils.logger import get_logger

logger = get_logger(__name__)

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " ", ""],
)


def parse_pdf(file_path: str) -> List[Document]:
    logger.info(f"Parsing PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    chunks = _splitter.split_documents(pages)
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = os.path.basename(file_path)
        chunk.metadata["chunk_id"] = i
    logger.info(f"Parsed {len(pages)} pages → {len(chunks)} chunks")
    return chunks


def parse_text(file_path: str) -> List[Document]:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    chunks = _splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = os.path.basename(file_path)
        chunk.metadata["chunk_id"] = i
    return chunks


def parse_file(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext in (".txt", ".md", ".csv"):
        return parse_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
