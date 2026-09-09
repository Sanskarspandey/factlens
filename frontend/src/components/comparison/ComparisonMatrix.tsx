import React from 'react';
import { FactRelationship } from '../../types/comparison';
import { DiffViewer } from './DiffViewer';

interface ComparisonMatrixProps {
  relationships: FactRelationship[];
}

export const ComparisonMatrix: React.FC<ComparisonMatrixProps> = ({ relationships }) => {
  if (relationships.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No fact relationships found for the selected documents.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {relationships.map((rel) => (
        <DiffViewer key={rel.id} relationship={rel} />
      ))}
    </div>
  );
};
