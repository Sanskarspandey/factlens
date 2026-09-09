import React from 'react';
import { FactRelationship } from '../../types/comparison';
import { CheckCircle2, AlertTriangle, Info, Scale } from 'lucide-react';
import { RelationshipBadge } from '../common/RelationshipBadge';

interface WhyThisVerdictPanelProps {
  relationship: FactRelationship;
}

export const WhyThisVerdictPanel: React.FC<WhyThisVerdictPanelProps> = ({ relationship }) => {
  const relType = relationship.relationship;
  const valComp = relationship.value_comparison;
  const ctxComp = relationship.context_comparison;
  const checklist = relationship.verdict_checklist || [];

  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
        border: '1px solid rgba(99, 102, 241, 0.3)',
        backgroundColor: 'rgba(15, 23, 42, 0.85)',
      }}
    >
      {/* Panel Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '0.85rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '6px',
              backgroundColor: 'rgba(99, 102, 241, 0.2)',
              color: '#818cf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Scale size={16} />
          </div>
          <div>
            <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
              WHY THIS VERDICT?
            </h4>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              Deterministic Rule & Context Execution Audit Trail
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Engine: {relationship.reasoning_method || 'DETERMINISTIC'}
          </span>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 600,
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399',
              padding: '2px 8px',
              borderRadius: '4px',
            }}
          >
            Confidence: {(relationship.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Structured Deterministic Checklist */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
        {checklist.length > 0 ? (
          checklist.map((item, idx) => {
            const isPass = item.status === 'PASS';
            const isWarn = item.status === 'WARN';
            return (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  padding: '0.65rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: isPass
                    ? 'rgba(16, 185, 129, 0.04)'
                    : isWarn
                    ? 'rgba(245, 158, 11, 0.06)'
                    : 'rgba(255, 255, 255, 0.02)',
                  border: isPass
                    ? '1px solid rgba(16, 185, 129, 0.15)'
                    : isWarn
                    ? '1px solid rgba(245, 158, 11, 0.25)'
                    : '1px solid var(--border-color)',
                  fontSize: '13px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {isPass ? (
                    <CheckCircle2 size={16} color="#34d399" />
                  ) : isWarn ? (
                    <AlertTriangle size={16} color="#fbbf24" />
                  ) : (
                    <Info size={16} color="#818cf8" />
                  )}
                  <span style={{ fontWeight: 600, color: isPass ? '#f3f4f6' : isWarn ? '#fef3c7' : '#e2e8f0' }}>
                    {item.label}
                  </span>
                </div>

                {item.detail && (
                  <span
                    style={{
                      fontSize: '12px',
                      color: isPass ? '#a7f3d0' : isWarn ? '#fde68a' : 'var(--text-secondary)',
                      fontFamily: item.detail.includes('%') || item.detail.includes('₹') || item.detail.includes('$') ? 'var(--font-mono)' : 'inherit',
                    }}
                  >
                    {item.detail}
                  </span>
                )}
              </div>
            );
          })
        ) : (
          /* Fallback if checklist not populated */
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', padding: '0.5rem' }}>
            {relationship.rationale}
          </div>
        )}
      </div>

      {/* Quantitative & Dimensional Variance Callout */}
      {relType === 'CONTRADICTED' && valComp && (
        <div
          style={{
            backgroundColor: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            padding: '0.85rem 1rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
            fontSize: '12.5px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f87171', fontWeight: 700 }}>
            <AlertTriangle size={15} />
            MATERIAL NUMERICAL DISAGREEMENT DETECTED
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem', marginTop: '0.25rem', fontFamily: 'var(--font-mono)' }}>
            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Fact A:</span>
              <div style={{ color: '#f9fafb', fontWeight: 600 }}>{valComp.source_formatted || valComp.source_raw}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Fact B:</span>
              <div style={{ color: '#f9fafb', fontWeight: 600 }}>{valComp.candidate_formatted || valComp.candidate_raw}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Difference:</span>
              <div style={{ color: '#f87171', fontWeight: 700 }}>{valComp.percentage_difference?.toFixed(2)}%</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Tolerance:</span>
              <div style={{ color: '#94a3b8', fontWeight: 600 }}>{(valComp.match_tolerance * 100).toFixed(2)}%</div>
            </div>
          </div>
        </div>
      )}

      {relType === 'CONTEXTUALLY_DIFFERENT' && ctxComp && Object.keys(ctxComp.dimension_differences || {}).length > 0 && (
        <div
          style={{
            backgroundColor: 'rgba(168, 85, 247, 0.08)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            borderRadius: 'var(--radius-md)',
            padding: '0.85rem 1rem',
            fontSize: '12.5px',
          }}
        >
          <div style={{ color: '#c084fc', fontWeight: 700, marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Info size={15} />
            CONTEXTUAL DIVERGENCE ANALYSIS
          </div>
          <div style={{ color: '#e2e8f0', lineHeight: 1.5 }}>
            {Object.entries(ctxComp.dimension_differences).map(([k, v], i) => (
              <div key={i}>
                • <strong style={{ textTransform: 'capitalize' }}>{k.replace('_', ' ')}:</strong> {v}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Final Determination Verdict Block */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'rgba(0, 0, 0, 0.4)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          padding: '1rem 1.25rem',
        }}
      >
        <div>
          <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
            Final System Determination
          </span>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            {relationship.rationale}
          </div>
        </div>
        <RelationshipBadge relationship={relType} size="lg" />
      </div>
    </div>
  );
};
