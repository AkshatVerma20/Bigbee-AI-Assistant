from langchain_core.tools import tool


@tool
def document_search(query: str) -> str:
    """Search the contents of uploaded documents for information relevant to a query.
    Use this when the user asks questions about documents, PDFs, or uploaded files.
    Input: a natural language query about the document content.
    """
    from rag.retriever import retrieve_context
    context, sources = retrieve_context(query, top_k=4)
    if not context:
        return "No relevant content found in uploaded documents. Try uploading a PDF first."
    return f"Sources: {', '.join(sources)}\n\n{context}"
