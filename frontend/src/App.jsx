import { useState } from 'react'
import AgentProgress from './components/AgentProgress.jsx'
import Navbar from './components/Navbar.jsx'
import ReportViewer from './components/ReportViewer.jsx'
import ResearchForm from './components/ResearchForm.jsx'
import './App.css'

const initialAgents = [
  { name: 'Research Analyst', description: 'Finds current, reliable sources' },
  { name: 'Fact Checker', description: 'Verifies claims and evidence' },
  { name: 'Content Writer', description: 'Creates your final report' },
]

function App() {
  const [report, setReport] = useState('')
  const [loading, setLoading] = useState(false)
  const [agents, setAgents] = useState(initialAgents)

  function updateAgentProgress(agentName, status) {
    setAgents((currentAgents) =>
      currentAgents.map((agent) =>
        agent.name === agentName ? { ...agent, status } : agent,
      ),
    )
  }

  function resetAgentProgress() {
    setAgents(initialAgents.map((agent) => ({ ...agent, status: 'waiting' })))
  }

  return (
    <div className="app-shell">
      <Navbar />
      <main className="main-content">
        <section className="intro">
          <div className="eyebrow">
            <span className="eyebrow-dot" />
            AI-POWERED RESEARCH
          </div>
          <h1>
            Research, made
            <span> remarkable.</span>
          </h1>
          <p>
            Explore any topic with a team of AI agents that research, verify,
            and bring the findings together for you.
          </p>
        </section>

        <div className="workspace-grid">
          <aside className="left-column">
            <ResearchForm
              loading={loading}
              onProgress={updateAgentProgress}
              onResetProgress={resetAgentProgress}
              onReport={setReport}
              onLoadingChange={setLoading}
            />
            <AgentProgress agents={agents} loading={loading} />
          </aside>
          <ReportViewer report={report} loading={loading} />
        </div>
        <footer className="page-footer">
          <span>Thoughtful research starts with a good question.</span>
          <span>AI Research Assistant</span>
        </footer>
      </main>
    </div>
  )
}

export default App
