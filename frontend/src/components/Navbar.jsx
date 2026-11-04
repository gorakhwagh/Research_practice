function SparkleMark() {
  return (
    <svg
      aria-hidden="true"
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
    >
      <path
        d="M12 2.8 14.2 9.8 21.2 12l-7 2.2-2.2 7-2.2-7-7-2.2 7-2.2L12 2.8Z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
      <path
        d="m19 2 .7 2.3L22 5l-2.3.7L19 8l-.7-2.3L16 5l2.3-.7L19 2Z"
        fill="currentColor"
      />
    </svg>
  )
}

function Navbar() {
  return (
    <header className="navbar">
      <a className="brand" href="/" aria-label="AI Research Assistant home">
        <span className="brand-mark">
          <SparkleMark />
        </span>
        <span>
          <span className="brand-name">AI Research Assistant</span>
          <span className="brand-caption">Powered by CrewAI + FastAPI</span>
        </span>
      </a>
      <span className="navbar-badge">
        <span className="navbar-badge-dot" />
        Your research team is ready
      </span>
    </header>
  )
}

export default Navbar
