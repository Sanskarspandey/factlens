import React from 'react';
import { ReconciliationSession } from '../../types/comparison';

import { Card } from '../common/Card';
import { ComparisonMatrix } from './ComparisonMatrix';
import { StatCard } from '../common/StatCard';
import { CheckCircle2, XCircle, Clock, HelpCircle } from 'lucide-react';

interface ReconciliationViewProps {
  session?: ReconciliationSession;
}

export const ReconciliationView: React.FC<ReconciliationViewProps> = ({ session }) => {
  const stats = session?.summary_stats || {
    total_comparisons: 0,
    corroborated_count: 0,
    contradicted_count: 0,
    contextually_different_count: 0,
    uncertain_count: 0,
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        <StatCard
          label="Corroborated"
          value={stats.corroborated_count}
          icon={<CheckCircle2 size={24} />}
          color="var(--color-corroborated)"
        />
        <StatCard
          label="Contradicted"
          value={stats.contradicted_count}
          icon={<XCircle size={24} />}
          color="var(--color-contradicted)"
        />
        <StatCard
          label="Contextually Different"
          value={stats.contextually_different_count}
          icon={<Clock size={24} />}
          color="var(--color-contextual)"
        />
        <StatCard
          label="Uncertain / Ambiguous"
          value={stats.uncertain_count}
          icon={<HelpCircle size={24} />}
          color="var(--color-uncertain)"
        />
      </div>

      {/* Comparisons Feed */}
      <Card title="Cross-Document Fact Comparisons & Reconciled Claims">
        <ComparisonMatrix relationships={session?.relationships || []} />
      </Card>
    </div>
  );
};
