import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import { motion } from 'framer-motion';
import { Shield } from 'lucide-react';

interface LoginPageProps {
    isDarkMode: boolean;
}

export const LoginPage: React.FC<LoginPageProps> = ({ isDarkMode }) => {
    return (
        <div className="flex-center" style={{ minHeight: '100vh', flexDirection: 'column', background: 'var(--bg-deep)', position: 'relative', overflow: 'hidden' }}>
            {/* Background Orbs */}
            <div style={{ position: 'absolute', top: '10%', left: '10%', width: '300px', height: '300px', background: 'var(--primary)', filter: 'blur(150px)', opacity: isDarkMode ? 0.1 : 0.05, pointerEvents: 'none' }} />
            <div style={{ position: 'absolute', bottom: '10%', right: '10%', width: '300px', height: '300px', background: 'var(--secondary)', filter: 'blur(150px)', opacity: isDarkMode ? 0.1 : 0.05, pointerEvents: 'none' }} />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ textAlign: 'center', marginBottom: '2rem', zIndex: 10 }}
            >
                <div className="glow-primary flex-center" style={{ background: 'var(--primary)', width: '64px', height: '64px', borderRadius: '16px', margin: '0 auto 1.5rem' }}>
                    <Shield size={32} color={isDarkMode ? 'var(--bg-deep)' : '#fff'} />
                </div>
                <h1 className="text-gradient" style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '0.5rem' }}>VORTEX</h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '1rem', letterSpacing: '1px' }}>COGNITIVE DEFENSE OS</p>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="glass"
                style={{ padding: '4px', borderRadius: '24px', zIndex: 10 }}
            >
                <SignIn
                    appearance={{
                        variables: {
                            colorPrimary: isDarkMode ? '#00f2ff' : '#007bff',
                            colorText: isDarkMode ? '#e0e0e0' : '#1a1a1a',
                            colorTextSecondary: isDarkMode ? '#808080' : '#6c757d',
                            colorBackground: isDarkMode ? '#0a0a0a' : '#ffffff',
                            colorInputBackground: isDarkMode ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.03)',
                            colorInputText: isDarkMode ? '#fff' : '#000',
                            borderRadius: '12px',
                            fontFamily: 'Outfit, sans-serif'
                        },
                        elements: {
                            rootBox: "clerk-root",
                            card: {
                                background: isDarkMode ? "rgba(10,10,10,0.8)" : "rgba(255,255,255,0.8)",
                                border: isDarkMode ? "1px solid rgba(255,255,255,0.08)" : "1px solid rgba(0,0,0,0.08)",
                                backdropFilter: "blur(20px)",
                                boxShadow: isDarkMode ? "0 20px 40px rgba(0,0,0,0.4)" : "0 20px 40px rgba(0,0,0,0.1)"
                            },
                            headerTitle: { fontSize: '1.5rem', fontWeight: 700 },
                            socialButtonsBlockButton: {
                                background: isDarkMode ? "rgba(255,255,255,0.03)" : "rgba(0,0,0,0.03)",
                                border: isDarkMode ? "1px solid rgba(255,255,255,0.1)" : "1px solid rgba(0,0,0,0.1)",
                                "&:hover": { background: isDarkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)" }
                            },
                            formButtonPrimary: {
                                textTransform: 'uppercase',
                                letterSpacing: '1px',
                                fontWeight: 600
                            }
                        }
                    }}
                />
            </motion.div>

            <div style={{ marginTop: '2rem', color: 'var(--text-dim)', fontSize: '0.75rem', zIndex: 10 }}>
                ACCESS RESTRICTED TO AUTHORIZED PERSONNEL ONLY
            </div>
        </div>
    );
};
