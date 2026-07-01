import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

const baselineOptions = {
  feelings: [
    'Apprehensive',
    'Curious',
    'Hesitant',
    'Inspired',
    'Intrigued',
    'Optimistic',
    'Resistant',
    'Tentative',
  ],
  motivations: [
    'Achievement & Recognition',
    'Autonomy & Freedom',
    'Competition',
    'Connection & Belonging',
    'Enjoyment & Passion',
    'Financial Reward & Security',
    'Responsibility & Duty',
    'Personal Growth & Mastery',
    'Purpose & Meaning',
    "I'd rather not say",
  ],
  values: [
    'Achievement',
    'Authenticity',
    'Balance',
    'Collaboration & Teamwork',
    'Contribution & Service',
    'Courage',
    'Creativity',
    'Excellence',
    'Growth & Learning',
    'Health & Well-being',
    'Independence',
    'Integrity',
    'Perseverance & Resilience',
    'Responsibility',
    "I'd rather not say",
  ],
  mindsets: [
    'Fear of Failure (or success)',
    'Fixed Mindset (things cannot be improved)',
    'Lack of Clarity',
    'Negative self-talk',
    'Perfectionism',
    "I'd rather not say",
  ],
  obstacles: [
    'Lack of accountability',
    'Over commitment',
    'Poor habits (e.g. sleep, diet)',
    'Procrastination',
    'Unrealistic expectations',
    "I'd rather not say",
  ],
  external_factors: [
    'Environmental distractions (e.g. clutter, noise)',
    'Competing obligations (e.g. family, health, work)',
    'Financial constraints (limited resources to invest in tools, training, support)',
    'Systemic barriers (lack of access to networks, opportunities or support)',
    'Toxic relationships (people who discourage, sabotage, or drain motivation)',
    "I'd rather not say",
  ],
  learning_preferences: [
    'Doing or taking action',
    'Listening to podcasts/audio',
    'Watching short videos',
    'Reading',
  ],
}

const initialBaseline = {
  attitude_score: 5,
  effort_score: 5,
  feelings: [],
  motivations: [],
  motivation_score: 5,
  values: [],
  age: 35,
  mindsets: [],
  obstacles: [],
  external_factors: [],
  daily_commitment_minutes: 30,
  preferred_time_ranges: [],
  learning_preferences: [],
  notes: '',
}

async function requestJson(path, options) {
  const response = await fetch(`${API_BASE}${path}`, options)
  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = Array.isArray(data?.detail)
      ? data.detail.map((item) => item.msg).join(', ')
      : data?.detail || data?.error

    throw new Error(detail || `Request failed with status ${response.status}`)
  }

  if (data?.error) {
    throw new Error(data.error)
  }

  return data
}

function toggleLimited(list, value, limit = 2) {
  if (list.includes(value)) {
    return list.filter((item) => item !== value)
  }

  if (list.length >= limit) return list

  return [...list, value]
}

function getClockAngles(time) {
  const [hours = 0, minutes = 0] = time.split(':').map(Number)
  const hourAngle = ((hours % 12) + minutes / 60) * 30
  const minuteAngle = minutes * 6

  return { hourAngle, minuteAngle }
}

function formatDisplayTime(time) {
  const [hours = 0, minutes = 0] = time.split(':').map(Number)
  const period = hours >= 12 ? 'PM' : 'AM'
  const displayHours = hours % 12 || 12

  return `${String(displayHours).padStart(2, '0')}:${String(minutes).padStart(2, '0')} ${period}`
}

function inferPlanDays(text) {
  const match = text?.match(/\b(?:over|next|within|in)\s+(?:the\s+)?(?:next\s+)?(\d{1,3})\s+days?\b/i)
  const days = Number(match?.[1])

  return days >= 1 ? days : 60
}

