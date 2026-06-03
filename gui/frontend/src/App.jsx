import { useEffect, useState } from 'react'
import './App.css'

const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:7000'

function App() {
  const [token, setToken] = useState('')
  const [username, setUsername] = useState('')
  const [status, setStatus] = useState(null)
  const [model, setModel] = useState(null)
  const [nodeId, setNodeId] = useState('')
  const [points, setPoints] = useState(null)
  const [prompt, setPrompt] = useState('')
  const [inference, setInference] = useState(null)
  const [error, setError] = useState('')

  const headers = token ? { Authorization: 'Bearer ' + token } : {}

  const handleLogin = async (event) => {
    event.preventDefault()
    setError('')
    const response = await fetch(`${backendUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username })
    })
    if (!response.ok) {
      setError('Login failed')
      return
    }
    const data = await response.json()
    setToken(data.token)
  }

  const loadStatus = async () => {
    const response = await fetch(`${backendUrl}/status`, { headers })
    if (response.ok) {
      setStatus(await response.json())
    }
  }

  const loadModel = async () => {
    const response = await fetch(`${backendUrl}/models/current`, { headers })
    if (response.ok) {
      setModel(await response.json())
    }
  }

  const loadPoints = async () => {
    if (!nodeId) return
    const response = await fetch(`${backendUrl}/points/${nodeId}`, { headers })
    if (response.ok) {
      setPoints(await response.json())
    }
  }

  const submitInference = async (event) => {
    event.preventDefault()
    const response = await fetch(`${backendUrl}/infer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify({ prompt })
    })
    if (response.ok) {
      setInference(await response.json())
    }
  }

  useEffect(() => {
    if (!token) return
    loadStatus()
    loadModel()
  }, [token])

  if (!token) {
    return (
      <div className="app">
        <form className="card" onSubmit={handleLogin}>
          <h1>Mesh AI Login</h1>
          <label>
            Username
            <input value={username} onChange={(event) => setUsername(event.target.value)} required />
          </label>
          <button type="submit">Sign in</button>
          {error && <p className="error">{error}</p>}
        </form>
      </div>
    )
  }

  return (
    <div className="app">
      <header>
        <h1>Mesh AI Dashboard</h1>
        <button type="button" onClick={() => setToken('')}>Sign out</button>
      </header>

      <section className="grid">
        <div className="card">
          <h2>Network Health</h2>
          <p>Nodes: {status?.nodes ?? '—'}</p>
          <p>Total Capacity (GB): {status?.total_capacity_gb ?? '—'}</p>
          <button type="button" onClick={loadStatus}>Refresh</button>
        </div>
        <div className="card">
          <h2>Active Model</h2>
          <p>ID: {model?.id ?? '—'}</p>
          <p>Tier: {model?.tier ?? '—'}</p>
          <p>Layers: {model?.layers ?? '—'}</p>
          <button type="button" onClick={loadModel}>Refresh</button>
        </div>
      </section>

      <section className="grid">
        <div className="card">
          <h2>Points Balance</h2>
          <label>
            Node ID
            <input value={nodeId} onChange={(event) => setNodeId(event.target.value)} placeholder="node-uuid" />
          </label>
          <button type="button" onClick={loadPoints}>Get Balance</button>
          <p>Balance: {points?.balance ?? '—'}</p>
        </div>
        <div className="card">
          <h2>Inference</h2>
          <form onSubmit={submitInference}>
            <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder="Ask the mesh..." required />
            <button type="submit">Run</button>
          </form>
          <p>Status: {inference?.status ?? '—'}</p>
          <p>Output: {inference?.output ?? '—'}</p>
        </div>
      </section>
    </div>
  )
}

export default App
