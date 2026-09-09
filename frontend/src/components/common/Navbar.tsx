import React from 'react';
import { ActiveTab } from '../../App';
import { Layers, FileText, CheckCircle2, GitCompare, Network, AlertTriangle, PlayCircle, FlaskConical } from 'lucide-react';

interface NavbarProps {
  activeTab: ActiveTab;
  onSelectTab: (tab: ActiveTab) => void;
  onLoadDemo?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, onSelectTab, onLoadDemo }) => {
  const navItems: { key: ActiveTab; label: string; icon: React.ReactNode }[] = [
    { key: 'dashboard', label: 'Dashboard', icon: <Layers size={17} /> },
    { key: 'documents', label: 'Documents', icon: <FileText size={17} /> },
    { key: 'facts', label: 'Facts', icon: <CheckCircle2 size={17} /> },
    { key: 'compare', label: 'Compare', icon: <GitCompare size={17} /> },
    { key: 'reconciliation', label: 'Reconciliation', icon: <Network size={17} /> },
    { key: 'evaluation', label: 'Evaluation Lab', icon: <FlaskConical size={17} /> },
    { key: 'audit', label: 'Audit & Failures', icon: <AlertTriangle size={17} /> },
    { key: 'demo', label: 'Demo Cases', icon: <PlayCircle size={17} /> },
  ];

  return (
    <header style={{
      borderBottom: '1px solid var(--border-color)',
      backgroundColor: 'rgba(11, 15, 25, 0.92)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '0 2rem',
    }}>
      <div style={{
        maxWidth: '1480px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '68px',
      }}>
        {/* Brand & Subtitle */}
        <div
          style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', cursor: 'pointer' }}
          onClick={() => onSelectTab('dashboard')}
        >
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '9px',
            background: 'var(--accent-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '18px',
            color: '#ffffff',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
          }}>
            FL
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '-0.02em', color: '#f9fafb' }}>Fact</span>
              <span style={{ fontSize: '18px', fontWeight: 800, color: 'var(--accent-primary)', letterSpacing: '-0.02em' }}>Lens</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 500, letterSpacing: '0.01em' }}>
              Evidence-grounded cross-document fact intelligence
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '0.35rem' }}>
          {navItems.map((item) => {
            const isActive = activeTab === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onSelectTab(item.key)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  padding: '0.5rem 0.85rem',
                  borderRadius: 'var(--radius-md)',
                  border: 'none',
                  fontSize: '13.5px',
                  fontWeight: isActive ? 600 : 500,
                  cursor: 'pointer',
                  backgroundColor: isActive ? 'rgba(99, 102, 241, 0.18)' : 'transparent',
                  color: isActive ? '#a5b4fc' : 'var(--text-secondary)',
                  borderBottom: isActive ? '2px solid var(--accent-primary)' : '2px solid transparent',
                  transition: 'all 0.15s ease',
                }}
              >
                {item.icon}
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Quick Action */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {onLoadDemo && (
            <button
              onClick={onLoadDemo}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                color: '#a5b4fc',
                border: '1px solid rgba(99, 102, 241, 0.4)',
                padding: '0.4rem 0.85rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              <PlayCircle size={15} />
              Quick Demo
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
