import React, { useState, useRef } from 'react'

const FORMATS = [
  { label: 'Spreadsheets', exts: ['csv','tsv','xlsx','xls'],   color: 'var(--emerald)' },
  { label: 'Documents',    exts: ['pdf','docx','txt','md'],    color: 'var(--accent)' },
  { label: 'Data',         exts: ['json','xml','yaml'],        color: 'var(--amber)' },
  { label: 'Images',       exts: ['png','jpg','webp','gif'],   color: '#7C3AED' },
  { label: 'Code',         exts: ['py','js','ts','sql','log'], color: '#0891B2' },
]

export default function UploadView({ onFile, error }) {
  const [drag, setDrag] = useState(false)
  const ref = useRef()
  const pick = f => f && onFile(f)

  return (
    <div style={{
      flex: 1, display: 'flex', overflow: 'auto',
      background: 'var(--bg)',
    }}>
      {/* Left column — upload */}
      <div style={{
        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '48px 40px',
      }}>
        <div style={{ width: '100%', maxWidth: 440, animation: 'rise .4s ease' }}>

          {/* Badge */}
          <div style={{ marginBottom: 20 }}>
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: 5,
              padding: '4px 10px', borderRadius: 'var(--r99)',
              background: 'var(--accent-soft)', border: '1px solid var(--accent-ring)',
              fontSize: 11, fontWeight: 600, letterSpacing: '.06em',
              textTransform: 'uppercase', color: 'var(--accent)',
            }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--accent)', flexShrink: 0 }} />
              100% Local · No API Key
            </span>
          </div>

          <h1 style={{
            fontSize: 32, fontWeight: 700, letterSpacing: '-0.7px',
            lineHeight: 1.15, color: 'var(--ink)', marginBottom: 14,
          }}>
            Analyze any file<br />
            <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>with local AI</span>
          </h1>
          <p style={{ color: 'var(--ink-2)', fontSize: 15, lineHeight: 1.65, marginBottom: 32 }}>
            Upload a file and instantly get pandas statistics, auto-generated charts, outlier detection, and streaming AI insights — all offline.
          </p>

          {/* Error */}
          {error && (
            <div style={{
              marginBottom: 16, padding: '10px 14px', borderRadius: 'var(--r8)',
              background: 'var(--ruby-soft)', border: '1px solid var(--ruby-ring)',
              color: 'var(--ruby)', fontSize: 13, fontWeight: 500,
              display: 'flex', gap: 8, alignItems: 'center', animation: 'appear .2s',
            }}>
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8">
                <circle cx="8" cy="8" r="7"/><path d="M8 5v4M8 11v.5"/>
              </svg>
              {error}
            </div>
          )}

          {/* Dropzone */}
          <div
            onDrop={e => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]) }}
            onDragOver={e => { e.preventDefault(); setDrag(true) }}
            onDragLeave={e => { if (!e.currentTarget.contains(e.relatedTarget)) setDrag(false) }}
            onClick={() => ref.current.click()}
            style={{
              border: '1.5px dashed ' + (drag ? 'var(--accent)' : 'var(--border-md)'),
              borderRadius: 'var(--r16)',
              padding: '40px 28px',
              textAlign: 'center',
              cursor: 'pointer',
              background: drag ? 'var(--accent-soft)' : 'var(--surface)',
              transition: 'all .18s',
              boxShadow: drag ? '0 0 0 3px rgba(37,99,235,.1), var(--s1)' : 'var(--s1)',
            }}
          >
            <div style={{
              width: 56, height: 56, borderRadius: 14, margin: '0 auto 16px',
              background: drag
                ? 'var(--accent)' : 'var(--bg2)',
              border: '1px solid ' + (drag ? 'transparent' : 'var(--border)'),
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all .18s',
              boxShadow: drag ? '0 6px 20px rgba(37,99,235,.28)' : 'none',
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                stroke={drag ? '#fff' : 'var(--ink-4)'} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <p style={{ fontWeight: 600, fontSize: 16, color: drag ? 'var(--accent)' : 'var(--ink)', marginBottom: 5, transition: 'color .18s' }}>
              {drag ? 'Drop to analyze' : 'Drop your file here'}
            </p>
            <p style={{ color: 'var(--ink-4)', fontSize: 13 }}>
              or{' '}
              <span style={{
                color: 'var(--accent)', fontWeight: 500,
                textDecoration: 'underline', textDecorationStyle: 'dotted', textUnderlineOffset: '2px',
              }}>browse files</span>
            </p>
          </div>
          <input ref={ref} type="file" accept="*" hidden onChange={e => pick(e.target.files[0])} />

          {/* Privacy tag */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 7, justifyContent: 'center',
            marginTop: 16, padding: '8px 14px', borderRadius: 'var(--r8)',
            background: 'var(--emerald-soft)', border: '1px solid var(--emerald-ring)',
            fontSize: 12.5, color: 'var(--emerald)', fontWeight: 500,
          }}>
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M8 1L2 3.5V8c0 4 2.8 7 6 7s6-3 6-7V3.5L8 1z"/>
            </svg>
            Your files never leave your machine
          </div>
        </div>
      </div>

      {/* Right column — formats */}
      <div style={{
        width: 280, borderLeft: '1px solid var(--border)',
        background: 'var(--bg2)',
        padding: '40px 24px',
        flexShrink: 0, overflowY: 'auto',
      }}>
        <p style={{
          fontSize: 11, fontWeight: 700, letterSpacing: '.08em',
          textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 20,
        }}>Supported formats</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {FORMATS.map(g => (
            <div key={g.label}>
              <p style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--ink-2)', marginBottom: 7 }}>
                {g.label}
              </p>
              <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
                {g.exts.map(e => (
                  <span key={e} style={{
                    fontSize: 11.5, fontFamily: 'var(--mono)',
                    padding: '3px 8px', borderRadius: 'var(--r6)',
                    background: 'var(--surface)', border: '1px solid var(--border)',
                    color: 'var(--ink-3)',
                  }}>.{e}</span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div style={{
          marginTop: 32, padding: '16px', borderRadius: 'var(--r10)',
          background: 'var(--surface)', border: '1px solid var(--border)',
        }}>
          <p style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 10 }}>
            What you get
          </p>
          {[
            'Instant pandas statistics',
            'Auto-generated charts',
            'Outlier & trend detection',
            'Streaming AI insights',
            'Multi-turn Q&A chat',
          ].map((f, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 7 }}>
              <div style={{
                width: 16, height: 16, borderRadius: '50%', flexShrink: 0,
                background: 'var(--accent-soft)', border: '1px solid var(--accent-ring)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="8" height="8" viewBox="0 0 10 10" fill="none" stroke="var(--accent)" strokeWidth="1.8" strokeLinecap="round">
                  <polyline points="2 5 4 7 8 3"/>
                </svg>
              </div>
              <span style={{ fontSize: 12.5, color: 'var(--ink-2)' }}>{f}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}