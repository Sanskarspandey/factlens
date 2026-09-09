import React from 'react';
import { FactRelationship } from '../../types/comparison';
import { RelationshipBadge } from '../common/RelationshipBadge';

interface DiffViewerProps {
  relationship: FactRelationship;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ relationship }) => {
  const factA = relationship.fact_a || relationship.source_fact;
  const factB = relationship.fact_b || relationship.candidate_fact;

  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
      }}
    >
      {/* Relationship Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <RelationshipBadge relationship={relationship.relationship} size="sm" />
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Confidence: {(relationship.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Side-by-side Fact Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* Document A Fact */}
        <div style={{
          backgroundColor: 'rgba(0, 0, 0, 0.25)',
          padding: '1rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
        }}>
          <div style={{ fontSize: '12px', color: '#818cf8', fontWeight: 600, marginBottom: '4px' }}>
            {factA?.document_filename || 'Source Document A'} • Page {factA?.page_number}
          </div>
          <h5 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>{factA?.statement}</h5>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
            Normalized: <strong>{factA?.normalized_value?.toLocaleString()} {factA?.unit || ''}</strong> • Period: {factA?.time_period || 'N/A'}
          </div>
          <div style={{ fontSize: '12px', fontStyle: 'italic', color: 'var(--text-secondary)', borderLeft: '2px solid var(--accent-primary)', paddingLeft: '8px' }}>
            "{factA?.evidence_quote}"
          </div>
        </div>

        {/* Document B Fact */}
        <div style={{
          backgroundColor: 'rgba(0, 0, 0, 0.25)',
          padding: '1rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
        }}>
          <div style={{ fontSize: '12px', color: '#818cf8', fontWeight: 600, marginBottom: '4px' }}>
            {factB?.document_filename || 'Source Document B'} • Page {factB?.page_number}
          </div>
          <h5 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>{factB?.statement}</h5>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
            Normalized: <strong>{factB?.normalized_value?.toLocaleString()} {factB?.unit || ''}</strong> • Period: {factB?.time_period || 'N/A'}
          </div>
          <div style={{ fontSize: '12px', fontStyle: 'italic', color: 'var(--text-secondary)', borderLeft: '2px solid #a855f7', paddingLeft: '8px' }}>
            "{factB?.evidence_quote}"
          </div>
        </div>
      </div>

      {/* Rationale & Diagnosis */}
      <div style={{
        backgroundColor: 'rgba(255, 255, 255, 0.03)',
        padding: '0.85rem 1rem',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-color)',
      }}>
        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
          Reconciliation Rationale
        </span>
        <p style={{ fontSize: '13px', color: 'var(--text-primary)', marginTop: '4px' }}>
          {relationship.rationale}
        </p>
      </div>
    </div>
  );
};