function App() {
  const [phase, setPhase] = useState('aspiration')
  const [forces, setForces] = useState([])
  const [selectedForce, setSelectedForce] = useState('')
  const [manualForceText, setManualForceText] = useState('')
  const [classifiedForce, setClassifiedForce] = useState(null)
  const [forceDetails, setForceDetails] = useState(null)
  const [selectedDetail, setSelectedDetail] = useState('')
  const [rootData, setRootData] = useState(null)
  const [selectedRoots, setSelectedRoots] = useState([])
  const [aspiration, setAspiration] = useState('')
  const [aspirationId, setAspirationId] = useState('')
  const [baseline, setBaseline] = useState(initialBaseline)
  const [timeDraft, setTimeDraft] = useState({ start: '13:56', end: '17:00' })
  const [activeTimeField, setActiveTimeField] = useState('start')
  const [baselineResult, setBaselineResult] = useState(null)
  const [planResult, setPlanResult] = useState(null)
  const [loading, setLoading] = useState({
    forces: true,
    details: false,
    roots: false,
    classify: false,
    aspiration: false,
    baseline: false,
    plan: false,
    task: false,
  })
  const [error, setError] = useState('')

  const activeForce = useMemo(
    () => forces.find((force) => force.slug === selectedForce),
    [forces, selectedForce],
  )
  const canGenerateAspiration =
    selectedForce && selectedDetail && selectedRoots.length > 0 && !loading.aspiration
  const aspirationTitle = activeForce?.label
    ? `BeTTY AI has created your ${activeForce.label} Aspiration`
    : 'BeTTY AI has created your Aspiration'
  const activeClockTime = timeDraft[activeTimeField] || timeDraft.start
  const clockAngles = getClockAngles(activeClockTime)
  const gapAnalysis = baselineResult?.gap_analysis

  useEffect(() => {
    async function loadForces() {
      setError('')
      setLoading((current) => ({ ...current, forces: true }))

      try {
        const data = await requestJson('/forces')
        setForces(data)
      } catch (err) {
        setError(`Could not load forces. ${err.message}`)
      } finally {
        setLoading((current) => ({ ...current, forces: false }))
      }
    }

    loadForces()
  }, [])

  useEffect(() => {
    if (!selectedForce) return

    async function loadForceDetails() {
      setError('')
      setForceDetails(null)
      setSelectedDetail('')
      setRootData(null)
      setSelectedRoots([])
      setAspiration('')
      setAspirationId('')
      setBaselineResult(null)
      setLoading((current) => ({ ...current, details: true }))

      try {
        const data = await requestJson(`/forces/${selectedForce}`)
        setForceDetails(data)
      } catch (err) {
        setError(`Could not load force details. ${err.message}`)
      } finally {
        setLoading((current) => ({ ...current, details: false }))
      }
    }

    loadForceDetails()
  }, [selectedForce])

  useEffect(() => {
    if (!selectedForce || !selectedDetail) return

    async function loadRootCauses() {
      setError('')
      setRootData(null)
      setSelectedRoots([])
      setAspiration('')
      setAspirationId('')
      setBaselineResult(null)
      setLoading((current) => ({ ...current, roots: true }))

      try {
        const detailQuery = new URLSearchParams({ detail: selectedDetail }).toString()
        const data = await requestJson(`/forces/${selectedForce}/detail?${detailQuery}`)
        setRootData(data)
      } catch (err) {
        setError(`Could not load root causes. ${err.message}`)
      } finally {
        setLoading((current) => ({ ...current, roots: false }))
      }
    }

    loadRootCauses()
  }, [selectedForce, selectedDetail])

  function selectForce(slug, classification = null) {
    setAspiration('')
    setAspirationId('')
    setBaselineResult(null)
    setClassifiedForce(classification)
    setSelectedForce(slug)
    setSelectedRoots([])
  }

  function selectRootCause(rootCause) {
    setAspiration('')
    setAspirationId('')
    setBaselineResult(null)
    setSelectedRoots((current) => toggleLimited(current, rootCause))
  }

  function selectDetail(detail) {
    setSelectedDetail(detail)
    setSelectedRoots([])
    setAspiration('')
    setAspirationId('')
    setBaselineResult(null)
  }

  function updateBaseline(field, value) {
    setBaseline((current) => ({ ...current, [field]: value }))
    setBaselineResult(null)
  }

  function toggleBaselineOption(field, value, limit = 2) {
    setBaseline((current) => ({
      ...current,
      [field]: toggleLimited(current[field], value, limit),
    }))
    setBaselineResult(null)
  }

  function addTimeRange() {
    if (!timeDraft.start || !timeDraft.end) return

    updateBaseline('preferred_time_ranges', [
      ...baseline.preferred_time_ranges,
      { start: timeDraft.start, end: timeDraft.end },
    ])
  }

  function removeTimeRange(indexToRemove) {
    updateBaseline(
      'preferred_time_ranges',
      baseline.preferred_time_ranges.filter((_, index) => index !== indexToRemove),
    )
  }

  async function classifyManualForce(event) {
    event.preventDefault()

    if (!manualForceText.trim()) {
      setError('Please describe what you want to improve first.')
      return
    }

    setError('')
    setClassifiedForce(null)
    setLoading((current) => ({ ...current, classify: true }))

    try {
      const data = await requestJson('/forces/classify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: manualForceText }),
      })
      selectForce(data.slug, data)
    } catch (err) {
      setError(`Could not classify your input. ${err.message}`)
    } finally {
      setLoading((current) => ({ ...current, classify: false }))
    }
  }

  async function submitAspiration(event) {
    event.preventDefault()

    if (!canGenerateAspiration) return

    setError('')
    setAspiration('')
    setAspirationId('')
    setBaselineResult(null)
    setLoading((current) => ({ ...current, aspiration: true }))

    try {
      const payload = {
        force: activeForce?.label || selectedForce,
        issue: selectedDetail,
        root_causes: selectedRoots,
      }
      const data = await requestJson('/generate-aspiration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      setAspiration(data.aspiration)
      setAspirationId(data.aspiration_id || data.id || '')
    } catch (err) {
      setError(`Could not generate aspiration. ${err.message}`)
    } finally {
      setLoading((current) => ({ ...current, aspiration: false }))
    }
  }

  async function submitBaseline(event) {
    event.preventDefault()

    if (!aspirationId) {
      setError('Could not save baseline because the aspiration ID was not returned by the backend.')
      return
    }

    setError('')
    setBaselineResult(null)
    setLoading((current) => ({ ...current, baseline: true }))

    try {
      const data = await requestJson(`/baseline/${aspirationId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(baseline),
      })
      let nextResult = data

      try {
        const gapData = await requestJson(`/gap-analysis/${aspirationId}`, {
          method: 'POST',
        })
        nextResult = { ...data, gap_analysis: gapData }
      } catch {
        nextResult = data
      }

      setBaselineResult(nextResult)
      setPhase('gap-analysis')
    } catch (err) {
      setError(`Could not save baseline. ${err.message}`)
    } finally {
      setLoading((current) => ({ ...current, baseline: false }))
    }
  }

  async function generatePlan() {
    if (!aspirationId) {
      setError('Could not generate a plan because the aspiration ID is missing.')
      return
    }

    setError('')
    setLoading((current) => ({ ...current, plan: true }))

    try {
      const data = await requestJson('/plan/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          journey_id: aspirationId,
          plan_days: inferPlanDays(aspiration),
        }),
      })

      setPlanResult(data.data || data)
      setPhase('plan')
    } catch (err) {
      setError(`Could not generate your change plan. ${err.message}`)
    } finally {
      setLoading((current) => ({ ...current, plan: false }))
    }
  }

  async function toggleTaskCompletion(taskIndex, completed) {
    if (!aspirationId) return

    setError('')
    setLoading((current) => ({ ...current, task: true }))

    try {
      const data = await requestJson(`/plan/${aspirationId}/tasks/${taskIndex}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed }),
      })

      setPlanResult(data.data || data)
    } catch (err) {
      setError(`Could not update the task. ${err.message}`)
    } finally {
      setLoading((current) => ({ ...current, task: false }))
    }
  }

  if (phase === 'plan') {
    return (
      <PlanPage
        error={error}
        forceLabel={activeForce?.label || selectedForce || 'Growth'}
        loadingTask={loading.task}
        onBack={() => setPhase('gap-analysis')}
        onToggleTask={toggleTaskCompletion}
        plan={planResult}
        aspirationId={aspirationId}
        onReplaceSuccess={(taskId, updatedTask) => {
          setPlanResult((current) => {
            if (!current) return current
            const updatedTasks = current.tasks.map((t) => {
              if (t.task_id === taskId) {
                return updatedTask
              }
              return t
            })
            return { ...current, tasks: updatedTasks }
          })
        }}
      />
    )
  }

  if (phase === 'gap-analysis') {
    return (
      <main className="gap-shell">
        <header className="gap-header">
          <h1>My Gap Analysis</h1>
          <p>
            Where I am <strong>(my baseline)</strong>
            <span>|</span>
            Where I want to be <strong>(my aspiration)</strong>
          </p>
        </header>

        <section className="gap-board">
          <div className="gap-title-row">
            <h2>{gapAnalysis?.from_title || `From ${selectedDetail || 'Current State'}`}</h2>
            <h2>{gapAnalysis?.to_title || `To ${activeForce?.label || 'My Aspiration'} Journey`}</h2>
          </div>

          <div className="gap-grid">
            <GapCard
              icon="A"
              title="Where I am"
              text={
                gapAnalysis?.where_i_am ||
                gapAnalysis?.current_state ||
                'Your current baseline will appear here after saving.'
              }
            />
            <GapCard
              icon="B"
              title="Where I want to be"
              text={
                gapAnalysis?.where_i_want_to_be ||
                gapAnalysis?.desired_state ||
                gapAnalysis?.aspiration ||
                aspiration
              }
            />
            <GapList
              icon="!"
              items={gapAnalysis?.my_obstacles || gapAnalysis?.obstacles || gapAnalysis?.blockers || []}
              title="My Obstacles"
            />
            <GapList
              icon="*"
              items={gapAnalysis?.my_success_criteria || gapAnalysis?.success_criteria || []}
              title="My Success Criteria"
              subtitle="(My Stops & Starts)"
            />
          </div>

          <div className="gap-footer">
            <button className="gap-back" onClick={() => setPhase('baseline')} type="button">
              &lt;- Back to baseline
            </button>
            <button className="gap-action" disabled={loading.plan} onClick={generatePlan} type="button">
              {loading.plan ? 'Generating Plan...' : 'Generate My Change Plan ->'}
            </button>
          </div>
          {error && <p className="form-message error-message">{error}</p>}
        </section>
      </main>
    )
  }

  if (phase === 'baseline') {
    return (
      <main className="baseline-shell">
        <header className="baseline-header">
          <h1>Baseline your Current State</h1>
          <p>The next questions help BeTTY diagnose the gap between your current state and your Aspiration.</p>
        </header>

        <form className="baseline-form" onSubmit={submitBaseline}>
          <section className="baseline-card aspiration-card">
            <div className="aspiration-card-header">
              <div className="avatar-mark">AI</div>
              <div>
                <h2>{aspirationTitle}</h2>
                <p>Please feel free to edit it to make it align with your needs.</p>
              </div>
              <button className="icon-button" type="button" aria-label="Collapse aspiration">
                ^
              </button>
            </div>

            <div className="aspiration-preview">
              <p>{aspiration}</p>
              <div className="aspiration-actions">
                <button className="edit-button" onClick={() => setPhase('aspiration')} type="button">
                  Edit
                </button>
                <span>{aspiration.length} chars</span>
              </div>
            </div>
          </section>

          <section className="baseline-card">
            <h2>Please rate past attitude and efforts regarding this Aspiration.</h2>
            <div className="slider-grid">
              <SliderField
                label="Attitude you had"
                maxLabel="10 Positive"
                minLabel="1 Negative"
                onChange={(value) => updateBaseline('attitude_score', value)}
                value={baseline.attitude_score}
              />
              <SliderField
                label="Efforts"
                maxLabel="10 High"
                minLabel="1 Low"
                onChange={(value) => updateBaseline('effort_score', value)}
                value={baseline.effort_score}
              />
            </div>
          </section>

          <OptionSection
            field="feelings"
            max={2}
            onToggle={toggleBaselineOption}
            options={baselineOptions.feelings}
            selected={baseline.feelings}
            title="How are you feeling right now about starting your personal development journey?"
            subtitle="Please select up to two words."
          />

          <OptionSection
            field="motivations"
            max={2}
            onToggle={toggleBaselineOption}
            options={baselineOptions.motivations}
            selected={baseline.motivations}
            title="Please share up to two motives that will fuel you to achieve your Aspiration."
          />

          <section className="baseline-card">
            <h2>
              On a scale from 1-10, 1 being no motivation, 10 being extremely motivated, how
              motivated are you to reach your aspiration?
            </h2>
            <SliderField
              label="Motivation"
              maxLabel="10 High"
              minLabel="1 Low"
              onChange={(value) => updateBaseline('motivation_score', value)}
              value={baseline.motivation_score}
            />
          </section>

          <OptionSection
            field="values"
            max={2}
            onToggle={toggleBaselineOption}
            options={baselineOptions.values}
            selected={baseline.values}
            title="Please share up to two of your values so that BeTTY will understand how to support you to keep your focus over a long period of time when working toward your Aspiration."
          />

          <section className="baseline-card">
            <h2>What is your age range?</h2>
            <SliderField
              label="Age"
              max={99}
              maxLabel="99"
              min={18}
              minLabel="18"
              onChange={(value) => updateBaseline('age', value)}
              value={baseline.age}
            />
          </section>

          <OptionSection
            field="mindsets"
            max={2}
            onToggle={toggleBaselineOption}
            options={baselineOptions.mindsets}
            selected={baseline.mindsets}
            title="Please identify up to two mindsets that are an obstacle for you."
          />

          <OptionSection
            field="obstacles"
            max={2}
            onToggle={toggleBaselineOption}
            options={baselineOptions.obstacles}
            selected={baseline.obstacles}
            title="Please identify up to two actions or beliefs that are an obstacle for you."
          />

          <OptionSection
            field="external_factors"
            max={2}
            onToggle={toggleBaselineOption}
            options={baselineOptions.external_factors}
            selected={baseline.external_factors}
            title="Please identify up to two external factors or circumstances that are an obstacle for you."
          />

          <section className="baseline-card">
            <h2>How many minutes are you willing to invest in yourself each day?</h2>
            <SliderField
              label="Daily commitment"
              max={100}
              maxLabel="100 min"
              min={10}
              minLabel="10 min"
              onChange={(value) => updateBaseline('daily_commitment_minutes', value)}
              suffix=" mins"
              value={baseline.daily_commitment_minutes}
            />
          </section>

          <section className="baseline-card time-card">
            <h2>When do you prefer to complete your daily tasks?</h2>
            <p>Add one or more preferred time slots. BeTTY will schedule tasks within these ranges.</p>
            <div className="time-builder">
              <div className="time-panel">
                <div className="time-input-row">
                  <label>
                    <span>Start time</span>
                    <input
                      onChange={(event) =>
                        setTimeDraft((current) => ({ ...current, start: event.target.value }))
                      }
                      onFocus={() => setActiveTimeField('start')}
                      type="time"
                      value={timeDraft.start}
                    />
                    <strong>{formatDisplayTime(timeDraft.start)}</strong>
                  </label>
                  <span className="time-arrow">-&gt;</span>
                  <label>
                    <span>End time</span>
                    <input
                      onChange={(event) =>
                        setTimeDraft((current) => ({ ...current, end: event.target.value }))
                      }
                      onFocus={() => setActiveTimeField('end')}
                      type="time"
                      value={timeDraft.end}
                    />
                    <strong>{formatDisplayTime(timeDraft.end)}</strong>
                  </label>
                </div>
                <div className="clock-status">
                  Showing {activeTimeField === 'start' ? 'start' : 'end'} time:{' '}
                  <strong>{formatDisplayTime(activeClockTime)}</strong>
                </div>
                <div className="clock-face" aria-hidden="true">
                  {Array.from({ length: 60 }, (_, tick) => (
                    <i
                      className={tick % 5 === 0 ? 'clock-tick major' : 'clock-tick'}
                      key={tick}
                      style={{ transform: `rotate(${tick * 6}deg)` }}
                    />
                  ))}
                  <span
                    className="hand hand-hour"
                    style={{ transform: `rotate(${clockAngles.hourAngle}deg)` }}
                  />
                  <span
                    className="hand hand-minute"
                    style={{ transform: `rotate(${clockAngles.minuteAngle}deg)` }}
                  />
                  {[12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((hour, index) => (
                    <b className={`hour hour-${index}`} key={hour}>
                      {hour}
                    </b>
                  ))}
                </div>
                <button className="blue-button" onClick={addTimeRange} type="button">
                  + Add Time Range
                </button>
                <div className="active-ranges">
                  <strong>Active time ranges</strong>
                  {baseline.preferred_time_ranges.length ? (
                    baseline.preferred_time_ranges.map((range, index) => (
                      <div className="active-range-row" key={`${range.start}-${range.end}-${index}`}>
                        <span>
                          {formatDisplayTime(range.start)} - {formatDisplayTime(range.end)}
                        </span>
                        <button onClick={() => removeTimeRange(index)} type="button">
                          Remove
                        </button>
                      </div>
                    ))
                  ) : (
                    <em>No time ranges configured. Please add at least one range.</em>
                  )}
                </div>
              </div>
            </div>
          </section>

          <OptionSection
            field="learning_preferences"
            max={2}
            onToggle={toggleBaselineOption}
            options={baselineOptions.learning_preferences}
            selected={baseline.learning_preferences}
            title="Related to this Aspiration, how do you prefer to learn?"
            subtitle="Please select up to two options."
          />

          <section className="baseline-card">
            <h2>Please add anything else you would like BeTTY to know to baseline your current state.</h2>
            <label className="notes-field">
              <textarea
                maxLength={200}
                onChange={(event) => updateBaseline('notes', event.target.value)}
                placeholder="Type here"
                value={baseline.notes}
              />
              <span>{baseline.notes.length}/200</span>
            </label>
          </section>

          {error && <p className="form-message error-message">{error}</p>}
          {baselineResult && (
            <p className="form-message success-message">
              Baseline saved. Readiness: {baselineResult.readiness?.score} ({baselineResult.readiness?.level})
            </p>
          )}

          <div className="baseline-nav">
            <button className="back-button" onClick={() => setPhase('aspiration')} type="button">
              &lt;- Back
            </button>
            <button className="next-button" disabled={loading.baseline} type="submit">
              {loading.baseline ? 'Saving...' : 'Next ->'}
            </button>
          </div>
        </form>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <section className="intro-band">
        <div>
          <p className="eyebrow">Psychology Force Analysis</p>
          <h1>Find the gap between where you are and what needs attention.</h1>
          <p className="intro-copy">
            Choose a life force, name the specific issue, select likely root causes, and get a
            focused aspiration from your backend.
          </p>
        </div>
        <div className="status-panel" aria-live="polite">
          <span className={error ? 'status-dot error' : 'status-dot'} />
          <div>
            <strong>{error ? 'Connection needs attention' : 'Backend connected'}</strong>
            <p>{error || 'Using FastAPI endpoints through the Vite /api proxy.'}</p>
          </div>
        </div>
      </section>

      <form className="workspace" onSubmit={submitAspiration}>
        <section className="panel">
          <div className="section-heading">
            <span>1</span>
            <div>
              <h2>Select a force</h2>
              <p>Start with the area you want to improve.</p>
            </div>
          </div>

          {loading.forces ? (
            <p className="muted">Loading forces...</p>
          ) : (
            <>
              <div className="choice-grid force-grid">
                {forces.map((force) => (
                  <button
                    className={force.slug === selectedForce ? 'choice active' : 'choice'}
                    key={force.slug}
                    onClick={() => selectForce(force.slug)}
                    type="button"
                  >
                    {force.label}
                  </button>
                ))}
              </div>

              <div className="manual-force">
                <label>
                  <span>Or describe it in your own words</span>
                  <input
                    onChange={(event) => setManualForceText(event.target.value)}
                    placeholder="Example: I am struggling to save money"
                    type="text"
                    value={manualForceText}
                  />
                </label>
                <button
                  className="secondary-button"
                  disabled={loading.classify}
                  onClick={classifyManualForce}
                  type="button"
                >
                  {loading.classify ? 'Selecting force...' : 'Auto-select force'}
                </button>
              </div>

              {classifiedForce && (
                <p className="classification-note">
                  Selected <strong>{classifiedForce.label}</strong>
                  {classifiedForce.reason ? `: ${classifiedForce.reason}` : ''}
                </p>
              )}
            </>
          )}
        </section>

        {selectedForce && (
          <section className="panel">
            <div className="section-heading">
              <span>2</span>
              <div>
                <h2>Pick the issue</h2>
                <p>{forceDetails?.question || 'Choose a force to see its question.'}</p>
              </div>
            </div>

            {loading.details ? (
              <p className="muted">Loading details...</p>
            ) : (
              <div className="choice-grid">
                {forceDetails?.options?.map((detail) => (
                  <button
                    className={detail === selectedDetail ? 'choice active' : 'choice'}
                    key={detail}
                    onClick={() => selectDetail(detail)}
                    type="button"
                  >
                    {detail}
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {selectedDetail && (
          <section className="panel">
            <div className="section-heading">
              <span>3</span>
              <div>
                <h2>Choose up to two root causes</h2>
                <p>{rootData?.question || 'Select an issue to reveal root causes.'}</p>
              </div>
            </div>

            {loading.roots ? (
              <p className="muted">Loading root causes...</p>
            ) : (
              <div className="choice-grid">
                {rootData?.root_causes?.map((rootCause) => (
                  <button
                    className={selectedRoots.includes(rootCause) ? 'choice active' : 'choice'}
                    key={rootCause}
                    onClick={() => selectRootCause(rootCause)}
                    type="button"
                  >
                    {rootCause}
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {selectedRoots.length > 0 && (
          <section className="panel">
            <div className="section-heading">
              <span>4</span>
              <div>
                <h2>Create My Aspiration</h2>
                <p>Turn your selected force, issue, and root causes into a focused aspiration.</p>
              </div>
            </div>

            <button className="submit-button" disabled={!canGenerateAspiration} type="submit">
              {loading.aspiration ? 'Creating aspiration...' : 'Create My Aspiration'}
            </button>
          </section>
        )}
      </form>

      {aspiration && (
        <section className="results-panel">
          <div className="section-heading">
            <span>5</span>
            <div>
              <h2>Your aspiration</h2>
              <p>Generated by the backend from your selected inputs.</p>
            </div>
          </div>

          <div className="result-summary">
            <h3>Aspiration</h3>
            <p>{aspiration}</p>
          </div>

          <button className="next-button result-next" onClick={() => setPhase('baseline')} type="button">
            Next -&gt;
          </button>
        </section>
      )}
    </main>
  )
}

function SliderField({
  label,
  value,
  onChange,
  min = 1,
  max = 10,
  minLabel,
  maxLabel,
  suffix = '',
}) {
  return (
    <div className="slider-card">
      <div className="slider-topline">
        <strong>{label}</strong>
        <span>
          {value}
          {suffix}
        </span>
      </div>
      <input
        max={max}
        min={min}
        onChange={(event) => onChange(Number(event.target.value))}
        type="range"
        value={value}
      />
      <div className="slider-labels">
        <span>{minLabel}</span>
        <span>{maxLabel}</span>
      </div>
    </div>
  )
}

function OptionSection({ title, subtitle, field, options, selected, onToggle, max }) {
  return (
    <section className="baseline-card">
      <h2>{title}</h2>
      {subtitle && <p>{subtitle}</p>}
      <div className="baseline-option-box">
        {options.map((option) => (
          <button
            className={selected.includes(option) ? 'baseline-chip selected' : 'baseline-chip'}
            key={option}
            onClick={() => onToggle(field, option, max)}
            type="button"
          >
            {option}
          </button>
        ))}
        {field !== 'learning_preferences' && (
          <button
            className="baseline-chip"
            onClick={() => {
              const value = window.prompt('Write your own')
              if (value?.trim()) onToggle(field, value.trim(), max)
            }}
            type="button"
          >
            Write your own
          </button>
        )}
      </div>
    </section>
  )
}

function GapCard({ icon, title, text }) {
  return (
    <article className="gap-card">
      <h3>
        <span>{icon}</span>
        {title}
      </h3>
      <div className="gap-content">
        <p>{text}</p>
      </div>
    </article>
  )
}

function GapList({ icon, title, subtitle, items }) {
  const safeItems = items.length ? items : ['No items returned yet.']

  return (
    <article className="gap-card">
      <h3>
        <span>{icon}</span>
        {title}
        {subtitle && <small>{subtitle}</small>}
      </h3>
      <div className="gap-content">
        <ul>
          {safeItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </article>
  )
}

function PlanPage({ plan, forceLabel, error, loadingTask, onBack, onToggleTask, aspirationId, onReplaceSuccess }) {
  const [replaceTaskTarget, setReplaceTaskTarget] = useState(null)
  const tasks = plan?.tasks || []
  const resources = normalizeResources(plan?.resources)
  const totalTasks = plan?.total_tasks ?? tasks.length
  const completedTasks =
    plan?.completed_tasks ?? tasks.filter((task) => task.completed).length
  const completionPercent = totalTasks ? Math.round((completedTasks / totalTasks) * 100) : 0
  const planDays =
    plan?.plan_days ||
    Math.max(
      ...tasks.map((task) => Number(task.day) || 0),
      totalTasks,
      0,
    )
  const planResourceCount = resources.reduce((count, group) => count + group.items.length, 0)
  const taskResourceCount = tasks.reduce(
    (count, task) =>
      count +
      normalizeResources(task.resources || task).reduce(
        (groupCount, group) => groupCount + group.items.length,
        0,
      ),
    0,
  )
  const resourceCount = planResourceCount + taskResourceCount

  return (
    <main className="plan-shell">
      <header className="plan-header">
        <h1>{forceLabel} - Empowered {forceLabel} Foundations</h1>
        <p>Embark on a journey to build confidence through informed actions and creative solutions.</p>

        <div className="plan-stats">
          <PlanStat label="Total Tasks" value={totalTasks} />
          <PlanStat label="Completed Tasks" percent={completionPercent} value={completedTasks} />
          {resourceCount > 0 && <PlanStat label="Resources" value={resourceCount} />}
        </div>
      </header>

      <section className="plan-accordion">
        <strong>To Active</strong>
        <span>^</span>
      </section>

      <section className="task-panel">
        <div className="task-panel-header">
          <strong>Tasks & Activities</strong>
          <span>{forceLabel}</span>
          {planDays > 0 && <span>{planDays} Day Plan</span>}
        </div>

        <div className="task-list">
          {tasks.length ? (
            tasks.map((task, index) => (
              <TaskCard
                disabled={loadingTask}
                index={index}
                key={`${task.day}-${task.title}-${index}`}
                onToggleTask={onToggleTask}
                onOpenReplaceModal={setReplaceTaskTarget}
                task={task}
              />
            ))
          ) : (
            <p className="plan-empty">No tasks returned yet.</p>
          )}
        </div>
      </section>

      {planResourceCount > 0 && (
        <section className="resource-panel">
          <div className="task-panel-header">
            <strong>Resources</strong>
            <span>Books, Videos & Audios</span>
          </div>
          <div className="resource-grid">
            {resources.map((group) => (
              <ResourceGroup group={group} key={group.key} />
            ))}
          </div>
        </section>
      )}

      {error && <p className="form-message error-message">{error}</p>}

      <div className="plan-nav">
        <button className="gap-back" onClick={onBack} type="button">
          &lt;- Back to gap analysis
        </button>
      </div>

      {replaceTaskTarget && (
        <ReplaceTaskModal
          task={replaceTaskTarget}
          tasks={tasks}
          aspirationId={aspirationId}
          onClose={() => setReplaceTaskTarget(null)}
          onReplaceSuccess={onReplaceSuccess}
        />
      )}
    </main>
  )
}

function PlanStat({ label, value, percent }) {
  return (
    <article className="plan-stat">
      <span>{label}</span>
      <strong>{String(value).padStart(2, '0')}</strong>
      {typeof percent === 'number' && <em>{percent}%</em>}
    </article>
  )
}

function TaskCard({ task, index, disabled, onToggleTask, onOpenReplaceModal }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const complete = Boolean(task.completed)
  const resources = normalizeResources(task.resources || task)
  const taskResources = resources.filter((group) => group.items.length > 0)

  useEffect(() => {
    if (!menuOpen) return

    const handleOutsideClick = () => {
      setMenuOpen(false)
    }

    const timer = setTimeout(() => {
      window.addEventListener('click', handleOutsideClick)
    }, 0)

    return () => {
      clearTimeout(timer)
      window.removeEventListener('click', handleOutsideClick)
    }
  }, [menuOpen])

  return (
    <article className={complete ? 'task-card complete' : 'task-card'}>
      <button
        className={`task-menu ${menuOpen ? 'active' : ''}`}
        type="button"
        aria-label="Task actions"
        onClick={() => setMenuOpen(!menuOpen)}
      >
        ...
      </button>

      {menuOpen && (
        <div className="task-dropdown-menu">
          <button
            className="task-dropdown-item"
            type="button"
            onClick={() => {
              setMenuOpen(false)
              onOpenReplaceModal(task)
            }}
          >
            <span className="task-dropdown-icon">🔄</span>
            Replace Task
          </button>
        </div>
      )}

      <div>
        <h2>{task.title}</h2>
        <p>{task.description || task.rationale}</p>
      </div>

      {taskResources.length > 0 && (
        <div className="task-resource-row">
          {taskResources.map((group) => (
            <ResourceGroup compact group={group} key={group.key} />
          ))}
        </div>
      )}

      <div className="task-card-footer">
        <div className="task-meta">
          <span>Day {String(task.day).padStart(2, '0')}</span>
          <span>{task.scheduled_time}</span>
          <span>{task.duration_minutes} mins</span>
        </div>
        <button
          className={complete ? 'complete-button done' : 'complete-button'}
          disabled={disabled}
          onClick={() => onToggleTask(index, !complete)}
          type="button"
        >
          {complete ? 'Completed' : 'Mark as Complete'}
        </button>
      </div>
    </article>
  )
}

function normalizeResources(source = {}) {
  if (Array.isArray(source)) {
    const grouped = source.reduce(
      (groups, item) => {
        const key = getResourceGroupKey(item?.type || item?.resource_type)
        groups[key].push(item)
        return groups
      },
      {
        books: [],
        videos: [],
        audios: [],
        resources: [],
      },
    )

    return buildResourceGroups(grouped)
  }

  return buildResourceGroups({
    books: Array.isArray(source.books) ? source.books : [],
    videos: Array.isArray(source.videos) ? source.videos : [],
    audios: Array.isArray(source.audios) ? source.audios : [],
    resources: Array.isArray(source.resources) ? source.resources : [],
  })
}

function buildResourceGroups(grouped) {
  return [
    {
      key: 'books',
      label: 'Books',
      items: grouped.books || [],
    },
    {
      key: 'videos',
      label: 'Videos',
      items: grouped.videos || [],
    },
    {
      key: 'audios',
      label: 'Audios',
      items: grouped.audios || [],
    },
    {
      key: 'resources',
      label: 'Resources',
      items: grouped.resources || [],
    },
  ].filter((group) => group.items.length > 0)
}

function getResourceGroupKey(type = '') {
  const normalized = String(type).toLowerCase()

  if (normalized.includes('book') || normalized.includes('read')) return 'books'
  if (normalized.includes('video') || normalized.includes('watch')) return 'videos'
  if (normalized.includes('audio') || normalized.includes('podcast') || normalized.includes('listen')) {
    return 'audios'
  }

  return 'resources'
}

function ResourceGroup({ group, compact = false }) {
  return (
    <article className={compact ? 'resource-group compact' : 'resource-group'}>
      <h3>{group.label}</h3>
      <div className="resource-list">
        {group.items.map((item, index) => (
          <ResourceItem item={item} key={`${group.key}-${item.title || index}`} />
        ))}
      </div>
    </article>
  )
}

function ResourceItem({ item }) {
  const title = typeof item === 'string' ? item : item.title
  const detail = typeof item === 'string' ? '' : item.reason || item.description || item.category
  const type = typeof item === 'string' ? '' : item.type
  const url = typeof item === 'string' ? '' : item.url || item.link || item.href
  const fallbackUrl = title ? buildResourceSearchUrl(type, title) : ''
  const displayUrl = url || fallbackUrl

  return (
    <div className="resource-item">
      <div className="resource-title-row">
        {displayUrl ? (
          <a href={displayUrl} rel="noreferrer" target="_blank">
            {title}
          </a>
        ) : (
          <strong>{title}</strong>
        )}
        {type && <span>{type}</span>}
      </div>
      {detail && <p>{detail}</p>}
      {displayUrl && (
        <a className="resource-link" href={displayUrl} rel="noreferrer" target="_blank">
          Open resource
        </a>
      )}
    </div>
  )
}

function buildResourceSearchUrl(type, title) {
  const query = encodeURIComponent(title)
  const normalized = String(type).toLowerCase()

  if (normalized.includes('video')) return `https://www.youtube.com/results?search_query=${query}`
  if (normalized.includes('audio') || normalized.includes('podcast')) {
    return `https://www.google.com/search?q=${query}+podcast`
  }
  if (normalized.includes('book') || normalized.includes('read')) {
    return `https://www.google.com/search?q=${query}+book`
  }

  return `https://www.google.com/search?q=${query}`
}

function ReplaceTaskModal({ task, tasks, aspirationId, onClose, onReplaceSuccess }) {
  const [activeTask, setActiveTask] = useState(task)
  const [alternatives, setAlternatives] = useState([])
  const [loading, setLoading] = useState(false)
  const [replacing, setReplacing] = useState(false)
  const [selectedAlternativeId, setSelectedAlternativeId] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    async function fetchAlternatives() {
      setLoading(true)
      setError('')
      setAlternatives([])
      setSelectedAlternativeId(null)
      try {
        const data = await requestJson(`/tasks/${aspirationId}/${activeTask.task_id}/alternatives`, {
          method: 'POST'
        })
        if (active) {
          if (data.success && data.alternatives) {
            setAlternatives(data.alternatives)
          } else {
            setError(data.message || 'Failed to generate alternatives.')
          }
        }
      } catch (err) {
        if (active) {
          setError(err.message || 'An error occurred while fetching alternatives.')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    if (activeTask?.task_id) {
      fetchAlternatives()
    }

    return () => {
      active = false
    }
  }, [activeTask, aspirationId])

  const handleTaskChange = (e) => {
    const selectedId = e.target.value
    const foundTask = tasks.find((t) => t.task_id === selectedId)
    if (foundTask) {
      setActiveTask(foundTask)
    }
  }

  const handleReplaceSubmit = async () => {
    if (!selectedAlternativeId) return
    setReplacing(true)
    setError('')
    try {
      const data = await requestJson(`/tasks/${aspirationId}/${activeTask.task_id}/replace`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alternative_id: selectedAlternativeId }),
      })
      if (data.success && data.task) {
        onReplaceSuccess(activeTask.task_id, data.task)
        onClose()
      } else {
        setError(data.message || 'Failed to replace task.')
      }
    } catch (err) {
      setError(err.message || 'An error occurred while replacing task.')
    } finally {
      setReplacing(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Replace Task with AI</h2>
          <button className="modal-close" onClick={onClose} type="button" aria-label="Close">
            &times;
          </button>
        </div>

        <div className="modal-field">
          <label htmlFor="task-select">Search Task</label>
          <select
            id="task-select"
            className="modal-select"
            value={activeTask.task_id}
            onChange={handleTaskChange}
          >
            {tasks.map((t) => (
              <option key={t.task_id} value={t.task_id}>
                {t.title}
              </option>
            ))}
          </select>
        </div>

        <div className="alternatives-section">
          {loading ? (
            <div className="alternatives-loading">
              <div className="spinner"></div>
              <p>Generating alternatives with AI...</p>
            </div>
          ) : error ? (
            <div className="modal-error-container">
              <p className="modal-error">{error}</p>
            </div>
          ) : (
            <div className="alternatives-list">
              {alternatives.map((alt) => (
                <label
                  key={alt.alternative_id}
                  className={`alt-card ${selectedAlternativeId === alt.alternative_id ? 'selected' : ''}`}
                >
                  <input
                    type="radio"
                    name="alternative_task"
                    value={alt.alternative_id}
                    checked={selectedAlternativeId === alt.alternative_id}
                    onChange={() => setSelectedAlternativeId(alt.alternative_id)}
                    className="alt-radio"
                  />
                  <div className="alt-card-content">
                    <h3>{alt.title}</h3>
                    <p className="alt-card-desc">{alt.description}</p>
                    <div className="alt-card-meta">
                      <span className="alt-meta-item">
                        <span className="alt-icon">🕒</span>
                        {alt.scheduled_time} | {alt.duration_minutes} min
                      </span>
                      {alt.resources && alt.resources.map((res, i) => (
                        <span key={i} className="alt-meta-item resource">
                          <span className="alt-icon">
                            {res.resource_type === 'video' ? '▶️' : res.resource_type === 'audio' ? '🎙️' : '📚'}
                          </span>
                          Rec: {res.title} {res.url && <span className="link-icon">🔗</span>}
                        </span>
                      ))}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {error && !loading && (
          <div className="modal-error-container">
            <p className="modal-error">{error}</p>
          </div>
        )}

        <div className="modal-actions">
          <button className="modal-btn-cancel" onClick={onClose} type="button" disabled={replacing}>
            Cancel
          </button>
          <button
            className="modal-btn-submit"
            onClick={handleReplaceSubmit}
            type="button"
            disabled={!selectedAlternativeId || replacing || loading}
          >
            {replacing ? 'Updating...' : 'Update Task'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
