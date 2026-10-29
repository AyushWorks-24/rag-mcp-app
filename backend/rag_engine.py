
import os
import uuid
import chromadb
import fitz


class RAGEngine:
    def __init__(self):
        os.makedirs("vector_db", exist_ok=True)
        self.client = chromadb.PersistentClient(path="vector_db")
        self.collection = self.client.get_or_create_collection(
            name="pdf_chunks"
        )

    def process_pdf(self, pdf_path: str) -> str:
        document_id = str(uuid.uuid4())
        pdf = fitz.open(pdf_path)
        chunks = []

        for page_number, page in enumerate(pdf):
            text = page.get_text("text")
            words = text.split()

            for start in range(0, len(words), 180):
                chunk = " ".join(words[start:start + 180])
                if len(chunk.strip()) > 40:
                    chunks.append((page_number + 1, chunk))

        pdf.close()

        if not chunks:
            raise ValueError("No readable text found in this PDF.")

        self.collection.add(
            ids=[f"{document_id}_{i}" for i in range(len(chunks))],
            documents=[chunk for _, chunk in chunks],
            metadatas=[
                {"document_id": document_id, "page": page}
                for page, _ in chunks
            ]
        )

        return document_id

    def retrieve(self, document_id: str, query: str, top_k: int = 5) -> list[str]:
        count = self.collection.count()

        if count == 0:
            return []

        result = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, count),
            where={"document_id": document_id}
        )

        return result.get("documents", [[]])[0]
