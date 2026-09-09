import React from 'react';
import { CandidateMatch } from '../../types/comparison';
import { ScoreBar } from '../common/ScoreBar';
import { GitCompare, Sparkles, FileText } from 'lucide-react';

interface CandidateMatchesListProps {
  candidates: CandidateMatch[];
  sourceFactId?: string;
  onCompare: (candidateFactId: string) => void;
  isLoading?: boolean;
}

export const CandidateMatchesList: React.FC<CandidateMatchesListProps> = ({
  candidates,
  onCompare,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <Sparkles className="animate-spin" size={24} style={{ margin: '0 auto 0.75rem', color: '#818cf8' }} />
        <div>Retrieving semantic vector candidates from ChromaDB...</div>
      </div>
    );
  }

  if (candidates.length === 0) {
    return (
      <div
        style={{
          padding: '1.5rem',
          textAlign: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.02)',
          borderRadius: 'var(--radius-md)',
          border: '1px dashed var(--border-color)',
          color: 'var(--text-secondary)',
          fontSize: '13px',
        }}
      >
        No candidate matches found across other documents.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
          {candidates.length} Candidate{candidates.length > 1 ? 's' : ''} Identified
        </span>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          Ranked by semantic & structured compatibility
        </span>
      </div>

      {candidates.map((cand) => {
        const candidateFact = cand.candidate_fact;
        const targetId = candidateFact?.id || cand.candidate_fact_id;
        const docName = candidateFact?.document_filename || `Doc ${candidateFact?.document_id?.slice(0, 6) || ''}`;
        const pageNum = candidateFact?.page_number || 1;

        return (
          <div
            key={cand.id || targetId}
            style={{
              backgroundColor: 'rgba(17, 24, 39, 0.9)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem',
              transition: 'border-color 0.15s ease',
            }}
          >
            {/* Candidate Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.75rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
                  <FileText size={13} color="#818cf8" />
                  <span style={{ fontSize: '12px', fontWeight: 600, color: '#c7d2fe' }}>
                    {docName} • Page {pageNum}
                  </span>
                  <span
                    style={{
                      fontSize: '10px',
                      fontWeight: 700,
                      backgroundColor: 'rgba(99, 102, 241, 0.18)',
                      color: '#a5b4fc',
                      padding: '1px 6px',
                      borderRadius: '4px',
                    }}
                  >
                    {cand.match_type}
                  </span>
                </div>
                <div style={{ fontSize: '13.5px', fontWeight: 600, color: '#f9fafb' }}>
                  {candidateFact?.statement || cand.reason || 'Fact statement'}
                </div>
              </div>

              {/* Action */}
              <button
                onClick={() => onCompare(targetId)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  backgroundColor: 'var(--accent-primary)',
                  color: '#ffffff',
                  border: 'none',
                  padding: '0.45rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  flexShrink: 0,
                  transition: 'background-color 0.15s ease',
                }}
              >
                <GitCompare size={13} />
                Compare
              </button>
            </div>

            {/* Fact details summary */}
            {candidateFact && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', fontSize: '12px', color: 'var(--text-secondary)' }}>
                <span>
                  Value: <strong style={{ color: '#f3f4f6' }}>{candidateFact.raw_value}</strong>
                  {candidateFact.normalized_value !== null && candidateFact.normalized_value !== undefined && (
                    <span style={{ color: '#818cf8' }}> ({candidateFact.normalized_value.toLocaleString()} {candidateFact.unit || ''})</span>
                  )}
                </span>
                <span>•</span>
                <span>Period: <strong style={{ color: '#f3f4f6' }}>{candidateFact.time_period || 'N/A'}</strong></span>
                <span>•</span>
                <span>Scope: <strong style={{ color: '#f3f4f6' }}>{candidateFact.scope || 'N/A'}</strong></span>
              </div>
            )}

            {/* Evidence Quote */}
            {candidateFact?.evidence_quote && (
              <div
                style={{
                  fontSize: '12px',
                  fontStyle: 'italic',
                  color: '#cbd5e1',
                  backgroundColor: 'rgba(0, 0, 0, 0.3)',
                  borderLeft: '2px solid #818cf8',
                  padding: '6px 10px',
                  borderRadius: '0 4px 4px 0',
                }}
              >
                "{candidateFact.evidence_quote}"
              </div>
            )}

            {/* Score Breakdown Bar */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '0.5rem',
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                padding: '0.6rem 0.75rem',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              <ScoreBar score={cand.overall_score} label="Overall Match" />
              <ScoreBar score={cand.semantic_similarity} label="Semantic Sim" />
              <ScoreBar score={cand.entity_score} label="Entity Score" />
              <ScoreBar score={cand.attribute_score} label="Attribute Score" />
              <ScoreBar score={cand.time_score} label="Time Score" />
              <ScoreBar score={cand.scope_score} label="Scope Score" />
            </div>
          </div>
        );
      })}
    </div>
  );
};
