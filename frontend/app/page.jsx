'use client';

import { useState } from 'react';
import InputForm from '@/components/InputForm';
import LoadingScreen from '@/components/LoadingScreen';
import ResultsDashboard from '@/components/ResultsDashboard';
import { submitWorkflow } from '@/lib/api';

export default function HomePage() {
  const [appState, setAppState] = useState('idle');
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  async function handleSubmit(values) {
    setAppState('loading');
    setErrorMsg('');
    try {
      const data = await submitWorkflow(values);
      setResult(data);
      setAppState('success');
      // Scroll to top of results
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Something went wrong');
      setAppState('error');
    }
  }

  function handleReset() {
    setAppState('idle');
    setResult(null);
    setErrorMsg('');
  }

  return (
    <div className="container">
      {appState === 'idle' && (
        <InputForm onSubmit={handleSubmit} />
      )}

      {appState === 'loading' && (
        <LoadingScreen />
      )}

      {appState === 'success' && result && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
            <div>
              <h2 style={{ fontSize: '1.6rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
                <span className="gradient-text">Analysis Complete</span> ✨
              </h2>
              <p style={{ marginTop: 4, fontSize: '0.9rem' }}>
                Here&apos;s your complete product launch package for{' '}
                <strong style={{ color: 'var(--violet-400)', textTransform: 'capitalize' }}>
                  {result.platform.selected}
                </strong>
              </p>
            </div>
            <button className="btn-secondary" onClick={handleReset}>
              ← New Analysis
            </button>
          </div>
          <ResultsDashboard data={result} />
        </>
      )}

      {appState === 'error' && (
        <div>
          <div className="error-banner" style={{ marginBottom: 24 }}>
            <span className="error-icon">⚠️</span>
            <div>
              <p className="error-title">Analysis Failed</p>
              <p className="error-msg">{errorMsg}</p>
            </div>
          </div>
          <button className="btn-secondary" onClick={handleReset}>
            ← Try Again
          </button>
        </div>
      )}
    </div>
  );
}
