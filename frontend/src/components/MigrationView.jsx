import { useState } from 'react'
import { api } from '../utils/api'

export default function MigrationView({ data, updateStageData }) {
  const [loading, setLoading] = useState(false)

  const genPlan = async () => {
    setLoading(true)
    try {
      const result = await api.generateMigrationPlan()
      updateStageData('migration', result)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const items = data?.migration_items || []
  const summary = data?.summary || {}
  const approach = data?.recommended_approach || {}

  return (
    <div className="fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">🔄 Migration Plan</h1>
          <p className="section-description">OQS-style hybrid crypto migration recommendations</p>
        </div>
        <button className="btn btn-primary" onClick={genPlan} disabled={loading}>
          {loading ? '⏳ Generating...' : '📝 Generate Plan'}
        </button>
      </div>

      {data && (
        <>
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <div className="stat-card danger">
              <div className="stat-value danger">{summary.critical_migrations || 0}</div>
              <div className="stat-label">Critical Migrations</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-value warning">{summary.high_priority || 0}</div>
              <div className="stat-label">High Priority</div>
            </div>
            <div className="stat-card cyan">
              <div className="stat-value cyan">{summary.readiness_score || 0}</div>
              <div className="stat-label">Readiness Score</div>
            </div>
            <div className="stat-card success">
              <div className="stat-value success">{data.total_items || 0}</div>
              <div className="stat-label">Total Items</div>
            </div>
          </div>

          {approach.approach && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <div className="card-header">
                <span className="card-title">Migration Strategy</span>
                <span className={`badge ${approach.phase === 'IMMEDIATE' ? 'badge-critical' : approach.phase === 'SHORT-TERM' ? 'badge-high' : 'badge-low'}`}>
                  {approach.phase}
                </span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.8, marginBottom: '12px' }}>
                {approach.approach}
              </p>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                <p>📋 <strong>Strategy:</strong> {approach.recommended_strategy}</p>
                <p>📖 <strong>Standards:</strong> {approach.standards_reference}</p>
              </div>
            </div>
          )}

          <div className="card">
            <div className="card-header"><span className="card-title">Migration Playbook</span></div>
            {items.map((item, i) => (
              <div key={i} style={{ padding: '20px', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                  <span style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-muted)' }}>#{i + 1}</span>
                  <span className={`badge badge-${item.severity?.toLowerCase() || 'medium'}`}>{item.severity}</span>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{item.current_algorithm}</span>
                  <span style={{ color: 'var(--text-muted)' }}>→</span>
                  <span style={{ color: 'var(--text-accent)', fontWeight: 600 }}>{item.recommended_replacement}</span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  📁 {item.file}:{item.line} | Effort: {item.migration_effort} | {item.timeline}
                </div>
                {item.quantum_threat && (
                  <p style={{ fontSize: '12px', color: '#fca5a5', marginBottom: '8px' }}>⚡ {item.quantum_threat}</p>
                )}
                {item.hybrid_option && (
                  <p style={{ fontSize: '12px', color: 'var(--text-accent)', marginBottom: '8px' }}>🔀 Hybrid: {item.hybrid_option}</p>
                )}
                
                {item.mosca_analysis && (
                  <div style={{ padding: '10px', marginTop: '10px', marginBottom: '12px', background: 'var(--bg-solid)', borderRadius: 'var(--radius-sm)', borderLeft: `3px solid ${item.mosca_analysis.is_at_risk ? 'var(--critical)' : 'var(--success)'}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-primary)' }}>📐 Mosca's Theorem Analysis</span>
                      <span className={`badge ${item.mosca_analysis.is_at_risk ? 'badge-critical' : 'badge-low'}`} style={{ fontSize: '10px' }}>
                        {item.mosca_analysis.recommendation}
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)' }}>
                      Formula: M + O ≥ C → 
                      <span style={{ fontWeight: 800, color: item.mosca_analysis.is_at_risk ? 'var(--critical)' : 'var(--success)', marginLeft: '8px' }}>
                        {item.mosca_analysis.mosca_formula}
                      </span>
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
                      M = Migration Time ({item.mosca_analysis.m_years}y)<br/>
                      O = Safe Shelf-life ({item.mosca_analysis.o_years}y)<br/>
                      S = System Lifespan ({item.mosca_analysis.s_years}y)<br/>
                      C = Quantum Collapse Time ({item.mosca_analysis.c_years}y)
                    </div>
                  </div>
                )}

                {item.code_suggestion && (
                  <div style={{ marginTop: '10px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Before:</div>
                    <div className="code-block" style={{ marginBottom: '8px', borderLeft: '3px solid var(--critical)' }}>
                      {item.code_suggestion.before}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>After (PQC):</div>
                    <div className="code-block" style={{ borderLeft: '3px solid var(--low)' }}>
                      {item.code_suggestion.after_pqc}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {!data && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
          <h3>No Migration Plan</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Run discovery first, then generate a migration plan</p>
          <button className="btn btn-primary" onClick={genPlan}>📝 Generate Plan</button>
        </div>
      )}
    </div>
  )
}
