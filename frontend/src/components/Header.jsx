export default function Header({ title }) {
  return (
    <header className="header">
      <div>
        <h2 className="header-title">{title}</h2>
      </div>
      <div className="header-actions">
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          🟢 SonarQube Connected
        </span>
      </div>
    </header>
  )
}
