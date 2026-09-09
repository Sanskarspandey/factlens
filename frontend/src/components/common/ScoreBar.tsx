import React from 'react';

interface ScoreBarProps {
  label: string;
  score: number; // 0.0 to 1.0
  showPercent?: boolean;
}

export const ScoreBar: React.FC<ScoreBarProps> = ({ label, score, showPercent = true }) => {
  const clampedScore = Math.max(0, Math.min(1, score));
  const percent = Math.round(clampedScore * 100);

  const getColor = (val: number) => {
    if (val >= 0.75) return '#10b981'; // Green
    if (val >= 0.50) return '#6366f1'; // Indigo
    if (val >= 0.30) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  const barColor = getColor(clampedScore);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
        <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
        {showPercent && (
          <span style={{ fontWeight: 600, color: barColor, fontFamily: 'var(--font-mono)' }}>
            {percent}% ({clampedScore.toFixed(2)})
          </span>
        )}
      </div>
      <div
        style={{
          width: '100%',
          height: '6px',
          backgroundColor: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '3px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${percent}%`,
            height: '100%',
            backgroundColor: barColor,
            borderRadius: '3px',
            transition: 'width 0.3s ease',
          }}
        />
      </div>
    </div>
  );
};
