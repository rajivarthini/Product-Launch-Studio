'use client';

import { useEffect, useState } from 'react';

const STEPS = [
  { label: 'Sending images to AI…', icon: '📤' },
  { label: 'Analysing product with Gemini Vision…', icon: '🔍' },
  { label: 'Checking license & compliance…', icon: '🔏' },
  { label: 'Generating marketplace listing…', icon: '📝' },
  { label: 'Creating packaging design…', icon: '📦' },
  { label: 'Fetching price insights…', icon: '💰' },
  { label: 'Cleaning & enhancing images…', icon: '✨' },
  { label: 'Finalising your package…', icon: '🎁' },
];

export default function LoadingScreen() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((s) => (s < STEPS.length - 1 ? s + 1 : s));
    }, 2800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-screen">
      <div className="spinner-orbit">
        <div className="spinner-core" />
        <div className="spinner-inner" />
      </div>
      <div>
        <p className="loading-title gradient-text">Processing Your Product</p>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: 6 }}>This usually takes 30–60 seconds</p>
      </div>
      <div className="loading-steps">
        {STEPS.map((step, i) => (
          <div
            key={i}
            className={`loading-step${i === activeStep ? ' active' : ''}`}
            style={{ opacity: i <= activeStep ? 1 : 0.3, animationDelay: `${i * 0.08}s` }}
          >
            <span style={{ fontSize: 16 }}>{step.icon}</span>
            <span>
              {i < activeStep ? '✅ ' : ''}
              {step.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
