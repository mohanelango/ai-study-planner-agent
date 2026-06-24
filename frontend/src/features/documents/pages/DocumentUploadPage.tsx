import { FormEvent, useState } from "react";

import { uploadDocument } from "../services/documentsApi";
import type { DocumentUploadResponse } from "../types/documents";

export function DocumentUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [goalId, setGoalId] = useState("");
  const [result, setResult] = useState<DocumentUploadResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    setError(null);
    setIsUploading(true);
    setResult(null);
    try {
      const response = await uploadDocument({ file, title: title || undefined, goalId: goalId || undefined });
      setResult(response.data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not upload document");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="hero-card form-card">
      <p className="eyebrow">Documents</p>
      <h1>Upload PDF</h1>
      <form onSubmit={onSubmit} className="stacked-form">
        <label>PDF file<input accept="application/pdf,.pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} required type="file" /></label>
        <label>Title<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Optional" /></label>
        <label>Goal ID<input value={goalId} onChange={(event) => setGoalId(event.target.value)} placeholder="Optional" /></label>
        <button type="submit" disabled={isUploading}>{isUploading ? "Uploading..." : "Upload PDF"}</button>
      </form>
      {error ? <p className="status error">{error}</p> : null}
      {result ? (
        <div className="status-panel wide-panel">
          <strong>Uploaded: {result.document.title}</strong>
          <span>Status: {result.document.status}</span>
          <span>Background job: {result.background_job_id}</span>
          <a className="button-link" href={`/documents/${result.document.id}`}>View document</a>
        </div>
      ) : null}
    </section>
  );
}

