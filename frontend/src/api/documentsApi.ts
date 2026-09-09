import { apiFetch } from './client';
import { Document } from '../types/document';
import { PaginatedResponse } from '../types/api';

export const documentsApi = {
  getDocuments: async (skip = 0, limit = 50): Promise<Document[]> => {
    return apiFetch<Document[]>(`/documents?skip=${skip}&limit=${limit}`);
  },

  listDocuments: async (
    page = 1,
    limit = 50
  ): Promise<PaginatedResponse<Document>> => {
    const skip = (page - 1) * limit;
    const docs = await apiFetch<Document[]>(`/documents?skip=${skip}&limit=${limit}`);
    return {
      items: docs,
      total: docs.length,
      page,
      limit,
      total_pages: Math.ceil(docs.length / limit) || 1,
    };
  },

  getDocument: async (documentId: string): Promise<Document> => {
    return apiFetch<Document>(`/documents/${documentId}`);
  },

  uploadDocument: async (file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);

    return apiFetch<Document>('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  },

  uploadPDF: async (file: File): Promise<Document> => {
    return documentsApi.uploadDocument(file);
  },

  processDocument: async (
    documentId: string
  ): Promise<{
    document_id: string;
    filename: string;
    status: string;
    num_pages: number;
    facts_count: number;
    document: Document;
  }> => {
    const res = await apiFetch<any>(`/documents/${documentId}/process`, {
      method: 'POST',
    });
    const doc = await documentsApi.getDocument(documentId);
    return {
      ...res,
      document: doc,
    };
  },

  deleteDocument: async (documentId: string): Promise<{ deleted_document_id: string }> => {
    return apiFetch(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  },
};
