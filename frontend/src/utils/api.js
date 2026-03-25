const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('text/plain')) return response.text();
    return response.json();
  } catch (error) {
    console.error(`API call failed: ${endpoint}`, error);
    throw error;
  }
}

export const api = {
  // Pipeline
  runFullPipeline: (path) => fetchApi(`/pipeline/run-all?target_path=${encodeURIComponent(path || '../../src')}`, { method: 'POST' }),
  getPipelineStatus: () => fetchApi('/pipeline/status'),

  // Discovery
  runDiscovery: (path) => fetchApi(`/discovery/scan?target_path=${encodeURIComponent(path || '../../src')}`, { method: 'POST' }),
  getDiscoveryResults: () => fetchApi('/discovery/results'),

  // Risk
  runRiskAnalysis: (hostname) => fetchApi(`/risk/analyze?hostname=${encodeURIComponent(hostname || 'example.com')}`, { method: 'POST' }),
  getRiskResults: () => fetchApi('/risk/results'),
  scanTLS: (host) => fetchApi(`/risk/scan-tls?hostname=${encodeURIComponent(host || 'example.com')}`, { method: 'POST' }),
  scanCVEs: () => fetchApi('/risk/cve-scan'),

  // Evaluation
  runEvaluation: () => fetchApi('/evaluation/run'),
  getEvaluationResults: () => fetchApi('/evaluation/results'),

  // Testing
  runBenchmarks: (iters) => fetchApi(`/testing/run?iterations=${iters || 50}`),
  getTestingResults: () => fetchApi('/testing/results'),

  // Migration
  generateMigrationPlan: () => fetchApi('/migration/plan', { method: 'POST' }),
  getMigrationResults: () => fetchApi('/migration/results'),

  // Monitoring
  checkSonarQube: () => fetchApi('/monitoring/status'),
  getMonitoringReport: () => fetchApi('/monitoring/report'),

  // CBOM
  generateCBOM: () => fetchApi('/cbom/generate', { method: 'POST' }),
  getCBOMJson: () => fetchApi('/cbom/json'),
  getCBOMMarkdown: () => fetchApi('/cbom/markdown'),
};
