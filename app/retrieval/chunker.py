from app.models.schemas import SourceDocument


def chunk_text(text: str, max_chunk_size: int, overlap: int) -> list[str]:
    text = text.strip()
    if not text:
        return []

    if max_chunk_size <= 0:
        return [text]

    chunks: list[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + max_chunk_size, text_len)
        chunks.append(text[start:end].strip())
        if end >= text_len:
            break
        start = max(0, end - overlap)

    return [c for c in chunks if c]


def chunk_documents(docs: list[SourceDocument], max_chunk_size: int, overlap: int) -> list[SourceDocument]:
    chunked: list[SourceDocument] = []
    for doc in docs:
        pieces = chunk_text(doc.content, max_chunk_size=max_chunk_size, overlap=overlap)
        if not pieces:
            continue
        for idx, piece in enumerate(pieces):
            metadata = dict(doc.metadata)
            metadata["chunk_index"] = idx
            metadata["chunk_count"] = len(pieces)
            chunked.append(
                SourceDocument(
                    source=doc.source,
                    type=doc.type,
                    content=piece,
                    metadata=metadata,
                )
            )
    return chunked
