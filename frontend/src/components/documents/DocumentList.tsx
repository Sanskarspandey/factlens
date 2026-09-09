import React from 'react';
import { Document } from '../../types/document';
import { FileText, Trash2, ArrowRight } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

interface DocumentListProps {
  documents: Document[];
  onSelectDocument?: (doc: Document) => void;
  onDeleteDocument?: (id: string) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onSelectDocument,
  onDeleteDocument,
}) => {
  if (documents.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No documents uploaded yet. Upload arbitrary PDFs to begin extracting facts.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="glass-panel"
          style={{
            padding: '1rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            transition: 'border-color 0.15s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)',
            }}>
              <FileText size={20} />
            </div>
            <div>
              <h4 style={{ fontSize: '15px', fontWeight: 600 }}>{doc.filename}</h4>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                {doc.num_pages} pages • {(doc.file_size / (1024 * 1024)).toFixed(2)} MB • {doc.fact_count || 0} facts extracted
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Badge label={doc.status} variant={doc.status === 'PROCESSED' ? 'corroborated' : 'neutral'} size="sm" />
            {onSelectDocument && (
              <Button variant="secondary" size="sm" onClick={() => onSelectDocument(doc)}>
                View Facts <ArrowRight size={14} />
              </Button>
            )}
            {onDeleteDocument && (
              <Button variant="danger" size="sm" onClick={() => onDeleteDocument(doc.id)}>
                <Trash2 size={14} />
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
