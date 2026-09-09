import React, { useState, useEffect } from 'react';
import { comparisonApi } from '../api/comparisonApi';
import { factsApi } from '../api/factsApi';
import { Fact } from '../types/fact';
import { FactRelationship } from '../types/comparison';
import { RelationshipBadge } from '../components/common/RelationshipBadge';
import { ValueComparisonPanel } from '../components/comparison/ValueComparisonPanel';
import { ContextComparisonMatrix } from '../components/comparison/ContextComparisonMatrix';
import { EvidenceComparisonPanel } from '../components/comparison/EvidenceComparisonPanel';
import { WhyThisVerdictPanel } from '../components/comparison/WhyThisVerdictPanel';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  GitCompare,
  RotateCcw,
} from 'lucide-react';

interface ComparisonPageProps {
  initialFactAId?: string | null;
  initialFactBId?: string | null;
  initialRelationship?: FactRelationship | null;
}

export const ComparisonPage: React.FC<ComparisonPageProps> = ({
  initialFactAId,
  initialFactBId,
  initialRelationship,
}) => {
  const [allFacts, setAllFacts] = useState<Fact[]>([]);
  const [factAId, setFactAId] = useState<string>(initialFactAId || '');
  const [factBId, setFactBId] = useState<string>(initialFactBId || '');
  const [comparisonResult, setComparisonResult] = useState<FactRelationship | null>(
    initialRelationship || null
  );
  const [isComparing, setIsComparing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load available facts for selection
  useEffect(() => {
    const fetchFacts = async () => {
      try {
        const res = await factsApi.listFacts({ limit: 300 });
        setAllFacts(res.items || []);

        // If initial ids provided and we don't have comparisonResult yet, run compare
        if (initialFactAId && initialFactBId && !initialRelationship) {
          runComparison(initialFactAId, initialFactBId);
        }
      } catch (err: any) {
        console.error('Failed to load facts for comparison selector:', err);
      }
    };

    fetchFacts();
  }, [initialFactAId, initialFactBId]);

  useEffect(() => {
    if (initialRelationship) {
      setComparisonResult(initialRelationship);
      const aId = initialRelationship.fact_a?.id || initialRelationship.source_fact?.id || initialRelationship.source_fact_id || initialRelationship.fact_a_id;
      const bId = initialRelationship.fact_b?.id || initialRelationship.candidate_fact?.id || initialRelationship.candidate_fact_id || initialRelationship.fact_b_id;
      if (aId) setFactAId(aId);
      if (bId) setFactBId(bId);
    }
  }, [initialRelationship]);

  const runComparison = async (aId: string, bId: string) => {
    if (!aId || !bId) {
      setError('Please select both Fact A and Fact B to execute cross-document comparison.');
      return;
    }
    if (aId === bId) {
      setError('Cannot compare a fact against itself. Please select two distinct facts.');
      return;
    }

    try {
      setIsComparing(true);
      setError(null);
      const res = await comparisonApi.comparePair(aId, bId);
      setComparisonResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to execute cross-document reconciliation reasoning.');
    } finally {
      setIsComparing(false);
    }
  };

  const handleManualCompare = (e: React.FormEvent) => {
    e.preventDefault();
    runComparison(factAId, factBId);
  };

  const selectedFactA =
    comparisonResult?.fact_a || comparisonResult?.source_fact || allFacts.find((f) => f.id === factAId);
  const selectedFactB =
    comparisonResult?.fact_b || comparisonResult?.candidate_fact || allFacts.find((f) => f.id === factBId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#f9fafb' }}>
            Cross-Document Fact Comparison & Diagnosis
          </h2>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Multi-dimensional reconciliation across numerical values, reporting scopes, and grounded source quotes
          </div>
        </div>

        {comparisonResult && (
          <button
            onClick={() => {
              setComparisonResult(null);
              setFactAId('');
              setFactBId('');
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-color)',
              padding: '0.45rem 0.85rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '12.5px',
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={13} />
            Reset Selection
          </button>
        )}
      </div>

      {error && <ErrorAlert message={error} onRetry={() => runComparison(factAId, factBId)} />}

      {/* Fact Selector Controls */}
      <div
        className="glass-panel"
        style={{
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <GitCompare size={18} color="#818cf8" />
          <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#f9fafb' }}>
            Select Fact Pair For Comparison
          </h3>
        </div>

        <form onSubmit={handleManualCompare} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            {/* Fact A Selector */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#818cf8' }}>
                Fact A (Source Document)
              </label>
              <select
                value={factAId}
                onChange={(e) => setFactAId(e.target.value)}
                style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  color: '#f9fafb',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.75rem 1rem',
                  fontSize: '13px',
                  outline: 'none',
                  width: '100%',
                }}
              >
                <option value="">-- Choose Source Fact A --</option>
                {allFacts.map((f) => (
                  <option key={f.id} value={f.id}>
                    [{f.entity} • {f.attribute}] {f.statement} ({f.raw_value}) — {f.document_filename || 'Doc'} p.{f.page_number}
                  </option>
                ))}
              </select>
            </div>

            {/* Fact B Selector */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#a855f7' }}>
                Fact B (Candidate Document)
              </label>
              <select
                value={factBId}
                onChange={(e) => setFactBId(e.target.value)}
                style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  color: '#f9fafb',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.75rem 1rem',
                  fontSize: '13px',
                  outline: 'none',
                  width: '100%',
                }}
              >
                <option value="">-- Choose Candidate Fact B --</option>
                {allFacts.map((f) => (
                  <option key={f.id} value={f.id}>
                    [{f.entity} • {f.attribute}] {f.statement} ({f.raw_value}) — {f.document_filename || 'Doc'} p.{f.page_number}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
            <button
              type="submit"
              disabled={isComparing || !factAId || !factBId}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'var(--accent-primary)',
                color: '#ffffff',
                border: 'none',
                padding: '0.65rem 1.5rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13.5px',
                fontWeight: 600,
                cursor: isComparing || !factAId || !factBId ? 'not-allowed' : 'pointer',
                opacity: isComparing || !factAId || !factBId ? 0.6 : 1,
                boxShadow: '0 0 20px rgba(99, 102, 241, 0.35)',
              }}
            >
              <GitCompare size={15} />
              {isComparing ? 'Reconciling Documents...' : 'Execute Pair Reconciliation'}
            </button>
          </div>
        </form>
      </div>

      {/* Comparison Diagnosis Results */}
      {isComparing ? (
        <LoadingState message="Executing numerical normalization, context matrix comparison, and reconciliation rules..." />
      ) : comparisonResult && selectedFactA && selectedFactB ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          {/* Primary Relationship Banner */}
          <div
            className="glass-panel"
            style={{
              padding: '1.5rem 2rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid var(--border-color)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  Reconciliation Outcome
                </span>
                <div style={{ marginTop: '4px' }}>
                  <RelationshipBadge relationship={comparisonResult.relationship} showDescription size="lg" />
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  Diagnosis Confidence
                </span>
                <div style={{ fontSize: '22px', fontWeight: 800, color: '#34d399', marginTop: '2px' }}>
                  {(comparisonResult.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Why This Verdict Deterministic Breakdown */}
            <WhyThisVerdictPanel relationship={comparisonResult} />
          </div>

          {/* Side-by-side Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            {/* Fact A Overview */}
            <div
              style={{
                backgroundColor: 'rgba(99, 102, 241, 0.04)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase' }}>
                  Source A • {selectedFactA.document_filename || 'Doc A'} (p.{selectedFactA.page_number})
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  ID: {selectedFactA.id?.slice(0, 8)}...
                </span>
              </div>
              <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#f9fafb' }}>
                {selectedFactA.statement}
              </h4>
              <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                Reported Value: <strong style={{ color: '#f3f4f6' }}>{selectedFactA.raw_value}</strong>
                {selectedFactA.normalized_value !== null && selectedFactA.normalized_value !== undefined && (
                  <span style={{ color: '#818cf8' }}> ({selectedFactA.currency || ''} {selectedFactA.normalized_value.toLocaleString()} {selectedFactA.unit || ''})</span>
                )}
              </div>
            </div>

            {/* Fact B Overview */}
            <div
              style={{
                backgroundColor: 'rgba(168, 85, 247, 0.04)',
                border: '1px solid rgba(168, 85, 247, 0.25)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: '#a855f7', textTransform: 'uppercase' }}>
                  Source B • {selectedFactB.document_filename || 'Doc B'} (p.{selectedFactB.page_number})
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  ID: {selectedFactB.id?.slice(0, 8)}...
                </span>
              </div>
              <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#f9fafb' }}>
                {selectedFactB.statement}
              </h4>
              <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                Reported Value: <strong style={{ color: '#f3f4f6' }}>{selectedFactB.raw_value}</strong>
                {selectedFactB.normalized_value !== null && selectedFactB.normalized_value !== undefined && (
                  <span style={{ color: '#a855f7' }}> ({selectedFactB.currency || ''} {selectedFactB.normalized_value.toLocaleString()} {selectedFactB.unit || ''})</span>
                )}
              </div>
            </div>
          </div>

          {/* Numerical Value Comparison Panel */}
          <ValueComparisonPanel
            valueComparison={comparisonResult.value_comparison}
            factA={selectedFactA}
            factB={selectedFactB}
          />

          {/* Context Matrix Panel (8 dimensions) */}
          <ContextComparisonMatrix
            factA={selectedFactA}
            factB={selectedFactB}
            contextComparison={comparisonResult.context_comparison}
          />

          {/* Evidence Quotes Comparison Panel */}
          <EvidenceComparisonPanel
            factA={selectedFactA}
            factB={selectedFactB}
            evidenceA={comparisonResult.supporting_evidence?.source_evidence}
            evidenceB={comparisonResult.supporting_evidence?.candidate_evidence}
          />
        </div>
      ) : null}
    </div>
  );
};
