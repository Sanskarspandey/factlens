import React from 'react';
import { Fact } from '../../types/fact';
import { SupportingEvidenceItem } from '../../types/comparison';
import { Quote, FileText, ExternalLink, BookmarkCheck } from 'lucide-react';

interface EvidenceComparisonPanelProps {
  factA: Fact;
  factB: Fact;
  evidenceA?: SupportingEvidenceItem | null;
  evidenceB?: SupportingEvidenceItem | null;
  onOpenDocument?: (docId: string, page?: number) => void;
}

export const EvidenceComparisonPanel: React.FC<EvidenceComparisonPanelProps> = ({
  factA,
  factB,
  evidenceA,
  evidenceB,
  onOpenDocument,
}) => {
  const quoteA = evidenceA?.evidence_quote || factA.evidence_quote || 'No evidence quote recorded.';
  const quoteB = evidenceB?.evidence_quote || factB.evidence_quote || 'No evidence quote recorded.';

  const docNameA = factA.document_filename || `Document #${factA.document_id?.slice(0, 8)}`;
  const docNameB = factB.document_filename || `Document #${factB.document_id?.slice(0, 8)}`;

  const pageA = evidenceA?.page_number || factA.page_number || 1;
  const pageB = evidenceB?.page_number || factB.page_number || 1;

  const bboxA = factA.bounding_box;
  const bboxB = factB.bounding_box;

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
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Quote size={18} color="#818cf8" />
          <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
            Grounded Source Evidence Comparison
          </h4>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <BookmarkCheck size={14} color="#34d399" />
          Verbatim grounded quotes extracted directly from source PDFs
        </div>
      </div>

      {/* Side-by-side Evidence Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        {/* Evidence A */}
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  backgroundColor: 'rgba(99, 102, 241, 0.2)',
                  color: '#a5b4fc',
                  padding: '2px 7px',
                  borderRadius: '4px',
                }}
              >
                SOURCE A
              </span>
              {(factA.source_type === 'SYNTHETIC_DEMO' || factA.id.startsWith('fact_demo_') || factA.document_id.startsWith('doc_demo_')) && (
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
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#f3f4f6' }}>
                {docNameA}
              </span>
            </div>
            <span
              style={{
                fontSize: '12px',
                fontWeight: 600,
                color: '#c7d2fe',
                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                padding: '2px 8px',
                borderRadius: '4px',
              }}
            >
              Page {pageA}
            </span>
          </div>

          <div
            style={{
              position: 'relative',
              backgroundColor: 'rgba(0, 0, 0, 0.35)',
              borderLeft: '3px solid #6366f1',
              borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
              padding: '0.85rem 1rem',
              fontSize: '13px',
              fontStyle: 'italic',
              color: '#e2e8f0',
              lineHeight: 1.6,
            }}
          >
            "{quoteA}"
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto', paddingTop: '0.5rem' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {bboxA ? `BBox: [${bboxA.slice(0, 4).map((n) => Math.round(n)).join(', ')}]` : 'Location: Page Text Stream'}
            </div>
            {onOpenDocument && (
              <button
                onClick={() => onOpenDocument(factA.document_id, pageA)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  background: 'none',
                  border: 'none',
                  color: '#818cf8',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  padding: '4px 6px',
                }}
              >
                <FileText size={13} />
                View Document
                <ExternalLink size={11} />
              </button>
            )}
          </div>
        </div>

        {/* Evidence B */}
        <div
          style={{
            backgroundColor: 'rgba(168, 85, 247, 0.04)',
            border: '1px solid rgba(168, 85, 247, 0.25)',
            borderRadius: 'var(--radius-md)',
            padding: '1.1rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  backgroundColor: 'rgba(168, 85, 247, 0.2)',
                  color: '#d8b4fe',
                  padding: '2px 7px',
                  borderRadius: '4px',
                }}
              >
                SOURCE B
              </span>
              {(factB.source_type === 'SYNTHETIC_DEMO' || factB.id.startsWith('fact_demo_') || factB.document_id.startsWith('doc_demo_')) && (
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
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#f3f4f6' }}>
                {docNameB}
              </span>
            </div>
            <span
              style={{
                fontSize: '12px',
                fontWeight: 600,
                color: '#e9d5ff',
                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                padding: '2px 8px',
                borderRadius: '4px',
              }}
            >
              Page {pageB}
            </span>
          </div>

          <div
            style={{
              position: 'relative',
              backgroundColor: 'rgba(0, 0, 0, 0.35)',
              borderLeft: '3px solid #a855f7',
              borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
              padding: '0.85rem 1rem',
              fontSize: '13px',
              fontStyle: 'italic',
              color: '#e2e8f0',
              lineHeight: 1.6,
            }}
          >
            "{quoteB}"
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto', paddingTop: '0.5rem' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {bboxB ? `BBox: [${bboxB.slice(0, 4).map((n) => Math.round(n)).join(', ')}]` : 'Location: Page Text Stream'}
            </div>
            {onOpenDocument && (
              <button
                onClick={() => onOpenDocument(factB.document_id, pageB)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  background: 'none',
                  border: 'none',
                  color: '#c084fc',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  padding: '4px 6px',
                }}
              >
                <FileText size={13} />
                View Document
                <ExternalLink size={11} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
