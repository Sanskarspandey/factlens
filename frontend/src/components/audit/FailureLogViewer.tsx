import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Badge } from '../common/Badge';

export interface ExtractionFailureLog {
  id: string;
  document_filename: string;
  page_number?: number;
  stage: string;
  error_type: string;
  error_message: string;
  raw_content?: string;
  created_at: string;
}

interface FailureLogViewerProps {
  logs: ExtractionFailureLog[];
}

export const FailureLogViewer: React.FC<FailureLogViewerProps> = ({ logs }) => {
  if (logs.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No extraction failures or ungrounded anomalies recorded.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {logs.map((log) => (
        <div
          key={log.id}
          className="glass-panel"
          style={{
            padding: '1.25rem',
            borderLeft: '4px solid var(--color-contradicted)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle size={18} color="var(--color-contradicted)" />
              <span style={{ fontWeight: 600, fontSize: '14px' }}>{log.error_type}</span>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>• {log.document_filename} (Page {log.page_number || 'N/A'})</span>
            </div>
            <Badge label={log.stage} variant="neutral" size="sm" />
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{log.error_message}</p>

          {log.raw_content && (
            <div style={{
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              padding: '0.5rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '12px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-secondary)',
              maxHeight: '80px',
              overflowY: 'auto',
            }}>
              {log.raw_content}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
