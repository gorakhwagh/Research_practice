const statusLabels = {
  waiting: 'Waiting',
  working: 'Working',
  completed: 'Complete',
}

function AgentIcon({ name }) {
  if (name === 'Research Analyst') {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <circle
          cx="10.8"
          cy="10.8"
          r="6.8"
          stroke="currentColor"
          strokeWidth="1.7"
        />
        <path
          d="m16 16 4.2 4.2M8 10.8h5.6M10.8 8v5.6"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="1.7"
        />
      </svg>
    )
  }

  if (name === 'Fact Checker') {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path
          d="M12 3 19 6v5c0 4.5-2.8 8-7 10-4.2-2-7-5.5-7-10V6l7-3Z"
          stroke="currentColor"
          strokeLinejoin="round"
          strokeWidth="1.7"
        />
        <path
          d="m8.7 12 2.1 2.1 4.6-4.7"
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="1.7"
        />
      </svg>
    )
  }

  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
      <path
        d="M5 4.5h14A1.5 1.5 0 0 1 20.5 6v12a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 18V6A1.5 1.5 0 0 1 5 4.5Z"
        stroke="currentColor"
        strokeWidth="1.7"
      />
      <path
        d="M7.5 9h9m-9 3h9m-9 3h5"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.7"
      />
    </svg>
  )
}

function AgentProgress({ agents, loading }) {
  return (
    <section className="panel progress-panel" aria-live="polite">
      <div className="progress-heading">
        <h2>Your research team</h2>
        <span className={`live-label${loading ? ' is-live' : ''}`}>
          <span className="live-dot" />
          {loading ? 'Live progress' : '3 agents'}
        </span>
      </div>
      <div className="agent-list">
        {agents.map((agent) => {
          const status = agent.status || 'waiting'
          return (
            <div
              className={`agent-row is-${status}`}
              key={agent.name}
              aria-label={`${agent.name}: ${statusLabels[status]}`}
            >
              <span className="agent-icon" aria-hidden="true">
                <AgentIcon name={agent.name} />
              </span>
              <span className="agent-copy">
                <span className="agent-name">{agent.name}</span>
                <span className="agent-description">{agent.description}</span>
              </span>
              <span className="agent-status">
                {status === 'working' && (
                  <span className="status-spinner" aria-hidden="true" />
                )}
                {status === 'completed' && (
                  <svg
                    aria-hidden="true"
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <path
                      d="m5 12 4.5 4.5L19 7"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                    />
                  </svg>
                )}
                {statusLabels[status]}
              </span>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default AgentProgress
