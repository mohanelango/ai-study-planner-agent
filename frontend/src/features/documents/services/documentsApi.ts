import { del, get, postForm } from "../../../shared/api/httpClient";
import type { ApiResponse, DocumentChunk, DocumentRecord, DocumentStatus, DocumentUploadResponse } from "../types/documents";

export function fetchDocuments(goalId?: string) {
  const query = goalId ? `?goal_id=${encodeURIComponent(goalId)}` : "";
  return get<ApiResponse<DocumentRecord[]>>(`/documents${query}`);
}

export function fetchDocument(documentId: string) {
  return get<ApiResponse<DocumentRecord>>(`/documents/${documentId}`);
}

export function fetchDocumentStatus(documentId: string) {
  return get<ApiResponse<DocumentStatus>>(`/documents/${documentId}/status`);
}

export function fetchDocumentChunks(documentId: string) {
  return get<ApiResponse<DocumentChunk[]>>(`/documents/${documentId}/chunks`);
}

export function uploadDocument(input: { file: File; title?: string; goalId?: string }) {
  const formData = new FormData();
  formData.append("file", input.file);
  if (input.title) formData.append("title", input.title);
  if (input.goalId) formData.append("goal_id", input.goalId);
  return postForm<ApiResponse<DocumentUploadResponse>>("/documents/upload", formData);
}

export function deleteDocument(documentId: string) {
  return del<ApiResponse<Record<string, never>>>(`/documents/${documentId}`);
}

