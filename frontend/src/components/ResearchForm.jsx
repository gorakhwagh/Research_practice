import { useEffect, useRef, useState } from 'react'
import api from '../services/api.js'

const agentNames = new Set([
  'Research Analyst',
  'Fact Checker',
  'Content Writer',
])

function makeRunId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID()
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (character) => {
    const random = Math.floor(Math.random() * 16)
    const value = character === 'x' ? random : (random & 0x3) | 0x8
    return value.toString(16)
  })
}

function ResearchForm({
  loading,
  onProgress,
  onResetProgress,
  onReport,
  onLoadingChange,
}) {
  const [topic, setTopic] = useState('')
  const [error, setError] = useState('')
  const eventSourceRef = useRef(null)

  useEffect(
    () => () => {
      eventSourceRef.current?.close()
    },
    [],
  )

  function connectToProgress(runId) {
    const baseUrl = api.defaults.baseURL.replace(/\/+$/, '')
    const url = new URL(`${baseUrl}/api/research/events`)
    url.searchParams.set('run_id', runId)

    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    for (const eventName of ['agent_started', 'agent_completed']) {
      eventSource.addEventListener(eventName, (event) => {
        try {
          const progress = JSON.parse(event.data)
          if (agentNames.has(progress.agent)) {
            onProgress(progress.agent, progress.status)
          }
        } catch {
          eventSource.close()
          setError('Received an unreadable progress update. Please try again.')
          onLoadingChange(false)
        }
      })
    }

    eventSource.addEventListener('run_failed', (event) => {
      try {
        const failure = JSON.parse(event.data)
        setError(failure.message || 'Research could not be completed.')
      } catch {
        setError('Research could not be completed. Please try again.')
      }
      eventSource.close()
    })

    eventSource.addEventListener('run_completed', () => {
      eventSource.close()
    })

    eventSource.onerror = () => {
      if (eventSource.readyState === EventSource.CLOSED) {
        eventSource.close()
      }
    }

    return eventSource
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const researchTopic = topic.trim()

    if (!researchTopic) {
      setError('Enter a research topic to get started.')
      return
    }

    if (researchTopic.length > 500) {
      setError('Keep your research topic under 500 characters.')
      return
    }

    setError('')
    onReport('')
    onResetProgress()
    onLoadingChange(true)

    const runId = makeRunId()
    const eventSource = connectToProgress(runId)

    try {
      const { data } = await api.post('/api/research', {
        topic: researchTopic,
        run_id: runId,
      })
      onReport(data.report)
    } catch (requestError) {
      const detail = requestError.response?.data?.detail
      setError(
        typeof detail === 'string'
          ? detail
          : 'Unable to reach the research service. Check that the backend is running and try again.',
      )
    } finally {
      eventSource.close()
      if (eventSourceRef.current === eventSource) {
        eventSourceRef.current = null
      }
      onLoadingChange(false)
    }
  }

  return (
    <form className="panel research-form" onSubmit={handleSubmit}>
      <div className="panel-heading">
        <span className="heading-icon" aria-hidden="true">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none">
            <circle
              cx="10.8"
              cy="10.8"
              r="6.8"
              stroke="currentColor"
              strokeWidth="1.7"
            />
            <path
              d="m16 16 4.2 4.2M10.8 7.5v6.6M7.5 10.8h6.6"
              stroke="currentColor"
              strokeLinecap="round"
              strokeWidth="1.7"
            />
          </svg>
        </span>
        <span>
          <h2>Start your research</h2>
          <p>What would you like to learn about?</p>
        </span>
      </div>

      <label className="topic-label" htmlFor="research-topic">
        Research topic
      </label>
      <textarea
        id="research-topic"
        className="topic-input"
        maxLength={500}
        placeholder="e.g. How is AI transforming renewable energy forecasting?"
        value={topic}
        onChange={(event) => setTopic(event.target.value)}
        disabled={loading}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? 'research-error' : undefined}
        required
      />
      {error && (
        <p className="form-error" id="research-error" role="alert">
          {error}
        </p>
      )}

      <button className="submit-button" type="submit" disabled={loading}>
        {loading ? (
          <>
            <span className="button-spinner" aria-hidden="true" />
            Researching your topic
          </>
        ) : (
          <>
            Generate research report
            <svg
              aria-hidden="true"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                d="M5 12h14m-6-6 6 6-6 6"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.8"
              />
            </svg>
          </>
        )}
      </button>
      <p className="secure-note">
        <svg
          aria-hidden="true"
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
        >
          <path
            d="M7 10V7a5 5 0 0 1 10 0v3m-11 0h12a2 2 0 0 1 2 2v8H4v-8a2 2 0 0 1 2-2Z"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.7"
          />
        </svg>
        Your research stays private
      </p>
    </form>
  )
}

export default ResearchForm
