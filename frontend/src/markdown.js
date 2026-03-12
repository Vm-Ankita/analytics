export function renderMd(text) {
  if (!text) return ''
  const lines = text.split('\n')
  const out   = []
  let inUL = false, inOL = false

  const close = () => {
    if (inUL) { out.push('</ul>'); inUL = false }
    if (inOL) { out.push('</ol>'); inOL = false }
  }
  const inline = s => s
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,     '<em>$1</em>')
    .replace(/`(.+?)`/g,       '<code>$1</code>')

  for (const raw of lines) {
    if      (/^### /.test(raw)) { close(); out.push(`<h3>${inline(raw.slice(4))}</h3>`) }
    else if (/^## /.test(raw))  { close(); out.push(`<h2>${inline(raw.slice(3))}</h2>`) }
    else if (/^# /.test(raw))   { close(); out.push(`<h1>${inline(raw.slice(2))}</h1>`) }
    else if (/^[-*] /.test(raw)) {
      if (!inUL) { close(); out.push('<ul>'); inUL = true }
      out.push(`<li>${inline(raw.slice(2))}</li>`)
    }
    else if (/^\d+\. /.test(raw)) {
      if (!inOL) { close(); out.push('<ol>'); inOL = true }
      out.push(`<li>${inline(raw.replace(/^\d+\. /, ''))}</li>`)
    }
    else if (/^---+$/.test(raw.trim())) { close(); out.push('<hr/>') }
    else if (raw.trim() === '')         { close(); out.push('<br/>') }
    else                                { close(); out.push(`<p>${inline(raw)}</p>`) }
  }
  close()
  return out.join('')
}
