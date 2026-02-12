import React from 'react';
import { Globe, RefreshCw, AlertCircle } from 'lucide-react';

interface SourcesListProps {
    sources: Record<string, any>;
}

export const SourcesList: React.FC<SourcesListProps> = ({ sources }) => {
    return (
        <div className="section" style={{ padding: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <Globe size={18} color="var(--primary)" />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Media Intelligence Sources</h3>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.75rem' }}>
                {Object.entries(sources).map(([name, status]) => (
                    <div key={name} className="glass" style={{ padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div
                            style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                background: status.status === 'online' ? 'var(--success)' : 'var(--danger)',
                                boxShadow: status.status === 'online' ? '0 0 10px var(--success)' : '0 0 10px var(--danger)'
                            }}
                        />
                        <div style={{ flex: 1 }}>
                            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{name}</div>
                            <div className="mono" style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                                {status.http_code ? `HTTP ${status.http_code}` : status.error || 'OFFLINE'}
                            </div>
                        </div>
                        {status.status === 'online' ? <RefreshCw size={12} className="animate-spin" style={{ opacity: 0.3 }} /> : <AlertCircle size={12} color="var(--danger)" />}
                    </div>
                ))}
            </div>
        </div>
    );
};
