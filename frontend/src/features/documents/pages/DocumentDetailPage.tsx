import { useEffect, useState } from "react";

import { fetchDocument, fetchDocumentChunks, fetchDocumentStatus } from "../services/documentsApi";
import type { DocumentChunk, DocumentRecord, DocumentStatus } from "../types/documents";

function getDocumentIdFromPath(): string {
  return window.location.pathname.split("/")[2] ?? "";
}

export function DocumentDetailPage() {
  const documentId = getDocumentIdFromPath();
  const [document, setDocument] = useState<DocumentRecord | null>(null);
  const [status, setStatus] = useState<DocumentStatus | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    try {
      const [documentResponse, statusResponse] = await Promise.all([fetchDocument(documentId), fetchDocumentStatus(documentId)]);
      setDocument(documentResponse.data);
      setStatus(statusResponse.data);
      if (statusResponse.data.status === "processed") {
        const chunksResponse = await fetchDocumentChunks(documentId);
        setChunks(chunksResponse.data);
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load document");
    }
  }

  useEffect(() => {
    void load();
  }, [documentId]);

  return (
    <section className="hero-card">
      <p className="eyebrow">Documents</p>
      <h1>Document Detail</h1>
      {error ? <p className="status error">{error}</p> : null}
      {document && status ? (
        <div className="status-panel wide-panel">
          <h2>{document.title}</h2>
          <span>Filename: {document.original_filename}</span>
          <span>Status: {status.status}</span>
          <span>Characters: {status.extracted_text_char_count ?? 0}</span>
          <span>Chunks: {status.chunk_count ?? 0}</span>
          {status.processing_error ? <p className="status error">{status.processing_error}</p> : null}
          <button type="button" onClick={() => void load()}>Refresh Status</button>
        </div>
      ) : <p className="status">Loading document...</p>}
      {status?.status === "processed" ? (
        <div className="calendar-list">
          {chunks.map((chunk) => (
            <details className="status-panel wide-panel" key={chunk.id}>
              <summary>Chunk {chunk.chunk_index + 1} · pages {chunk.page_start ?? "?"}-{chunk.page_end ?? "?"} · ~{chunk.token_estimate ?? 0} tokens</summary>
              <p>{chunk.text}</p>
            </details>
          ))}
        </div>
      ) : <p className="status">Chunks appear after Celery processing finishes.</p>}
    </section>
  );
}

