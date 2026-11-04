function DocumentIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M7 3.5h7l5 5V20a.5.5 0 0 1-.5.5h-11A1.5 1.5 0 0 1 6 19V5a1.5 1.5 0 0 1 1-1.5Z"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="1.6"
      />
      <path
        d="M14 4v5h5M9 13h6m-6 3.5h6"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.6"
      />
    </svg>
  )
}

function ReportViewer({ report, loading }) {
  return (
    <section className="panel report-panel" aria-live="polite">
      <header className="report-header">
        <div className="report-title">
          <span className="heading-icon" aria-hidden="true">
            <DocumentIcon />
          </span>
          <span>
            <h2>Research report</h2>
            <p>Your verified findings, all in one place</p>
          </span>
        </div>
        <span className="report-badge">
          <svg
            aria-hidden="true"
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="m12 3 2.2 5.3L20 10.5l-5.8 2.2L12 18l-2.2-5.3L4 10.5l5.8-2.2L12 3Z"
              stroke="currentColor"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
          </svg>
          AI-generated
        </span>
      </header>
      <div className="report-content">
        {loading ? (
          <div className="report-placeholder">
            <span className="loading-indicator" aria-hidden="true" />
            <h3>Building your research report</h3>
            <p>
              Our agents are gathering sources, checking the facts, and
              preparing your findings.
            </p>
          </div>
        ) : report ? (
          <article className="report-text">{report}</article>
        ) : (
          <div className="report-placeholder">
            <span className="placeholder-art" aria-hidden="true">
              <DocumentIcon />
            </span>
            <h3>Your report will appear here</h3>
            <p>
              Submit a topic and your research team will prepare a thoughtful,
              fact-checked report.
            </p>
            <div className="placeholder-hints" aria-hidden="true">
              <span>Research</span>
              <span>Fact-check</span>
              <span>Report</span>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

export default ReportViewer
