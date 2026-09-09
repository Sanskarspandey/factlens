import React, { useState, useRef } from 'react';
import { documentsApi } from '../../api/documentsApi';
import { Document } from '../../types/document';
import {
  Upload,
  X,
  FileText,
  CheckCircle2,
  AlertCircle,
  Play,
  Database,
  ShieldCheck,
} from 'lucide-react';


interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDocumentProcessed: (doc: Document) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onDocumentProcessed,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [uploadedDoc, setUploadedDoc] = useState<Document | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processedDoc, setProcessedDoc] = useState<Document | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a valid PDF file. Other file formats are not supported.');
      return;
    }
    setError(null);
    setSelectedFile(file);
    setUploadedDoc(null);
    setProcessedDoc(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    try {
      setIsUploading(true);
      setError(null);
      const doc = await documentsApi.uploadPDF(selectedFile);
      setUploadedDoc(doc);
    } catch (err: any) {
      setError(err.message || 'Failed to upload PDF document.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcess = async () => {
    if (!uploadedDoc) return;
    try {
      setIsProcessing(true);
      setError(null);
      const res = await documentsApi.processDocument(uploadedDoc.id);
      setProcessedDoc(res.document);
      onDocumentProcessed(res.document);
    } catch (err: any) {
      setError(err.message || 'Failed to process document facts.');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetState = () => {
    setSelectedFile(null);
    setUploadedDoc(null);
    setProcessedDoc(null);
    setError(null);
    onClose();
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: '560px',
          maxWidth: '100%',
          padding: '1.75rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
          backgroundColor: '#0f172a',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                color: '#818cf8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Upload size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#f9fafb' }}>
                Ingest Source PDF
              </h3>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                Deterministic ingestion, fact extraction & vector indexing
              </div>
            </div>
          </div>

          <button
            onClick={resetState}
            style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Error banner */}
        {error && (
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              fontSize: '12.5px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <AlertCircle size={16} />
            <div>{error}</div>
          </div>
        )}

        {/* Upload Dropzone */}
        {!uploadedDoc && !processedDoc && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: `2px dashed ${isDragging ? 'var(--accent-primary)' : 'var(--border-color)'}`,
              backgroundColor: isDragging ? 'rgba(99, 102, 241, 0.08)' : 'rgba(255, 255, 255, 0.02)',
              borderRadius: 'var(--radius-md)',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.75rem',
              transition: 'all 0.2s ease',
            }}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept=".pdf,application/pdf"
              style={{ display: 'none' }}
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  handleFileSelected(e.target.files[0]);
                }
              }}
            />

            <FileText size={38} color={selectedFile ? '#818cf8' : '#64748b'} />

            {selectedFile ? (
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#f3f4f6' }}>
                  {selectedFile.name}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready to upload
                </div>
              </div>
            ) : (
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#f3f4f6' }}>
                  Drag & drop your PDF file here, or browse
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Annual Reports, Investor Presentations, ESG disclosures (PDF only)
                </div>
              </div>
            )}
          </div>
        )}

        {/* Uploaded state / Processing trigger */}
        {uploadedDoc && !processedDoc && (
          <div
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#f9fafb' }}>
                  {uploadedDoc.filename}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                  ID: {uploadedDoc.id.slice(0, 16)}... • SHA-256: {uploadedDoc.file_hash.slice(0, 12)}...
                </div>
              </div>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  backgroundColor: 'rgba(99, 102, 241, 0.2)',
                  color: '#a5b4fc',
                  padding: '3px 8px',
                  borderRadius: '4px',
                }}
              >
                {uploadedDoc.status}
              </span>
            </div>

            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              PDF stored successfully. Click "Process Document" to extract grounded facts, calculate embeddings, and index into ChromaDB.
            </p>

            <button
              onClick={handleProcess}
              disabled={isProcessing}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                backgroundColor: 'var(--accent-primary)',
                color: '#ffffff',
                border: 'none',
                padding: '0.65rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13.5px',
                fontWeight: 600,
                cursor: isProcessing ? 'not-allowed' : 'pointer',
                opacity: isProcessing ? 0.7 : 1,
              }}
            >
              <Play size={15} />
              {isProcessing ? 'Extracting & Grounding Facts...' : 'Process Document Pipeline'}
            </button>
          </div>
        )}

        {/* Processed Success Checklist */}
        {processedDoc && (
          <div
            style={{
              backgroundColor: 'rgba(16, 185, 129, 0.05)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: 'var(--radius-md)',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#34d399' }}>
              <CheckCircle2 size={18} />
              <h4 style={{ fontSize: '15px', fontWeight: 700 }}>
                Document Pipeline Complete
              </h4>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '13px', color: '#e2e8f0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={14} color="#34d399" />
                <span><strong>{processedDoc.page_count ?? processedDoc.num_pages}</strong> Pages Extracted</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={14} color="#34d399" />
                <span><strong>{processedDoc.fact_count ?? 0}</strong> Facts Extracted & Normalized</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldCheck size={14} color="#34d399" />
                <span>Evidence Grounded with Verbatim Quotes</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Database size={14} color="#34d399" />
                <span>Fact Embeddings Indexed in ChromaDB</span>
              </div>
            </div>

            <button
              onClick={resetState}
              style={{
                marginTop: '0.5rem',
                backgroundColor: 'var(--accent-primary)',
                color: '#ffffff',
                border: 'none',
                padding: '0.6rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              View Ingested Document
            </button>
          </div>
        )}

        {/* Action Button for Initial Upload */}
        {selectedFile && !uploadedDoc && !processedDoc && (
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button
              onClick={() => setSelectedFile(null)}
              style={{
                backgroundColor: 'transparent',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
                padding: '0.5rem 1rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={isUploading}
              style={{
                backgroundColor: 'var(--accent-primary)',
                color: '#ffffff',
                border: 'none',
                padding: '0.5rem 1.25rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                fontWeight: 600,
                cursor: isUploading ? 'not-allowed' : 'pointer',
                opacity: isUploading ? 0.7 : 1,
              }}
            >
              {isUploading ? 'Uploading PDF...' : 'Upload & Compute Hash'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
