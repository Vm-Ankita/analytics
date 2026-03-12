import React from 'react'
import { renderMd } from '../markdown.js'

const PROSE = `
  .prose { font-size: 13.5px; line-height: 1.72; }
  .prose p      { color: var(--ink-2); margin: 5px 0; }
  .prose h1     { font-size: 15px; font-weight: 700; color: var(--ink); margin: 20px 0 8px; letter-spacing: -.25px; }
  .prose h2     { font-size: 13px; font-weight: 600; color: var(--ink); margin: 18px 0 7px;
                  padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  .prose h3     { font-size: 11px; font-weight: 700; text-transform: uppercase;
                  letter-spacing: .07em; color: var(--accent); margin: 14px 0 5px; }
  .prose ul, .prose ol { padding-left: 18px; margin: 6px 0; }
  .prose li     { color: var(--ink-2); margin: 4px 0; }
  .prose strong { color: var(--ink); font-weight: 600; }
  .prose em     { color: var(--ink-3); }
  .prose code   { font-family: var(--mono); font-size: 12px; background: var(--bg2);
                  border: 1px solid var(--border); padding: 1px 6px; border-radius: 4px; color: var(--accent); }
  .prose hr     { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
`

export default function AnalysisPanel({ fileInfo, summary, preview, chartB64, insights }) {
  return (
    <div style={{
      width: '50%', display: 'flex', flexDirection: 'column',
      borderRight: '1px solid var(--border)', overflow: 'hidden',
      background: 'var(--surface)',
    }}>
      <style>{PROSE}</style>

      {/* Header */}
      <div style={{
        height: 44, padding: '0 18px',
        borderBottom: '1px solid var(--border)',
        display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0,
      }}>
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="var(--ink-3)" strokeWidth="1.6" strokeLinecap="round">
          <path d="M12 14V7M8 14V2M4 14v-4"/>
        </svg>
        <span style={{ fontWeight: 600, fontSize: 13, color: 'var(--ink)' }}>Analysis</span>
        {summary && (
          <div style={{ display: 'flex', gap: 4, marginLeft: 2 }}>
            <Tag mono>{summary.total_rows?.toLocaleString()} rows</Tag>
            <Tag mono>{summary.total_cols} cols</Tag>
          </div>
        )}
        <div style={{ flex: 1 }} />
        {fileInfo && <Tag accent>{fileInfo.label}</Tag>}
      </div>

      {/* Scrollable body */}
      <div style={{ flex: 1, overflowY: 'auto' }}>

        {/* Image preview */}
        {preview && (
          <Block label="Preview">
            <img src={preview} alt="preview" style={{
              maxHeight: 160, maxWidth: '100%', display: 'block',
              borderRadius: 8, border: '1px solid var(--border)',
            }} />
          </Block>
        )}

        {/* Chart */}
        {chartB64 && (
          <Block label="Chart">
            <div style={{ borderRadius: 8, overflow: 'hidden', border: '1px solid var(--border)', boxShadow: 'var(--s0)' }}>
              <img src={`data:image/png;base64,${chartB64}`} alt="chart" style={{ width: '100%', display: 'block' }} />
            </div>
          </Block>
        )}

        {/* Auto-insights */}
        {summary?.auto_insights?.length > 0 && (
          <Block label="Detected Patterns">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              {summary.auto_insights.map((ins, i) => (
                <div key={i} style={{
                  padding: '8px 12px', borderRadius: 8,
                  background: 'var(--accent-soft)', border: '1px solid var(--accent-ring)',
                  fontSize: 13, color: 'var(--ink)',
                  display: 'flex', gap: 8, alignItems: 'flex-start',
                  animation: `rise .3s ease ${i * .05}s both`,
                }}>
                  <svg style={{ flexShrink: 0, marginTop: 1 }} width="12" height="12" viewBox="0 0 14 14" fill="none" stroke="var(--accent)" strokeWidth="1.8" strokeLinecap="round">
                    <circle cx="7" cy="7" r="6"/><path d="M7 4v4M7 9.5v.5"/>
                  </svg>
                  <span dangerouslySetInnerHTML={{ __html: renderMd(ins) }} style={{ flex: 1 }} />
                </div>
              ))}
            </div>
          </Block>
        )}

        {/* Column cards */}
        {summary?.columns && Object.keys(summary.columns).length > 0 && (
          <Block label={`${Object.keys(summary.columns).length} Columns`}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))', gap: 6 }}>
              {Object.entries(summary.columns).map(([col, info], i) => (
                <ColCard key={col} col={col} info={info} i={i} />
              ))}
            </div>
          </Block>
        )}

        {/* AI insights */}
        <Block label="AI Insights" last>
          {insights ? (
            <div className="prose" dangerouslySetInnerHTML={{ __html: renderMd(insights) }} />
          ) : (
            <div style={{ display: 'flex', gap: 5, alignItems: 'center', padding: '2px 0' }}>
              {[0,1,2].map(i => (
                <div key={i} style={{
                  width: 7, height: 7, borderRadius: '50%', background: 'var(--border-md)',
                  animation: `pulse3 1.3s ease ${i * .19}s infinite`,
                }} />
              ))}
              <span style={{ fontSize: 12.5, color: 'var(--ink-4)', marginLeft: 6 }}>Generating insights…</span>
            </div>
          )}
        </Block>
      </div>
    </div>
  )
}

