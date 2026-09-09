import React from 'react';
import { Fact } from '../../types/fact';
import { Badge } from '../common/Badge';
import { Quote, AlertCircle } from 'lucide-react';

interface FactCardProps {
  fact: Fact;
}

export const FactCard: React.FC<FactCardProps> = ({ fact }) => {
  const isUncertain = fact.status === 'UNCERTAIN' || fact.confidence < 0.8 || !!fact.uncertainty_notes;

  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
        borderLeft: isUncertain ? '4px solid var(--color-uncertain)' : '4px solid var(--accent-primary)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600 }}>
            {fact.document_filename || `Doc: ${fact.document_id.slice(0, 8)}`} • Page {fact.page_number}
          </span>
          <h4 style={{ fontSize: '15px', fontWeight: 600, marginTop: '4px', color: 'var(--text-primary)' }}>
            {fact.statement}
          </h4>
        </div>
        <Badge
          label={fact.status}
          variant={fact.status === 'VERIFIED' ? 'corroborated' : fact.status === 'UNCERTAIN' ? 'uncertain' : 'info'}
          size="sm"
        />
      </div>

      {/* Semantic Tags & Normalization */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', fontSize: '12px' }}>
        {fact.entity && (
          <span style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '2px 8px', borderRadius: '4px' }}>
            Entity: <strong>{fact.entity}</strong>
          </span>
        )}
        {fact.attribute && (
          <span style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '2px 8px', borderRadius: '4px' }}>
            Metric: <strong>{fact.attribute}</strong>
          </span>
        )}
        {fact.normalized_value !== undefined && (
          <span style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#818cf8', padding: '2px 8px', borderRadius: '4px' }}>
            Normalized: <strong>{fact.normalized_value.toLocaleString()} {fact.unit || ''}</strong>
          </span>
        )}
        {fact.time_period && (
          <span style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--color-contextual)', padding: '2px 8px', borderRadius: '4px' }}>
            Period: <strong>{fact.time_period}</strong>
          </span>
        )}
      </div>

      {/* Grounding Evidence Quote */}
      <div style={{
        backgroundColor: 'rgba(0, 0, 0, 0.25)',
        borderLeft: '2px solid var(--border-color)',
        padding: '0.5rem 0.75rem',
        borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
        display: 'flex',
        gap: '0.5rem',
        fontSize: '13px',
        color: 'var(--text-secondary)',
        fontStyle: 'italic',
      }}>
        <Quote size={16} style={{ flexShrink: 0, marginTop: '2px', opacity: 0.6 }} />
        <span>"{fact.evidence_quote}"</span>
      </div>

      {/* Uncertainty preserved note */}
      {fact.uncertainty_notes && (
        <div style={{
          backgroundColor: 'var(--color-uncertain-bg)',
          border: '1px solid var(--color-uncertain-border)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '12px',
          color: 'var(--color-uncertain)',
        }}>
          <AlertCircle size={14} />
          <span>Uncertainty Note: {fact.uncertainty_notes}</span>
        </div>
      )}
    </div>
  );
};
