import React from 'react';
import { RelationshipType } from '../../types/comparison';
import { CheckCircle2, AlertOctagon, ArrowLeftRight, HelpCircle } from 'lucide-react';

interface RelationshipBadgeProps {
  relationship: RelationshipType;
  size?: 'sm' | 'md' | 'lg';
  showDescription?: boolean;
}

export const RelationshipBadge: React.FC<RelationshipBadgeProps> = ({
  relationship,
  size = 'md',
  showDescription = false,
}) => {
  const configs: Record<
    RelationshipType,
    {
      label: string;
      color: string;
      bg: string;
      border: string;
      icon: React.ReactNode;
      description: string;
    }
  > = {
    CORROBORATED: {
      label: 'CORROBORATED',
      color: '#10b981',
      bg: 'rgba(16, 185, 129, 0.12)',
      border: 'rgba(16, 185, 129, 0.35)',
      icon: <CheckCircle2 size={size === 'lg' ? 20 : size === 'md' ? 16 : 14} />,
      description: 'Both sources report consistent values for the same metric, fiscal period, and reporting scope.',
    },
    CONTRADICTED: {
      label: 'CONTRADICTED',
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.12)',
      border: 'rgba(239, 68, 68, 0.35)',
      icon: <AlertOctagon size={size === 'lg' ? 20 : size === 'md' ? 16 : 14} />,
      description: 'Both sources describe the same context, but report mutually exclusive, divergent numerical values.',
    },
    CONTEXTUALLY_DIFFERENT: {
      label: 'CONTEXTUALLY DIFFERENT',
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.12)',
      border: 'rgba(245, 158, 11, 0.35)',
      icon: <ArrowLeftRight size={size === 'lg' ? 20 : size === 'md' ? 16 : 14} />,
      description: 'The values differ due to differing reporting scopes (Consolidated vs Standalone), periods, or accounting definitions.',
    },
    UNCERTAIN: {
      label: 'UNCERTAIN',
      color: '#a855f7',
      bg: 'rgba(168, 85, 247, 0.12)',
      border: 'rgba(168, 85, 247, 0.35)',
      icon: <HelpCircle size={size === 'lg' ? 20 : size === 'md' ? 16 : 14} />,
      description: 'Insufficient grounded evidence, unparseable numeric values, or ambiguous metric definitions.',
    },
  };

  const config = configs[relationship] || configs.UNCERTAIN;

  const fontSizes = {
    sm: '11.5px',
    md: '13px',
    lg: '15px',
  };

  const paddings = {
    sm: '3px 8px',
    md: '5px 12px',
    lg: '8px 16px',
  };

  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', gap: '4px' }}>
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: config.bg,
          color: config.color,
          border: `1px solid ${config.border}`,
          borderRadius: 'var(--radius-full)',
          padding: paddings[size],
          fontSize: fontSizes[size],
          fontWeight: 700,
          letterSpacing: '0.02em',
          width: 'fit-content',
        }}
      >
        {config.icon}
        {config.label}
      </span>
      {showDescription && (
        <span style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px', lineHeight: 1.4 }}>
          {config.description}
        </span>
      )}
    </div>
  );
};
