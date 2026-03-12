import React, { useRef, useEffect } from 'react'
import { renderMd } from '../markdown.js'

const PROSE = `
  .prose { font-size: 13.5px; line-height: 1.72; }
  .prose p      { color: var(--ink-2); margin: 5px 0; }
  .prose h1     { font-size: 15px; font-weight: 700; color: var(--ink); margin: 18px 0 7px; letter-spacing: -.2px; }
  .prose h2     { font-size: 13px; font-weight: 600; color: var(--ink); margin: 14px 0 6px; padding-bottom: 7px; border-bottom: 1px solid var(--border); }
  .prose h3     { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: var(--accent); margin: 12px 0 5px; }
  .prose ul, .prose ol { padding-left: 18px; margin: 5px 0; }
  .prose li     { color: var(--ink-2); margin: 4px 0; }
  .prose strong { color: var(--ink); font-weight: 600; }
  .prose em     { color: var(--ink-3); }
  .prose code   { font-family: var(--mono); font-size: 12px; background: var(--bg2);
                  border: 1px solid var(--border); padding: 1px 6px; border-radius: 4px; color: var(--accent); }
  .prose hr     { border: none; border-top: 1px solid var(--border); margin: 14px 0; }
`

const SUGGESTIONS = {
  tabular:  ['What are the key trends?', 'Any outliers I should know about?', 'Show column correlations', 'Top 3 actionable insights'],
  document: ['What are the main topics?', 'Summarize key findings', 'Any action items?', 'Give me a 3-sentence summary'],
  image:    ['What is shown in this image?', 'Is there any text visible?', 'What stands out?', 'Describe the main elements'],
  code:     ['What does this code do?', 'Are there any bugs?', 'How could this be improved?', 'What are the main functions?'],
  data:     ['Describe the data structure', 'What are the key fields?', 'Any nested relationships?', 'Quick summary'],
  text:     ["What's this document about?", 'Key points?', 'Any statistics mentioned?', 'Main conclusions'],
  unknown:  ['Summarize this file', 'Key insights?', 'Most important info?', 'Any patterns?'],
}

