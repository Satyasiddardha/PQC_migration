import { useState } from 'react'
import { api } from '../utils/api'

export default function TestingView({ data, updateStageData }) {
  const [loading, setLoading] = useState(false)

  const runBench = async () => {
    setLoading(true)
    try {
      const result = await api.runBenchmarks(50)
      updateStageData('testing', result)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const kemBench = data?.kem_benchmarks || []
  const sigBench = data?.sig_benchmarks || []
  const analysis = data?.analysis

  return (
    <div className="fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">🧪 PQC Benchmarking</h1>
          <p className="section-description">
            {data?.measured ? '✅ Real benchmarks via liboqs-python' : '📊 Reference benchmark data'}
            {data?.iterations ? ` — ${data.iterations} iterations` : ''}
          </p>
        </div>
        <button className="btn btn-primary" onClick={runBench} disabled={loading}>
          {loading ? '⏳ Benchmarking...' : '🧪 Run Benchmarks'}
        </button>
      </div>

      {data && (
        <>
          {analysis && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <div className="card-header"><span className="card-title">Analysis Summary</span></div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                {analysis.recommendation}
              </p>
              <div style={{ marginTop: '12px', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                <div className="badge badge-info">🏆 Fastest KEM: {analysis.fastest_kem || 'N/A'}</div>
                <div className="badge badge-info">🏆 Fastest Sig: {analysis.fastest_sig || 'N/A'}</div>
                <div className={`badge ${analysis.migration_readiness === 'READY' ? 'badge-low' : 'badge-medium'}`}>
                  Readiness: {analysis.migration_readiness || 'N/A'}
                </div>
              </div>
            </div>
          )}

          {kemBench.length > 0 && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <div className="card-header"><span className="card-title">KEM Benchmarks</span></div>
              <table className="data-table">
                <thead>
                  <tr><th>Algorithm</th><th>NIST</th><th>KeyGen (ms)</th><th>Encaps (ms)</th><th>Decaps (ms)</th><th>Total (ms)</th><th>Pub Key</th><th>Ciphertext</th></tr>
                </thead>
                <tbody>
                  {kemBench.map((k, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{k.algorithm}</td>
                      <td><span className="badge badge-info">{k.nist_level}</span></td>
                      <td className="mono">{(k.keygen_ms?.mean ?? k.keygen_ms)?.toFixed?.(4) ?? '—'}</td>
                      <td className="mono">{(k.encaps_ms?.mean ?? k.encaps_ms)?.toFixed?.(4) ?? '—'}</td>
                      <td className="mono">{(k.decaps_ms?.mean ?? k.decaps_ms)?.toFixed?.(4) ?? '—'}</td>
                      <td className="mono" style={{ color: 'var(--text-accent)' }}>{k.total_mean_ms?.toFixed?.(4) ?? '—'}</td>
                      <td className="mono">{k.sizes?.public_key || '—'}</td>
                      <td className="mono">{k.sizes?.ciphertext || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {sigBench.length > 0 && (
            <div className="card">
              <div className="card-header"><span className="card-title">Signature Benchmarks</span></div>
              <table className="data-table">
                <thead>
                  <tr><th>Algorithm</th><th>NIST</th><th>KeyGen (ms)</th><th>Sign (ms)</th><th>Verify (ms)</th><th>Total (ms)</th><th>Pub Key</th><th>Signature</th></tr>
                </thead>
                <tbody>
                  {sigBench.map((s, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{s.algorithm}</td>
                      <td><span className="badge badge-info">{s.nist_level}</span></td>
                      <td className="mono">{(s.keygen_ms?.mean ?? s.keygen_ms)?.toFixed?.(4) ?? '—'}</td>
                      <td className="mono">{(s.sign_ms?.mean ?? s.sign_ms)?.toFixed?.(4) ?? '—'}</td>
                      <td className="mono">{(s.verify_ms?.mean ?? s.verify_ms)?.toFixed?.(4) ?? '—'}</td>
                      <td className="mono" style={{ color: 'var(--text-accent)' }}>{s.total_mean_ms?.toFixed?.(4) ?? '—'}</td>
                      <td className="mono">{s.sizes?.public_key || '—'}</td>
                      <td className="mono">{s.sizes?.signature || '—'}</td>
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
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🧪</div>
          <h3>No Benchmark Data</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Run PQC benchmarks to measure algorithm performance</p>
          <button className="btn btn-primary" onClick={runBench}>🧪 Start Benchmarks</button>
        </div>
      )}
    </div>
  )
}
