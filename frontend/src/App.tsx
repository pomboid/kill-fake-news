import { useState, useEffect } from 'react';
import { ClerkProvider, SignedIn, SignedOut, UserButton, useUser } from '@clerk/clerk-react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { StatsGrid } from './components/StatsGrid';
import { VerifyForm } from './components/VerifyForm';
import { HistoryList } from './components/HistoryList';
import { SourcesList } from './components/SourcesList';
import { SchedulerInfo } from './components/SchedulerInfo';
import { LoginPage } from './pages/Login';
import { NewsCatalog } from './pages/NewsCatalog';
import { motion } from 'framer-motion';

const API_BASE = import.meta.env.VITE_API_URL || '';
const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || '';

if (!CLERK_PUBLISHABLE_KEY) {
  console.warn("Missing VITE_CLERK_PUBLISHABLE_KEY. Please add it to your .env file.");
}

function Dashboard({ isDarkMode, toggleTheme }: { isDarkMode: boolean, toggleTheme: () => void }) {
  const { user } = useUser();
  const [data, setData] = useState<any>(null);
  const [sources, setSources] = useState<any>({});
  const [history, setHistory] = useState<any[]>([]);
  const [quality, setQuality] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState(localStorage.getItem('vortex_api_key') || '');

  const fetchData = async () => {
    const headers: any = { 'Content-Type': 'application/json' };
    if (apiKey) headers['X-API-Key'] = apiKey;
    if (user?.id) headers['X-User-ID'] = user.id;

    try {
      const responses = await Promise.allSettled([
        fetch(`${API_BASE}/api/status`, { headers }),
        fetch(`${API_BASE}/api/sources`, { headers }),
        fetch(`${API_BASE}/api/history?limit=10`, { headers }),
        fetch(`${API_BASE}/api/quality`, { headers })
      ]);

      const [statusRes, sourcesRes, historyRes, qualityRes] = responses;

      if (statusRes.status === 'fulfilled' && statusRes.value.status === 401) {
        setLoading(false);
        const key = prompt('VORTEX ACCESS REQUIRED. Enter API Key:');
        if (key) {
          localStorage.setItem('vortex_api_key', key);
          setApiKey(key);
        }
        return;
      }

      if (statusRes.status === 'rejected') {
        throw new Error('BACKEND_OFFLINE');
      }

      const status = statusRes.value.ok ? await statusRes.value.json() : null;
      const srcs = (sourcesRes.status === 'fulfilled' && sourcesRes.value.ok) ? await sourcesRes.value.json() : { sources: {} };
      const hist = (historyRes.status === 'fulfilled' && historyRes.value.ok) ? await historyRes.value.json() : { entries: [] };
      const qual = (qualityRes.status === 'fulfilled' && qualityRes.value.ok) ? await qualityRes.value.json() : null;

      if (status) {
        setData(status);
        setSources(srcs.sources || {});
        setHistory(hist.entries || []);
        setQuality(qual);
        setError(null);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (e: any) {
      console.error('Fetch error:', e);
      setError(e.message === 'BACKEND_OFFLINE' ? 'VORTEX Backend is offline. Please start server.py' : e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [apiKey, user?.id]);

  const handleVerify = async (claim: string) => {
    const headers: any = { 'Content-Type': 'application/json' };
    if (apiKey) headers['X-API-Key'] = apiKey;
    if (user?.id) headers['X-User-ID'] = user.id;

    const res = await fetch(`${API_BASE}/api/verify`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ claim })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Verification failed');
    }

    const result = await res.json();
    fetchData(); // Refresh history
    return result;
  };

  if (loading && !data) {
    return (
      <div className="flex-center" style={{ height: '100vh', flexDirection: 'column', gap: '1rem' }}>
        <div className="glow-primary" style={{ width: '50px', height: '50px', border: '3px solid var(--primary)', borderRadius: '50%', borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }} />
        <div className="mono text-gradient" style={{ letterSpacing: '2px', fontWeight: 600 }}>BOOTING VORTEX OS...</div>
        {error && <div style={{ color: 'var(--danger)', fontSize: '0.8rem', marginTop: '1rem' }}>{error}</div>}
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="flex-center" style={{ height: '100vh', flexDirection: 'column', gap: '1.5rem', padding: '2rem', textAlign: 'center' }}>
        <div style={{ color: 'var(--danger)', background: 'rgba(255, 77, 77, 0.1)', padding: '2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--danger)' }}>
          <h2 style={{ marginBottom: '1rem' }}>SYSTEM CRITICAL ERROR</h2>
          <p className="mono" style={{ fontSize: '0.9rem' }}>{error}</p>
          <button
            onClick={() => fetchData()}
            style={{ marginTop: '2rem', background: 'var(--primary)', color: 'var(--bg-deep)', padding: '0.5rem 2.5rem' }}
          >
            RETRY CONNECTION
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '1400px',
      margin: '0 auto',
      paddingBottom: '4rem',
      paddingTop: '5rem'
    }}>
      <Navbar
        isOnline={!!data}
        uptime={data ? `${Math.floor(data.uptime_seconds / 3600)}h ${Math.floor((data.uptime_seconds % 3600) / 60)}m` : '0h 0m'}
        isDarkMode={isDarkMode}
        toggleTheme={toggleTheme}
      >
        <UserButton afterSignOutUrl="/" />
      </Navbar>

      <main style={{ marginTop: '1rem' }}>
        <StatsGrid stats={{
          reference: data.reference_articles,
          analyzed: data.analyzed_articles,
          quality: quality?.score || 0,
          sources: { online: Object.values(sources).filter((s: any) => s.status === 'online').length, total: Object.keys(sources).length }
        }} />

        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '2rem', padding: '1rem', marginTop: '1rem' }}>
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
            <VerifyForm onVerify={handleVerify} />
            <div style={{ marginTop: '1rem' }}>
              <SchedulerInfo scheduler={data.scheduler} />
            </div>
            <div style={{ marginTop: '1rem' }}>
              <SourcesList sources={sources} />
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
            <HistoryList entries={history} />
          </motion.div>
        </div>
      </main>

      <footer style={{ textAlign: 'center', marginTop: '4rem', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
        <p>© 2026 VORTEX COGNITIVE DEFENSE SYSTEM — LATEST BUILD 1.0.0</p>
        <p className="mono">GEMINI-2.0-FLASH-ENABLED</p>
      </footer>
    </div>
  );
}

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => localStorage.getItem('vortex_theme') !== 'light');

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    document.documentElement.setAttribute('data-theme', newMode ? 'dark' : 'light');
    localStorage.setItem('vortex_theme', newMode ? 'dark' : 'light');
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <BrowserRouter>
        <SignedIn>
          <Routes>
            <Route path="/" element={<Dashboard isDarkMode={isDarkMode} toggleTheme={toggleTheme} />} />
            <Route path="/news" element={<NewsCatalog isDarkMode={isDarkMode} toggleTheme={toggleTheme} />} />
          </Routes>
        </SignedIn>
        <SignedOut>
          <LoginPage isDarkMode={isDarkMode} />
        </SignedOut>
      </BrowserRouter>
    </ClerkProvider>
  );
}

export default App;
