const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    
    // If sending FormData (like a file upload), the browser must automatically set the Content-Type boundary
    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
    }

    const response = await fetch(url, {
      ...options,
      headers
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
  runPipelineUpload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetchApi('/pipeline/upload-zip', { method: 'POST', body: formData });
  },
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

  // Intelligence Engine
  generateIntelligenceRecommendations: (assets) => fetchApi('/intelligence/recommendations', {
    method: 'POST',
    body: JSON.stringify({ assets })
  }),
};
