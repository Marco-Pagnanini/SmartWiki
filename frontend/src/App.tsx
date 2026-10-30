import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent, ReactNode } from 'react'
import './App.css'

type Role = 'user' | 'assistant'

interface Message {
  role: Role
  content: string
  error?: boolean
}

const SUGGESTIONS = [
  'Cosa sai fare?',
  'Trova il documento manuale-ferie.pdf',
  'Aggiungi un nuovo documento alla wiki',
]

// Markdown minimo per le risposte (grassetto, `codice`, elenchi), senza HTML grezzo
function renderInline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) return <strong key={i}>{part.slice(2, -2)}</strong>
    if (part.startsWith('`') && part.endsWith('`')) return <code key={i}>{part.slice(1, -1)}</code>
    return part
  })
}

function Markdown({ text }: { text: string }) {
  const blocks: ReactNode[] = []
  let list: string[] = []
  const flush = () => {
    if (list.length) {
      blocks.push(<ul key={blocks.length}>{list.map((item, i) => <li key={i}>{renderInline(item)}</li>)}</ul>)
      list = []
    }
  }
  for (const line of text.split('\n')) {
    const item = line.match(/^\s*[-*]\s+(.*)$/)
    if (item) {
      list.push(item[1])
    } else {
      flush()
      if (line.trim()) blocks.push(<p key={blocks.length}>{renderInline(line)}</p>)
    }
  }
  flush()
  return <>{blocks}</>
}

function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
      <path fill="currentColor" d="M3.4 20.4 21 12 3.4 3.6l-.01 6.53L15.99 12 3.39 13.87z" />
    </svg>
  )
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // La textarea cresce con il testo, fino a un massimo
  useEffect(() => {
    const el = inputRef.current
    if (!el) return
    el.style.height = 'auto'
    // Vuota: altezza naturale (una riga); misurarla al primo render può dare valori errati
    if (input) el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [input])

  async function send(text: string) {
    const message = text.trim()
    if (!message || loading) return
    // Al backend va solo la conversazione riuscita, senza i messaggi di errore
    const history = messages.filter((m) => !m.error).map(({ role, content }) => ({ role, content }))
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : `Errore ${res.status}`)
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }])
    } catch (e) {
      const detail = e instanceof Error ? e.message : 'Errore sconosciuto'
      setMessages((prev) => [...prev, { role: 'assistant', content: `Qualcosa è andato storto: ${detail}`, error: true }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    send(input)
  }

  // Invio manda il messaggio, Maiusc+Invio va a capo
  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      send(input)
    }
  }

  const empty = messages.length === 0

  return (
    <div className="app">
      <header className="topbar">
        <img src="/logo.png" alt="" className="topbar-logo" />
        <span className="topbar-title">Smart Wiki</span>
      </header>

      <main className={`chat ${empty ? 'chat-empty' : ''}`}>
        {empty ? (
          <section className="welcome">
            <img src="/logo.png" alt="Logo Smart Wiki" className="welcome-logo" />
            <h1 className="welcome-title">Ciao!</h1>
            <p className="welcome-subtitle">Come posso aiutarti con la wiki oggi?</p>
            <div className="suggestions">
              {SUGGESTIONS.map((s) => (
                <button key={s} type="button" className="suggestion" onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </section>
        ) : (
          <div className="messages">
            {messages.map((m, i) =>
              m.role === 'user' ? (
                <div key={i} className="msg msg-user">
                  <div className="bubble">{m.content}</div>
                </div>
              ) : (
                <div key={i} className={`msg msg-assistant ${m.error ? 'msg-error' : ''}`}>
                  <img src="/logo.png" alt="" className="avatar" />
                  <div className="answer">
                    <Markdown text={m.content} />
                  </div>
                </div>
              ),
            )}
            {loading && (
              <div className="msg msg-assistant" aria-live="polite">
                <img src="/logo.png" alt="" className="avatar avatar-thinking" />
                <div className="answer thinking">
                  <span className="shimmer" />
                  <span className="shimmer short" />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      <footer className="composer-area">
        <form className="composer" onSubmit={onSubmit}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Chiedi a Smart Wiki"
            rows={1}
            aria-label="Messaggio"
            autoFocus
          />
          <button type="submit" className="send" disabled={!input.trim() || loading} aria-label="Invia">
            <SendIcon />
          </button>
        </form>
        <p className="disclaimer">Smart Wiki può commettere errori: verifica le informazioni importanti.</p>
      </footer>
    </div>
  )
}

export default App
