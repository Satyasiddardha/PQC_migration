import { useState } from 'react'
import { api } from '../utils/api'

export default function RiskView({ data, updateStageData }) {
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('overview')
  const [targetHost, setTargetHost] = useState('example.com')

  const runAnalysis = async () => {
    setLoading(true)
    try {
      const result = await api.runRiskAnalysis(targetHost)
      updateStageData('risk', result)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const analysis = data?.analysis
  const tls = data?.tls
  const cve = data?.cve

  return (
    <div className="fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">⚠️ Risk Assessment</h1>
          <p className="section-description">SSLyze TLS analysis + CVE vulnerability scanning</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <input 
            type="text" 
            value={targetHost} 
            onChange={e => setTargetHost(e.target.value)} 
            placeholder="e.g. google.com"
            style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text-primary)', width: '200px', fontSize: '14px' }}
          />
          <button className="btn btn-primary" onClick={runAnalysis} disabled={loading}>
            {loading ? '⏳ Analyzing...' : '🔎 Run Risk Analysis'}
          </button>
        </div>
      </div>

      {data && (
        <>
          <div className="stats-grid">
            <div className="stat-card danger">
              <div className="stat-value danger">{analysis?.severity_breakdown?.critical || 0}</div>
              <div className="stat-label">Critical</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-value warning">{analysis?.severity_breakdown?.high || 0}</div>
              <div className="stat-label">High</div>
            </div>
            <div className="stat-card info">
              <div className="stat-value" style={{ color: '#f59e0b' }}>{analysis?.severity_breakdown?.medium || 0}</div>
              <div className="stat-label">Medium</div>
            </div>
            <div className="stat-card success">
              <div className="stat-value success">{analysis?.severity_breakdown?.low || 0}</div>
              <div className="stat-label">Low</div>
            </div>
            <div className="stat-card pink">
              <div className="stat-value" style={{ color: '#ec4899' }}>{analysis?.risk_percentage || 0}%</div>
              <div className="stat-label">Risk Score</div>
            </div>
            <div className="stat-card cyan">
              <div className="stat-value cyan">{analysis?.quantum_vulnerable_count || 0}</div>
              <div className="stat-label">Quantum Vulnerable</div>
            </div>
          </div>

          <div className="tabs">
            {['overview', 'tls', 'cve'].map(t => (
              <button key={t} className={`tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
                {t === 'overview' ? '📊 Overview' : t === 'tls' ? '🔒 TLS Analysis' : '🐛 CVE Database'}
              </button>
            ))}
          </div>

          {tab === 'overview' && analysis && (
            <div className="card">
              <div className="card-header"><span className="card-title">Risk Findings</span></div>
              <table className="data-table">
                <thead>
                  <tr><th>Source</th><th>Severity</th><th>Risk Score</th><th>Details</th><th>Quantum</th></tr>
                </thead>
                <tbody>
                  {(analysis.findings || []).slice(0, 20).map((f, i) => (
                    <tr key={i}>
                      <td><span className="badge badge-info">{f.source}</span></td>
                      <td><span className={`badge badge-${f.severity?.toLowerCase() || 'medium'}`}>{f.severity}</span></td>
                      <td className="mono">{f.risk_score}</td>
                      <td style={{ maxWidth: '400px', fontSize: '12px' }}>{f.description?.substring(0, 120)}</td>
                      <td>{f.quantum_vulnerable ? '⚠️' : '✅'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === 'tls' && tls && (
            <div className="card">
              <div className="card-header">
                <span className="card-title">TLS Analysis — {tls.target}</span>
                <span className="badge badge-info">SSLyze + CertCheck</span>
              </div>
              
              {/* Prominent Certificate Status Block */}
              {tls.findings?.filter(f => f.type === 'certificate_validity').map((certObj, idx) => (
                <div key={`cert-${idx}`} style={{ 
                  margin: '16px', padding: '16px', borderRadius: '12px',
                  background: certObj.severity === 'CRITICAL' ? 'rgba(239,68,68,0.1)' : certObj.severity === 'HIGH' ? 'rgba(245,158,11,0.1)' : 'rgba(16,185,129,0.1)',
                  border: `1px solid var(--${certObj.severity === 'CRITICAL' ? 'danger' : certObj.severity === 'HIGH' ? 'warning' : 'success'})`
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <span style={{ fontSize: '24px' }}>
                      {certObj.severity === 'CRITICAL' ? '🚨' : certObj.severity === 'HIGH' ? '⚠️' : '✅'}
                    </span>
                    <h3 style={{ margin: 0, fontSize: '16px', color: 'var(--text-primary)' }}>SSL Certificate Status</h3>
                  </div>
                  <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>{certObj.message}</p>
                  <p style={{ fontSize: '13px', color: 'var(--text-accent)' }}>💡 {certObj.recommendation}</p>
                </div>
              ))}

              <h4 style={{ margin: '20px 16px 10px', fontSize: '14px', color: 'var(--text-secondary)' }}>Protocol & Cipher Suite Config</h4>
              {(tls.findings || []).filter(f => f.type !== 'certificate_validity').map((f, i) => (
                <div key={i} style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <span className={`badge badge-${f.severity?.toLowerCase() || 'medium'}`}>{f.severity}</span>
                    <span style={{ fontWeight: 600, fontSize: '13px' }}>{f.protocol}</span>
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>{f.message}</p>
                  <p style={{ fontSize: '12px', color: 'var(--text-accent)' }}>💡 {f.recommendation}</p>
                  {f.cipher_suites && (
                    <div className="code-block" style={{ marginTop: '8px', fontSize: '11px' }}>
                      {f.cipher_suites.join('\n')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {tab === 'cve' && cve && (
            <div className="card">
              <div className="card-header">
                <span className="card-title">Crypto CVE Database</span>
                <span className="badge badge-info">{cve.tool}</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr><th>CVE ID</th><th>Library</th><th>Severity</th><th>CVSS</th><th>Description</th><th>Quantum</th></tr>
                </thead>
                <tbody>
                  {(cve.findings || []).map((f, i) => (
                    <tr key={i}>
                      <td className="mono" style={{ color: 'var(--text-accent)' }}>{f.cve_id}</td>
                      <td style={{ fontWeight: 600 }}>{f.library}</td>
                      <td><span className={`badge badge-${f.severity?.toLowerCase()}`}>{f.severity}</span></td>
                      <td className="mono">{f.cvss}</td>
                      <td style={{ fontSize: '12px', maxWidth: '300px' }}>{f.description?.substring(0, 100)}</td>
                      <td>{f.quantum_relevant ? '⚠️' : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {!data && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <h3>No Risk Data</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Run discovery first, then analyze risk</p>
          <button className="btn btn-primary" onClick={runAnalysis}>🔎 Analyze Risk</button>
        </div>
      )}
    </div>
  )
}
