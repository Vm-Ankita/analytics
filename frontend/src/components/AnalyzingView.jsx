import React, { useEffect, useState } from 'react'

const STEPS = [
  { label: 'Parsing file', delay: 0 },
  { label: 'Computing statistics', delay: 600 },
  { label: 'Generating chart', delay: 1400 },
  { label: 'Starting AI analysis', delay: 2200 },
]

export default function AnalyzingView({ fileInfo }) {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const timers = STEPS.map((s, i) =>
      setTimeout(() => setStep(i), s.delay)
    )
    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div style={{
      flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)', flexDirection: 'column', gap: 0,
    }}>
      <div style={{ animation: 'rise .4s ease', textAlign: 'center', maxWidth: 380 }}>

        {/* Spinner */}
        <div style={{
          width: 48, height: 48, margin: '0 auto 28px',
          border: '2.5px solid var(--border)',
          borderTopColor: 'var(--accent)',
          borderRadius: '50%',
          animation: 'spin .75s linear infinite',
        }} />

        <h2 style={{
          fontSize: 20, fontWeight: 600, letterSpacing: '-0.3px',
          color: 'var(--ink)', marginBottom: 6,
        }}>Analyzing your file</h2>

        {fileInfo && (
          <p style={{
            fontSize: 13, color: 'var(--ink-3)', marginBottom: 28,
            fontFamily: 'var(--mono)',
            display: 'inline-flex', alignItems: 'center', gap: 6,
          }}>
            <span>{fileInfo.icon}</span>
            {fileInfo.name}
          </p>
        )}

        {/* Step list */}
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 'var(--r12)', padding: '4px 0',
          boxShadow: 'var(--s1)', textAlign: 'left',
        }}>
          {STEPS.map((s, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 16px',
              borderBottom: i < STEPS.length - 1 ? '1px solid var(--border)' : 'none',
              opacity: i <= step ? 1 : 0.35,
              transition: 'opacity .3s ease',
            }}>
              <div style={{
                width: 20, height: 20, borderRadius: '50%', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: i < step ? 'var(--emerald-soft)' : i === step ? 'var(--accent-soft)' : 'var(--bg2)',
                border: '1px solid ' + (i < step ? 'var(--emerald-ring)' : i === step ? 'var(--accent-ring)' : 'var(--border)'),
                transition: 'all .3s',
              }}>
                {i < step ? (
                  <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="var(--emerald)" strokeWidth="2" strokeLinecap="round">
                    <polyline points="2 6 5 9 10 3"/>
                  </svg>
                ) : i === step ? (
                  <div style={{
                    width: 7, height: 7,
                    border: '1.5px solid var(--accent)', borderTopColor: 'transparent',
                    borderRadius: '50%', animation: 'spin .6s linear infinite',
                  }} />
                ) : (
                  <div style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--border-strong)' }} />
                )}
              </div>
              <span style={{
                fontSize: 13, fontWeight: i === step ? 500 : 400,
                color: i <= step ? 'var(--ink)' : 'var(--ink-4)',
                transition: 'all .3s',
              }}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}