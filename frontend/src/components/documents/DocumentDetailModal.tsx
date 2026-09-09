import React, { useState, useEffect } from 'react';
import { Document } from '../../types/document';
import { Fact } from '../../types/fact';
import { factsApi } from '../../api/factsApi';
import { X, FileText } from 'lucide-react';

interface DocumentDetailModalProps {
  document: Document | null;
  onClose: () => void;
  onSelectFact: (fact: Fact) => void;
}

export const DocumentDetailModal: React.FC<DocumentDetailModalProps> = ({
  document,
  onClose,
  onSelectFact,
}) => {
  const [facts, setFacts] = useState<Fact[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!document) return;

    const fetchDocumentFacts = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const res = await factsApi.listFacts({ document_id: document.id, limit: 100 });
        setFacts(res.items || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load facts for this document.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocumentFacts();
  }, [document?.id]);

  if (!document) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 90,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: '900px',
          maxWidth: '100%',
          maxHeight: '88vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#0f172a',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '1.25rem 1.75rem',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                color: '#818cf8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <FileText size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f9fafb' }}>
                {document.filename}
              </h3>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                ID: {document.id} • SHA-256: {document.file_hash.slice(0, 16)}...
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Document Stats Bar */}
        <div
          style={{
            padding: '1rem 1.75rem',
            backgroundColor: 'rgba(0, 0, 0, 0.25)',
            borderBottom: '1px solid var(--border-color)',
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '1rem',
          }}
        >
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Status</span>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#34d399' }}>
              {document.status}
            </div>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Pages Processed</span>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#f9fafb' }}>
              {document.page_count ?? document.num_pages} Pages
            </div>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Facts Extracted</span>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#818cf8' }}>
              {document.fact_count ?? 0} Grounded Facts
            </div>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Uploaded Date</span>
            <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-secondary)' }}>
              {new Date(document.created_at).toLocaleDateString()}
            </div>
          </div>
        </div>

        {/* Facts Table Section */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem 1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h4 style={{ fontSize: '14px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
              Facts Extracted From This Document ({facts.length})
            </h4>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Click any fact row to inspect grounded quote & search candidate matches
            </span>
          </div>

          {isLoading ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Loading extracted facts...
            </div>
          ) : error ? (
            <div style={{ padding: '1rem', color: '#f87171' }}>{error}</div>
          ) : facts.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              No facts extracted for this document yet.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', textAlign: 'left' }}>
                    <th style={{ padding: '8px 10px' }}>Entity</th>
                    <th style={{ padding: '8px 10px' }}>Attribute</th>
                    <th style={{ padding: '8px 10px' }}>Value</th>
                    <th style={{ padding: '8px 10px' }}>Period</th>
                    <th style={{ padding: '8px 10px' }}>Scope</th>
                    <th style={{ padding: '8px 10px' }}>Confidence</th>
                    <th style={{ padding: '8px 10px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {facts.map((fact, idx) => (
                    <tr
                      key={fact.id}
                      onClick={() => {
                        onClose();
                        onSelectFact(fact);
                      }}
                      style={{
                        borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                        backgroundColor: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.015)',
                        cursor: 'pointer',
                        transition: 'background-color 0.15s ease',
                      }}
                    >
                      <td style={{ padding: '9px 10px', fontWeight: 600, color: '#f3f4f6' }}>
                        {fact.entity}
                      </td>
                      <td style={{ padding: '9px 10px', color: '#818cf8', fontWeight: 500 }}>
                        {fact.attribute}
                      </td>
                      <td style={{ padding: '9px 10px', color: '#f9fafb' }}>
                        <div>{fact.raw_value}</div>
                        {fact.normalized_value !== null && fact.normalized_value !== undefined && (
                          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                            {fact.normalized_value.toLocaleString()} {fact.unit || ''}
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '9px 10px', color: 'var(--text-secondary)' }}>
                        {fact.time_period || fact.fiscal_year || '—'}
                      </td>
                      <td style={{ padding: '9px 10px', color: 'var(--text-secondary)' }}>
                        {fact.scope || '—'}
                      </td>
                      <td style={{ padding: '9px 10px' }}>
                        <span
                          style={{
                            fontSize: '11px',
                            fontWeight: 600,
                            backgroundColor: 'rgba(16, 185, 129, 0.15)',
                            color: '#34d399',
                            padding: '2px 6px',
                            borderRadius: '4px',
                          }}
                        >
                          {(fact.confidence * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td style={{ padding: '9px 10px' }}>
                        <span
                          style={{
                            fontSize: '10px',
                            fontWeight: 700,
                            backgroundColor: 'rgba(99, 102, 241, 0.15)',
                            color: '#a5b4fc',
                            padding: '2px 6px',
                            borderRadius: '4px',
                          }}
                        >
                          {fact.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
