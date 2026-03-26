import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import DiscoveryView from './components/DiscoveryView'
import RiskView from './components/RiskView'
import EvaluationView from './components/EvaluationView'
import TestingView from './components/TestingView'
import MigrationView from './components/MigrationView'
import MonitoringView from './components/MonitoringView'
import CBOMView from './components/CBOMView'
import IntelligenceView from './components/IntelligenceView'
import { api } from './utils/api'

const VIEWS = {
  dashboard: { label: 'Dashboard', icon: '📊' },
  discovery: { label: 'Discovery', icon: '🔍' },
  risk: { label: 'Risk Assessment', icon: '⚠️' },
  intelligence: { label: 'NIST Intelligence', icon: '🧠' },
  evaluation: { label: 'PQC Evaluation', icon: '🔬' },
  testing: { label: 'Testing', icon: '🧪' },
  migration: { label: 'Migration', icon: '🔄' },
  monitoring: { label: 'Monitoring', icon: '📡' },
  cbom: { label: 'CBOM', icon: '📋' },
}

export default function App() {
  const [activeView, setActiveView] = useState('dashboard')
  const [pipelineData, setPipelineData] = useState({
    discovery: null, risk: null, evaluation: null,
    testing: null, migration: null, monitoring: null, cbom: null,
  })
  const [loading, setLoading] = useState(false)
  const [runningStage, setRunningStage] = useState(null)

  const updateStageData = (stage, data) => {
    setPipelineData(prev => ({ ...prev, [stage]: data }))
  }

  const runFullPipeline = async () => {
    setLoading(true)
    setRunningStage('discovery')
    try {
      // Run stages sequentially for visibility
      setRunningStage('discovery')
      const disc = await api.runDiscovery('../../src')
      updateStageData('discovery', disc)

      setRunningStage('risk')
      const risk = await api.runRiskAnalysis()
      updateStageData('risk', risk)

      setRunningStage('evaluation')
      const evalData = await api.runEvaluation()
      updateStageData('evaluation', evalData)

      setRunningStage('testing')
      const test = await api.runBenchmarks(50)
      updateStageData('testing', test)

      setRunningStage('migration')
      const mig = await api.generateMigrationPlan()
      updateStageData('migration', mig)

      setRunningStage('monitoring')
      const mon = await api.getMonitoringReport()
      updateStageData('monitoring', mon)

      setRunningStage('cbom')
      const cbom = await api.generateCBOM()
      updateStageData('cbom', cbom)

      setRunningStage(null)
    } catch (err) {
      console.error('Pipeline error:', err)
    }
    setLoading(false)
    setRunningStage(null)
  }

  const getStageStatus = (stage) => {
    if (runningStage === stage) return 'running'
    if (pipelineData[stage]) return 'completed'
    return 'pending'
  }

  const renderView = () => {
    const props = { data: pipelineData, updateStageData, setActiveView }
    switch (activeView) {
      case 'dashboard': return <Dashboard {...props} runFullPipeline={runFullPipeline} loading={loading} getStageStatus={getStageStatus} runningStage={runningStage} />
      case 'discovery': return <DiscoveryView data={pipelineData.discovery} updateStageData={updateStageData} />
      case 'risk': return <RiskView data={pipelineData.risk} updateStageData={updateStageData} />
      case 'intelligence': return <IntelligenceView data={pipelineData.discovery} />
      case 'evaluation': return <EvaluationView data={pipelineData.evaluation} updateStageData={updateStageData} />
      case 'testing': return <TestingView data={pipelineData.testing} updateStageData={updateStageData} />
      case 'migration': return <MigrationView data={pipelineData.migration} updateStageData={updateStageData} />
      case 'monitoring': return <MonitoringView data={pipelineData.monitoring} updateStageData={updateStageData} />
      case 'cbom': return <CBOMView data={pipelineData.cbom} updateStageData={updateStageData} />
      default: return <Dashboard {...props} />
    }
  }

  return (
    <div className="app-layout">
      <Sidebar activeView={activeView} setActiveView={setActiveView} views={VIEWS} pipelineData={pipelineData} />
      <Header title={VIEWS[activeView]?.label || 'Dashboard'} />
      <main className="main-content">
        {renderView()}
      </main>
    </div>
  )
}
