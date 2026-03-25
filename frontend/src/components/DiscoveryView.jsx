import { useState } from 'react'
import { api } from '../utils/api'

export default function DiscoveryView({ data, updateStageData }) {
  const [loading, setLoading] = useState(false)
  const [scanPath, setScanPath] = useState('../../src')

  const runScan = async () => {
    setLoading(true)
    try {
      const result = await api.runDiscovery(scanPath)
      updateStageData('discovery', result)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const findings = data?.findings || []
  const grouped = {}
  findings.forEach(f => {
    const algo = f.algorithm || 'Unknown'
    if (!grouped[algo]) grouped[algo] = []
    grouped[algo].push(f)
  })

  return (
    <div className="fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">🔍 Cryptographic Discovery</h1>
          <p className="section-description">Semgrep + regex-based static analysis for crypto assets</p>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <input
            type="text"
            value={scanPath}
            onChange={e => setScanPath(e.target.value)}
            style={{
              background: 'var(--bg-glass)', border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)', padding: '8px 14px', color: 'var(--text-primary)',
              fontFamily: 'var(--font-mono)', fontSize: '12px', width: '200px',
            }}
          />
          <button className="btn btn-primary" onClick={runScan} disabled={loading}>
            {loading ? '⏳ Scanning...' : '🔍 Scan'}
          </button>
        </div>
      </div>

      {data && (
        <>
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <div className="stat-card cyan">
              <div className="stat-value cyan">{data.total || 0}</div>
              <div className="stat-label">Total Findings</div>
            </div>
            <div className="stat-card danger">
              <div className="stat-value danger">{findings.filter(f => f.severity === 'HIGH' || f.severity === 'ERROR' || f.severity === 'CRITICAL').length}</div>
              <div className="stat-label">High / Critical</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-value warning">{Object.keys(grouped).length}</div>
              <div className="stat-label">Unique Algorithms</div>
            </div>
            <div className="stat-card info">
              <div className="stat-value" style={{ color: '#3b82f6' }}>{findings.filter(f => f.quantum_vulnerable).length}</div>
              <div className="stat-label">Quantum Vulnerable</div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">Discovered Crypto Assets</span>
              <span className="badge badge-info">Tool: {data.tool || 'scanner'}</span>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Algorithm</th>
                  <th>Severity</th>
                  <th>File</th>
                  <th>Line</th>
                  <th>Quantum Risk</th>
                  <th>PQC Replacement</th>
                </tr>
              </thead>
              <tbody>
                {findings.map((f, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{f.algorithm}</td>
                    <td><span className={`badge badge-${f.severity === 'ERROR' || f.severity === 'CRITICAL' ? 'critical' : f.severity === 'HIGH' ? 'high' : f.severity === 'WARNING' || f.severity === 'MEDIUM' ? 'medium' : 'low'}`}>{f.severity}</span></td>
                    <td className="mono">{f.file}</td>
                    <td className="mono">{f.line}</td>
                    <td>{f.quantum_vulnerable ? '⚠️ Vulnerable' : '✅ Safe'}</td>
                    <td style={{ fontSize: '12px' }}>{f.pqc_replacement || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {findings.length > 0 && (
            <div className="card" style={{ marginTop: '20px' }}>
              <div className="card-header">
                <span className="card-title">Code Context</span>
              </div>
              {findings.slice(0, 5).map((f, i) => (
                <div key={i} style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    📁 {f.file}:{f.line} — <span style={{ color: f.quantum_vulnerable ? 'var(--critical)' : 'var(--low)' }}>{f.algorithm}</span>
                  </div>
                  <div className="code-block">
                    <span className="code-line-number">{f.line}</span>
                    <span style={{ color: f.quantum_vulnerable ? '#fca5a5' : '#86efac' }}>{f.code_snippet}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {!data && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
          <h3 style={{ fontSize: '18px', marginBottom: '8px' }}>No Scan Results</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Click "Scan" to discover cryptographic assets in your codebase</p>
          <button className="btn btn-primary" onClick={runScan}>🔍 Start Discovery</button>
        </div>
      )}
    </div>
  )
}
