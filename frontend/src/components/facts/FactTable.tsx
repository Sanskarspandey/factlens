import React from 'react';
import { Fact } from '../../types/fact';
import { FactCard } from './FactCard';

interface FactTableProps {
  facts: Fact[];
  isLoading?: boolean;
}

export const FactTable: React.FC<FactTableProps> = ({ facts, isLoading }) => {
  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
        Loading grounded facts...
      </div>
    );
  }

  if (facts.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No facts found matching current filters.
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '1rem' }}>
      {facts.map((fact) => (
        <FactCard key={fact.id} fact={fact} />
      ))}
    </div>
  );
};
