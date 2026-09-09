import React, { useState, useEffect } from 'react';
import { factsApi } from '../api/factsApi';
import { documentsApi } from '../api/documentsApi';
import { Fact } from '../types/fact';
import { Document } from '../types/document';
import { FactDetailDrawer } from '../components/facts/FactDetailDrawer';
import { LoadingState } from '../components/common/LoadingState';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { Search } from 'lucide-react';

interface FactsPageProps {
  onCompareFacts?: (factAId: string, factBId: string) => void;
  selectedFactId?: string | null;
}

export const FactsPage: React.FC<FactsPageProps> = ({ onCompareFacts, selectedFactId }) => {
  const [facts, setFacts] = useState<Fact[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedDocId, setSelectedDocId] = useState<string>('');
  const [selectedEntity, setSelectedEntity] = useState<string>('');
  const [selectedAttribute, setSelectedAttribute] = useState<string>('');

  // Selected Fact Drawer
  const [activeFact, setActiveFact] = useState<Fact | null>(null);

  const fetchFactsAndDocs = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [factsRes, docsRes] = await Promise.all([
        factsApi.listFacts({
          document_id: selectedDocId || undefined,
          entity: selectedEntity || undefined,
          attribute: selectedAttribute || undefined,
          limit: 200,
        }),
        documentsApi.listDocuments(1, 100).catch(() => ({ items: [] })),
      ]);

      setFacts(factsRes.items || []);
      setDocuments(docsRes.items || []);

      if (selectedFactId) {
        const target = (factsRes.items || []).find((f: Fact) => f.id === selectedFactId);
        if (target) setActiveFact(target);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch extracted facts catalogue.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFactsAndDocs();
  }, [selectedDocId, selectedEntity, selectedAttribute]);

  // Derived filter options
  const entities = Array.from(new Set(facts.map((f) => f.entity).filter(Boolean)));

  const filteredFacts = facts.filter((f) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const statement = f.statement ? f.statement.toLowerCase() : '';
    const entity = f.entity ? f.entity.toLowerCase() : '';
    const attribute = f.attribute ? f.attribute.toLowerCase() : '';
    const rawVal = f.raw_value ? f.raw_value.toLowerCase() : '';
    const quote = f.evidence_quote ? f.evidence_quote.toLowerCase() : '';

    return (
      statement.includes(q) ||
      entity.includes(q) ||
      attribute.includes(q) ||
      rawVal.includes(q) ||
      quote.includes(q)
    );
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#f9fafb' }}>
            Fact Intelligence Explorer
          </h2>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Grounded facts extracted across all ingested documents with exact quotes & normalized dimensions
          </div>
        </div>
        <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          Showing <strong>{filteredFacts.length}</strong> grounded fact{filteredFacts.length === 1 ? '' : 's'}
        </div>
      </div>

      {error && <ErrorAlert message={error} onRetry={fetchFactsAndDocs} />}

      {/* Filter & Search Bar */}
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
            placeholder="Search statement, entity, metric, or quote..."
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

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Document Filter */}
          <select
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.4)',
              color: '#f9fafb',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.45rem 0.75rem',
              fontSize: '12.5px',
              outline: 'none',
            }}
          >
            <option value="">All Documents ({documents.length})</option>
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.filename}
              </option>
            ))}
          </select>

          {/* Entity Filter */}
          {entities.length > 1 && (
            <select
              value={selectedEntity}
              onChange={(e) => setSelectedEntity(e.target.value)}
              style={{
                backgroundColor: 'rgba(0, 0, 0, 0.4)',
                color: '#f9fafb',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.45rem 0.75rem',
                fontSize: '12.5px',
                outline: 'none',
              }}
            >
              <option value="">All Entities ({entities.length})</option>
              {entities.map((ent) => (
                <option key={ent} value={ent}>
                  {ent}
                </option>
              ))}
            </select>
          )}

          {/* Reset Filters */}
          {(selectedDocId || selectedEntity || selectedAttribute || searchQuery) && (
            <button
              onClick={() => {
                setSelectedDocId('');
                setSelectedEntity('');
                setSelectedAttribute('');
                setSearchQuery('');
              }}
              style={{
                background: 'none',
                border: 'none',
                color: '#818cf8',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Facts Table View */}
      {isLoading ? (
        <LoadingState message="Loading grounded fact catalogue..." />
      ) : filteredFacts.length === 0 ? (
        <EmptyState
          title="No Facts Found"
          message={
            searchQuery || selectedDocId
              ? 'No facts matched your filter criteria.'
              : 'No facts have been extracted yet. Please upload and process a document.'
          }
        />
      ) : (
        <div className="glass-panel" style={{ overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                  <th style={{ padding: '12px 14px', width: '16%' }}>Entity & Metric</th>
                  <th style={{ padding: '12px 14px', width: '32%' }}>Statement & Evidence</th>
                  <th style={{ padding: '12px 14px', width: '15%' }}>Normalized Value</th>
                  <th style={{ padding: '12px 14px', width: '12%' }}>Period / Scope</th>
                  <th style={{ padding: '12px 14px', width: '12%' }}>Source Doc</th>
                  <th style={{ padding: '12px 14px', width: '13%', textAlign: 'center' }}>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {filteredFacts.map((fact, idx) => (
                  <tr
                    key={fact.id}
                    onClick={() => setActiveFact(fact)}
                    style={{
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                      backgroundColor: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.015)',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease',
                    }}
                  >
                    {/* Entity & Attribute */}
                    <td style={{ padding: '12px 14px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 700, color: '#f3f4f6' }}>{fact.entity}</span>
                        {(fact.source_type === 'SYNTHETIC_DEMO' || fact.id.startsWith('fact_demo_') || fact.document_id.startsWith('doc_demo_')) && (
                          <span
                            style={{
                              fontSize: '9px',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              backgroundColor: 'rgba(245, 158, 11, 0.15)',
                              color: '#fbbf24',
                              border: '1px solid rgba(245, 158, 11, 0.3)',
                              padding: '1px 4px',
                              borderRadius: '3px',
                            }}
                          >
                            Demo
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '12px', color: '#818cf8', fontWeight: 600, marginTop: '2px' }}>
                        {fact.attribute}
                      </div>
                    </td>

                    {/* Statement & Quote Preview */}
                    <td style={{ padding: '12px 14px' }}>
                      <div style={{ fontWeight: 500, color: '#f9fafb', lineHeight: 1.4 }}>
                        {fact.statement}
                      </div>
                      <div
                        style={{
                          fontSize: '11.5px',
                          fontStyle: 'italic',
                          color: 'var(--text-secondary)',
                          marginTop: '4px',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          maxWidth: '380px',
                        }}
                      >
                        "{fact.evidence_quote}"
                      </div>
                    </td>

                    {/* Value */}
                    <td style={{ padding: '12px 14px' }}>
                      <div style={{ fontWeight: 600, color: '#e0e7ff' }}>
                        {fact.normalized_value !== null && fact.normalized_value !== undefined
                          ? `${fact.currency ? fact.currency + ' ' : ''}${fact.normalized_value.toLocaleString()} ${fact.unit || ''}`.trim()
                          : fact.raw_value}
                      </div>
                      {fact.normalized_value !== null && fact.normalized_value !== undefined && (
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                          Raw: {fact.raw_value}
                        </div>
                      )}
                    </td>

                    {/* Period & Scope */}
                    <td style={{ padding: '12px 14px', color: 'var(--text-secondary)' }}>
                      <div>{fact.time_period || fact.fiscal_year || '—'}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        {fact.scope || 'Consolidated'}
                      </div>
                    </td>

                    {/* Source Doc & Page */}
                    <td style={{ padding: '12px 14px' }}>
                      <div
                        style={{
                          fontSize: '12px',
                          color: '#c7d2fe',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          maxWidth: '140px',
                        }}
                        title={fact.document_filename || ''}
                      >
                        {fact.document_filename || `Doc #${fact.document_id.slice(0, 6)}`}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        Page {fact.page_number}
                      </div>
                    </td>

                    {/* Confidence */}
                    <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                      <span
                        style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          backgroundColor: 'rgba(16, 185, 129, 0.15)',
                          color: '#34d399',
                          padding: '3px 8px',
                          borderRadius: '4px',
                        }}
                      >
                        {(fact.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Fact Detail Drawer */}
      <FactDetailDrawer
        fact={activeFact}
        onClose={() => setActiveFact(null)}
        onCompareWith={(targetFactId) => {
          if (activeFact) {
            onCompareFacts?.(activeFact.id, targetFactId);
          }
        }}
      />
    </div>
  );
};
