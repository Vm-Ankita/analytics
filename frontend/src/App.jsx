import React, { useState, useCallback, useRef } from 'react'
import Topbar        from './components/Topbar.jsx'
import UploadView    from './components/UploadView.jsx'
import AnalyzingView from './components/AnalyzingView.jsx'
import Workspace     from './components/Workspace.jsx'
import { analyzeFile, askStream } from './api.js'

export default function App() {
  const [phase, setPhase]         = useState('upload')
  const [fileInfo, setFileInfo]   = useState(null)
  const [summary, setSummary]     = useState(null)
  const [rows, setRows]           = useState(null)
  const [rawText, setRawText]     = useState('')
  const [chartB64, setChartB64]   = useState(null)
  const [preview, setPreview]     = useState(null)
  const [imageB64, setImageB64]   = useState(null)
  const [insights, setInsights]   = useState('')
  const [modelUsed, setModelUsed] = useState('')
  const [chat, setChat]           = useState([])
  const [streaming, setStreaming] = useState(null)
  const [input, setInput]         = useState('')
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState('')

  const phaseRef    = useRef('upload')
  const metaGotRef  = useRef(false)   // ← tracks if meta arrived

  const goPhase = (p) => { setPhase(p); phaseRef.current = p }

  // ── Upload ──────────────────────────────────────────────────────────────
  const handleFile = useCallback(async (file) => {
    setError('')
    metaGotRef.current = false
    goPhase('analyzing')

    const ext = file.name.split('.').pop().toLowerCase()
    setFileInfo({ name: file.name, ext, icon: '📄', color: '#2563eb', label: ext.toUpperCase() })
    setSummary(null); setRows(null); setRawText('')
    setChartB64(null); setPreview(null); setImageB64(null)
    setInsights(''); setChat([])

    if (['png','jpg','jpeg','gif','webp'].includes(ext)) {
      const reader = new FileReader()
      reader.onload = e => {
        setPreview(e.target.result)
        setImageB64(e.target.result.split(',')[1])
      }
      reader.readAsDataURL(file)
    }

    try {
      setLoading(true)

      const result = await analyzeFile(file, {
        onMeta: (meta) => {
          console.log('✅ meta received', meta)   // helps debug
          metaGotRef.current = true

          if (meta.file_info)           setFileInfo(meta.file_info)
          if (meta.structured_summary)  setSummary(meta.structured_summary)
          if (meta.rows?.length)        setRows(meta.rows)
          if (meta.raw_text)            setRawText(meta.raw_text)
          if (meta.model_used)          setModelUsed(meta.model_used)
          if (meta.chart_b64)           setChartB64(meta.chart_b64)

          goPhase('ready')
        },
        onToken: (partial) => {
          setInsights(partial)
          // Fallback: if meta never fired but tokens are arriving, show workspace
          if (phaseRef.current !== 'ready') goPhase('ready')
        },
      })

      // Final state from completed stream
      if (result?.file_info)           setFileInfo(result.file_info)
      if (result?.structured_summary)  setSummary(result.structured_summary)
      if (result?.rows?.length)        setRows(result.rows)
      if (result?.chart_b64)           setChartB64(result.chart_b64)
      if (result?.insights)            setInsights(result.insights)

      // Safety fallback — if nothing fired at all, still show workspace
      if (phaseRef.current !== 'ready') goPhase('ready')

    } catch (err) {
      console.error('analyze error:', err)
      setError(err.message)
      goPhase('upload')
    } finally {
      setLoading(false)
    }
  }, [])

  // ── Q&A ─────────────────────────────────────────────────────────────────
  const handleSend = useCallback(async () => {
    if (!input.trim() || loading) return
    const q = input.trim()
    setInput('')
    const updated = [...chat, { role: 'user', content: q }]
    setChat(updated)
    setLoading(true)
    setStreaming('')

    let ctx = `File: "${fileInfo?.name}" (${fileInfo?.label})\n`
    if (summary) {
      ctx += `Rows: ${summary.total_rows}, Cols: ${summary.total_cols}\n`
      const auto = (summary.auto_insights || []).slice(0, 3).join('; ')
      if (auto) ctx += `Auto-insights: ${auto}\n`
    } else if (rawText) {
      ctx += `Content:\n${rawText.slice(0, 2000)}\n`
    }

    const hdrs = summary ? Object.keys(summary.columns) : null

    try {
      let acc = ''
      await askStream({
        question:     q,
        fileContext:  ctx,
        conversation: updated,
        imageBase64:  imageB64,
        rows:         rows,
        headers:      hdrs,
        onToken: t => { acc += t; setStreaming(acc) },
      })
      setChat([...updated, { role: 'assistant', content: acc }])
    } catch (err) {
      setChat([...updated, { role: 'assistant', content: `⚠ ${err.message}` }])
    } finally {
      setStreaming(null)
      setLoading(false)
    }
  }, [input, loading, chat, fileInfo, summary, rows, rawText, insights, imageB64])

  // ── Reset ────────────────────────────────────────────────────────────────
  const handleReset = useCallback(() => {
    goPhase('upload')
    setFileInfo(null); setSummary(null); setRows(null); setRawText('')
    setChartB64(null); setPreview(null); setImageB64(null)
    setInsights(''); setChat([]); setError(''); setStreaming(null)
  }, [])

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Topbar fileInfo={fileInfo} phase={phase} modelUsed={modelUsed} onReset={handleReset} />
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {phase === 'upload'    && <UploadView    onFile={handleFile} error={error} />}
        {phase === 'analyzing' && <AnalyzingView fileInfo={fileInfo} />}
        {phase === 'ready'     && (
          <Workspace
            fileInfo={fileInfo}   summary={summary}
            preview={preview}     chartB64={chartB64}
            insights={insights}   chat={chat}
            streaming={streaming} loading={loading}
            input={input}         setInput={setInput}
            onSend={handleSend}
          />
        )}
      </div>
    </div>
  )
}