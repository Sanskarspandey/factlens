import React, { useState, useEffect } from 'react';
import { Fact } from '../../types/fact';
import { CandidateMatch } from '../../types/comparison';
import { factsApi } from '../../api/factsApi';
import { CandidateMatchesList } from './CandidateMatchesList';
import {
  X,
  Sparkles,
  FileText,
  ShieldCheck,
  ExternalLink,
  GitBranch,
} from 'lucide-react';

interface FactDetailDrawerProps {
  fact: Fact | null;
  onClose: () => void;
  onCompareWith: (targetFactId: string) => void;
  onOpenDocument?: (docId: string, page?: number) => void;
}

export const FactDetailDrawer: React.FC<FactDetailDrawerProps> = ({
  fact,
  onClose,
  onCompareWith,
  onOpenDocument,
}) => {
  const [candidates, setCandidates] = useState<CandidateMatch[]>([]);
  const [isLoadingCandidates, setIsLoadingCandidates] = useState<boolean>(false);
  const [candidateError, setCandidateError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [showLineage, setShowLineage] = useState<boolean>(true);

  // Reset candidates state when fact changes
  useEffect(() => {
    setCandidates([]);
    setCandidateError(null);
    setHasSearched(false);
  }, [fact?.id]);

  if (!fact) return null;

  const isDemo = Boolean(
    fact.source_type === 'SYNTHETIC_DEMO' ||
    fact.id?.startsWith('fact_demo_') ||
    fact.document_id?.startsWith('doc_demo_')
  );

  const handleFindMatches = async () => {
    try {
      setIsLoadingCandidates(true);
      setCandidateError(null);
      const res = await factsApi.getCandidateMatches(fact.id, 10);
      setCandidates(res.candidates || []);
      setHasSearched(true);
    } catch (err: any) {
      setCandidateError(err.message || 'Failed to retrieve candidate matches.');
    } finally {
      setIsLoadingCandidates(false);
    }
  };

  const fmt = (val: string | number | null | undefined) => {
    if (val === null || val === undefined || val === '') return '—';
    return String(val);
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: '680px',
        maxWidth: '92vw',
        backgroundColor: '#0f172a',
        borderLeft: '1px solid var(--border-color)',
        boxShadow: '-10px 0 30px rgba(0, 0, 0, 0.6)',
        zIndex: 100,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'rgba(15, 23, 42, 0.98)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div
            style={{
              width: '30px',
              height: '30px',
              borderRadius: '6px',
              backgroundColor: 'rgba(99, 102, 241, 0.2)',
              color: '#818cf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <ShieldCheck size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f9fafb' }}>
              Fact Trust & Provenance Audit
            </h3>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              ID: {fact.id.slice(0, 16)}...
            </span>
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '4px',
          }}
        >
          <X size={20} />
        </button>
      </div>

      {/* Scrollable Content */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem',
        }}
      >
        {/* Statement & Provenance Summary Header */}
        <div
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  color: '#818cf8',
                  letterSpacing: '0.05em',
                }}
              >
                {fact.entity} • {fact.attribute}
              </span>
              {isDemo ? (
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    backgroundColor: 'rgba(245, 158, 11, 0.15)',
                    color: '#fbbf24',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                    padding: '1px 6px',
                    borderRadius: '4px',
                    letterSpacing: '0.04em',
                  }}
                >
                  ⚡ Evaluator Demo Fixture
                </span>
              ) : (
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    backgroundColor: 'rgba(59, 130, 246, 0.15)',
                    color: '#60a5fa',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    padding: '1px 6px',
                    borderRadius: '4px',
                    letterSpacing: '0.04em',
                  }}
                >
                  📄 PDF Source
                </span>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  backgroundColor:
                    fact.status === 'VERIFIED'
                      ? 'rgba(16, 185, 129, 0.15)'
                      : fact.status === 'UNCERTAIN'
                      ? 'rgba(245, 158, 11, 0.15)'
                      : 'rgba(239, 68, 68, 0.15)',
                  color:
                    fact.status === 'VERIFIED'
                      ? '#34d399'
                      : fact.status === 'UNCERTAIN'
                      ? '#fbbf24'
                      : '#f87171',
                  padding: '2px 8px',
                  borderRadius: '4px',
                }}
              >
                Grounding: {fact.status} ({(fact.confidence * 100).toFixed(0)}%)
              </span>
            </div>
          </div>

          <h4 style={{ fontSize: '15.5px', fontWeight: 600, color: '#f3f4f6', lineHeight: 1.5 }}>
            {fact.statement}
          </h4>

          {fact.uncertainty_notes && (
            <div
              style={{
                backgroundColor: 'rgba(245, 158, 11, 0.08)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '12.5px',
                color: '#fef3c7',
              }}
            >
              <strong>Uncertainty / Caveat:</strong> {fact.uncertainty_notes}
            </div>
          )}
        </div>

        {/* Fact Lineage Timeline / Stepper */}
        <div
          className="glass-panel"
          style={{
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.85rem',
            border: '1px solid rgba(99, 102, 241, 0.25)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <GitBranch size={16} color="#818cf8" />
              <h5 style={{ fontSize: '12.5px', fontWeight: 700, textTransform: 'uppercase', color: '#f3f4f6' }}>
                End-to-End Grounding Lineage
              </h5>
            </div>
            <button
              onClick={() => setShowLineage(!showLineage)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-secondary)',
                fontSize: '11px',
                cursor: 'pointer',
              }}
            >
              {showLineage ? 'Collapse' : 'Expand'}
            </button>
          </div>

          {showLineage && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.25rem' }}>
              {/* Node 1: Source Document */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', backgroundColor: 'rgba(99, 102, 241, 0.3)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 700 }}>
                    1
                  </div>
                  <div style={{ width: '2px', height: '18px', backgroundColor: 'rgba(99, 102, 241, 0.3)' }} />
                </div>
                <div style={{ fontSize: '12px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>SOURCE DOCUMENT: </span>
                  <span style={{ color: '#f3f4f6', fontWeight: 500 }}>{fact.document_filename || fact.document_id}</span>
                </div>
              </div>

              {/* Node 2: Source Page */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', backgroundColor: 'rgba(99, 102, 241, 0.3)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 700 }}>
                    2
                  </div>
                  <div style={{ width: '2px', height: '18px', backgroundColor: 'rgba(99, 102, 241, 0.3)' }} />
                </div>
                <div style={{ fontSize: '12px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>SOURCE PAGE: </span>
                  <span style={{ color: '#c7d2fe', fontWeight: 600 }}>Page {fact.page_number}</span>
                  {fact.bounding_box && (
                    <span style={{ color: 'var(--text-muted)', fontSize: '11px', marginLeft: '6px' }}>
                      [BBox: {fact.bounding_box.map((n) => Math.round(n)).join(', ')}]
                    </span>
                  )}
                </div>
              </div>

              {/* Node 3: Verbatim Quote */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', backgroundColor: 'rgba(99, 102, 241, 0.3)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 700 }}>
                    3
                  </div>
                  <div style={{ width: '2px', height: '18px', backgroundColor: 'rgba(99, 102, 241, 0.3)' }} />
                </div>
                <div style={{ fontSize: '12px', flex: 1 }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>EVIDENCE QUOTE: </span>
                  <span style={{ color: '#e2e8f0', fontStyle: 'italic' }}>"{fact.evidence_quote}"</span>
                </div>
              </div>

              {/* Node 4: Extracted Fact */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', backgroundColor: 'rgba(99, 102, 241, 0.3)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 700 }}>
                    4
                  </div>
                  <div style={{ width: '2px', height: '18px', backgroundColor: 'rgba(99, 102, 241, 0.3)' }} />
                </div>
                <div style={{ fontSize: '12px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>NORMALIZATION & CONTEXT: </span>
                  <span style={{ color: '#a5b4fc', fontWeight: 600 }}>
                    {fact.currency ? fact.currency + ' ' : ''}{fact.normalized_value_str || (fact.normalized_value ? fact.normalized_value.toLocaleString() : fact.raw_value)}
                  </span>
                  <span style={{ color: 'var(--text-secondary)' }}> • {fact.time_period || fact.fiscal_year || 'Period N/A'} • {fact.scope || 'Consolidated'}</span>
                </div>
              </div>

              {/* Node 5: ChromaDB & Candidates */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', backgroundColor: 'rgba(16, 185, 129, 0.3)', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 700 }}>
                    ✓
                  </div>
                </div>
                <div style={{ fontSize: '12px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>CHROMA VECTOR STORE: </span>
                  <span style={{ color: '#34d399', fontWeight: 500 }}>
                    {fact.indexing_status === 'INDEXED' ? 'Indexed in ChromaDB (384-dim)' : 'Ready for Candidate Matching'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Structured Dimensions Grid */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <h5 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
            Normalized Dimensions & Metadata
          </h5>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '0.75rem',
              backgroundColor: 'rgba(0, 0, 0, 0.25)',
              padding: '1rem',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
            }}
          >
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Raw Value:</span>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#f9fafb' }}>{fmt(fact.raw_value)}</div>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Normalized Value:</span>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#a5b4fc' }}>
                {fact.normalized_value !== null && fact.normalized_value !== undefined
                  ? `${fact.currency ? fact.currency + ' ' : ''}${fact.normalized_value.toLocaleString()} ${fact.unit || ''}`
                  : '—'}
              </div>
            </div>

            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Currency:</span>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#f3f4f6' }}>{fmt(fact.currency)}</div>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Unit / Multiplier:</span>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#f3f4f6' }}>{fmt(fact.unit)}</div>
            </div>

            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Time Period:</span>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#f3f4f6' }}>{fmt(fact.time_period)}</div>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Fiscal Year / Quarter:</span>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#f3f4f6' }}>
                {fact.fiscal_year ? `${fact.fiscal_year} ${fact.quarter || ''}` : fmt(fact.quarter)}
              </div>
            </div>

            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Reporting Scope:</span>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#f3f4f6' }}>{fmt(fact.scope)}</div>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Geography:</span>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#f3f4f6' }}>{fmt(fact.geography)}</div>
            </div>

            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Value Status:</span>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#f3f4f6' }}>{fmt(fact.value_status)}</div>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Extraction Status:</span>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#f3f4f6' }}>{fmt(fact.status)}</div>
            </div>
          </div>

          {fact.definition && (
            <div
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                fontSize: '12px',
                color: 'var(--text-secondary)',
              }}
            >
              <strong style={{ color: '#e2e8f0' }}>Metric Definition:</strong> {fact.definition}
            </div>
          )}
        </div>

        {/* Source Evidence Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h5 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
              Source Grounded Evidence
            </h5>
            {onOpenDocument && (
              <button
                onClick={() => onOpenDocument(fact.document_id, fact.page_number)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#818cf8',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <FileText size={12} />
                Open PDF Page
                <ExternalLink size={10} />
              </button>
            )}
          </div>

          <div
            style={{
              backgroundColor: 'rgba(99, 102, 241, 0.04)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              borderRadius: 'var(--radius-md)',
              padding: '1.1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#f9fafb' }}>
                {fact.document_filename || `Document ID: ${fact.document_id}`}
              </span>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  color: '#c7d2fe',
                  padding: '2px 8px',
                  borderRadius: '4px',
                }}
              >
                Page {fact.page_number}
              </span>
            </div>

            <div
              style={{
                backgroundColor: 'rgba(0, 0, 0, 0.4)',
                borderLeft: '3px solid #6366f1',
                padding: '0.85rem 1rem',
                borderRadius: '0 4px 4px 0',
                fontSize: '13px',
                fontStyle: 'italic',
                color: '#e2e8f0',
                lineHeight: 1.6,
              }}
            >
              "{fact.evidence_quote}"
            </div>

            {fact.bounding_box && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Page Coordinates: [{fact.bounding_box.map((n) => Math.round(n)).join(', ')}]
              </div>
            )}
          </div>
        </div>

        {/* Candidate Matching Trigger & Results */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h5 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
              Cross-Document Semantic Matching
            </h5>

            <button
              onClick={handleFindMatches}
              disabled={isLoadingCandidates}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'var(--accent-primary)',
                color: '#ffffff',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                fontWeight: 600,
                cursor: isLoadingCandidates ? 'not-allowed' : 'pointer',
                opacity: isLoadingCandidates ? 0.7 : 1,
                boxShadow: '0 0 15px rgba(99, 102, 241, 0.3)',
              }}
            >
              <Sparkles size={14} />
              {isLoadingCandidates ? 'Matching in ChromaDB...' : 'Find Related Facts'}
            </button>
          </div>

          {candidateError && (
            <div
              style={{
                padding: '0.75rem',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: 'var(--radius-sm)',
                color: '#f87171',
                fontSize: '12px',
              }}
            >
              {candidateError}
            </div>
          )}

          {hasSearched && (
            <CandidateMatchesList
              candidates={candidates}
              sourceFactId={fact.id}
              isLoading={isLoadingCandidates}
              onCompare={(candId) => {
                onClose();
                onCompareWith(candId);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};
