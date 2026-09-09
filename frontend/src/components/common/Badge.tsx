import React from 'react';
import { RelationshipType } from '../../types/comparison';

interface BadgeProps {
  label: string;
  variant?: 'corroborated' | 'contradicted' | 'contextual' | 'uncertain' | 'neutral' | 'info';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({ label, variant = 'neutral', size = 'md' }) => {
  const styles: Record<string, { bg: string; color: string; border: string }> = {
    corroborated: {
      bg: 'var(--color-corroborated-bg)',
      color: 'var(--color-corroborated)',
      border: 'var(--color-corroborated-border)',
    },
    contradicted: {
      bg: 'var(--color-contradicted-bg)',
      color: 'var(--color-contradicted)',
      border: 'var(--color-contradicted-border)',
    },
    contextual: {
      bg: 'var(--color-contextual-bg)',
      color: 'var(--color-contextual)',
      border: 'var(--color-contextual-border)',
    },
    uncertain: {
      bg: 'var(--color-uncertain-bg)',
      color: 'var(--color-uncertain)',
      border: 'var(--color-uncertain-border)',
    },
    neutral: {
      bg: 'rgba(156, 163, 175, 0.1)',
      color: 'var(--text-secondary)',
      border: 'rgba(156, 163, 175, 0.2)',
    },
    info: {
      bg: 'rgba(99, 102, 241, 0.1)',
      color: '#818cf8',
      border: 'rgba(99, 102, 241, 0.3)',
    },
  };

  const current = styles[variant] || styles.neutral;
  const isSm = size === 'sm';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: isSm ? '2px 8px' : '4px 12px',
        borderRadius: 'var(--radius-full)',
        fontSize: isSm ? '11px' : '12px',
        fontWeight: 600,
        backgroundColor: current.bg,
        color: current.color,
        border: `1px solid ${current.border}`,
        letterSpacing: '0.02em',
        textTransform: 'uppercase',
      }}
    >
      {label}
    </span>
  );
};

export const getRelationshipBadge = (rel: RelationshipType) => {
  switch (rel) {
    case 'CORROBORATED':
      return <Badge label="CORROBORATED" variant="corroborated" />;
    case 'CONTRADICTED':
      return <Badge label="CONTRADICTED" variant="contradicted" />;
    case 'CONTEXTUALLY_DIFFERENT':
      return <Badge label="CONTEXTUALLY DIFFERENT" variant="contextual" />;
    case 'UNCERTAIN':
      return <Badge label="UNCERTAIN" variant="uncertain" />;
  }
};
