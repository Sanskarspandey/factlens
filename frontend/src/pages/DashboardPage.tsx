import React, { useState, useEffect } from 'react';
import { ActiveTab } from '../App';
import { statsApi } from '../api/statsApi';
import { documentsApi } from '../api/documentsApi';
import { reconciliationApi } from '../api/reconciliationApi';
import { auditApi } from '../api/auditApi';
import { SystemStats } from '../types/api';
import { Document } from '../types/document';
import { FactRelationship } from '../types/comparison';
import { ExtractionFailureItem } from '../types/audit';
import { RelationshipBadge } from '../components/common/RelationshipBadge';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  FileText,
  CheckCircle2,
  GitCompare,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Layers,
  PlayCircle,
} from 'lucide-react';


interface DashboardPageProps {
  onNavigate: (tab: ActiveTab) => void;
  onSelectDocument?: (doc: Document) => void;
  onSelectComparison?: (rel: FactRelationship) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigate,
  onSelectDocument,
  onSelectComparison,
}) => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [recentDocs, setRecentDocs] = useState<Document[]>([]);
  const [recentReconciliations, setRecentReconciliations] = useState<FactRelationship[]>([]);
  const [recentFailures, setRecentFailures] = useState<ExtractionFailureItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [statsData, docsData, reconsData, failuresData] = await Promise.all([
        statsApi.getStats().catch(() => ({
          documents: 0,
          pages: 0,
          facts: 0,
          reconciliations: 0,
          corroborated: 0,
          contradicted: 0,
          contextually_different: 0,
          uncertain: 0,
        })),
        documentsApi.listDocuments(1, 5).catch(() => ({ items: [], total: 0, page: 1, limit: 5, total_pages: 0 })),
        reconciliationApi.listReconciliations({ limit: 5 }).catch(() => ({ items: [], total: 0, page: 1, limit: 5, total_pages: 0 })),
        auditApi.getFailures(undefined, undefined, 0, 5).catch(() => []),
      ]);

      setStats(statsData);
      setRecentDocs(docsData.items || []);
      setRecentReconciliations(reconsData.items || []);
      setRecentFailures(Array.isArray(failuresData) ? failuresData : []);

    } catch (err: any) {
      setError(err.message || 'Failed to load system dashboard telemetry.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return <LoadingState message="Loading FactLens real-time telemetry..." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {error && <ErrorAlert message={error} onRetry={fetchDashboardData} />}

      {/* Hero / System Overview Banner */}
      <div
        className="glass-panel"
        style={{
          padding: '2rem 2.5rem',
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.08) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1.5rem',
        }}
      >
        <div style={{ maxWidth: '680px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <ShieldCheck size={18} color="#818cf8" />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              FactLens • Evidence-Grounded Fact Intelligence
            </span>
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, color: '#f9fafb', lineHeight: 1.25 }}>
            Don't just extract facts. Verify them.
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '0.6rem', lineHeight: 1.6 }}>
            FactLens extracts source-grounded facts, normalizes their meaning and units, and determines whether cross-document differences represent corroboration, contradiction, contextual variation, or uncertainty.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.25rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => onNavigate('documents')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'var(--accent-primary)',
                color: '#ffffff',
                border: 'none',
                padding: '0.55rem 1.1rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13.5px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <FileText size={15} />
              Ingest PDFs
            </button>
            <button
              onClick={() => onNavigate('compare')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                color: '#f9fafb',
                border: '1px solid var(--border-color)',
                padding: '0.55rem 1.1rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13.5px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <GitCompare size={15} />
              Compare Facts
            </button>
            <button
              onClick={() => onNavigate('demo')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                color: '#a5b4fc',
                border: '1px solid rgba(99, 102, 241, 0.4)',
                padding: '0.55rem 1.1rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13.5px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <PlayCircle size={15} />
              Evaluator Demo Mode
            </button>
          </div>
        </div>

        {/* Quick System Status Card */}
        <div
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.3)',
            padding: '1.25rem 1.5rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
            minWidth: '220px',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
          }}
        >
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            System Health & Indices
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontSize: '13px', fontWeight: 600 }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981' }} />
            Pipeline Online
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Vector Store: <strong>ChromaDB</strong>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Normalization: <strong>Deterministic</strong>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Grounding: <strong>Strict Quote & Page</strong>
          </div>
        </div>
      </div>

      {/* Primary Telemetry Cards */}
      <div>
        <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '0.75rem', letterSpacing: '0.04em' }}>
          Document & Extraction Metrics
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          <div
            className="glass-panel"
            onClick={() => onNavigate('documents')}
            style={{ padding: '1.25rem', cursor: 'pointer', transition: 'border-color 0.15s ease' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span style={{ fontSize: '12.5px', fontWeight: 600 }}>Documents</span>
              <FileText size={18} color="#818cf8" />
            </div>
            <div style={{ fontSize: '26px', fontWeight: 800, color: '#f9fafb', marginTop: '0.5rem' }}>
              {stats?.documents ?? 0}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Ingested PDF documents
            </div>
          </div>

          <div
            className="glass-panel"
            onClick={() => onNavigate('documents')}
            style={{ padding: '1.25rem', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span style={{ fontSize: '12.5px', fontWeight: 600 }}>Pages Processed</span>
              <Layers size={18} color="#38bdf8" />
            </div>
            <div style={{ fontSize: '26px', fontWeight: 800, color: '#f9fafb', marginTop: '0.5rem' }}>
              {stats?.pages ?? 0}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Extracted via PyMuPDF
            </div>
          </div>

          <div
            className="glass-panel"
            onClick={() => onNavigate('facts')}
            style={{ padding: '1.25rem', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span style={{ fontSize: '12.5px', fontWeight: 600 }}>Facts Extracted</span>
              <CheckCircle2 size={18} color="#34d399" />
            </div>
            <div style={{ fontSize: '26px', fontWeight: 800, color: '#f9fafb', marginTop: '0.5rem' }}>
              {stats?.facts ?? 0}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Grounded with quotes & indexed
            </div>
          </div>

          <div
            className="glass-panel"
            onClick={() => onNavigate('reconciliation')}
            style={{ padding: '1.25rem', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span style={{ fontSize: '12.5px', fontWeight: 600 }}>Reconciliations</span>
              <GitCompare size={18} color="#a855f7" />
            </div>
            <div style={{ fontSize: '26px', fontWeight: 800, color: '#f9fafb', marginTop: '0.5rem' }}>
              {stats?.reconciliations ?? 0}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Evaluated fact pairs
            </div>
          </div>
        </div>
      </div>

      {/* 4-Way Reconciliation Status Cards */}
      <div>
        <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '0.75rem', letterSpacing: '0.04em' }}>
          Reconciliation Breakdown (4-Way Logic)
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          {/* Corroborated */}
          <div
            className="glass-panel"
            onClick={() => onNavigate('reconciliation')}
            style={{
              padding: '1.25rem',
              cursor: 'pointer',
              borderLeft: '4px solid #10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.05)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#34d399' }}>✓ CORROBORATED</span>
            </div>
            <div style={{ fontSize: '24px', fontWeight: 800, color: '#f9fafb', marginTop: '0.5rem' }}>
              {stats?.corroborated ?? 0}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Identical contexts, equal values
            </div>
          </div>

          {/* Contradicted */}
          <div
            className="glass-panel"
            onClick={() => onNavigate('reconciliation')}
            style={{
              padding: '1.25rem',
              cursor: 'pointer',
              borderLeft: '4px solid #ef4444',
              backgroundColor: 'rgba(239, 68, 68, 0.05)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#f87171' }}>! CONTRADICTED</span>
            </div>
            <div style={{ fontSize: '24px', fontWeight: 800, color: '#f9fafb', marginTop: '0.5rem' }}>
              {stats?.contradicted ?? 0}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Matching context, conflicting values
            </div>
          </div>

          {/* Contextually Different */}
          <div
            className="glass-panel"
            onClick={() => onNavigate('reconciliation')}
            style={{
              padding: '1.25rem',
              cursor: 'pointer',
              borderLeft: '4px solid #f59e0b',
              backgroundColor: 'rgba(245, 158, 11, 0.05)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#fbbf24' }}>↔ CONTEXTUAL DIFF</span>
            </div>
            <div style={{ fontSize: '24px', fontWeight: 800, color: '#f9fafb', marginTop: '0.5rem' }}>
              {stats?.contextually_different ?? 0}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Scope, geography or period differs
            </div>
          </div>

          {/* Uncertain */}
          <div
            className="glass-panel"
            onClick={() => onNavigate('audit')}
            style={{
              padding: '1.25rem',
              cursor: 'pointer',
              borderLeft: '4px solid #8b5cf6',
              backgroundColor: 'rgba(139, 92, 246, 0.05)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#c084fc' }}>? UNCERTAIN</span>
            </div>
            <div style={{ fontSize: '24px', fontWeight: 800, color: '#f9fafb', marginTop: '0.5rem' }}>
              {stats?.uncertain ?? 0}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Insufficient grounding or ambiguity
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity Sections (Documents, Reconciliations, Failures) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
        {/* Recent Documents */}
        <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.6rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText size={16} color="#818cf8" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#f9fafb' }}>Recent Documents</h3>
            </div>
            <button
              onClick={() => onNavigate('documents')}
              style={{ background: 'none', border: 'none', color: '#818cf8', fontSize: '12px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '3px' }}
            >
              View All <ArrowRight size={12} />
            </button>
          </div>

          {recentDocs.length === 0 ? (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              No documents uploaded yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {recentDocs.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => onSelectDocument?.(doc)}
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    padding: '0.65rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: onSelectDocument ? 'pointer' : 'default',
                  }}
                >
                  <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '220px' }}>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#f3f4f6' }}>{doc.filename}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      {doc.page_count ?? doc.num_pages} Pages • {doc.fact_count ?? 0} Facts
                    </div>

                  </div>
                  <span
                    style={{
                      fontSize: '10px',
                      fontWeight: 700,
                      backgroundColor: 'rgba(16, 185, 129, 0.15)',
                      color: '#34d399',
                      padding: '2px 6px',
                      borderRadius: '4px',
                    }}
                  >
                    {doc.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Reconciliations */}
        <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.6rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <GitCompare size={16} color="#a855f7" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#f9fafb' }}>Recent Reconciliations</h3>
            </div>
            <button
              onClick={() => onNavigate('reconciliation')}
              style={{ background: 'none', border: 'none', color: '#818cf8', fontSize: '12px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '3px' }}
            >
              View All <ArrowRight size={12} />
            </button>
          </div>

          {recentReconciliations.length === 0 ? (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              No reconciliation runs executed yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {recentReconciliations.map((rel) => (
                <div
                  key={rel.id}
                  onClick={() => onSelectComparison?.(rel)}
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    padding: '0.65rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: onSelectComparison ? 'pointer' : 'default',
                  }}
                >
                  <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '200px' }}>
                    <div style={{ fontSize: '12.5px', fontWeight: 600, color: '#f3f4f6' }}>
                      {rel.fact_a?.attribute || 'Metric'}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      {rel.fact_a?.entity} • {rel.fact_a?.time_period || 'Period'}
                    </div>
                  </div>
                  <RelationshipBadge relationship={rel.relationship} size="sm" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Audit / Uncertainties */}
        <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.6rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle size={16} color="#fbbf24" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#f9fafb' }}>Audit & Failures</h3>
            </div>
            <button
              onClick={() => onNavigate('audit')}
              style={{ background: 'none', border: 'none', color: '#818cf8', fontSize: '12px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '3px' }}
            >
              View Audit Log <ArrowRight size={12} />
            </button>
          </div>

          {recentFailures.length === 0 && (!stats || stats.uncertain === 0) ? (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: '#34d399', fontSize: '13px' }}>
              ✓ No active extraction failures or ungrounded anomalies.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {recentFailures.slice(0, 3).map((fail) => (
                <div
                  key={fail.id}
                  style={{
                    backgroundColor: 'rgba(239, 68, 68, 0.05)',
                    padding: '0.6rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    fontSize: '12px',
                  }}
                >
                  <div style={{ fontWeight: 600, color: '#f87171' }}>
                    {fail.stage}: {fail.error_type}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px', marginTop: '2px' }}>
                    {fail.error_message}
                  </div>
                </div>
              ))}
              {stats && stats.uncertain > 0 && (
                <div
                  style={{
                    backgroundColor: 'rgba(139, 92, 246, 0.08)',
                    padding: '0.6rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid rgba(139, 92, 246, 0.25)',
                    fontSize: '12px',
                    color: '#c084fc',
                  }}
                >
                  <strong>{stats.uncertain}</strong> uncertain relationship cases preserved for audit.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
