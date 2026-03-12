import React, { useEffect, useState } from 'react'
import { checkHealth } from '../api.js'

export default function Topbar({ fileInfo, phase, modelUsed, onReset }) {
  const [health, setHealth] = useState(null)
  useEffect(() => {
    checkHealth().then(setHealth).catch(() => setHealth({ ollama: 'disconnected' }))
  }, [])

  const online = health?.ollama === 'connected'
  const model  = modelUsed || health?.model || 'ollama'

  return (
    <header style={{
      height: 52, background: 'var(--surface)',
      borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center',
      padding: '0 20px', gap: 14, flexShrink: 0,
      boxShadow: 'var(--s0)',
    }}>

      {/* Wordmark */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
        <div style={{
          width: 30, height: 30, borderRadius: 8, flexShrink: 0,
          background: 'var(--ink)', display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
            <rect x="2" y="12" width="3" height="6" rx="1" fill="white" fillOpacity=".9"/>
            <rect x="7" y="7"  width="3" height="11" rx="1" fill="white"/>
            <rect x="12" y="4" width="3" height="14" rx="1" fill="white" fillOpacity=".7"/>
            <rect x="17" y="1" width="1" height="17" rx=".5" fill="white" fillOpacity=".3"/>
          </svg>
        </div>
        <span style={{ fontWeight: 600, fontSize: 15, letterSpacing: '-0.3px', color: 'var(--ink)' }}>
          Academic Analytics
        </span>
      </div>

      <div style={{ width: 1, height: 18, background: 'var(--border)', flexShrink: 0 }} />

      {/* Connection badge */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 5,
        padding: '3px 10px', borderRadius: 'var(--r99)',
        background: online ? 'var(--emerald-soft)' : 'var(--ruby-soft)',
        border: '1px solid ' + (online ? 'var(--emerald-ring)' : 'var(--ruby-ring)'),
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: '50%', flexShrink: 0,
          background: online ? 'var(--emerald)' : 'var(--ruby)',
        }} />
        <span style={{
          fontSize: 11.5, fontWeight: 500, fontFamily: 'var(--mono)',
          color: online ? 'var(--emerald)' : 'var(--ruby)',
          letterSpacing: '.01em',
        }}>
          {online ? model : 'disconnected'}
        </span>
      </div>

      {/* File breadcrumb */}
      {fileInfo && (
        <>
          <div style={{ width: 1, height: 18, background: 'var(--border)', flexShrink: 0 }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, minWidth: 0, animation: 'appear .2s ease' }}>
            <span style={{ fontSize: 15, flexShrink: 0 }}>{fileInfo.icon}</span>
            <span style={{
              fontSize: 13, fontWeight: 500, color: 'var(--ink-2)',
              whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 180,
            }}>{fileInfo.name}</span>
            <span style={{
              fontSize: 10.5, fontFamily: 'var(--mono)', fontWeight: 500, flexShrink: 0,
              padding: '1px 7px', borderRadius: 'var(--r3)',
              background: 'var(--accent-soft)', color: 'var(--accent)',
              border: '1px solid var(--accent-ring)',
            }}>{fileInfo.label}</span>
          </div>
        </>
      )}

      <div style={{ flex: 1 }} />

      {phase !== 'upload' && (
        <button onClick={onReset} style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '6px 13px', borderRadius: 'var(--r8)',
          border: '1px solid var(--border-md)',
          background: 'var(--surface)', color: 'var(--ink-3)',
          fontSize: 13, fontWeight: 500, transition: 'all .14s',
        }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg2)'; e.currentTarget.style.color = 'var(--ink)'; e.currentTarget.style.borderColor = 'var(--border-strong)' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'var(--surface)'; e.currentTarget.style.color = 'var(--ink-3)'; e.currentTarget.style.borderColor = 'var(--border-md)' }}
        >
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <path d="M2 8a6 6 0 1 0 6-6 6 6 0 0 1-4.2 1.7"/><path d="M2 3.7V8h4.3"/>
          </svg>
          New File
        </button>
      )}
    </header>
  )
}