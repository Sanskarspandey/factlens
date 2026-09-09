import React, { useState, useEffect } from 'react';
import { documentsApi } from '../api/documentsApi';
import { Document } from '../types/document';
import { Fact } from '../types/fact';
import { UploadModal } from '../components/documents/UploadModal';
import { DocumentDetailModal } from '../components/documents/DocumentDetailModal';
import { LoadingState } from '../components/common/LoadingState';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  FileText,
  Upload,
  Search,
  CheckCircle2,
  AlertCircle,
  Play,
  Clock,
  Sparkles,
  ExternalLink,
} from 'lucide-react';


interface DocumentsPageProps {
  onSelectFact?: (fact: Fact) => void;
}

export const DocumentsPage: React.FC<DocumentsPageProps> = ({ onSelectFact }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [processingDocId, setProcessingDocId] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await documentsApi.listDocuments(1, 100);
      setDocuments(res.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch ingested documents list.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleProcessDocument = async (docId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      setProcessingDocId(docId);
      await documentsApi.processDocument(docId);
      await fetchDocuments();
    } catch (err: any) {
      alert(`Processing failed: ${err.message || 'Unknown error'}`);
    } finally {
      setProcessingDocId(null);
    }
  };

  const filteredDocs = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399',
              padding: '3px 8px',
              borderRadius: '4px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <CheckCircle2 size={12} />
            COMPLETED
          </span>
        );
      case 'PROCESSING':
        return (
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              backgroundColor: 'rgba(99, 102, 241, 0.2)',
              color: '#a5b4fc',
              padding: '3px 8px',
              borderRadius: '4px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Sparkles size={12} className="animate-spin" />
            PROCESSING
          </span>
        );
      case 'FAILED':
        return (
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              color: '#f87171',
              padding: '3px 8px',
              borderRadius: '4px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <AlertCircle size={12} />
            FAILED
          </span>
        );
      case 'UPLOADED':
      default:
        return (
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              backgroundColor: 'rgba(245, 158, 11, 0.15)',
              color: '#fbbf24',
              padding: '3px 8px',
              borderRadius: '4px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Clock size={12} />
            UPLOADED
          </span>
        );
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#f9fafb' }}>
            Document Management
          </h2>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            FactLens is not hard-coded to the starter dataset. Upload any text-based PDF to extract and reconcile facts. <em>(Best results with text-based PDFs.)</em>
          </div>
        </div>

        <button
          onClick={() => setIsUploadModalOpen(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'var(--accent-primary)',
            color: '#ffffff',
            border: 'none',
            padding: '0.6rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '13.5px',
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.35)',
          }}
        >
          <Upload size={16} />
          Upload PDF Document
        </button>
      </div>

      {error && <ErrorAlert message={error} onRetry={fetchDocuments} />}

      {/* Search & Filter Bar */}
      <div
        className="glass-panel"
        style={{
          padding: '0.75rem 1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
        }}
      >
        <Search size={16} color="var(--text-secondary)" />
        <input
          type="text"
          placeholder="Filter documents by filename or keyword..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            background: 'none',
            border: 'none',
            color: '#f9fafb',
            fontSize: '13.5px',
            width: '100%',
            outline: 'none',
          }}
        />
      </div>

      {/* Document List View */}
      {isLoading ? (
        <LoadingState message="Loading ingested document catalogue..." />
      ) : filteredDocs.length === 0 ? (
        <EmptyState
          title="No Documents Found"
          message={
            searchQuery
              ? 'No documents matched your search filter.'
              : 'Upload a financial PDF (such as an Annual Report or Investor Presentation) to start extraction.'
          }
          actionLabel="Upload PDF Now"
          onAction={() => setIsUploadModalOpen(true)}
        />
      ) : (
        <div className="glass-panel" style={{ overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                  <th style={{ padding: '12px 16px', width: '38%' }}>Document Filename</th>
                  <th style={{ padding: '12px 16px', width: '14%' }}>Pages</th>
                  <th style={{ padding: '12px 16px', width: '14%' }}>Facts</th>
                  <th style={{ padding: '12px 16px', width: '16%' }}>Status</th>
                  <th style={{ padding: '12px 16px', width: '18%', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc, idx) => (
                  <tr
                    key={doc.id}
                    onClick={() => setSelectedDocument(doc)}
                    style={{
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                      backgroundColor: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.015)',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease',
                    }}
                  >
                    <td style={{ padding: '12px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                        <FileText size={18} color="#818cf8" />
                        <div>
                          <div style={{ fontWeight: 600, color: '#f3f4f6' }}>{doc.filename}</div>
                          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                            Uploaded {new Date(doc.created_at).toLocaleDateString()} • Hash: {doc.file_hash.slice(0, 10)}...
                          </div>
                        </div>
                      </div>
                    </td>

                    <td style={{ padding: '12px 16px', color: '#f9fafb' }}>
                      <span style={{ fontWeight: 600 }}>{doc.page_count ?? doc.num_pages}</span> Pages
                    </td>

                    <td style={{ padding: '12px 16px', color: '#818cf8' }}>
                      <span style={{ fontWeight: 600 }}>{doc.fact_count ?? 0}</span> Facts
                    </td>

                    <td style={{ padding: '12px 16px' }}>
                      {getStatusBadge(doc.status)}
                    </td>

                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                      {doc.status === 'UPLOADED' || doc.status === 'PENDING' || !doc.fact_count ? (

                        <button
                          onClick={(e) => handleProcessDocument(doc.id, e)}
                          disabled={processingDocId === doc.id}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            backgroundColor: 'rgba(99, 102, 241, 0.2)',
                            color: '#a5b4fc',
                            border: '1px solid rgba(99, 102, 241, 0.4)',
                            padding: '4px 10px',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '12px',
                            fontWeight: 600,
                            cursor: processingDocId === doc.id ? 'not-allowed' : 'pointer',
                          }}
                        >
                          <Play size={12} />
                          {processingDocId === doc.id ? 'Processing...' : 'Process Facts'}
                        </button>
                      ) : (
                        <button
                          onClick={() => setSelectedDocument(doc)}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            background: 'none',
                            border: 'none',
                            color: '#818cf8',
                            fontSize: '12px',
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}
                        >
                          Inspect Facts
                          <ExternalLink size={11} />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onDocumentProcessed={() => {
          setIsUploadModalOpen(false);
          fetchDocuments();
        }}
      />

      {/* Document Detail & Extracted Facts Modal */}
      <DocumentDetailModal
        document={selectedDocument}
        onClose={() => setSelectedDocument(null)}
        onSelectFact={(fact) => {
          setSelectedDocument(null);
          onSelectFact?.(fact);
        }}
      />
    </div>
  );
};
