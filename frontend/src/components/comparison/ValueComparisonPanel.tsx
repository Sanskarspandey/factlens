import React from 'react';
import { ValueComparisonResult } from '../../types/comparison';
import { Fact } from '../../types/fact';
import { Calculator, CheckCircle, AlertCircle, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export interface ValueComparisonPanelProps {
  valueComp?: ValueComparisonResult;
  valueComparison?: ValueComparisonResult;
  factA?: Fact;
  factB?: Fact;
  currency?: string;
}

export const ValueComparisonPanel: React.FC<ValueComparisonPanelProps> = ({
  valueComp,
  valueComparison,
  factA,
  factB,
  currency,
}) => {
  const comp = valueComparison || valueComp;

  if (!comp) {
    return (
      <div className="glass-panel" style={{ padding: '1.25rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        No numeric value comparison data available.
      </div>
    );
  }

  const {
    source_formatted,
    source_raw,
    source_normalized,
    candidate_formatted,
    candidate_raw,
    candidate_normalized,
    absolute_difference,
    percentage_difference,
    direction,
    within_tolerance,
    match_tolerance,
  } = comp;

  const displayCurrency = currency || factA?.currency || factB?.currency || '';
  const isNumericAvailable =
    source_normalized !== undefined &&
    candidate_normalized !== undefined &&
    source_normalized !== null &&
    candidate_normalized !== null;

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#818cf8',
          }}>
            <Calculator size={18} />
          </div>
          <h3 style={{ fontSize: '15px', fontWeight: 700 }}>Deterministic Value Comparison</h3>
        </div>

        {isNumericAvailable && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '12px',
              fontWeight: 700,
              backgroundColor: within_tolerance ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
              color: within_tolerance ? '#10b981' : '#ef4444',
              border: `1px solid ${within_tolerance ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            }}
          >
            {within_tolerance ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
            {within_tolerance ? `Within ${(match_tolerance * 100).toFixed(0)}% Tolerance` : 'Material Discrepancy'}
          </div>
        )}
      </div>

      {/* Side by side values */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1rem',
        marginBottom: '1.25rem',
      }}>
        {/* Source A */}
        <div style={{
          padding: '1rem',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--border-color)',
        }}>
          <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '4px' }}>
            Source Fact Value ({factA?.document_filename || 'Source A'})
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#f9fafb', fontFamily: 'var(--font-mono)' }}>
            {source_formatted || source_raw || factA?.raw_value || 'N/A'}
          </div>
          {source_normalized !== undefined && source_normalized !== null && (
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
              Normalized: {source_normalized.toLocaleString()} {displayCurrency}
            </div>
          )}
        </div>

        {/* Source B */}
        <div style={{
          padding: '1rem',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--border-color)',
        }}>
          <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '4px' }}>
            Candidate Fact Value ({factB?.document_filename || 'Source B'})
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#f9fafb', fontFamily: 'var(--font-mono)' }}>
            {candidate_formatted || candidate_raw || factB?.raw_value || 'N/A'}
          </div>
          {candidate_normalized !== undefined && candidate_normalized !== null && (
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>
              Normalized: {candidate_normalized.toLocaleString()} {displayCurrency}
            </div>
          )}
        </div>
      </div>

      {/* Arithmetic Breakdown */}
      {isNumericAvailable ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '0.75rem',
          padding: '1rem',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-color)',
        }}>
          <div>
            <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>Absolute Diff</div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#f9fafb', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
              {absolute_difference !== undefined ? absolute_difference.toLocaleString() : 'N/A'}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>Percentage Diff</div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: within_tolerance ? '#10b981' : '#ef4444', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
              {percentage_difference !== undefined ? `${percentage_difference.toFixed(2)}%` : 'N/A'}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>Configured Tolerance</div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#9ca3af', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
              {(match_tolerance * 100).toFixed(1)}%
            </div>
          </div>
          <div>
            <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>Direction</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '14px', fontWeight: 700, color: '#f9fafb', marginTop: '2px' }}>
              {direction === 'INCREASE' && <ArrowUpRight size={15} style={{ color: '#ef4444' }} />}
              {direction === 'DECREASE' && <ArrowDownRight size={15} style={{ color: '#f59e0b' }} />}
              {direction === 'EQUAL' && <Minus size={15} style={{ color: '#10b981' }} />}
              {direction || 'N/A'}
            </div>
          </div>
        </div>
      ) : (
        <div style={{ fontSize: '13px', color: '#a855f7', fontStyle: 'italic', padding: '0.5rem' }}>
          Exact numeric arithmetic unavailable (one or both values are qualitative or missing).
        </div>
      )}
    </div>
  );
};
