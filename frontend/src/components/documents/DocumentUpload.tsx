import React, { useState } from 'react';
import { UploadCloud, File } from 'lucide-react';

import { Button } from '../common/Button';

interface DocumentUploadProps {
  onUploadSuccess?: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    try {
      // API call placeholder for subsequent implementation
      setTimeout(() => {
        setIsUploading(false);
        setSelectedFile(null);
        if (onUploadSuccess) onUploadSuccess();
      }, 1000);
    } catch (err) {
      setIsUploading(false);
    }
  };

  return (
    <div
      style={{
        border: '2px dashed var(--border-color)',
        borderRadius: 'var(--radius-lg)',
        padding: '2.5rem',
        textAlign: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.02)',
        transition: 'all 0.2s ease',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--accent-primary)',
        }}>
          <UploadCloud size={28} />
        </div>
        <div>
          <h4 style={{ fontSize: '16px', fontWeight: 600 }}>Upload Arbitrary PDF Documents</h4>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Supports any PDF file layout (10-K, ESG reports, research papers, earnings releases)
          </p>
        </div>
        <input
          type="file"
          id="pdf-upload"
          accept="application/pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <label htmlFor="pdf-upload">
          <Button variant="secondary" size="md" type="button" onClick={() => document.getElementById('pdf-upload')?.click()}>
            Browse PDF File
          </Button>
        </label>
        {selectedFile && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
            <File size={16} color="var(--accent-primary)" />
            <span style={{ fontSize: '14px', color: 'var(--text-primary)' }}>{selectedFile.name}</span>
            <Button size="sm" onClick={handleUpload} disabled={isUploading}>
              {isUploading ? 'Processing...' : 'Upload & Ingest'}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
