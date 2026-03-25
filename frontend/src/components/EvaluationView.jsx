import { useState } from 'react'
import { api } from '../utils/api'

export default function EvaluationView({ data, updateStageData }) {
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('kem')

  const runEval = async () => {
    setLoading(true)
    try {
      const result = await api.runEvaluation()
      updateStageData('evaluation', result)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const kems = data?.kem_algorithms || []
  const sigs = data?.signature_algorithms || []
  const classical = data?.classical_algorithms || []

  const formatSize = (bytes) => bytes >= 1024 ? `${(bytes / 1024).toFixed(1)} KB` : `${bytes} B`

  return (
    <div className="fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">🔬 PQC Algorithm Evaluation</h1>
          <p className="section-description">
            {data?.liboqs_available ? '✅ Using liboqs-python — real PQC algorithm execution' : '📊 Using NIST reference data'}
          </p>
        </div>
        <button className="btn btn-primary" onClick={runEval} disabled={loading}>
          {loading ? '⏳ Evaluating...' : '🔬 Run Evaluation'}
        </button>
      </div>

      {data && (
        <>
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <div className="stat-card cyan">
              <div className="stat-value cyan">{data.summary?.total_pqc_evaluated || 0}</div>
              <div className="stat-label">PQC Algorithms</div>
            </div>
            <div className="stat-card success">
              <div className="stat-value success">{kems.length}</div>
              <div className="stat-label">KEM Algorithms</div>
            </div>
            <div className="stat-card info">
              <div className="stat-value" style={{ color: '#3b82f6' }}>{sigs.length}</div>
              <div className="stat-label">Signature Algorithms</div>
            </div>
            <div className="stat-card pink">
              <div className="stat-value" style={{ color: '#ec4899' }}>{data.liboqs_available ? 'Real' : 'Ref'}</div>
              <div className="stat-label">Data Source</div>
            </div>
          </div>

          <div className="tabs">
            {['kem', 'sig', 'classical', 'compare'].map(t => (
              <button key={t} className={`tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
                {t === 'kem' ? '🔐 KEM Algorithms' : t === 'sig' ? '✍️ Signatures' : t === 'classical' ? '📜 Classical' : '📊 Compare'}
              </button>
            ))}
          </div>

          {tab === 'kem' && (
            <div className="card">
              <div className="card-header"><span className="card-title">Key Encapsulation Mechanisms (KEM)</span></div>
              <table className="data-table">
                <thead>
                  <tr><th>Algorithm</th><th>NIST Level</th><th>Pub Key</th><th>Ciphertext</th><th>KeyGen (ms)</th><th>Encaps (ms)</th><th>Decaps (ms)</th><th>Total (ms)</th></tr>
                </thead>
                <tbody>
                  {kems.map((k, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{k.name}</td>
                      <td><span className="badge badge-info">Level {k.nist_level}</span></td>
                      <td className="mono">{formatSize(k.public_key_size)}</td>
                      <td className="mono">{formatSize(k.ciphertext_size)}</td>
                      <td className="mono">{k.keygen_time_ms?.toFixed ? k.keygen_time_ms.toFixed(3) : k.keygen_time_ms}</td>
                      <td className="mono">{k.encaps_time_ms?.toFixed ? k.encaps_time_ms.toFixed(3) : k.encaps_time_ms}</td>
                      <td className="mono">{k.decaps_time_ms?.toFixed ? k.decaps_time_ms.toFixed(3) : k.decaps_time_ms}</td>
                      <td className="mono" style={{ color: 'var(--text-accent)' }}>{k.total_time_ms?.toFixed ? k.total_time_ms.toFixed(3) : k.total_time_ms}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === 'sig' && (
            <div className="card">
              <div className="card-header"><span className="card-title">Digital Signature Algorithms</span></div>
              <table className="data-table">
                <thead>
                  <tr><th>Algorithm</th><th>NIST Level</th><th>Pub Key</th><th>Signature</th><th>KeyGen (ms)</th><th>Sign (ms)</th><th>Verify (ms)</th><th>Total (ms)</th></tr>
                </thead>
                <tbody>
                  {sigs.map((s, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{s.name}</td>
                      <td><span className="badge badge-info">Level {s.nist_level}</span></td>
                      <td className="mono">{formatSize(s.public_key_size)}</td>
                      <td className="mono">{formatSize(s.signature_size)}</td>
                      <td className="mono">{s.keygen_time_ms?.toFixed ? s.keygen_time_ms.toFixed(3) : s.keygen_time_ms}</td>
                      <td className="mono">{s.sign_time_ms?.toFixed ? s.sign_time_ms.toFixed(3) : s.sign_time_ms}</td>
                      <td className="mono">{s.verify_time_ms?.toFixed ? s.verify_time_ms.toFixed(3) : s.verify_time_ms}</td>
                      <td className="mono" style={{ color: 'var(--text-accent)' }}>{s.total_time_ms?.toFixed ? s.total_time_ms.toFixed(3) : s.total_time_ms}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === 'classical' && (
            <div className="card">
              <div className="card-header"><span className="card-title">Classical Algorithms (Reference)</span></div>
              <table className="data-table">
                <thead>
                  <tr><th>Algorithm</th><th>Type</th><th>Pub Key</th><th>KeyGen (ms)</th><th>Operation (ms)</th><th>Quantum Safe</th><th>Threat</th></tr>
                </thead>
                <tbody>
                  {classical.map((c, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.name}</td>
                      <td>{c.type}</td>
                      <td className="mono">{formatSize(c.public_key_size)}</td>
                      <td className="mono">{c.keygen_time_ms}</td>
                      <td className="mono">{c.operation_time_ms}</td>
                      <td>{c.quantum_safe ? '✅' : '❌'}</td>
                      <td style={{ fontSize: '11px', maxWidth: '250px' }}>{c.quantum_threat}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === 'compare' && (
            <div className="card">
              <div className="card-header"><span className="card-title">Performance Comparison: Classical vs PQC</span></div>
              <div className="bar-chart" style={{ marginTop: '16px' }}>
                <div style={{ fontWeight: 600, fontSize: '13px', marginBottom: '12px', color: 'var(--text-secondary)' }}>Key Generation Time (ms) — Lower is better</div>
                {[
                  { label: 'RSA-2048', value: 150, color: 'danger' },
                  ...kems.slice(0, 3).map(k => ({ label: k.name?.split('(')[0], value: k.keygen_time_ms, color: 'cyan' })),
                ].map((bar, i) => (
                  <div className="bar-row" key={i}>
                    <span className="bar-label">{bar.label}</span>
                    <div className="bar-track">
                      <div className={`bar-fill ${bar.color}`} style={{ width: `${Math.min(100, (bar.value / 150) * 100)}%` }} />
                    </div>
                    <span className="bar-value">{bar.value < 1 ? bar.value.toFixed(3) : bar.value.toFixed(1)}</span>
                  </div>
                ))}
              </div>
              <div className="bar-chart" style={{ marginTop: '32px' }}>
                <div style={{ fontWeight: 600, fontSize: '13px', marginBottom: '12px', color: 'var(--text-secondary)' }}>Public Key Size (bytes) — Lower is better</div>
                {[
                  { label: 'RSA-2048', value: 256, color: 'danger' },
                  { label: 'ECDSA P-256', value: 64, color: 'warning' },
                  ...kems.slice(0, 3).map(k => ({ label: k.name?.split('(')[0], value: k.public_key_size, color: 'cyan' })),
                ].map((bar, i) => {
                  const max = Math.max(...kems.map(k => k.public_key_size), 256)
                  return (
                    <div className="bar-row" key={i}>
                      <span className="bar-label">{bar.label}</span>
                      <div className="bar-track">
                        <div className={`bar-fill ${bar.color}`} style={{ width: `${(bar.value / max) * 100}%` }} />
                      </div>
                      <span className="bar-value">{formatSize(bar.value)}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </>
      )}

      {!data && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔬</div>
          <h3>No Evaluation Data</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Run the PQC evaluation to compare algorithms</p>
          <button className="btn btn-primary" onClick={runEval}>🔬 Evaluate PQC</button>
        </div>
      )}
    </div>
  )
}
