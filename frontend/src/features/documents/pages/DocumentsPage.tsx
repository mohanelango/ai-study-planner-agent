import { useEffect, useState } from "react";

import { fetchDocuments } from "../services/documentsApi";
import type { DocumentRecord } from "../types/documents";

export function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments()
      .then((response) => setDocuments(response.data))
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load documents"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <section className="hero-card">
      <p className="eyebrow">Documents</p>
      <h1>Documents</h1>
      <p className="subtitle">Upload PDFs and track ingestion status. Embeddings and ask-from-notes are intentionally not implemented yet.</p>
      <a className="button-link" href="/documents/upload">Upload Document</a>
      {isLoading ? <p className="status">Loading documents...</p> : null}
      {error ? <p className="status error">{error}</p> : null}
      <div className="calendar-list">
        {documents.map((document) => (
          <article className="status-panel wide-panel" key={document.id}>
            <h2>{document.title}</h2>
            <span>Filename: {document.original_filename}</span>
            <span>Status: {document.status}</span>
            <span>Chunks: {document.chunk_count ?? 0}</span>
            <span>Uploaded: {document.uploaded_at ?? document.created_at}</span>
            <a className="button-link secondary" href={`/documents/${document.id}`}>View detail</a>
          </article>
        ))}
      </div>
    </section>
  );
}

