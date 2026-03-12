import React from 'react'
import AnalysisPanel from './AnalysisPanel.jsx'
import ChatPanel from './ChatPanel.jsx'

export default function Workspace({ fileInfo, summary, preview, chartB64, insights, chat, streaming, loading, input, setInput, onSend }) {
  return (
    <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
      <AnalysisPanel fileInfo={fileInfo} summary={summary} preview={preview} chartB64={chartB64} insights={insights} />
      <ChatPanel fileInfo={fileInfo} chat={chat} streaming={streaming} loading={loading} input={input} setInput={setInput} onSend={onSend} />
    </div>
  )
}