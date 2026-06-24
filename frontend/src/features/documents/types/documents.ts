export type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T;
};

export type DocumentRecord = {
  id: string;
  goal_id: string | null;
  title: string;
  original_filename: string;
  content_type: string;
  file_size_bytes: number | null;
  status: string;
  extracted_text_char_count: number | null;
  chunk_count: number | null;
  uploaded_at: string | null;
  processed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentUploadResponse = {
  document: DocumentRecord;
  background_job_id: string;
};

export type DocumentStatus = {
  id: string;
  title: string;
  original_filename: string;
  status: string;
  extracted_text_char_count: number | null;
  chunk_count: number | null;
  uploaded_at: string | null;
  processed_at: string | null;
  processing_error: string | null;
};

export type DocumentChunk = {
  id: string;
  document_id: string;
  chunk_index: number;
  text: string;
  page_start: number | null;
  page_end: number | null;
  token_estimate: number | null;
};

