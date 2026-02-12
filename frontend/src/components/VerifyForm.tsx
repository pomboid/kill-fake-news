import React, { useState } from 'react';
import { Search, Loader2, AlertTriangle, CheckCircle2, HelpCircle, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface VerifyFormProps {
    onVerify: (claim: string) => Promise<any>;
}

export const VerifyForm: React.FC<VerifyFormProps> = ({ onVerify }) => {
    const [claim, setClaim] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [progress, setProgress] = useState(0);

    const handleVerify = async () => {
        if (claim.length < 10) return;
        setLoading(true);
        setResult(null);
        setProgress(10);

        // Fake progress steps
        const interval = setInterval(() => {
            setProgress(p => (p < 90 ? p + (90 - p) * 0.1 : p));
        }, 1000);

        try {
            const data = await onVerify(claim);
            setResult(data);
            setProgress(100);
        } catch (e: any) {
            setResult({ error: e.message });
        } finally {
            clearInterval(interval);
            setLoading(false);
            setTimeout(() => setProgress(0), 1000);
        }
    };

    const getVerdictIcon = (v: string) => {
        if (v.includes('VERDADEIRO')) return <CheckCircle2 color="var(--success)" />;
        if (v.includes('FALSO')) return <AlertTriangle color="var(--danger)" />;
        return <HelpCircle color="var(--primary)" />;
    };

    return (
        <div className="section" style={{ padding: '1rem' }}>
            <div className="glass" style={{ padding: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                    <Search size={20} color="var(--primary)" />
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Cortex Verification Engine</h2>
                </div>

                <textarea
                    value={claim}
                    onChange={(e) => setClaim(e.target.value)}
                    placeholder="Paste a claim or news snippet to verify with Gemini AI..."
                    maxLength={10000}
                    className="mono"
                    style={{
                        width: '100%',
                        minHeight: '150px',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-glass)',
                        color: 'var(--text-main)',
                        padding: '1.5rem',
                        fontSize: '1rem',
                        resize: 'vertical',
                        marginBottom: '1rem'
                    }}
                />

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div className="mono" style={{ fontSize: '0.8rem', color: claim.length > 9000 ? 'var(--danger)' : 'var(--text-muted)' }}>
                        {claim.length.toLocaleString()} / 10,000 chars
                    </div>
                    <button
                        onClick={handleVerify}
                        disabled={loading || claim.length < 10}
                        className="glow-primary"
                        style={{
                            background: loading ? 'var(--text-dim)' : 'var(--primary)',
                            color: 'var(--bg-deep)',
                            padding: '0.75rem 2rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            fontSize: '1rem'
                        }}
                    >
                        {loading ? <Loader2 className="animate-spin" size={20} /> : <Zap size={20} />}
                        {loading ? 'VERIFYING...' : 'RUN VERIFICATION'}
                    </button>
                </div>

                <AnimatePresence>
                    {progress > 0 && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            style={{ marginTop: '1.5rem' }}
                        >
                            <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                                <motion.div
                                    style={{ height: '100%', background: 'var(--primary)' }}
                                    animate={{ width: `${progress}%` }}
                                />
                            </div>
                            <div style={{ textAlign: 'center', fontSize: '0.75rem', marginTop: '0.5rem', color: 'var(--text-muted)' }}>
                                Processing using Google Gemini 2.0 Flash...
                            </div>
                        </motion.div>
                    )}

                    {result && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            style={{
                                marginTop: '1.5rem',
                                padding: '1.5rem',
                                border: '1px solid var(--border-glass)',
                                borderRadius: 'var(--radius-md)',
                                background: 'rgba(0,242,255,0.02)'
                            }}
                        >
                            {result.error ? (
                                <div style={{ color: 'var(--danger)', display: 'flex', gap: '0.5rem' }}>
                                    <AlertTriangle size={20} />
                                    <span>{result.error}</span>
                                </div>
                            ) : (
                                <>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                            {getVerdictIcon(result.veredito)}
                                            <span style={{ fontWeight: 700, fontSize: '1.2rem' }}>{result.veredito}</span>
                                        </div>
                                        <div className="mono" style={{ background: 'var(--border-glass)', padding: '4px 12px', borderRadius: '4px', fontSize: '0.9rem' }}>
                                            {result.confianca}% CONFIDENCE
                                        </div>
                                    </div>
                                    <p style={{ color: 'var(--text-main)', fontSize: '1.05rem', lineHeight: '1.7' }}>{result.analise}</p>
                                    {result.evidencias?.length > 0 && (
                                        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)' }}>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Evidence Sources</div>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                                {result.evidencias.map((ev: string, i: number) => (
                                                    <span key={i} className="mono" style={{ fontSize: '0.7rem', padding: '2px 8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                                                        {ev}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};
