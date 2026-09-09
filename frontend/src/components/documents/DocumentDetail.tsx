import React from 'react';
import { Document } from '../../types/document';
import { Card } from '../common/Card';

interface DocumentDetailProps {
  document: Document;
}

export const DocumentDetail: React.FC<DocumentDetailProps> = ({ document }) => {
  return (
    <Card title={document.filename} subtitle={`Document ID: ${document.id}`}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '1rem' }}>
        <div>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Status</span>
          <p style={{ fontWeight: 600 }}>{document.status}</p>
        </div>
        <div>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Pages</span>
          <p style={{ fontWeight: 600 }}>{document.num_pages}</p>
        </div>
        <div>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Hash (SHA-256)</span>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', wordBreak: 'break-all' }}>{document.file_hash}</p>
        </div>
      </div>
    </Card>
  );
};
