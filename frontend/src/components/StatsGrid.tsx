import React from 'react';
import { Database, Zap, ShieldCheck, Globe } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface StatsGridProps {
    stats: {
        reference: number;
        analyzed: number;
        quality: number;
        sources: { online: number; total: number };
    };
}

export const StatsGrid: React.FC<StatsGridProps> = ({ stats }) => {
    const navigate = useNavigate();
    const items = [
        {
            label: 'Reference Base',
            value: stats.reference.toLocaleString(),
            icon: <Database size={20} />,
            color: 'var(--primary)',
            clickable: true,
            onClick: () => navigate('/news')
        },
        { label: 'AI Analyzed', value: stats.analyzed.toLocaleString(), icon: <Zap size={20} />, color: 'var(--secondary)' },
        { label: 'Quality Index', value: `${stats.quality}%`, icon: <ShieldCheck size={20} />, color: 'var(--success)' },
        { label: 'Live Sources', value: `${stats.sources.online}/${stats.sources.total}`, icon: <Globe size={20} />, color: 'var(--primary)' },
    ];

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', padding: '0 1rem' }}>
            {items.map((item, idx) => (
                <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="glass"
                    onClick={item.onClick}
                    style={{
                        padding: '1.5rem',
                        position: 'relative',
                        overflow: 'hidden',
                        cursor: item.clickable ? 'pointer' : 'default',
                        transition: 'transform 0.2s, box-shadow 0.2s'
                    }}
                    whileHover={item.clickable ? { scale: 1.02, boxShadow: '0 8px 32px rgba(0,0,0,0.3)' } : {}}
                >
                    <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: item.color }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.5rem' }}>{item.label}</div>
                            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-main)' }}>{item.value}</div>
                        </div>
                        <div style={{ color: item.color, opacity: 0.8 }}>{item.icon}</div>
                    </div>
                    <div style={{ marginTop: '1rem', height: '2px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px' }}>
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: '100%' }}
                            transition={{ duration: 1, delay: 0.5 }}
                            style={{ height: '100%', background: item.color, opacity: 0.3 }}
                        />
                    </div>
                </motion.div>
            ))}
        </div>
    );
};
