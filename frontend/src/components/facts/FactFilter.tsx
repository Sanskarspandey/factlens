import React from 'react';
import { FactFilterParams } from '../../types/fact';
import { Search } from 'lucide-react';

interface FactFilterProps {
  filters: FactFilterParams;
  onChange: (filters: FactFilterParams) => void;
}

export const FactFilter: React.FC<FactFilterProps> = ({ filters, onChange }) => {
  return (
    <div
      className="glass-panel"
      style={{
        padding: '1rem',
        display: 'flex',
        gap: '1rem',
        alignItems: 'center',
        flexWrap: 'wrap',
      }}
    >
      <div style={{
        position: 'relative',
        flex: 1,
        minWidth: '220px',
      }}>
        <Search size={16} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-secondary)' }} />
        <input
          type="text"
          placeholder="Search facts, entities, metrics..."
          value={filters.search_query || ''}
          onChange={(e) => onChange({ ...filters, search_query: e.target.value })}
          style={{
            width: '100%',
            padding: '8px 12px 8px 34px',
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-primary)',
            fontSize: '14px',
          }}
        />
      </div>

      <input
        type="text"
        placeholder="Filter by Entity"
        value={filters.entity || ''}
        onChange={(e) => onChange({ ...filters, entity: e.target.value })}
        style={{
          padding: '8px 12px',
          backgroundColor: 'rgba(0, 0, 0, 0.2)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--text-primary)',
          fontSize: '14px',
        }}
      />

      <input
        type="text"
        placeholder="Time Period (e.g. FY2023)"
        value={filters.time_period || ''}
        onChange={(e) => onChange({ ...filters, time_period: e.target.value })}
        style={{
          padding: '8px 12px',
          backgroundColor: 'rgba(0, 0, 0, 0.2)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--text-primary)',
          fontSize: '14px',
        }}
      />
    </div>
  );
};
