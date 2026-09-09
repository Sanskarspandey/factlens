import React from 'react';
import { Fact } from '../../types/fact';
import { HelpCircle } from 'lucide-react';
import { Badge } from '../common/Badge';

interface UncertaintyCardProps {
  fact: Fact;
}

export const UncertaintyCard: React.FC<UncertaintyCardProps> = ({ fact }) => {
  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.25rem',
        borderLeft: '4px solid var(--color-uncertain)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <HelpCircle size={18} color="var(--color-uncertain)" />
          <span style={{ fontWeight: 600, fontSize: '14px' }}>Uncertain / Ambiguous Extraction</span>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            • {fact.document_filename || 'Doc'} (Page {fact.page_number})
          </span>
        </div>
        <Badge label={`Confidence ${(fact.confidence * 100).toFixed(0)}%`} variant="uncertain" size="sm" />
      </div>

      <p style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>
        {fact.statement}
      </p>

      {fact.uncertainty_notes && (
        <div style={{
          backgroundColor: 'var(--color-uncertain-bg)',
          border: '1px solid var(--color-uncertain-border)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.5rem 0.75rem',
          fontSize: '13px',
          color: 'var(--text-primary)',
        }}>
          <strong>Reason for uncertainty:</strong> {fact.uncertainty_notes}
        </div>
      )}

      <div style={{ fontSize: '12px', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
        Evidence quote: "{fact.evidence_quote}"
      </div>
    </div>
  );
};
