export default function Sidebar({ activeView, setActiveView, views, pipelineData }) {
  const stages = [
    { key: 'discovery', icon: '🔍', label: 'Discovery' },
    { key: 'risk', icon: '⚠️', label: 'Risk Assessment' },
    { key: 'intelligence', icon: '🧠', label: 'NIST Intelligence' },
    { key: 'evaluation', icon: '🔬', label: 'PQC Evaluation' },
    { key: 'testing', icon: '🧪', label: 'Testing' },
    { key: 'migration', icon: '🔄', label: 'Migration' },
    { key: 'monitoring', icon: '📡', label: 'Monitoring' },
    { key: 'cbom', icon: '📋', label: 'CBOM' },
  ]

  const getCount = (key) => {
    const d = pipelineData[key]
    if (!d) return null
    if (key === 'discovery') return d.total || d.findings?.length || 0
    if (key === 'risk') return d.analysis?.total || 0
    if (key === 'evaluation') return d.summary?.total_pqc_evaluated || 0
    if (key === 'migration') return d.total_items || 0
    return null
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>⚛ PQC Migration</h1>
        <div className="subtitle">Quantum-Safe Tool</div>
      </div>
      <nav className="sidebar-nav">
        <div className="nav-section-title">Overview</div>
        <div
          className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveView('dashboard')}
        >
          <span className="nav-icon">📊</span>
          Dashboard
        </div>

        <div className="nav-section-title">Pipeline Stages</div>
        {stages.map(s => {
          const count = getCount(s.key)
          return (
            <div
              key={s.key}
              className={`nav-item ${activeView === s.key ? 'active' : ''}`}
              onClick={() => setActiveView(s.key)}
            >
              <span className="nav-icon">{s.icon}</span>
              {s.label}
              {count !== null && <span className="nav-badge">{count}</span>}
            </div>
          )
        })}
      </nav>
    </aside>
  )
}
