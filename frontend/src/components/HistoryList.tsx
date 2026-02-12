import React from 'react';
import { Clock } from 'lucide-react';
import { motion } from 'framer-motion';

interface HistoryListProps {
    entries: any[];
}

export const HistoryList: React.FC<HistoryListProps> = ({ entries }) => {
    return (
        <div className="section" style={{ padding: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <Clock size={18} color="var(--primary)" />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Recent Activity</h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {entries.length === 0 ? (
                    <div className="glass flex-center" style={{ height: '100px', color: 'var(--text-muted)' }}>
                        No recent verifications
                    </div>
                ) : (
                    entries.map((item, idx) => {
                        const v = item.result?.veredito || '?';
                        const isFake = v.includes('FALSO') && !v.includes('PARCIALMENTE');
                        const isTrue = v.includes('VERDADEIRO');
                        const isPartial = v.includes('PARCIALMENTE');

                        let badgeColor = 'var(--primary)';
                        if (isFake) badgeColor = 'var(--danger)';
                        if (isTrue) badgeColor = 'var(--success)';
                        if (isPartial) badgeColor = 'var(--warning)';

                        return (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="glass"
                                style={{ padding: '1rem', borderLeft: `3px solid ${badgeColor}` }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                                            {item.claim.slice(0, 80)}{item.claim.length > 80 ? '...' : ''}
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            <span>{new Date(item.timestamp).toLocaleString()}</span>
                                            <span>•</span>
                                            <span>{item.result?.confianca}% Confidence</span>
                                        </div>
                                    </div>
                                    <div
                                        className="mono"
                                        style={{
                                            fontSize: '0.7rem',
                                            background: `${badgeColor}11`,
                                            color: badgeColor,
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            border: `1px solid ${badgeColor}33`,
                                            whiteSpace: 'nowrap'
                                        }}
                                    >
                                        {v}
                                    </div>
                                </div>
                            </motion.div>
                        );
                    })
                )}
            </div>
        </div>
    );
};
