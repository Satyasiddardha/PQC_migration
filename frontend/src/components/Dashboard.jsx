import { useState } from 'react'

const STAGES = [
  { key: 'discovery', icon: '🔍', label: 'Discovery', tool: 'Semgrep' },
  { key: 'risk', icon: '⚠️', label: 'Risk', tool: 'SSLyze + CVE' },
  { key: 'evaluation', icon: '🔬', label: 'Evaluation', tool: 'liboqs' },
  { key: 'testing', icon: '🧪', label: 'Testing', tool: 'liboqs Bench' },
  { key: 'migration', icon: '🔄', label: 'Migration', tool: 'Advisor' },
  { key: 'monitoring', icon: '📡', label: 'Monitoring', tool: 'SonarQube' },
  { key: 'cbom', icon: '📋', label: 'CBOM', tool: 'Generator' },
]

export default function Dashboard({ data, runFullPipeline, runUploadPipeline, loading, getStageStatus, runningStage, setActiveView }) {
  const cbom = data.cbom
  const summary = cbom?.summary || {}
  const discovery = data.discovery
  const risk = data.risk?.analysis

  const minCTime = cbom?.migration_plan?.items?.reduce((min, item) => {
    return Math.min(min, item.mosca_analysis?.c_years ?? 25)
  }, 25) || 8;

  return (
    <div className="fade-in">
      {/* Pipeline Visualization */}
      <div className="section-header">
        <div>
          <h1 className="section-title">PQC Migration Pipeline</h1>
          <p className="section-description">End-to-end post-quantum cryptography migration workflow</p>
        </div>
        <div style={{ display: 'flex', gap: '15px' }}>
          <label className="btn" style={{ cursor: loading ? 'not-allowed' : 'pointer', border: '1px solid #4ade80', color: '#4ade80', backgroundColor: 'transparent', padding: '10px 20px', borderRadius: '8px', fontWeight: 'bold' }}>
            <input type="file" accept=".zip" style={{ display: 'none' }} disabled={loading} onChange={(e) => {
              if (e.target.files && e.target.files[0]) runUploadPipeline(e.target.files[0]);
            }} />
            {loading ? '⏳ Processing...' : '📁 Upload Code (.zip)'}
          </label>
          <button className="btn btn-primary" onClick={runFullPipeline} disabled={loading}>
            {loading ? '⏳ Running Pipeline...' : '▶ Run Server Code'}
          </button>
        </div>
      </div>

      <div className="pipeline-container">
        {STAGES.map((stage, i) => {
          const status = getStageStatus(stage.key)
          return (
            <div key={stage.key} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                className={`pipeline-stage ${status}`}
                onClick={() => setActiveView(stage.key)}
              >
                <div className="pipeline-icon">{stage.icon}</div>
                <div className="pipeline-label">{stage.label}</div>
                <div className="pipeline-status">
                  {status === 'running' ? '⏳ Running...' : status === 'completed' ? '✅ Done' : '⬜ Pending'}
                </div>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {stage.tool}
                </div>
              </div>
              {i < STAGES.length - 1 && <div className="pipeline-arrow">→</div>}
            </div>
          )
        })}
      </div>

      {/* Executive Dashboard */}
      {cbom && (
        <div style={{ marginBottom: '40px' }}>
          <h2 style={{ fontSize: '20px', marginBottom: '16px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '24px' }}>📊</span> Executive Summary
          </h2>
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <div className={`stat-card ${summary.migration_readiness_score > 50 ? 'cyan' : 'danger'}`}>
              <div className={`stat-value ${summary.migration_readiness_score > 50 ? 'cyan' : 'danger'}`} style={{ fontSize: '36px' }}>{summary.migration_readiness_score || 0}/100</div>
              <div className="stat-label" style={{ fontSize: '13px' }}>Quantum Readiness</div>
            </div>
            <div className={`stat-card ${summary.overall_risk_percentage > 50 ? 'danger' : summary.overall_risk_percentage > 20 ? 'warning' : 'success'}`}>
              <div className={`stat-value ${summary.overall_risk_percentage > 50 ? 'danger' : summary.overall_risk_percentage > 20 ? 'warning' : 'success'}`} style={{ fontSize: '36px' }}>{summary.overall_risk_percentage || 0}%</div>
              <div className="stat-label" style={{ fontSize: '13px' }}>Overall Risk Score</div>
            </div>
            <div className={`stat-card ${minCTime < 3 ? 'danger' : 'warning'}`}>
              <div className={`stat-value ${minCTime < 3 ? 'danger' : 'warning'}`} style={{ fontSize: '36px' }}>{minCTime.toFixed(1)}y</div>
              <div className="stat-label" style={{ fontSize: '13px' }}>Time Left Before Risk</div>
            </div>
            <div className="stat-card info">
              <div className="stat-value info" style={{ fontSize: '36px' }}>0%</div>
              <div className="stat-label" style={{ fontSize: '13px' }}>Migration Progress</div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '20px' }}>
            <div className="card-header"><span className="card-title">Threat Timeline (Now → Quantum Break)</span></div>
            <div style={{ position: 'relative', height: '60px', marginTop: '30px', marginBottom: '30px', margin: '30px 40px' }}>
              <div style={{ position: 'absolute', top: '50%', left: '0', right: '0', height: '4px', background: 'var(--border-subtle)', borderRadius: '2px', transform: 'translateY(-50%)' }}></div>
              <div style={{ position: 'absolute', top: '50%', left: '0', width: `${Math.min(100, (minCTime / 10) * 100)}%`, height: '4px', background: `linear-gradient(90deg, var(--success), ${minCTime < 3 ? 'var(--critical)' : 'var(--warning)'})`, borderRadius: '2px', transform: 'translateY(-50%)' }}></div>
              
              <div style={{ position: 'absolute', top: '0', left: '0', transform: 'translateX(-50%)', textAlign: 'center' }}>
                <div style={{ width: '16px', height: '16px', borderRadius: '50%', background: 'var(--success)', margin: '0 auto 8px', border: '3px solid var(--bg-card)' }}></div>
                <div style={{ fontSize: '12px', fontWeight: 'bold' }}>Today</div>
              </div>
              
              <div style={{ position: 'absolute', top: '-4px', left: `${Math.min(100, (minCTime / 10) * 100)}%`, transform: 'translateX(-50%)', textAlign: 'center' }}>
                <div style={{ width: '22px', height: '22px', borderRadius: '50%', background: minCTime < 3 ? 'var(--critical)' : 'var(--warning)', margin: '0 auto 4px', border: '4px solid var(--bg-card)', boxShadow: `0 0 12px ${minCTime < 3 ? 'var(--critical)' : 'var(--warning)'}` }}></div>
                <div style={{ fontSize: '13px', fontWeight: 'bold', color: minCTime < 3 ? 'var(--critical)' : 'var(--warning)' }}>Q-Day<br/>({new Date().getFullYear() + Math.floor(minCTime)})</div>
              </div>

              <div style={{ position: 'absolute', top: '0', right: '0', transform: 'translateX(50%)', textAlign: 'center' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--border-subtle)', margin: '2px auto 10px' }}></div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>+10 Years</div>
              </div>
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', textAlign: 'center' }}>
              We have <strong>{minCTime.toFixed(1)} years</strong> to secure the infrastructure before quantum computers break currently deployed algorithms.
            </div>
          </div>
        </div>
      )}

      {/* Deep Dive Technical Stats */}
      {cbom && (
        <>
          <h2 style={{ fontSize: '18px', marginBottom: '12px', color: 'var(--text-secondary)' }}>Technical Analysis</h2>
          <div className="stats-grid">
            <div className="stat-card cyan">
              <div className="stat-value cyan">{summary.total_algorithms_found || 0}</div>
              <div className="stat-label">Algorithms Found</div>
            </div>
            <div className="stat-card danger">
              <div className="stat-value danger">{summary.quantum_vulnerable_algorithms || 0}</div>
              <div className="stat-label">Quantum Vulnerable</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-value warning">{summary.overall_risk_percentage || 0}%</div>
              <div className="stat-label">Risk Score</div>
            </div>
            <div className="stat-card pink">
              <div className="stat-value" style={{ color: '#ec4899' }}>{summary.critical_actions_needed || 0}</div>
              <div className="stat-label">Critical Actions</div>
            </div>
          </div>

          {/* Two column: Severity + Recommendation */}
          <div className="grid-2">
            <div className="card">
              <div className="card-header">
                <span className="card-title">Severity Breakdown</span>
              </div>
              {risk && (
                <div className="bar-chart">
                  {[
                    { label: 'Critical', value: risk.severity_breakdown?.critical || 0, color: 'danger', max: risk.total || 1 },
                    { label: 'High', value: risk.severity_breakdown?.high || 0, color: 'warning', max: risk.total || 1 },
                    { label: 'Medium', value: risk.severity_breakdown?.medium || 0, color: 'info', max: risk.total || 1 },
                    { label: 'Low', value: risk.severity_breakdown?.low || 0, color: 'success', max: risk.total || 1 },
                  ].map(bar => (
                    <div className="bar-row" key={bar.label}>
                      <span className="bar-label">{bar.label}</span>
                      <div className="bar-track">
                        <div className={`bar-fill ${bar.color}`} style={{ width: `${(bar.value / bar.max) * 100}%` }} />
                      </div>
                      <span className="bar-value">{bar.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card">
              <div className="card-header">
                <span className="card-title">Executive Recommendation</span>
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                <div className={`badge ${summary.migration_readiness_score > 50 ? 'badge-medium' : 'badge-critical'}`} style={{ marginBottom: '12px' }}>
                  {summary.migration_readiness_label || 'Run pipeline first'}
                </div>
                <p>{summary.recommendation || 'Run the full pipeline to generate recommendations.'}</p>
              </div>
            </div>
          </div>
        </>
      )}

      {!cbom && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚛</div>
          <h3 style={{ fontSize: '18px', marginBottom: '8px' }}>Ready to Analyze</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
            Click "Run Full Pipeline" to scan your codebase for quantum-vulnerable cryptography
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px' }}>
            <label className="btn" style={{ cursor: loading ? 'not-allowed' : 'pointer', border: '2px dashed #4ade80', color: '#4ade80', backgroundColor: 'transparent', padding: '10px 30px', borderRadius: '8px', fontSize: '1.1rem', fontWeight: 'bold' }}>
              <input type="file" accept=".zip" style={{ display: 'none' }} disabled={loading} onChange={(e) => {
                if (e.target.files && e.target.files[0]) runUploadPipeline(e.target.files[0]);
              }} />
              📁 Upload .zip
            </label>
            <button className="btn btn-primary" onClick={runFullPipeline} disabled={loading} style={{ padding: '10px 30px', fontSize: '1.1rem' }}>
              ▶ Scan Server Code
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="loading">
          <div className="spinner" />
          <div className="loading-text">Running {runningStage || 'pipeline'}...</div>
        </div>
      )}
    </div>
  )
}
