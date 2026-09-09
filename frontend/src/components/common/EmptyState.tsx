import React from 'react';
import { Inbox } from 'lucide-react';

export interface EmptyStateProps {
  title?: string;
  description?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No records found',
  description,
  message,
  actionLabel,
  onAction,
  icon = <Inbox size={36} style={{ color: 'var(--text-muted)' }} />,
}) => {
  const displayDesc = description || message || 'There are currently no items matching your criteria.';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 2rem',
        textAlign: 'center',
        borderRadius: 'var(--radius-lg)',
        border: '1px dashed var(--border-color)',
        backgroundColor: 'rgba(17, 24, 39, 0.4)',
        gap: '0.75rem',
      }}
    >
      <div style={{ marginBottom: '0.25rem' }}>{icon}</div>
      <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</h3>
      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '400px' }}>{displayDesc}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          style={{
            marginTop: '0.5rem',
            backgroundColor: 'var(--accent-primary)',
            color: '#ffffff',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
