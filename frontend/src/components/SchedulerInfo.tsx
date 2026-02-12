import React from 'react';
import { Calendar, Repeat } from 'lucide-react';

interface SchedulerInfoProps {
    scheduler: any;
}

export const SchedulerInfo: React.FC<SchedulerInfoProps> = ({ scheduler }) => {
    if (!scheduler) return null;

    const fmtNext = (iso: string) => {
        if (!iso) return 'Pending...';
        const diff = new Date(iso).getTime() - new Date().getTime();
        if (diff < 0) return 'Running...';
        if (diff > 3600000) return Math.floor(diff / 3600000) + 'h ' + Math.floor((diff % 3600000) / 60000) + 'm';
        return Math.floor(diff / 60000) + 'm';
    };

    const tasks = [
        { name: 'Crawler Pipeline', data: scheduler.collect_pipeline },
        { name: 'Source Monitor', data: scheduler.check_sources },
    ];

    return (
        <div className="section" style={{ padding: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <Calendar size={18} color="var(--primary)" />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Automation Ops</h3>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                {tasks.map((task, i) => (
                    <div key={i} className="glass" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--primary)' }}>{task.name}</div>
                            <Repeat size={14} style={{ opacity: 0.5 }} />
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Next run in:</span>
                            <span className="mono" style={{ color: 'var(--success)' }}>{fmtNext(task.data?.next_run)}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Last run:</span>
                            <span className="mono">{task.data?.last_run ? new Date(task.data.last_run).toLocaleTimeString() : 'Never'}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
