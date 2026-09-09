import React from 'react';
import { Fact } from '../../types/fact';
import { ContextComparisonResult } from '../../types/comparison';
import { CheckCircle2, XCircle, HelpCircle, Layers } from 'lucide-react';

interface ContextComparisonMatrixProps {
  factA: Fact;
  factB: Fact;
  contextComparison?: ContextComparisonResult | null;
}

interface DimensionRow {
  dimension: string;
  sourceA: string | number | null | undefined;
  sourceB: string | number | null | undefined;
  result: 'MATCH' | 'DIFFERENT' | 'UNKNOWN';
  detail?: string;
}

export const ContextComparisonMatrix: React.FC<ContextComparisonMatrixProps> = ({
  factA,
  factB,
  contextComparison,
}) => {
  // Helper to safely format values
  const fmt = (val: string | number | null | undefined) => {
    if (val === null || val === undefined || val === '') return '—';
    return String(val);
  };

  // Helper to determine match status if contextComparison is provided or fallback
  const getStatus = (
    valA: string | number | null | undefined,
    valB: string | number | null | undefined,
    explicitMatch?: boolean | null,
    explicitMismatch?: boolean | null
  ): 'MATCH' | 'DIFFERENT' | 'UNKNOWN' => {
    if (explicitMatch === true) return 'MATCH';
    if (explicitMismatch === true) return 'DIFFERENT';
    if (!valA || !valB || valA === '—' || valB === '—') return 'UNKNOWN';
    const strA = String(valA).trim().toLowerCase();
    const strB = String(valB).trim().toLowerCase();
    return strA === strB ? 'MATCH' : 'DIFFERENT';
  };

  const rows: DimensionRow[] = [
    {
      dimension: 'Entity',
      sourceA: factA.entity,
      sourceB: factB.entity,
      result: getStatus(factA.entity, factB.entity, contextComparison?.entity_match),
      detail: 'Target company or reporting organization',
    },
    {
      dimension: 'Attribute / Metric',
      sourceA: factA.attribute,
      sourceB: factB.attribute,
      result: getStatus(factA.attribute, factB.attribute, contextComparison?.attribute_match),
      detail: 'Financial or operational metric',
    },
    {
      dimension: 'Time Period',
      sourceA: factA.time_period || factA.fiscal_year || '—',
      sourceB: factB.time_period || factB.fiscal_year || '—',
      result: getStatus(
        factA.time_period || factA.fiscal_year,
        factB.time_period || factB.fiscal_year,
        contextComparison?.time_match
      ),
      detail: factA.quarter || factB.quarter ? `Q: ${fmt(factA.quarter)} vs ${fmt(factB.quarter)}` : undefined,
    },
    {
      dimension: 'Reporting Scope',
      sourceA: factA.scope || '—',
      sourceB: factB.scope || '—',
      result: getStatus(factA.scope, factB.scope, contextComparison?.scope_match),
      detail: 'Consolidated vs Standalone vs Segment',
    },
    {
      dimension: 'Geography',
      sourceA: factA.geography || '—',
      sourceB: factB.geography || '—',
      result: getStatus(factA.geography, factB.geography, contextComparison?.geography_match),
      detail: 'Jurisdiction or regional boundary',
    },
    {
      dimension: 'Currency & Unit',
      sourceA: [factA.currency, factA.unit].filter(Boolean).join(' ') || '—',
      sourceB: [factB.currency, factB.unit].filter(Boolean).join(' ') || '—',
      result: getStatus(
        [factA.currency, factA.unit].filter(Boolean).join(' '),
        [factB.currency, factB.unit].filter(Boolean).join(' '),
        contextComparison?.currency_match
      ),
      detail: 'Denominator and monetary standard',
    },
    {
      dimension: 'Definition / Context',
      sourceA: factA.definition || '—',
      sourceB: factB.definition || '—',
      result: getStatus(factA.definition, factB.definition),
      detail: 'Specific GAAP / non-GAAP / operational definition',
    },
    {
      dimension: 'Value Status',
      sourceA: factA.value_status || 'ACTUAL',
      sourceB: factB.value_status || 'ACTUAL',
      result: getStatus(factA.value_status || 'ACTUAL', factB.value_status || 'ACTUAL'),
      detail: 'Actual vs Guidance vs Restated vs Estimated',
    },
  ];

  const renderBadge = (res: 'MATCH' | 'DIFFERENT' | 'UNKNOWN') => {
    switch (res) {
      case 'MATCH':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 8px',
              borderRadius: '4px',
              fontSize: '11px',
              fontWeight: 700,
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399',
              border: '1px solid rgba(16, 185, 129, 0.3)',
            }}
          >
            <CheckCircle2 size={12} />
            MATCH
          </span>
        );
      case 'DIFFERENT':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 8px',
              borderRadius: '4px',
              fontSize: '11px',
              fontWeight: 700,
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              color: '#f87171',
              border: '1px solid rgba(239, 68, 68, 0.3)',
            }}
          >
            <XCircle size={12} />
            DIFFERENT
          </span>
        );
      case 'UNKNOWN':
      default:
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 8px',
              borderRadius: '4px',
              fontSize: '11px',
              fontWeight: 700,
              backgroundColor: 'rgba(156, 163, 175, 0.15)',
              color: '#9ca3af',
              border: '1px solid rgba(156, 163, 175, 0.25)',
            }}
          >
            <HelpCircle size={12} />
            UNKNOWN
          </span>
        );
    }
  };

  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Layers size={18} color="#818cf8" />
          <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
            Context Comparison Matrix
          </h4>
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          {contextComparison?.is_contextually_compatible ? (
            <span style={{ color: '#34d399', fontWeight: 600 }}>✓ All Critical Dimensions Match</span>
          ) : contextComparison?.scope_match === false ? (
            <span style={{ color: '#fbbf24', fontWeight: 600 }}>↔ Scope Difference Detected</span>
          ) : (
            <span>Dimensional Alignment Analysis</span>
          )}
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase' }}>
              <th style={{ padding: '8px 12px', width: '22%' }}>Dimension</th>
              <th style={{ padding: '8px 12px', width: '32%' }}>Source A ({factA.document_filename || 'Doc A'})</th>
              <th style={{ padding: '8px 12px', width: '32%' }}>Source B ({factB.document_filename || 'Doc B'})</th>
              <th style={{ padding: '8px 12px', width: '14%', textAlign: 'center' }}>Result</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr
                key={idx}
                style={{
                  borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                  backgroundColor: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.015)',
                }}
              >
                <td style={{ padding: '10px 12px', fontWeight: 600, color: '#f3f4f6' }}>
                  <div>{row.dimension}</div>
                  {row.detail && (
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 400, marginTop: '2px' }}>
                      {row.detail}
                    </div>
                  )}
                </td>
                <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>
                  <span style={{ color: '#f9fafb', fontWeight: 500 }}>{fmt(row.sourceA)}</span>
                </td>
                <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>
                  <span style={{ color: '#f9fafb', fontWeight: 500 }}>{fmt(row.sourceB)}</span>
                </td>
                <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                  {renderBadge(row.result)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {contextComparison?.dimension_differences && Object.keys(contextComparison.dimension_differences).length > 0 && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            fontSize: '12px',
            color: '#fde68a',
          }}
        >
          <strong>Contextual Nuances:</strong>{' '}
          {Object.entries(contextComparison.dimension_differences)
            .map(([dim, val]) => `${dim}: ${val}`)
            .join('; ')}
        </div>
      )}
    </div>

  );
};
