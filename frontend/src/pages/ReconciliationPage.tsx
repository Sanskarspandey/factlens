import React, { useState, useEffect } from 'react';
import { reconciliationApi } from '../api/reconciliationApi';
import { factsApi } from '../api/factsApi';
import { documentsApi } from '../api/documentsApi';
import { FactRelationship, RelationshipType } from '../types/comparison';
import { Fact } from '../types/fact';
import { Document } from '../types/document';
import { RelationshipBadge } from '../components/common/RelationshipBadge';
import { CrossDocMatrix } from '../components/comparison/CrossDocMatrix';
import { LoadingState } from '../components/common/LoadingState';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  Network,
  Play,
  Table,
  ExternalLink,
  Search,
} from 'lucide-react';

interface ReconciliationPageProps {
  onSelectComparison?: (relationship: FactRelationship) => void;
  onSelectFact?: (fact: Fact) => void;
}

export const ReconciliationPage: React.FC<ReconciliationPageProps> = ({
  onSelectComparison,
  onSelectFact,
}) => {
  const [relationships, setRelationships] = useState<FactRelationship[]>([]);
  const [allFacts, setAllFacts] = useState<Fact[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [activeView, setActiveView] = useState<'table' | 'matrix'>('table');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isReconciling, setIsReconciling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [relationshipFilter, setRelationshipFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [minConfidence] = useState<number>(0);

  const fetchReconciliationData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [reconsRes, factsRes, docsRes] = await Promise.all([
        reconciliationApi.listReconciliations({
          relationship: relationshipFilter !== 'ALL' ? (relationshipFilter as RelationshipType) : undefined,
          min_confidence: minConfidence > 0 ? minConfidence : undefined,
          limit: 200,
        }),
        factsApi.listFacts({ limit: 300 }),
        documentsApi.listDocuments(1, 100).catch(() => ({ items: [] })),
      ]);

      setRelationships(reconsRes.items || []);
      setAllFacts(factsRes.items || []);
      setDocuments(docsRes.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch cross-document reconciliation records.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReconciliationData();
  }, [relationshipFilter, minConfidence]);

  const handleRunFullReconciliation = async () => {
    try {
      setIsReconciling(true);
      setError(null);
      await reconciliationApi.runReconciliation({
        similarity_threshold: 0.65,
      });
      await fetchReconciliationData();
    } catch (err: any) {
      setError(err.message || 'Failed to execute batch reconciliation pipeline.');
    } finally {
      setIsReconciling(false);
    }
  };

  const filteredRelationships = relationships.filter((rel) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const statementA = rel.fact_a?.statement || rel.source_fact?.statement || '';
    const statementB = rel.fact_b?.statement || rel.candidate_fact?.statement || '';
    const metric = rel.fact_a?.attribute || rel.source_fact?.attribute || '';
    const entity = rel.fact_a?.entity || rel.source_fact?.entity || '';
    const rationale = rel.rationale || '';
    return (
      statementA.toLowerCase().includes(q) ||
      statementB.toLowerCase().includes(q) ||
      metric.toLowerCase().includes(q) ||
      entity.toLowerCase().includes(q) ||
      rationale.toLowerCase().includes(q)
    );
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#f9fafb' }}>
            Cross-Document Reconciliation & Comparison Matrix
          </h2>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Automated corroboration, contradiction detection, scope discrepancy analysis & uncertainty preservation
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* View Toggle */}
          <div
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.4)',
              padding: '3px',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              border: '1px solid var(--border-color)',
            }}
          >
            <button
              onClick={() => setActiveView('table')}
              style={{
                padding: '0.45rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                backgroundColor: activeView === 'table' ? 'var(--accent-primary)' : 'transparent',
                color: activeView === 'table' ? '#ffffff' : 'var(--text-secondary)',
                fontSize: '12.5px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
              }}
            >
              <Network size={14} />
              Reconciliation Log
            </button>
            <button
              onClick={() => setActiveView('matrix')}
              style={{
                padding: '0.45rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                backgroundColor: activeView === 'matrix' ? 'var(--accent-primary)' : 'transparent',
                color: activeView === 'matrix' ? '#ffffff' : 'var(--text-secondary)',
                fontSize: '12.5px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
              }}
            >
              <Table size={14} />
              Cross-Doc Matrix
            </button>
          </div>

          {/* Run Reconciliation Action */}
          <button
            onClick={handleRunFullReconciliation}
            disabled={isReconciling || documents.length === 0}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'var(--accent-primary)',
              color: '#ffffff',
              border: 'none',
              padding: '0.55rem 1.15rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '13px',
              fontWeight: 600,
              cursor: isReconciling || documents.length === 0 ? 'not-allowed' : 'pointer',
              opacity: isReconciling || documents.length === 0 ? 0.6 : 1,
              boxShadow: '0 0 20px rgba(99, 102, 241, 0.35)',
            }}
          >
            <Play size={14} />
            {isReconciling ? 'Reconciling Corpus...' : 'Run Corpus Reconciliation'}
          </button>
        </div>
      </div>

      {error && <ErrorAlert message={error} onRetry={fetchReconciliationData} />}

      {/* Filter Toolbar */}
      <div
        className="glass-panel"
        style={{
          padding: '1rem 1.25rem',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '1rem',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flex: 1, minWidth: '240px' }}>
          <Search size={16} color="var(--text-secondary)" />
          <input
            type="text"
            placeholder="Search metric, entity, or reconciliation rationale..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              background: 'none',
              border: 'none',
              color: '#f9fafb',
              fontSize: '13.5px',
              width: '100%',
              outline: 'none',
            }}
          />
        </div>

        {/* Relationship Status Pills */}
        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
          {[
            { id: 'ALL', label: 'All' },
            { id: 'CORROBORATED', label: '✓ Corroborated' },
            { id: 'CONTRADICTED', label: '! Contradicted' },
            { id: 'CONTEXTUALLY_DIFFERENT', label: '↔ Contextual Diff' },
            { id: 'UNCERTAIN', label: '? Uncertain' },
          ].map((pill) => {
            const isSelected = relationshipFilter === pill.id;
            return (
              <button
                key={pill.id}
                onClick={() => setRelationshipFilter(pill.id)}
                style={{
                  padding: '0.35rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '12px',
                  fontWeight: isSelected ? 700 : 500,
                  border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
                  backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.02)',
                  color: isSelected ? '#ffffff' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {pill.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <LoadingState message="Loading reconciled fact pairs and cross-document mappings..." />
      ) : activeView === 'matrix' ? (
        <CrossDocMatrix
          facts={allFacts}
          relationships={relationships}
          onSelectComparison={onSelectComparison}
          onSelectFact={onSelectFact}
        />
      ) : filteredRelationships.length === 0 ? (
        <EmptyState
          title="No Reconciliation Records Found"
          message={
            searchQuery || relationshipFilter !== 'ALL'
              ? 'No reconciled pairs match your filter criteria.'
              : 'Execute the corpus reconciliation pipeline or compare specific fact pairs to generate cross-document records.'
          }
          actionLabel="Run Corpus Reconciliation"
          onAction={handleRunFullReconciliation}
        />
      ) : (
        <div className="glass-panel" style={{ overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                  <th style={{ padding: '12px 14px', width: '22%' }}>Source Fact A</th>
                  <th style={{ padding: '12px 14px', width: '22%' }}>Candidate Fact B</th>
                  <th style={{ padding: '12px 14px', width: '18%' }}>Relationship</th>
                  <th style={{ padding: '12px 14px', width: '28%' }}>Reconciliation Rationale</th>
                  <th style={{ padding: '12px 14px', width: '10%', textAlign: 'right' }}>Diagnosis</th>
                </tr>
              </thead>
              <tbody>
                {filteredRelationships.map((rel, idx) => {
                  const factA = rel.fact_a || rel.source_fact;
                  const factB = rel.fact_b || rel.candidate_fact;

                  return (
                    <tr
                      key={rel.id}
                      onClick={() => onSelectComparison?.(rel)}
                      style={{
                        borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                        backgroundColor: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.015)',
                        cursor: onSelectComparison ? 'pointer' : 'default',
                        transition: 'background-color 0.15s ease',
                      }}
                    >
                      {/* Fact A */}
                      <td style={{ padding: '12px 14px' }}>
                        <div style={{ fontWeight: 600, color: '#f3f4f6' }}>
                          {factA?.statement || `Fact #${rel.source_fact_id || rel.fact_a_id}`}
                        </div>
                        <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '3px' }}>
                          {factA?.document_filename} (p.{factA?.page_number}) • Val:{' '}
                          <span style={{ color: '#818cf8', fontWeight: 600 }}>{factA?.raw_value}</span>
                        </div>
                      </td>

                      {/* Fact B */}
                      <td style={{ padding: '12px 14px' }}>
                        <div style={{ fontWeight: 600, color: '#f3f4f6' }}>
                          {factB?.statement || `Fact #${rel.candidate_fact_id || rel.fact_b_id}`}
                        </div>
                        <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '3px' }}>
                          {factB?.document_filename} (p.{factB?.page_number}) • Val:{' '}
                          <span style={{ color: '#a855f7', fontWeight: 600 }}>{factB?.raw_value}</span>
                        </div>
                      </td>

                      {/* Relationship Badge */}
                      <td style={{ padding: '12px 14px' }}>
                        <RelationshipBadge relationship={rel.relationship} size="sm" />
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                          Confidence: {(rel.confidence * 100).toFixed(0)}%
                        </div>
                      </td>

                      {/* Rationale */}
                      <td style={{ padding: '12px 14px' }}>
                        <div
                          style={{
                            fontSize: '12.5px',
                            color: '#e2e8f0',
                            lineHeight: 1.45,
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                          }}
                        >
                          {rel.rationale}
                        </div>
                      </td>

                      {/* Action */}
                      <td style={{ padding: '12px 14px', textAlign: 'right' }}>
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            color: '#818cf8',
                            fontSize: '12px',
                            fontWeight: 600,
                          }}
                        >
                          Inspect
                          <ExternalLink size={12} />
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
