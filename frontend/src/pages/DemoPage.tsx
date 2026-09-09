import React, { useState, useEffect } from 'react';
import { demoApi } from '../api/demoApi';
import { comparisonApi } from '../api/comparisonApi';
import { DemoCase } from '../types/api';
import { FactRelationship } from '../types/comparison';
import { RelationshipBadge } from '../components/common/RelationshipBadge';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  Database,
  GitCompare,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';

interface DemoPageProps {
  onSelectComparison: (rel: FactRelationship) => void;
  onComparePair: (factAId: string, factBId: string) => void;
}

const DEMO_FACT_PAIRS: Record<string, [string, string]> = {
  case_1_corroboration: ['fact_demo_corroborate_a', 'fact_demo_corroborate_b'],
  case_2_contradiction: ['fact_demo_contradict_a', 'fact_demo_contradict_b'],
  case_3_contextual_difference: ['fact_demo_scope_a', 'fact_demo_scope_b'],
  case_4_uncertainty: ['fact_demo_uncertain_a', 'fact_demo_uncertain_b'],
};

export const DemoPage: React.FC<DemoPageProps> = ({ onSelectComparison }) => {
  const [cases, setCases] = useState<DemoCase[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSeeding, setIsSeeding] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [seedSuccess, setSeedSuccess] = useState<string | null>(null);

  const fetchCases = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await demoApi.getCases();
      setCases(res.cases || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load evaluator demo cases.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleSeedDemo = async () => {
    try {
      setIsSeeding(true);
      setError(null);
      const res = await demoApi.seedDemo();
      setSeedSuccess(
        `Successfully seeded ${res.documents_created} documents, ${res.facts_created} grounded facts, and ${res.reconciliations_created} reconciliations.`
      );
      await fetchCases();
    } catch (err: any) {
      setError(err.message || 'Failed to populate demo corpus.');
    } finally {
      setIsSeeding(false);
    }
  };

  const handleExecuteCase = async (demoCase: DemoCase) => {
    const pair = DEMO_FACT_PAIRS[demoCase.id];
    const factAId = demoCase.fact_a_id || (pair ? pair[0] : '');
    const factBId = demoCase.fact_b_id || (pair ? pair[1] : '');

    if (!factAId || !factBId) {
      setError('Fact IDs not configured for this demo case.');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      // First ensure demo data is seeded if needed
      await demoApi.seedDemo().catch(() => {});
      const res = await comparisonApi.comparePair(factAId, factBId);
      onSelectComparison(res);
    } catch (err: any) {
      setError(err.message || 'Failed to execute demo comparison.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#f9fafb' }}>
            Evaluator Demonstration Showcase
          </h2>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Instant evaluation walkthrough of the 4 core reasoning relationships across multi-source financial disclosures
          </div>
        </div>

        <button
          onClick={handleSeedDemo}
          disabled={isSeeding}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'var(--accent-primary)',
            color: '#ffffff',
            border: 'none',
            padding: '0.6rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '13px',
            fontWeight: 600,
            cursor: isSeeding ? 'not-allowed' : 'pointer',
            opacity: isSeeding ? 0.7 : 1,
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.35)',
          }}
        >
          <Database size={15} />
          {isSeeding ? 'Seeding Demo Data...' : 'Reset & Seed Demo Fixtures'}
        </button>
      </div>

      {error && <ErrorAlert message={error} onRetry={fetchCases} />}

      {seedSuccess && (
        <div
          style={{
            padding: '0.85rem 1.25rem',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 'var(--radius-md)',
            color: '#34d399',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <CheckCircle2 size={16} />
          <div>{seedSuccess}</div>
        </div>
      )}

      {/* Explanatory Grid of 4 Cases */}
      {isLoading ? (
        <LoadingState message="Loading demo walkthrough cases..." />
      ) : cases.length === 0 ? (
        <div
          className="glass-panel"
          style={{
            padding: '3rem 2rem',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1rem',
          }}
        >
          <Database size={36} color="#818cf8" />
          <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#f9fafb' }}>
            No Demo Cases Loaded in Database
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '500px' }}>
            Click the button below to seed the 4 golden evaluation cases into the SQLite & ChromaDB pipeline.
          </p>
          <button
            onClick={handleSeedDemo}
            disabled={isSeeding}
            style={{
              backgroundColor: 'var(--accent-primary)',
              color: '#ffffff',
              border: 'none',
              padding: '0.65rem 1.5rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '13.5px',
              fontWeight: 600,
              cursor: isSeeding ? 'not-allowed' : 'pointer',
            }}
          >
            {isSeeding ? 'Seeding...' : 'Populate Demo Fixtures'}
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem' }}>
          {cases.map((demoCase, idx) => {
            return (
              <div
                key={demoCase.id || idx}
                className="glass-panel"
                style={{
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem',
                  borderTop: `4px solid ${
                    demoCase.expected_relationship === 'CORROBORATED'
                      ? '#10b981'
                      : demoCase.expected_relationship === 'CONTRADICTED'
                      ? '#ef4444'
                      : demoCase.expected_relationship === 'CONTEXTUALLY_DIFFERENT'
                      ? '#f59e0b'
                      : '#8b5cf6'
                  }`,
                }}
              >
                {/* Title & Badge */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                  <div>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      CASE #{idx + 1}
                    </span>
                    <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f9fafb', marginTop: '2px' }}>
                      {demoCase.title}
                    </h3>
                  </div>
                  <RelationshipBadge relationship={demoCase.expected_relationship} size="sm" />
                </div>

                {/* Description */}
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {demoCase.description}
                </p>

                {/* Source Fact Comparison Cards */}
                {(demoCase.fact_a_preview || demoCase.fact_b_preview) && (
                  <div
                    style={{
                      backgroundColor: 'rgba(0, 0, 0, 0.3)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.85rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.5rem',
                      fontSize: '12px',
                      border: '1px solid var(--border-color)',
                    }}
                  >
                    {demoCase.fact_a_preview && (
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#e2e8f0' }}>
                        <span style={{ color: '#818cf8', fontWeight: 600 }}>Source A:</span>
                        <span>{demoCase.fact_a_preview}</span>
                      </div>
                    )}
                    {demoCase.fact_b_preview && (
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#e2e8f0' }}>
                        <span style={{ color: '#a855f7', fontWeight: 600 }}>Source B:</span>
                        <span>{demoCase.fact_b_preview}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Action Trigger */}
                <button
                  onClick={() => handleExecuteCase(demoCase)}
                  style={{
                    marginTop: 'auto',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    backgroundColor: 'rgba(99, 102, 241, 0.15)',
                    color: '#a5b4fc',
                    border: '1px solid rgba(99, 102, 241, 0.35)',
                    padding: '0.55rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <GitCompare size={14} />
                  Diagnose & Compare This Case
                  <ArrowRight size={13} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
