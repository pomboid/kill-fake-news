import React from 'react';
import { Shield, Sun, Moon } from 'lucide-react';

interface NavbarProps {
    isOnline: boolean;
    uptime: string;
    isDarkMode: boolean;
    toggleTheme: () => void;
    children?: React.ReactNode;
}

export const Navbar: React.FC<NavbarProps> = ({ isOnline, uptime, isDarkMode, toggleTheme, children }) => {
    return (
        <nav className="header glass" style={{
            width: '100%',
            padding: '0.75rem 2rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            position: 'fixed',
            top: 0,
            left: 0,
            zIndex: 1000,
            borderRadius: 0,
            borderTop: 'none',
            borderLeft: 'none',
            borderRight: 'none'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div className="glow-primary flex-center" style={{ background: 'var(--primary)', padding: '8px', borderRadius: '8px' }}>
                    <Shield size={20} color="var(--bg-deep)" strokeWidth={2.5} />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <h1 className="text-gradient" style={{ fontSize: '1.1rem', fontWeight: 800, margin: 0, letterSpacing: '1px', lineHeight: 1 }}>VORTEX</h1>
                    <div style={{ fontSize: '0.55rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '2px', marginTop: '2px' }}>TERMINAL OS</div>
                </div>
                <div style={{ height: '20px', width: '1px', background: 'var(--border-glass)', margin: '0 0.5rem' }} />
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.6rem', background: isOnline ? 'rgba(0, 255, 136, 0.05)' : 'rgba(255, 77, 77, 0.05)', color: isOnline ? 'var(--success)' : 'var(--danger)', padding: '2px 8px', borderRadius: '3px', fontWeight: 700, border: `1px solid ${isOnline ? 'rgba(0, 255, 136, 0.1)' : 'rgba(255, 77, 77, 0.1)'}` }}>
                    {isOnline ? 'SYS_READY' : 'SYS_OFFLINE'}
                </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <div style={{ textAlign: 'right', borderRight: '1px solid var(--border-glass)', paddingRight: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <div style={{ fontSize: '0.55rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '1px' }}>Uptime</div>
                    <div className="mono" style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>{uptime}</div>
                </div>

                <button
                    onClick={toggleTheme}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        cursor: 'pointer',
                        padding: '4px',
                        transition: 'color 0.2s'
                    }}
                >
                    {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
                </button>

                <div style={{ display: 'flex', alignItems: 'center' }}>
                    {children}
                </div>
            </div>
        </nav>
    );
};
