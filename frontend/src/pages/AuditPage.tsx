import React, { useState, useEffect } from 'react';
import { auditApi } from '../api/auditApi';
import { factsApi } from '../api/factsApi';
import { ExtractionFailureItem, UncertainFactItem, UncertainReconciliationItem } from '../types/audit';
import { Fact } from '../types/fact';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  HelpCircle,
  ShieldAlert,
  AlertTriangle,
  Sparkles,
  BookmarkCheck,
} from 'lucide-react';

interface AuditPageProps {
  onSelectComparison?: (rel: any) => void;
}

export const AuditPage: React.FC<AuditPageProps> = () => {
  const [activeTab, setActiveTab] = useState<'grounding' | 'extraction' | 'uncertainties' | 'synthetic'>('grounding');
  const [failures, setFailures] = useState<ExtractionFailureItem[]>([]);
  const [uncertainFacts, setUncertainFacts] = useState<UncertainFactItem[]>([]);
  const [uncertainReconciliations, setUncertainReconciliations] = useState<UncertainReconciliationItem[]>([]);
  const [demoFacts, setDemoFacts] = useState<Fact[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAuditData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [failuresRes, uncertaintiesRes, factsRes] = await Promise.all([
        auditApi.getFailures(undefined, undefined, 0, 100).catch(() => []),
        auditApi.getUncertainties().catch(() => ({ uncertain_facts: [], uncertain_reconciliations: [] })),
        factsApi.getFacts({}, 0, 100).catch(() => [] as Fact[]),
      ]);

      setFailures(Array.isArray(failuresRes) ? failuresRes : []);
      setUncertainFacts(uncertaintiesRes.uncertain_facts || []);
      setUncertainReconciliations(uncertaintiesRes.uncertain_reconciliations || []);

      const allFacts: Fact[] = Array.isArray(factsRes) ? factsRes : [];
      const synthetic = allFacts.filter(
        (f: Fact) => f.source_type === 'SYNTHETIC_DEMO' || f.id.startsWith('fact_demo_') || f.document_id.startsWith('doc_demo_')
      );
      setDemoFacts(synthetic);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch system audit logs.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditData();
  }, []);

  const groundingFailures = failures.filter((f) => f.stage === 'GROUNDING_VERIFICATION' || f.error_type === 'UNGROUNDED_QUOTE');
  const extractionFailures = failures.filter((f) => f.stage !== 'GROUNDING_VERIFICATION' && f.error_type !== 'UNGROUNDED_QUOTE');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#f9fafb' }}>
            Audit, Provenance & Uncertainty Registry
          </h2>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Preserving extraction caveats, grounding failures, and transparently isolating synthetic demo fixtures
          </div>
        </div>

        {/* 4-way Tab switch */}
        <div
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            padding: '3px',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            border: '1px solid var(--border-color)',
            flexWrap: 'wrap',
          }}
        >
          <button
            onClick={() => setActiveTab('grounding')}
            style={{
              padding: '0.45rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: activeTab === 'grounding' ? 'rgba(239, 68, 68, 0.25)' : 'transparent',
              color: activeTab === 'grounding' ? '#f87171' : 'var(--text-secondary)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <ShieldAlert size={13} />
            Grounding Failures ({groundingFailures.length})
          </button>
          <button
            onClick={() => setActiveTab('extraction')}
            style={{
              padding: '0.45rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: activeTab === 'extraction' ? 'rgba(245, 158, 11, 0.25)' : 'transparent',
              color: activeTab === 'extraction' ? '#fbbf24' : 'var(--text-secondary)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <AlertTriangle size={13} />
            Extraction Failures ({extractionFailures.length})
          </button>
          <button
            onClick={() => setActiveTab('uncertainties')}
            style={{
              padding: '0.45rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: activeTab === 'uncertainties' ? 'rgba(139, 92, 246, 0.25)' : 'transparent',
              color: activeTab === 'uncertainties' ? '#c084fc' : 'var(--text-secondary)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <HelpCircle size={13} />
            Uncertain Facts ({uncertainFacts.length + uncertainReconciliations.length})
          </button>
          <button
            onClick={() => setActiveTab('synthetic')}
            style={{
              padding: '0.45rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              backgroundColor: activeTab === 'synthetic' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
              color: activeTab === 'synthetic' ? '#a5b4fc' : 'var(--text-secondary)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <Sparkles size={13} />
            Synthetic Demo Fixtures ({demoFacts.length})
          </button>
        </div>
      </div>

      {error && <ErrorAlert message={error} onRetry={fetchAuditData} />}

      {/* Core Principle Banner */}
      <div
        style={{
          padding: '1rem 1.25rem',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(139, 92, 246, 0.08)',
          border: '1px solid rgba(139, 92, 246, 0.25)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.75rem',
        }}
      >
        <BookmarkCheck size={18} color="#c084fc" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: '13px', color: '#e9d5ff', lineHeight: 1.5 }}>
          <strong>Core Product Principle:</strong> FactLens preserves uncertain or failed results instead of converting them into unsupported conclusions.
        </div>
      </div>

      {isLoading ? (
        <LoadingState message="Loading system audit telemetry..." />
      ) : activeTab === 'grounding' ? (
        /* Grounding Failures Tab */
        <div>
          <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#f3f4f6', marginBottom: '0.75rem' }}>
            Grounding Verification Failures ({groundingFailures.length})
          </h3>
          {groundingFailures.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: 'rgba(16, 185, 129, 0.05)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.25)', color: '#34d399', fontSize: '13.5px' }}>
              ✓ All extracted statements were strictly grounded in source page text.
            </div>
          ) : (
            <div className="glass-panel" style={{ overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                    <th style={{ padding: '10px 14px', width: '20%' }}>Document / Page</th>
                    <th style={{ padding: '10px 14px', width: '20%' }}>Error Type</th>
                    <th style={{ padding: '10px 14px', width: '60%' }}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {groundingFailures.map((f, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '10px 14px', fontWeight: 600 }}>{f.document_filename || f.document_id} (p.{f.page_number})</td>
                      <td style={{ padding: '10px 14px', color: '#f87171' }}>{f.error_type}</td>
                      <td style={{ padding: '10px 14px', color: '#e2e8f0' }}>{f.error_message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : activeTab === 'extraction' ? (
        /* Extraction Failures Tab */
        <div>
          <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#f3f4f6', marginBottom: '0.75rem' }}>
            Pipeline Extraction Failures ({extractionFailures.length})
          </h3>
          {extractionFailures.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: 'rgba(16, 185, 129, 0.05)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.25)', color: '#34d399', fontSize: '13.5px' }}>
              ✓ Zero unhandled parsing exceptions recorded across all ingested pages.
            </div>
          ) : (
            <div className="glass-panel" style={{ overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                    <th style={{ padding: '10px 14px', width: '20%' }}>Document / Page</th>
                    <th style={{ padding: '10px 14px', width: '15%' }}>Stage</th>
                    <th style={{ padding: '10px 14px', width: '20%' }}>Error Type</th>
                    <th style={{ padding: '10px 14px', width: '45%' }}>Error Message</th>
                  </tr>
                </thead>
                <tbody>
                  {extractionFailures.map((f, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '10px 14px', fontWeight: 600 }}>{f.document_filename || f.document_id} (p.{f.page_number})</td>
                      <td style={{ padding: '10px 14px', color: '#a5b4fc' }}>{f.stage}</td>
                      <td style={{ padding: '10px 14px', color: '#fbbf24' }}>{f.error_type}</td>
                      <td style={{ padding: '10px 14px', color: '#e2e8f0' }}>{f.error_message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : activeTab === 'uncertainties' ? (
        /* Uncertain Facts Tab */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#f3f4f6', marginBottom: '0.75rem' }}>
              Uncertain & Ambiguous Facts ({uncertainFacts.length})
            </h3>
            {uncertainFacts.length === 0 ? (
              <div style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-color)', color: 'var(--text-muted)', fontSize: '13px' }}>
                No uncertain facts in catalogue.
              </div>
            ) : (
              <div className="glass-panel" style={{ overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                      <th style={{ padding: '10px 14px', width: '25%' }}>Document & Entity</th>
                      <th style={{ padding: '10px 14px', width: '40%' }}>Extracted Statement</th>
                      <th style={{ padding: '10px 14px', width: '15%' }}>Confidence</th>
                      <th style={{ padding: '10px 14px', width: '20%' }}>Uncertainty Note</th>
                    </tr>
                  </thead>
                  <tbody>
                    {uncertainFacts.map((f, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '10px 14px', fontWeight: 600 }}>{f.entity || 'Unknown'} • {f.document_id}</td>
                        <td style={{ padding: '10px 14px', color: '#f3f4f6' }}>{f.statement}</td>
                        <td style={{ padding: '10px 14px', color: '#fbbf24' }}>{(f.confidence * 100).toFixed(0)}%</td>
                        <td style={{ padding: '10px 14px', color: '#e9d5ff', fontSize: '12px' }}>{f.uncertainty_notes || 'Preserved caveat'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Synthetic Demo Fixtures Tab */
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#f3f4f6' }}>
              Synthetic Evaluator Fixtures ({demoFacts.length})
            </h3>
            <span style={{ fontSize: '11.5px', color: '#fbbf24', backgroundColor: 'rgba(245, 158, 11, 0.15)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
              ⚡ Isolated Test Fixtures (Not Real PDF Claims)
            </span>
          </div>

          <div className="glass-panel" style={{ overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
                  <th style={{ padding: '10px 14px', width: '20%' }}>Fixture ID & Entity</th>
                  <th style={{ padding: '10px 14px', width: '45%' }}>Synthetic Statement</th>
                  <th style={{ padding: '10px 14px', width: '15%' }}>Value & Period</th>
                  <th style={{ padding: '10px 14px', width: '20%' }}>Test Intent</th>
                </tr>
              </thead>
              <tbody>
                {demoFacts.map((df, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '10px 14px' }}>
                      <div style={{ fontWeight: 600, color: '#fbbf24' }}>{df.id}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{df.entity} • {df.attribute}</div>
                    </td>
                    <td style={{ padding: '10px 14px', color: '#f3f4f6' }}>
                      {df.statement}
                    </td>
                    <td style={{ padding: '10px 14px', color: '#a5b4fc', fontFamily: 'var(--font-mono)' }}>
                      {df.raw_value} • {df.time_period || df.fiscal_year}
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {df.id.includes('corroborate') ? 'Corroboration Benchmark' : df.id.includes('contradict') ? 'Contradiction Benchmark' : df.id.includes('scope') ? 'Scope Isolation Benchmark' : 'Uncertainty Benchmark'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
