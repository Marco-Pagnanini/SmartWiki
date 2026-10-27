import { useEffect, useState } from 'react'
import './App.css'

type Status = 'loading' | 'ok' | 'error'

const MESSAGES: Record<Status, string> = {
  loading: 'Verifica connessione…',
  ok: 'Backend e database connessi',
  error: 'Backend o database non raggiungibili',
}

function App() {
  const [status, setStatus] = useState<Status>('loading')

  useEffect(() => {
    // Percorso relativo: funziona sia con il proxy di Vite sia con nginx
    fetch('/api/health/db')
      .then((res) => setStatus(res.ok ? 'ok' : 'error'))
      .catch(() => setStatus('error'))
  }, [])

  return (
    <main className="app">
      <h1>Smart Wiki</h1>
      <p className={`status status-${status}`}>{MESSAGES[status]}</p>
    </main>
  )
}

export default App
