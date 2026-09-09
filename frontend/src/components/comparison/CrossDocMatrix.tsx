import React, { useMemo } from 'react';
import { Fact } from '../../types/fact';
import { FactRelationship } from '../../types/comparison';
import { RelationshipBadge } from '../common/RelationshipBadge';
import { Table } from 'lucide-react';

interface CrossDocMatrixProps {
  facts: Fact[];
  relationships: FactRelationship[];
  onSelectComparison?: (rel: FactRelationship) => void;
  onSelectFact?: (fact: Fact) => void;
}

interface MetricRow {
  key: string;
  entity: string;
  attribute: string;
  period: string;
  scope: string;
  valuesByDoc: Record<string, { fact: Fact; displayValue: string }>;
  relationship?: FactRelationship;
}

export const CrossDocMatrix: React.FC<CrossDocMatrixProps> = ({
  facts,
  relationships,
  onSelectComparison,
  onSelectFact,
}) => {
  // Extract all unique documents
  const documents = useMemo(() => {
    const docMap = new Map<string, string>();
    facts.forEach((f) => {
      const docName = f.document_filename || `Doc ${f.document_id?.slice(0, 6)}`;
      docMap.set(f.document_id, docName);
    });
    return Array.from(docMap.entries()).map(([id, name]) => ({ id, name }));
  }, [facts]);

  // Group facts by metric key (Entity + Attribute + Period + Scope)
  const rows = useMemo(() => {
    const rowMap = new Map<string, MetricRow>();

    facts.forEach((f) => {
      const period = f.time_period || f.fiscal_year || 'FY';
      const scope = f.scope || 'Consolidated';
      const entity = f.entity || 'Entity';
      const attribute = f.attribute || 'Metric';
      const key = `${entity}::${attribute}::${period}::${scope}`.toLowerCase();

      if (!rowMap.has(key)) {
        rowMap.set(key, {
          key,
          entity,
          attribute,
          period,
          scope,
          valuesByDoc: {},
        });
      }

      const row = rowMap.get(key)!;
      let displayVal = f.raw_value;
      if (f.normalized_value !== null && f.normalized_value !== undefined) {
        displayVal = `${f.currency ? f.currency + ' ' : ''}${f.normalized_value.toLocaleString()} ${f.unit || ''}`.trim();
      }

      row.valuesByDoc[f.document_id] = {
        fact: f,
        displayValue: displayVal || f.statement || '—',
      };
    });

    // Attach relationships if we have pairs
    relationships.forEach((rel) => {
      const factA = rel.fact_a || rel.source_fact;
      const factB = rel.fact_b || rel.candidate_fact;
      if (!factA || !factB) return;
      const period = factA.time_period || factA.fiscal_year || 'FY';
      const scope = factA.scope || 'Consolidated';
      const entity = factA.entity || 'Entity';
      const attribute = factA.attribute || 'Metric';
      const key = `${entity}::${attribute}::${period}::${scope}`.toLowerCase();
      const row = rowMap.get(key);
      if (row && !row.relationship) {
        row.relationship = rel;
      }
    });

    return Array.from(rowMap.values());
  }, [facts, relationships]);

  if (facts.length === 0) {
    return null;
  }

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
          <Table size={18} color="#818cf8" />
          <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
            Cross-Document Evaluation Matrix
          </h4>
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          Comparing metrics across <strong>{documents.length}</strong> ingested document{documents.length > 1 ? 's' : ''}
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase' }}>
              <th style={{ padding: '10px 12px', width: '26%' }}>Metric / Fact Context</th>
              {documents.map((doc) => (
                <th
                  key={doc.id}
                  style={{
                    padding: '10px 12px',
                    maxWidth: '180px',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                  title={doc.name}
                >
                  {doc.name}
                </th>
              ))}
              <th style={{ padding: '10px 12px', textAlign: 'center', width: '18%' }}>Reconciliation</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr
                key={row.key}
                style={{
                  borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                  backgroundColor: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.015)',
                }}
              >
                {/* Metric Info */}
                <td style={{ padding: '10px 12px' }}>
                  <div style={{ fontWeight: 700, color: '#f3f4f6', fontSize: '13.5px' }}>
                    {row.attribute}
                  </div>
                  <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)', marginTop: '2px', display: 'flex', gap: '6px' }}>
                    <span>{row.entity}</span>
                    <span>•</span>
                    <span style={{ color: '#818cf8' }}>{row.period}</span>
                    <span>•</span>
                    <span>{row.scope}</span>
                  </div>
                </td>

                {/* Values per Document */}
                {documents.map((doc) => {
                  const entry = row.valuesByDoc[doc.id];
                  return (
                    <td key={doc.id} style={{ padding: '10px 12px' }}>
                      {entry ? (
                        <div
                          onClick={() => onSelectFact?.(entry.fact)}
                          style={{
                            cursor: 'pointer',
                            display: 'inline-block',
                            backgroundColor: 'rgba(255, 255, 255, 0.04)',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            border: '1px solid var(--border-color)',
                            transition: 'all 0.15s ease',
                          }}
                        >
                          <span style={{ fontWeight: 600, color: '#e0e7ff' }}>
                            {entry.displayValue}
                          </span>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                            Page {entry.fact.page_number}
                          </div>
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>—</span>
                      )}
                    </td>
                  );
                })}

                {/* Relationship result */}
                <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                  {row.relationship ? (
                    <div
                      onClick={() => onSelectComparison?.(row.relationship!)}
                      style={{ cursor: onSelectComparison ? 'pointer' : 'default', display: 'inline-block' }}
                      title="Click to view detailed comparison"
                    >
                      <RelationshipBadge relationship={row.relationship.relationship} size="sm" />
                    </div>
                  ) : Object.keys(row.valuesByDoc).length > 1 ? (
                    <span
                      style={{
                        fontSize: '11px',
                        color: 'var(--text-secondary)',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        padding: '3px 7px',
                        borderRadius: '4px',
                      }}
                    >
                      Multiple Sources
                    </span>
                  ) : (
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Single Source</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
