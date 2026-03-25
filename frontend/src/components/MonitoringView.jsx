import { useState } from 'react'
import { api } from '../utils/api'

export default function MonitoringView({ data, updateStageData }) {
  const [loading, setLoading] = useState(false)

  const fetchReport = async () => {
    setLoading(true)
    try {
      const result = await api.getMonitoringReport()
      updateStageData('monitoring', result)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const connected = data?.connected
  const issues = data?.issues
  const measures = data?.measures?.measures || {}
  const history = data?.scan_history

  return (
    <div className="fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">📡 Monitoring</h1>
          <p className="section-description">SonarQube integration — continuous crypto tracking</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {data?.timestamp && (
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Last updated: {new Date(data.timestamp).toLocaleTimeString()}
            </span>
          )}
          <button className="btn btn-primary" onClick={fetchReport} disabled={loading}>
            {loading ? '⏳ Fetching...' : '📡 Fetch Report'}
          </button>
        </div>
      </div>

      {data && (
        <>
          <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <div className={`stat-card ${connected ? 'success' : 'danger'}`}>
              <div className={`stat-value ${connected ? 'success' : 'danger'}`}>{connected ? '🟢' : '🔴'}</div>
              <div className="stat-label">SonarQube {connected ? 'Connected' : 'Offline'}</div>
            </div>
            <div className="stat-card cyan">
              <div className="stat-value cyan">{issues?.total_issues || 0}</div>
              <div className="stat-label">Total Issues</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-value warning">{issues?.crypto_issue_count || 0}</div>
              <div className="stat-label">Crypto Issues</div>
            </div>
            <div className="stat-card info">
              <div className="stat-value" style={{ color: '#3b82f6' }}>{data.sonarqube_version || '—'}</div>
              <div className="stat-label">SQ Version</div>
            </div>
          </div>

          {connected && (
            <div className="grid-2">
              <div className="card">
                <div className="card-header"><span className="card-title">Project Metrics</span></div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {Object.entries(measures).map(([key, value]) => (
                    <div key={key} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                      <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{key.replace(/_/g, ' ')}</span>
                      <span style={{ fontSize: '13px', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>{value}</span>
                    </div>
                  ))}
                  {Object.keys(measures).length === 0 && (
                    <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No metrics available. Run a SonarQube scan first.</p>
                  )}
                </div>
              </div>

              <div className="card">
                <div className="card-header"><span className="card-title">SonarQube Findings</span></div>
                
                {/* Crypto Issues */}
                <h4 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--warning)' }}>Crypto Vulnerabilities ({issues?.crypto_issue_count || 0})</h4>
                {(issues?.crypto_issues || []).length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    {issues.crypto_issues.slice(0, 8).map((issue, i) => (
                      <div key={i} style={{ padding: '10px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--warning)' }}>
                        <div style={{ fontSize: '13px', fontWeight: 600 }}>{issue.message?.substring(0, 100)}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
                          <span className={`badge badge-${issue.severity?.toLowerCase() || 'medium'}`} style={{ marginRight: '6px' }}>{issue.severity}</span>
                          <span style={{ marginRight: '6px' }}>{issue.type?.replace(/_/g, ' ')}</span>
                          File: {issue.component?.split(':').pop()} | Line: {issue.line}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '20px' }}>No crypto-related issues found.</p>
                )}

                {/* Other Issues */}
                <h4 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--text-secondary)' }}>General Code Issues ({(issues?.total_issues || 0) - (issues?.crypto_issue_count || 0)})</h4>
                {(issues?.other_issues || []).length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {issues.other_issues.slice(0, 5).map((issue, i) => (
                      <div key={`other-${i}`} style={{ padding: '10px', background: 'var(--bg-solid)', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--border-subtle)' }}>
                        <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-secondary)' }}>{issue.message?.substring(0, 100)}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
                          <span className={`badge badge-low`} style={{ marginRight: '6px' }}>{issue.severity}</span>
                          <span style={{ marginRight: '6px' }}>{issue.type?.replace(/_/g, ' ')}</span>
                          File: {issue.component?.split(':').pop()} | Line: {issue.line}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No general code issues found.</p>
                )}
              </div>
            </div>
          )}

          {history?.analyses?.length > 0 && (
            <div className="card" style={{ marginTop: '20px' }}>
              <div className="card-header"><span className="card-title">Scan History</span></div>
              <table className="data-table">
                <thead><tr><th>Date</th><th>Key</th><th>Events</th></tr></thead>
                <tbody>
                  {history.analyses.map((a, i) => (
                    <tr key={i}>
                      <td className="mono">{new Date(a.date).toLocaleString()}</td>
                      <td className="mono" style={{ fontSize: '11px' }}>{a.key?.substring(0, 20)}</td>
                      <td>{a.events?.length || 0} events</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!connected && (
            <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
              <p style={{ color: '#fca5a5' }}>⚠️ SonarQube is not running at {data.url}</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '8px' }}>
                Start SonarQube to enable monitoring: <code style={{ color: 'var(--text-accent)' }}>.\sonarqube-26.3.0.120487\bin\windows-x86-64\StartSonar.bat</code>
              </p>
            </div>
          )}
        </>
      )}

      {!data && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📡</div>
          <h3>No Monitoring Data</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Connect to SonarQube for continuous monitoring</p>
          <button className="btn btn-primary" onClick={fetchReport}>📡 Fetch Report</button>
        </div>
      )}
    </div>
  )
}
