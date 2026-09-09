import React from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: string;
  color?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon,
  trend,
  color = 'var(--accent-primary)',
}) => {
  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.25rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <div>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 500 }}>{label}</p>
        <h4 style={{ fontSize: '24px', fontWeight: 700, marginTop: '4px', color: 'var(--text-primary)' }}>{value}</h4>
        {trend && <p style={{ fontSize: '12px', color: '#10b981', marginTop: '2px' }}>{trend}</p>}
      </div>
      {icon && (
        <div style={{
          width: '44px',
          height: '44px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: color,
        }}>
          {icon}
        </div>
      )}
    </div>
  );
};
