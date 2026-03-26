import React, { useState } from 'react';
import { api } from '../utils/api';

export default function IntelligenceView({ data: discoveryData }) {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      // Extract cryptographic assets from Discovery stage
      const findings = discoveryData?.findings || [];
      const assets = findings.map(f => ({
        file: f.file,
        algorithm: f.algorithm,
        usage: f.category || 'encryption',
        risk_level: f.severity || 'Medium'
      }));

      // If no local findings, hit the endpoint with demo data so the user can see it work
      const payload = assets.length > 0 ? assets : [
        { file: 'src/auth/jwt.js', algorithm: 'RSA', usage: 'signature', risk_level: 'Critical' },
        { file: 'config/network.py', algorithm: 'TLS 1.2', usage: 'transport', risk_level: 'Medium' },
        { file: 'database/crypto.go', algorithm: 'AES', usage: 'symmetric', risk_level: 'Low' }
      ];

      const res = await api.generateIntelligenceRecommendations(payload);
      setRecommendations(res.recommendations);
    } catch (err) {
      setError(err.message || 'Failed to generate recommendations');
    }
    setLoading(false);
  };

  const getBadgeClass = (type) => {
    if (type.includes('Full PQC')) return 'severity-critical';
    if (type.includes('Hybrid')) return 'severity-high';
    return 'severity-info';
  };

  return (
    <div className="view-container">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>🧠 NIST Intelligence Layer</h2>
          <p style={{ color: '#9ca3af' }}>Automated Post-Quantum Migration Strategy mapping based on NIST standard algorithms.</p>
        </div>
        <button 
          onClick={handleGenerate} 
          disabled={loading}
          style={{
            padding: '10px 20px', backgroundColor: '#6366f1', color: 'white', 
            border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px'
          }}
        >
          {loading ? '🔮 Analyzing...' : '🔮 Generate PQC Recommendations'}
        </button>
      </div>

      {error && (
        <div style={{ padding: '15px', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderLeft: '4px solid #ef4444', color: '#fca5a5', marginBottom: '20px' }}>
          {error}
        </div>
      )}

      {!recommendations && !loading && !error && (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#9ca3af', backgroundColor: '#1e293b', borderRadius: '8px' }}>
          <span style={{ fontSize: '3rem', display: 'block', marginBottom: '15px' }}>🤖</span>
          <h3>Intelligence Engine Ready</h3>
          <p>Click "Generate PQC Recommendations" above to pipeline your discovered algorithms through the NIST AI mapping engine.</p>
        </div>
      )}

      {recommendations && (
        <div style={{ display: 'grid', gap: '15px' }}>
          {recommendations.map((rec, i) => (
            <div key={i} style={{ backgroundColor: '#1e293b', borderRadius: '8px', padding: '20px', border: '1px solid #334155' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
                <div>
                  <code style={{ color: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.1)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.85rem' }}>
                    {rec.file}
                  </code>
                </div>
                <span className={`severity-badge ${getBadgeClass(rec.migration_type)}`}>
                  {rec.migration_type}
                </span>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '15px', backgroundColor: 'rgba(0,0,0,0.2)', padding: '15px', borderRadius: '8px' }}>
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', textTransform: 'uppercase', letterSpacing: '1px' }}>Detected</span>
                  <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ef4444' }}>{rec.detected_algorithm}</span>
                </div>
                <div style={{ fontSize: '1.5rem', color: '#6366f1' }}>➔</div>
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', textTransform: 'uppercase', letterSpacing: '1px' }}>NIST Recommendation</span>
                  <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#22c55e' }}>{rec.pqc_recommendation}</span>
                </div>
              </div>

              <p style={{ color: '#cbd5e1', lineHeight: '1.6', margin: 0 }}>
                <strong>Reasoning:</strong> {rec.reason}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
