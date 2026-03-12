const BASE = '/api'

export async function checkHealth() {
  const res = await fetch('/health')
  if (!res.ok) throw new Error('Backend offline')
  return res.json()
}

export async function analyzeFile(file, { onMeta, onToken } = {}) {
  const form = new FormData()
  form.append('file', file)

  const res = await fetch(`${BASE}/analyze`, { method: 'POST', body: form })
  if (!res.ok) {
    const text = await res.text().catch(() => 'Server error')
    throw new Error(text || `HTTP ${res.status}`)
  }

  const reader  = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer   = ''
  let meta     = null
  let insights = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    // Split on double-newline (SSE event boundary) for reliability
    const events = buffer.split('\n\n')
    buffer = events.pop()  // keep incomplete last chunk

    for (const event of events) {
      // Each event may have multiple lines; find the data: line
      for (const line of event.split('\n')) {
        if (!line.startsWith('data: ')) continue
        const raw = line.slice(6).trim()
        if (!raw || raw === '[DONE]') continue

        let msg
        try { msg = JSON.parse(raw) }
        catch { continue }

        if (msg.type === 'meta') {
          meta = msg
          onMeta?.(meta)
        } else if (msg.type === 'token' && msg.token) {
          insights += msg.token
          onToken?.(insights)
        }
      }
    }
  }

  // Flush remaining buffer
  if (buffer) {
    for (const line of buffer.split('\n')) {
      if (!line.startsWith('data: ')) continue
      const raw = line.slice(6).trim()
      if (!raw || raw === '[DONE]') continue
      try {
        const msg = JSON.parse(raw)
        if (msg.type === 'meta') { meta = msg; onMeta?.(meta) }
        else if (msg.type === 'token' && msg.token) { insights += msg.token; onToken?.(insights) }
      } catch {}
    }
  }

  return { ...meta, insights }
}

export async function askStream({
  question, fileContext, conversation,
  imageBase64, rows, headers, onToken
}) {
  const res = await fetch(`${BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      file_context:  fileContext,
      conversation:  conversation.map(m => ({ role: m.role, content: m.content })),
      image_base64:  imageBase64 || null,
      rows:          rows    || null,
      headers:       headers || null,
    }),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => 'Server error')
    throw new Error(text || `HTTP ${res.status}`)
  }

  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) {
    const d = await res.json()
    onToken?.(d.answer)
    return d.answer
  }

  const reader  = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let full   = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop()

    for (const event of events) {
      for (const line of event.split('\n')) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6).trim()
        if (payload === '[DONE]') return full
        try {
          const { token } = JSON.parse(payload)
          if (token) { full += token; onToken?.(token) }
        } catch {}
      }
    }
  }
  return full
}