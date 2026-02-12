import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import { motion } from 'framer-motion';
import { ArrowLeft, ExternalLink, Calendar, Link as LinkIcon, Newspaper } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '';

import { Navbar } from '../components/Navbar';
import { UserButton } from '@clerk/clerk-react';

interface NewsCatalogProps {
    isDarkMode: boolean;
    toggleTheme: () => void;
}

export const NewsCatalog: React.FC<NewsCatalogProps> = ({ isDarkMode, toggleTheme }) => {
    const { user } = useUser();
    const navigate = useNavigate();
    const [news, setNews] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [apiKey] = useState(localStorage.getItem('vortex_api_key') || '');
    const [statusData, setStatusData] = useState<any>(null);

    const fetchNews = async () => {
        const headers: any = { 'Content-Type': 'application/json' };
        if (apiKey) headers['X-API-Key'] = apiKey;
        if (user?.id) headers['X-User-ID'] = user.id;

        try {
            const [newsRes, statusRes] = await Promise.all([
                fetch(`${API_BASE}/api/news?limit=100`, { headers }),
                fetch(`${API_BASE}/api/status`, { headers })
            ]);

            if (newsRes.ok) {
                const data = await newsRes.json();
                setNews(data.articles || []);
            }
            if (statusRes.ok) {
                const data = await statusRes.json();
                setStatusData(data);
            }
        } catch (e) {
            console.error('Failed to fetch news:', e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNews();
    }, []);

    return (
        <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 2rem 4rem 2rem', paddingTop: '5rem' }}>
            <Navbar
                isOnline={!!statusData}
                uptime={statusData ? `${Math.floor(statusData.uptime_seconds / 3600)}h ${Math.floor((statusData.uptime_seconds % 3600) / 60)}m` : '0h 0m'}
                isDarkMode={isDarkMode}
                toggleTheme={toggleTheme}
            >
                <UserButton afterSignOutUrl="/" />
            </Navbar>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: '1rem 0 2rem 0' }}>
                <button
                    onClick={() => navigate('/')}
                    className="glass"
                    style={{
                        padding: '0.6rem',
                        borderRadius: '0.6rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--primary)',
                        transition: 'all 0.2s'
                    }}
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="text-gradient" style={{ fontSize: '1.5rem', fontWeight: 800 }}>NEWS CATALOG</h1>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '1px' }}>VORTEX REFERENCE BASE / {news.length} ARTICLES</p>
                </div>
            </div>

            {loading ? (
                <div className="flex-center" style={{ minHeight: '400px', flexDirection: 'column', gap: '1rem' }}>
                    <div className="glow-primary" style={{ width: '40px', height: '40px', border: '3px solid var(--primary)', borderRadius: '50%', borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }} />
                    <p className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>SYNCHRONIZING DATABASE...</p>
                </div>
            ) : news.length === 0 ? (
                <div className="glass" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    <Newspaper size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
                    <p>No news articles found in the reference base.</p>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '1.5rem' }}>
                    {news.map((item, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.02 }}
                            className="glass"
                            style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                                <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)', lineHeight: 1.4, flex: 1 }}>{item.titulo}</h3>
                                <a
                                    href={item.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{ color: 'var(--primary)', opacity: 0.6, paddingTop: '4px' }}
                                    title="View Original"
                                >
                                    <ExternalLink size={18} />
                                </a>
                            </div>

                            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                                {item.subtitulo || item.sumario || (item.corpo_do_texto?.slice(0, 150) + '...')}
                            </p>

                            <div style={{ marginTop: 'auto', display: 'flex', flexWrap: 'wrap', gap: '0.8rem' }}>
                                {item.data_publicacao && (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.7rem', color: 'var(--text-dim)', background: 'var(--bg-card)', padding: '4px 8px', borderRadius: '4px' }}>
                                        <Calendar size={12} />
                                        {item.data_publicacao}
                                    </div>
                                )}
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.7rem', color: 'var(--text-dim)', background: 'var(--bg-card)', padding: '4px 8px', borderRadius: '4px' }}>
                                    <LinkIcon size={12} />
                                    {new URL(item.url).hostname}
                                </div>
                                <div style={{ marginLeft: 'auto', fontSize: '0.65rem', fontWeight: 700, color: 'var(--primary)', opacity: 0.5, letterSpacing: '1px' }}>
                                    {item.status_verificacao || 'UNCHECKED'}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
};