function Block({ label, children, last }) {
  return (
    <div style={{
      padding: '14px 18px',
      borderBottom: last ? 'none' : '1px solid var(--border)',
    }}>
      <p style={{
        fontSize: 10.5, fontWeight: 700, letterSpacing: '.08em',
        textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 10,
      }}>{label}</p>
      {children}
    </div>
  )
}

function Tag({ children, mono, accent }) {
  return (
    <span style={{
      fontSize: 11, padding: '2px 7px', borderRadius: 'var(--r3)',
      fontFamily: mono || accent ? 'var(--mono)' : 'var(--sans)',
      background: accent ? 'var(--accent-soft)' : 'var(--bg2)',
      color: accent ? 'var(--accent)' : 'var(--ink-3)',
      border: '1px solid ' + (accent ? 'var(--accent-ring)' : 'var(--border)'),
      fontWeight: 500,
    }}>{children}</span>
  )
}

function ColCard({ col, info, i }) {
  const isNum = info.type === 'numeric'
  return (
    <div style={{
      padding: '9px 10px', borderRadius: 8,
      background: 'var(--bg)', border: '1px solid var(--border)',
      animation: `rise .25s ease ${i * .03}s both`,
      transition: 'box-shadow .15s, border-color .15s',
    }}
      onMouseEnter={e => { e.currentTarget.style.boxShadow = 'var(--s1)'; e.currentTarget.style.borderColor = 'var(--border-md)' }}
      onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.borderColor = 'var(--border)' }}
    >
      <p style={{
        fontSize: 11.5, fontWeight: 600, color: 'var(--ink)',
        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginBottom: 6,
      }} title={col}>{col}</p>
      <span style={{
        fontSize: 9.5, fontFamily: 'var(--mono)', fontWeight: 500,
        padding: '1px 5px', borderRadius: 3,
        background: isNum ? 'var(--accent-soft)' : 'var(--bg2)',
        color: isNum ? 'var(--accent)' : 'var(--ink-4)',
        border: '1px solid ' + (isNum ? 'var(--accent-ring)' : 'var(--border)'),
        display: 'inline-block', marginBottom: 6,
      }}>{info.type}</span>
      {isNum ? (
        <div>
          <p style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--ink)', fontFamily: 'var(--mono)' }}>
            {Number(info.avg).toFixed(1)}
          </p>
          <p style={{ fontSize: 10.5, color: 'var(--ink-4)', fontFamily: 'var(--mono)', marginTop: 1 }}>
            {Number(info.min).toFixed(0)}–{Number(info.max).toFixed(0)}
          </p>
        </div>
      ) : (
        <div>
          <p style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--ink)' }}>{info.unique}</p>
          <p style={{ fontSize: 10.5, color: 'var(--ink-4)' }}>unique</p>
          {info.missing > 0 && (
            <p style={{ fontSize: 10.5, color: 'var(--ruby)', marginTop: 2 }}>{info.missing} null</p>
          )}
        </div>
      )}
    </div>
  )
}