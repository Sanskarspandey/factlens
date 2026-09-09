import React, { useState } from 'react';
import { Navbar } from './components/common/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { FactsPage } from './pages/FactsPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { ReconciliationPage } from './pages/ReconciliationPage';
import { AuditPage } from './pages/AuditPage';
import { DemoPage } from './pages/DemoPage';
import { EvaluationLabPage } from './pages/EvaluationLabPage';
import { Fact } from './types/fact';
import { FactRelationship } from './types/comparison';
import { demoApi } from './api/demoApi';

export type ActiveTab =
  | 'dashboard'
  | 'documents'
  | 'facts'
  | 'compare'
  | 'reconciliation'
  | 'audit'
  | 'evaluation'
  | 'demo';

export const App: React.FC = () => {
  const getInitialTab = (): ActiveTab => {
    const hash = window.location.hash.replace('#', '').toLowerCase();
    const validTabs: ActiveTab[] = [
      'dashboard',
      'documents',
      'facts',
      'compare',
      'reconciliation',
      'audit',
      'evaluation',
      'demo',
    ];
    return validTabs.includes(hash as ActiveTab) ? (hash as ActiveTab) : 'dashboard';
  };

  const [activeTab, setActiveTabState] = useState<ActiveTab>(getInitialTab);

  const handleSelectTab = (tab: ActiveTab) => {
    setActiveTabState(tab);
    window.location.hash = tab;
  };

  React.useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash.replace('#', '').toLowerCase();
      const validTabs: ActiveTab[] = [
        'dashboard',
        'documents',
        'facts',
        'compare',
        'reconciliation',
        'audit',
        'evaluation',
        'demo',
      ];
      if (validTabs.includes(hash as ActiveTab)) {
        setActiveTabState(hash as ActiveTab);
      }
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  // Shared navigation state
  const [selectedFactId, setSelectedFactId] = useState<string | null>(null);
  const [compareFactAId, setCompareFactAId] = useState<string | null>(null);
  const [compareFactBId, setCompareFactBId] = useState<string | null>(null);
  const [selectedRelationship, setSelectedRelationship] = useState<FactRelationship | null>(null);

  const handleNavigateToCompare = (factAId?: string, factBId?: string) => {
    if (factAId) setCompareFactAId(factAId);
    if (factBId) setCompareFactBId(factBId);
    setSelectedRelationship(null);
    handleSelectTab('compare');
  };

  const handleSelectComparison = (rel: FactRelationship) => {
    setSelectedRelationship(rel);
    if (rel.fact_a?.id) setCompareFactAId(rel.fact_a.id);
    if (rel.fact_b?.id) setCompareFactBId(rel.fact_b.id);
    handleSelectTab('compare');
  };

  const handleSelectFact = (fact: Fact) => {
    setSelectedFactId(fact.id);
    handleSelectTab('facts');
  };

  const handleQuickDemo = async () => {
    try {
      await demoApi.seedDemo();
    } catch (e) {
      console.error('Quick demo seed:', e);
    }
    handleSelectTab('evaluation');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-primary)' }}>
      <Navbar activeTab={activeTab} onSelectTab={handleSelectTab} onLoadDemo={handleQuickDemo} />
      <main style={{ flex: 1, padding: '2rem', maxWidth: '1480px', margin: '0 auto', width: '100%' }}>
        {activeTab === 'dashboard' && (
          <DashboardPage
            onNavigate={handleSelectTab}
            onSelectComparison={handleSelectComparison}
          />
        )}
        {activeTab === 'documents' && (
          <DocumentsPage onSelectFact={handleSelectFact} />
        )}
        {activeTab === 'facts' && (
          <FactsPage
            onCompareFacts={handleNavigateToCompare}
            selectedFactId={selectedFactId}
          />
        )}
        {activeTab === 'compare' && (
          <ComparisonPage
            initialFactAId={compareFactAId}
            initialFactBId={compareFactBId}
            initialRelationship={selectedRelationship}
          />
        )}
        {activeTab === 'reconciliation' && (
          <ReconciliationPage
            onSelectComparison={handleSelectComparison}
            onSelectFact={handleSelectFact}
          />
        )}
        {activeTab === 'audit' && (
          <AuditPage onSelectComparison={handleSelectComparison} />
        )}
        {activeTab === 'evaluation' && (
          <EvaluationLabPage onNavigateToCompare={handleNavigateToCompare} />
        )}
        {activeTab === 'demo' && (
          <DemoPage
            onSelectComparison={handleSelectComparison}
            onComparePair={handleNavigateToCompare}
          />
        )}
      </main>
    </div>
  );
};

export default App;