export default function ChatPanel({ fileInfo, chat, streaming, loading, input, setInput, onSend }) {
  const endRef   = useRef()
  const inputRef = useRef()
  const isEmpty  = chat.length === 0 && streaming === null
  const suggs    = SUGGESTIONS[fileInfo?.category] || SUGGESTIONS.unknown

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chat, streaming])

  return (
    <div style={{
      width: '50%', display: 'flex', flexDirection: 'column',
      overflow: 'hidden', background: 'var(--bg)',
    }}>
      <style>{PROSE}</style>

      {/* Header */}
      <div style={{
        height: 44, padding: '0 18px',
        borderBottom: '1px solid var(--border)',
        display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0,
        background: 'var(--surface)',
      }}>
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="var(--ink-3)" strokeWidth="1.6" strokeLinecap="round">
          <path d="M14 10a2 2 0 0 1-2 2H5l-3 3V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v6z"/>
        </svg>
        <span style={{ fontWeight: 600, fontSize: 13, color: 'var(--ink)' }}>Chat</span>
        {chat.length > 0 && (
          <span style={{
            fontSize: 11, padding: '2px 7px', borderRadius: 'var(--r99)',
            background: 'var(--bg2)', border: '1px solid var(--border)', color: 'var(--ink-4)',
          }}>
            {Math.floor(chat.length / 2)} turn{Math.floor(chat.length / 2) !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: 10 }}>

        {isEmpty && (
          <div style={{ animation: 'rise .35s ease' }}>
            {/* Welcome card */}
            <div style={{
              padding: '16px 18px', borderRadius: 'var(--r12)',
              background: 'var(--surface)', border: '1px solid var(--border)',
              boxShadow: 'var(--s1)', marginBottom: 16,
            }}>
              <p style={{ fontWeight: 600, fontSize: 14, color: 'var(--ink)', marginBottom: 5 }}>
                Ask anything about your file
              </p>
              <p style={{ fontSize: 13, color: 'var(--ink-3)', lineHeight: 1.65 }}>
                Statistics and charts are already computed. Ask follow-up questions for deeper AI analysis.
              </p>
            </div>

            <p style={{
              fontSize: 10.5, fontWeight: 700, letterSpacing: '.07em',
              textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 8,
            }}>Suggested questions</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              {suggs.map((q, i) => (
                <button key={q} onClick={() => { setInput(q); inputRef.current?.focus() }} style={{
                  textAlign: 'left', padding: '9px 13px', borderRadius: 'var(--r8)',
                  border: '1px solid var(--border)',
                  background: 'var(--surface)', color: 'var(--ink-2)',
                  fontSize: 13, transition: 'all .14s', width: '100%',
                  animation: `rise .3s ease ${i * .05}s both`,
                  display: 'flex', alignItems: 'center', gap: 8,
                }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'var(--accent-soft)'; e.currentTarget.style.borderColor = 'var(--accent-ring)'; e.currentTarget.style.color = 'var(--accent)' }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'var(--surface)'; e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--ink-2)' }}
                >
                  <svg width="12" height="12" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" style={{ flexShrink: 0, opacity: .5 }}>
                    <path d="M7 1v6M4 4l3-3 3 3M2 10h10M2 13h7"/>
                  </svg>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {chat.map((msg, i) => <Bubble key={i} msg={msg} />)}

        {/* Streaming */}
        {streaming !== null && (
          <div style={{ alignSelf: 'flex-start', maxWidth: '90%', animation: 'rise .2s ease' }}>
            <div style={{
              padding: '10px 14px', borderRadius: '3px 12px 12px 12px',
              background: 'var(--surface)', border: '1px solid var(--border)',
              boxShadow: 'var(--s1)',
            }}>
              {streaming ? (
                <div className="prose" dangerouslySetInnerHTML={{ __html: renderMd(streaming) }} />
              ) : (
                <div style={{ display: 'flex', gap: 5, alignItems: 'center', padding: '2px 0' }}>
                  {[0,1,2].map(i => (
                    <div key={i} style={{
                      width: 7, height: 7, borderRadius: '50%', background: 'var(--border-md)',
                      animation: `pulse3 1.3s ease ${i * .19}s infinite`,
                    }} />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '12px 18px', flexShrink: 0,
        borderTop: '1px solid var(--border)',
        background: 'var(--surface)',
      }}>
        <div style={{
          display: 'flex', gap: 8, alignItems: 'flex-end',
          padding: '8px 8px 8px 14px',
          borderRadius: 'var(--r10)',
          background: 'var(--bg)',
          border: '1.5px solid var(--border-md)',
          transition: 'border-color .15s, box-shadow .15s',
        }}
          onFocusCapture={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(37,99,235,.1)' }}
          onBlurCapture={e => { e.currentTarget.style.borderColor = 'var(--border-md)'; e.currentTarget.style.boxShadow = 'none' }}
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSend() } }}
            placeholder="Ask a question about your file…"
            rows={1}
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              color: 'var(--ink)', fontSize: 14, resize: 'none',
              lineHeight: 1.5, maxHeight: 120, overflow: 'auto', padding: 0,
            }}
          />
          <button onClick={onSend} disabled={loading || !input.trim()} style={{
            width: 34, height: 34, borderRadius: 8, flexShrink: 0,
            background: loading || !input.trim() ? 'var(--border)' : 'var(--ink)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'background .15s',
          }}
            onMouseEnter={e => { if (!loading && input.trim()) e.currentTarget.style.background = 'var(--accent)' }}
            onMouseLeave={e => { if (!loading && input.trim()) e.currentTarget.style.background = 'var(--ink)' }}
          >
            {loading ? (
              <div style={{
                width: 14, height: 14,
                border: '2px solid rgba(255,255,255,.25)',
                borderTopColor: '#fff', borderRadius: '50%',
                animation: 'spin .7s linear infinite',
              }} />
            ) : (
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round">
                <path d="M8 14V2M3 7l5-5 5 5"/>
              </svg>
            )}
          </button>
        </div>
        <p style={{ fontSize: 11, color: 'var(--ink-4)', marginTop: 6, paddingLeft: 2 }}>
          ↵ Send · Shift+↵ New line
        </p>
      </div>
    </div>
  )
}

function Bubble({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{
      alignSelf: isUser ? 'flex-end' : 'flex-start',
      maxWidth: '88%', animation: 'rise .22s ease',
    }}>
      {isUser ? (
        <div style={{
          padding: '9px 14px',
          borderRadius: '12px 3px 12px 12px',
          background: 'var(--ink)', color: '#fff',
          fontSize: 14, lineHeight: 1.55,
        }}>
          {msg.content}
        </div>
      ) : (
        <div style={{
          padding: '10px 14px',
          borderRadius: '3px 12px 12px 12px',
          background: 'var(--surface)', border: '1px solid var(--border)',
          boxShadow: 'var(--s1)',
        }}>
          <div className="prose" dangerouslySetInnerHTML={{ __html: renderMd(msg.content) }} />
        </div>
      )}
    </div>
  )
}