import { useState } from 'react'
import { api } from '../utils/api'

export default function CBOMView({ data, updateStageData }) {
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState('summary')

  const genCBOM = async () => {
    setLoading(true)
    try {
      const result = await api.generateCBOM()
      updateStageData('cbom', result)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const exportJson = () => {
    if (!data) return
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cbom_${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const summary = data?.summary || {}
  const inventory = data?.algorithm_inventory || []
  const migration = data?.migration_plan || {}
  const stages = data?.metadata?.pipeline_stages_completed || []

  return (
    <div className="fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">📋 Cryptographic Bill of Materials</h1>
          <p className="section-description">Unified CBOM from all pipeline stages</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-primary" onClick={genCBOM} disabled={loading}>
            {loading ? '⏳ Generating...' : '📋 Generate CBOM'}
          </button>
          {data && <button className="btn btn-secondary" onClick={exportJson}>⬇ Export JSON</button>}
        </div>
      </div>

      {data && (
        <>
          <div className="stats-grid">
            <div className="stat-card cyan">
              <div className="stat-value cyan">{summary.total_algorithms_found || 0}</div>
              <div className="stat-label">Algorithms</div>
            </div>
            <div className="stat-card danger">
              <div className="stat-value danger">{summary.quantum_vulnerable_algorithms || 0}</div>
              <div className="stat-label">Quantum Vulnerable</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-value warning">{summary.overall_risk_percentage || 0}%</div>
              <div className="stat-label">Risk Score</div>
            </div>
            <div className="stat-card success">
              <div className="stat-value success">{summary.migration_readiness_score || 0}</div>
              <div className="stat-label">Readiness</div>
            </div>
            <div className="stat-card info">
              <div className="stat-value" style={{ color: '#3b82f6' }}>{stages.length}</div>
              <div className="stat-label">Stages Completed</div>
            </div>
            <div className="stat-card pink">
              <div className="stat-value" style={{ color: '#ec4899' }}>{summary.critical_actions_needed || 0}</div>
              <div className="stat-label">Critical Actions</div>
            </div>
          </div>

          <div className="tabs">
            {['summary', 'inventory', 'migration', 'json'].map(t => (
              <button key={t} className={`tab ${viewMode === t ? 'active' : ''}`} onClick={() => setViewMode(t)}>
                {t === 'summary' ? '📊 Summary' : t === 'inventory' ? '📦 Inventory' : t === 'migration' ? '🔄 Migration' : '{ } JSON'}
              </button>
            ))}
          </div>

          {viewMode === 'summary' && (
            <div className="card">
              <div className="card-header"><span className="card-title">Executive Summary</span></div>
              <div style={{ marginBottom: '20px' }}>
                <div className={`badge ${summary.migration_readiness_score > 50 ? 'badge-medium' : 'badge-critical'}`} style={{ fontSize: '13px', padding: '6px 14px' }}>
                  {summary.migration_readiness_label || 'N/A'}
                </div>
              </div>
              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.8, marginBottom: '20px' }}>
                {summary.recommendation}
              </p>
              <div className="bar-chart">
                {[
                  { label: 'Critical', value: summary.severity_breakdown?.critical || 0, color: 'danger' },
                  { label: 'High', value: summary.severity_breakdown?.high || 0, color: 'warning' },
                  { label: 'Medium', value: summary.severity_breakdown?.medium || 0, color: 'info' },
                  { label: 'Low', value: summary.severity_breakdown?.low || 0, color: 'success' },
                ].map(bar => {
                  const max = Math.max(bar.value, 1)
                  const total = (summary.severity_breakdown?.critical || 0) + (summary.severity_breakdown?.high || 0) + (summary.severity_breakdown?.medium || 0) + (summary.severity_breakdown?.low || 0) || 1
                  return (
                    <div className="bar-row" key={bar.label}>
                      <span className="bar-label">{bar.label}</span>
                      <div className="bar-track">
                        <div className={`bar-fill ${bar.color}`} style={{ width: `${(bar.value / total) * 100}%` }} />
                      </div>
                      <span className="bar-value">{bar.value}</span>
                    </div>
                  )
                })}
              </div>
              <div style={{ marginTop: '20px', fontSize: '12px', color: 'var(--text-muted)' }}>
                <p>Pipeline stages: {stages.join(' → ')}</p>
                <p>Generated: {data.metadata?.generated_at}</p>
              </div>
            </div>
          )}

          {viewMode === 'inventory' && (
            <div className="card">
              <div className="card-header"><span className="card-title">Algorithm Inventory</span></div>
              <table className="data-table">
                <thead>
                  <tr><th>Algorithm</th><th>Category</th><th>Occurrences</th><th>Quantum Vulnerable</th><th>PQC Replacement</th></tr>
                </thead>
                <tbody>
                  {inventory.map((algo, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{algo.algorithm}</td>
                      <td>{algo.category}</td>
                      <td className="mono">{algo.total_occurrences}</td>
                      <td>{algo.quantum_vulnerable ? '⚠️ YES' : '✅ No'}</td>
                      <td style={{ fontSize: '12px' }}>{algo.pqc_replacement || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {inventory.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                  <div className="card-title" style={{ marginBottom: '12px' }}>Locations</div>
                  {inventory.map((algo, i) => (
                    <div key={i} style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-accent)', marginBottom: '6px' }}>
                        {algo.algorithm} ({algo.total_occurrences} locations)
                      </div>
                      {(algo.locations || []).map((loc, j) => (
                        <div key={j} style={{ fontSize: '12px', color: 'var(--text-muted)', paddingLeft: '12px' }}>
                          📁 {loc.file}:{loc.line} — <code style={{ color: 'var(--text-secondary)' }}>{loc.code_snippet?.substring(0, 80)}</code>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {viewMode === 'migration' && (
            <div className="card">
              <div className="card-header"><span className="card-title">Migration Summary</span></div>
              <div style={{ marginBottom: '16px' }}>
                <span className="badge badge-info" style={{ marginRight: '8px' }}>Total: {migration.total_items || 0}</span>
                <span className="badge badge-critical" style={{ marginRight: '8px' }}>Critical: {migration.summary?.critical_migrations || 0}</span>
                <span className="badge badge-high">High: {migration.summary?.high_priority || 0}</span>
              </div>
              {migration.recommended_approach && (
                <div style={{ padding: '16px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', marginBottom: '16px' }}>
                  <div style={{ fontWeight: 600, fontSize: '13px', marginBottom: '6px' }}>{migration.recommended_approach.phase} Priority</div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{migration.recommended_approach.approach}</p>
                </div>
              )}
              <table className="data-table">
                <thead><tr><th>#</th><th>Algorithm</th><th>Severity</th><th>Replacement</th><th>Effort</th><th>Timeline</th></tr></thead>
                <tbody>
                  {(migration.items || []).slice(0, 15).map((item, i) => (
                    <tr key={i}>
                      <td className="mono">{i + 1}</td>
                      <td style={{ fontWeight: 600 }}>{item.current_algorithm}</td>
                      <td><span className={`badge badge-${item.severity?.toLowerCase()}`}>{item.severity}</span></td>
                      <td style={{ fontSize: '12px', color: 'var(--text-accent)' }}>{item.recommended_replacement}</td>
                      <td>{item.migration_effort}</td>
                      <td style={{ fontSize: '12px' }}>{item.timeline}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {viewMode === 'json' && (
            <div className="card">
              <div className="card-header">
                <span className="card-title">Raw CBOM JSON</span>
                <button className="btn btn-sm btn-secondary" onClick={exportJson}>⬇ Download</button>
              </div>
              <div className="json-viewer">{JSON.stringify(data, null, 2)}</div>
            </div>
          )}
        </>
      )}

      {!data && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📋</div>
          <h3>No CBOM Generated</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Run the pipeline to generate a Cryptographic Bill of Materials</p>
          <button className="btn btn-primary" onClick={genCBOM}>📋 Generate CBOM</button>
        </div>
      )}
    </div>
  )
}
