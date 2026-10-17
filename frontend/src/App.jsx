// App.jsx
// 3-page flow with modern light theme.
// All inline styles now use light-theme CSS variables from App.css.
// Dark theme removed — sub-components (WesternPanel, AyurvedicPanel, etc.)
// are white-themed via Tailwind and this matches them correctly.

import './App.css'
import { useState } from "react"
import { getFullExplanation } from "./services/explanationService"

import DiseaseHeader   from "./components/DualExplanation/DiseaseHeader"
import PrakritiPills   from "./components/DualExplanation/PrakritiPills"
import WesternPanel    from "./components/DualExplanation/WesternPanel"
import AyurvedicPanel  from "./components/DualExplanation/AyurvedicPanel"
import PersonalizedBox from "./components/DualExplanation/PersonalizedBox"
import ReasoningPanel  from "./components/DualExplanation/ReasoningPanel"
import SafetyReferral  from "./components/SafetyReferral/SafetyReferral"
import LoadingSpinner  from "./components/common/LoadingSpinner"
import Disclaimer      from "./components/common/Disclaimer"

// ── Diseases ----------------------------------------------------------------
const DISEASES = [
  { id: "eczema",                name: "Eczema",                 confidence: 0.94 },
  { id: "psoriasis",             name: "Psoriasis",              confidence: 0.88 },
  { id: "acne",                  name: "Acne",                   confidence: 0.91 },
  { id: "vitiligo",              name: "Vitiligo",               confidence: 0.85 },
  { id: "fungal_infection",      name: "Fungal Infection",       confidence: 0.87 },
  { id: "urticaria",             name: "Urticaria",              confidence: 0.86 },
  { id: "dermatitis",            name: "Contact Dermatitis",     confidence: 0.88 },
  { id: "dry_skin",              name: "Dry Skin",               confidence: 0.90 },
  { id: "rosacea",               name: "Rosacea",                confidence: 0.87 },
  { id: "seborrheic_dermatitis", name: "Seborrheic Dermatitis",  confidence: 0.85 },
  { id: "ringworm",              name: "Ringworm",               confidence: 0.89 },
  { id: "scabies",               name: "Scabies",                confidence: 0.86 },
  { id: "melasma",               name: "Melasma",                confidence: 0.88 },
  { id: "folliculitis",          name: "Folliculitis",           confidence: 0.85 },
  { id: "warts",                 name: "Warts",                  confidence: 0.87 },
  { id: "alopecia",              name: "Alopecia",               confidence: 0.84 },
  { id: "hyperpigmentation",     name: "Hyperpigmentation",      confidence: 0.86 },
  { id: "cellulitis",            name: "Cellulitis",             confidence: 0.88 },
  { id: "ichthyosis",            name: "Ichthyosis",             confidence: 0.85 },
  { id: "chickenpox",            name: "Chickenpox",             confidence: 0.92 },
  { id: "lichen_planus",         name: "Lichen Planus",          confidence: 0.86 },
  { id: "impetigo",              name: "Impetigo",               confidence: 0.88 },
  { id: "tinea_versicolor",      name: "Tinea Versicolor",       confidence: 0.87 },
  { id: "keratosis_pilaris",     name: "Keratosis Pilaris",      confidence: 0.85 },
  { id: "pityriasis_rosea",      name: "Pityriasis Rosea",       confidence: 0.84 },
  { id: "perioral_dermatitis",   name: "Perioral Dermatitis",    confidence: 0.86 },
  { id: "neurodermatitis",       name: "Neurodermatitis",        confidence: 0.85 },
  { id: "miliaria",              name: "Miliaria (Heat Rash)",   confidence: 0.89 },
  { id: "erythema_multiforme",   name: "Erythema Multiforme",    confidence: 0.83 },
  { id: "pompholyx",             name: "Pompholyx",              confidence: 0.87 },
  { id: "melanoma",              name: "Melanoma (safety test)", confidence: 0.82 },
]

// Dosha config — colour used for slider fill gradient and pills
const DOSHA_CFG = {
  vata:  { color: "#3b82f6", dim: "#eff6ff", label: "Vata",  cls: "vata-slider"  },
  pitta: { color: "#f97316", dim: "#fff7ed", label: "Pitta", cls: "pitta-slider" },
  kapha: { color: "#10b981", dim: "#ecfdf5", label: "Kapha", cls: "kapha-slider" },
}

// Builds the coloured fill gradient for the slider track
// The JS inline style overrides the CSS background so the filled
// portion shows the dosha colour and the rest shows the border colour
const sliderTrack = (color, pct) =>
  `linear-gradient(to right, ${color} 0%, ${color} ${pct}%, #e2e8f0 ${pct}%)`

const STEPS = ["Test Inputs", "Dual Explanations", "Personalized Explanation"]

// ─────────────────────────────────────────────────────────────────────────────
// AppHeader
// Top bar with logo mark and dual-identity badges
// ─────────────────────────────────────────────────────────────────────────────

function AppHeader() {
  return (
    <div style={{
      background: "white",
      borderBottom: "1.5px solid var(--border)",
      padding: "14px 28px",
      display: "flex",
      alignItems: "center",
      gap: 14,
    }}>

      {/* Logo — two overlapping circles representing dual medicine */}
      <div style={{ position: "relative", width: 36, height: 36, flexShrink: 0 }}>
        <div style={{
          position: "absolute", top: 0, left: 0,
          width: 24, height: 24, borderRadius: "50%",
          background: "var(--primary-light)",
          border: "1.5px solid var(--primary-border)",
        }} />
        <div style={{
          position: "absolute", bottom: 0, right: 0,
          width: 24, height: 24, borderRadius: "50%",
          background: "var(--amber-light)",
          border: "1.5px solid var(--amber-border)",
        }} />
      </div>

      {/* Title */}
      <div>
        <h1 style={{
          margin: 0, fontSize: 16, fontWeight: 700,
          color: "var(--text-1)", letterSpacing: "-0.02em",
        }}>
          Novelty 3
          <span style={{ color: "var(--text-3)", fontWeight: 400, marginLeft: 8, fontSize: 15 }}>
            — Dual Perspective Skin Disease Explanation
          </span>
        </h1>
        <p style={{ margin: "2px 0 0", fontSize: 12, color: "var(--text-3)" }}>
          Explainable AI · Western dermatology + Ayurvedic medicine
        </p>
      </div>

      {/* Identity badges */}
      <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
        <span style={{
          padding: "4px 12px", borderRadius: 20,
          background: "var(--primary-light)",
          border: "1px solid var(--primary-border)",
          color: "var(--primary)",
          fontSize: 11, fontWeight: 600,
        }}>Western</span>
        <span style={{
          padding: "4px 12px", borderRadius: 20,
          background: "var(--amber-light)",
          border: "1px solid var(--amber-border)",
          color: "var(--amber)",
          fontSize: 11, fontWeight: 600,
        }}>Ayurvedic</span>
      </div>

    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// ProgressBar
// 3-step stepper. Active = blue filled. Done = green with tick. Future = gray.
// ─────────────────────────────────────────────────────────────────────────────

function ProgressBar({ page }) {
  return (
    <div style={{
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "center",
      padding: "20px 24px 14px",
      background: "white",
      borderBottom: "1.5px solid var(--border)",
    }}>
      {STEPS.map((label, i) => {
        const num    = i + 1
        const active = page === num
        const done   = page > num

        return (
          <div key={i} style={{ display: "flex", alignItems: "flex-start" }}>

            {/* Circle + label */}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
              <div style={{
                width: 36, height: 36,
                borderRadius: "50%",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 14, fontWeight: 600,
                border: "2px solid",
                transition: "all 0.3s",
                ...(done ? {
                  background: "var(--green-light)",
                  borderColor: "var(--green)",
                  color: "var(--green)",
                } : active ? {
                  background: "var(--primary)",
                  borderColor: "var(--primary)",
                  color: "white",
                  boxShadow: "0 0 0 4px var(--primary-light)",
                } : {
                  background: "white",
                  borderColor: "var(--border)",
                  color: "var(--text-3)",
                }),
              }}>
                {done ? (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : num}
              </div>

              <span style={{
                fontSize: 11, fontWeight: 500, whiteSpace: "nowrap",
                color: active ? "var(--primary)" : done ? "var(--green)" : "var(--text-3)",
              }}>
                {label}
              </span>
            </div>

            {/* Connector line */}
            {i < STEPS.length - 1 && (
              <div style={{
                width: 80, height: 2,
                marginTop: 17, marginLeft: 6, marginRight: 6,
                borderRadius: 1, flexShrink: 0,
                background: done ? "var(--green-border)" : "var(--border)",
                transition: "background 0.4s",
              }} />
            )}

          </div>
        )
      })}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// ContextChips
// Summary chips shown on pages 2 and 3 — disease, age, dominant dosha
// ─────────────────────────────────────────────────────────────────────────────

function ContextChips({ selectedDisease, prakriti, userContext }) {
  // Find dominant dosha by highest score
  const dominant = Object.entries(prakriti).sort((a, b) => b[1] - a[1])[0][0]
  const cfg       = DOSHA_CFG[dominant]

  const chips = [
    { label: selectedDisease.name,     bg: "var(--primary-light)",  color: "var(--primary)",  border: "var(--primary-border)"  },
    { label: userContext.age_group,     bg: "#f8fafc",               color: "var(--text-2)",   border: "var(--border)"           },
    { label: `${cfg.label} dominant`,  bg: cfg.dim,                 color: cfg.color,          border: `${cfg.color}40`          },
    ...(userContext.pregnancy_status
      ? [{ label: "Pregnant", bg: "var(--amber-light)", color: "var(--amber)", border: "var(--amber-border)" }]
      : []),
  ]

  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
      {chips.map((c, i) => (
        <span key={i} style={{
          padding: "5px 13px", borderRadius: 20,
          fontSize: 12, fontWeight: 500,
          background: c.bg, color: c.color,
          border: `1px solid ${c.border}`,
        }}>
          {c.label}
        </span>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// NavBar
// Back button on left, optional right slot (next button or label)
// ─────────────────────────────────────────────────────────────────────────────

function NavBar({ onBack, backLabel, rightSlot }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      marginBottom: 16,
    }}>
      <button className="btn-ghost" onClick={onBack}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        {backLabel}
      </button>
      {rightSlot}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// CardLoader
// Loading state that matches the card style
// ─────────────────────────────────────────────────────────────────────────────

function CardLoader({ message = "Generating explanation…" }) {
  return (
    <div className="app-card" style={{
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      padding: "60px 24px", gap: 14,
    }}>
      <div style={{
        width: 40, height: 40,
        border: "3px solid var(--border)",
        borderTop: "3px solid var(--primary)",
        borderRadius: "50%",
        animation: "spin 0.75s linear infinite",
      }} />
      <p style={{ margin: 0, fontSize: 14, color: "var(--text-2)" }}>{message}</p>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// CardError
// Error state displayed inside a card
// ─────────────────────────────────────────────────────────────────────────────

function CardError({ message }) {
  return (
    <div className="app-card" style={{
      padding: "20px 24px",
      borderColor: "#fecaca",
      background: "var(--red-light)",
    }}>
      <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
          stroke="var(--red)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"
          style={{ flexShrink: 0, marginTop: 1 }}>
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <div>
          <p style={{ margin: 0, fontSize: 14, color: "var(--red)", fontWeight: 500 }}>
            {message}
          </p>
          <p style={{ margin: "6px 0 0", fontSize: 12, color: "var(--text-3)", fontFamily: "monospace" }}>
            uvicorn app.main:app --reload --port 8000
          </p>
        </div>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// InputPage  (Page 1)
// ─────────────────────────────────────────────────────────────────────────────

function InputPage({
  selectedDisease, setSelectedDisease,
  prakriti, setPrakriti,
  userContext, setUserContext,
  onGenerate, loading,
}) {
  return (
    <div className="page-enter">
      <div className="app-card" style={{ padding: "28px 28px 24px" }}>

        {/* Card header */}
        <h2 style={{ margin: "0 0 4px", fontSize: 17, fontWeight: 600, color: "var(--text-1)" }}>
          Test inputs
        </h2>
        <p style={{ margin: "0 0 20px", fontSize: 13, color: "var(--text-3)" }}>
          In the real system these come from Novelty 1 and 2
        </p>

        <div className="section-divider" />

        {/* ── Disease + Age group ─────────────────────────────────────── */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>

          <div>
            <label className="field-label">Disease — from Novelty 2</label>
            <select
              value={selectedDisease.id}
              onChange={(e) =>
                setSelectedDisease(DISEASES.find(d => d.id === e.target.value))
              }
            >
              {DISEASES.map(d => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
            {/* Confidence indicator */}
            <div style={{ marginTop: 7, display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{
                width: 7, height: 7, borderRadius: "50%",
                background: selectedDisease.confidence >= 0.9
                  ? "var(--green)" : "var(--amber)",
                flexShrink: 0,
              }} />
              <span style={{ fontSize: 11, color: "var(--text-3)" }}>
                Model confidence: {Math.round(selectedDisease.confidence * 100)}%
              </span>
            </div>
          </div>

          <div>
            <label className="field-label">Age group — user context</label>
            <select
              value={userContext.age_group}
              onChange={(e) =>
                setUserContext(prev => ({ ...prev, age_group: e.target.value }))
              }
            >
              <option value="child">Child</option>
              <option value="teenager">Teenager</option>
              <option value="adult">Adult</option>
              <option value="elderly">Elderly</option>
            </select>
          </div>

        </div>

        {/* ── Prakriti sliders ──────────────────────────────────────────── */}
        <label className="field-label">Prakriti scores — from Novelty 1</label>
        <p style={{ margin: "-4px 0 16px", fontSize: 12, color: "var(--text-3)" }}>
          Adjust to see personalization change
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 20, marginBottom: 24 }}>
          {Object.entries(DOSHA_CFG).map(([dosha, cfg]) => {
            const pct = Math.round(prakriti[dosha] * 100)
            return (
              <div key={dosha}>

                {/* Dosha name + percentage pill */}
                <div style={{
                  display: "flex", justifyContent: "space-between",
                  alignItems: "center", marginBottom: 9,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{
                      width: 9, height: 9, borderRadius: "50%",
                      background: cfg.color, flexShrink: 0,
                    }} />
                    <span style={{ fontSize: 13, fontWeight: 500, color: "var(--text-1)" }}>
                      {cfg.label}
                    </span>
                  </div>
                  <span style={{
                    fontSize: 12, fontWeight: 600,
                    color: cfg.color,
                    background: cfg.dim,
                    border: `1px solid ${cfg.color}35`,
                    padding: "2px 10px",
                    borderRadius: 20,
                    minWidth: 46,
                    textAlign: "center",
                  }}>
                    {pct}%
                  </span>
                </div>

                {/* Slider — inline background gradient creates the fill effect */}
                <input
                  type="range"
                  min="0" max="100"
                  value={pct}
                  className={cfg.cls}
                  style={{ background: sliderTrack(cfg.color, pct) }}
                  onChange={(e) => setPrakriti(prev => ({
                    ...prev,
                    [dosha]: parseInt(e.target.value) / 100,
                  }))}
                />

              </div>
            )
          })}
        </div>

        {/* ── Pregnancy toggle ──────────────────────────────────────────── */}
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          background: "#f8fafc",
          border: "1.5px solid var(--border)",
          borderRadius: 12,
          padding: "12px 16px",
          marginBottom: 24,
        }}>
          <div>
            <p style={{ margin: 0, fontSize: 14, fontWeight: 500, color: "var(--text-1)" }}>
              Pregnancy status
            </p>
            <p style={{ margin: "2px 0 0", fontSize: 12, color: "var(--text-3)" }}>
              Modifies Ayurvedic advice and herb recommendations
            </p>
          </div>
          <label className="toggle">
            <input
              type="checkbox"
              checked={userContext.pregnancy_status}
              onChange={(e) =>
                setUserContext(prev => ({ ...prev, pregnancy_status: e.target.checked }))
              }
            />
            <span className="toggle-track" />
          </label>
        </div>

        {/* ── Generate button ───────────────────────────────────────────── */}
        <button className="btn-generate" onClick={onGenerate} disabled={loading}>
          {loading ? "Generating explanation…" : "Generate Explanation →"}
        </button>

      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// ExplanationPage  (Page 2)
// Shows Western + Ayurvedic explanation panels
// ─────────────────────────────────────────────────────────────────────────────

function ExplanationPage({
  data, prakriti, loading, error,
  selectedDisease, userContext,
  onBack, onNext,
}) {
  const nextBtn = (
    <button
      className="btn-next"
      onClick={onNext}
      disabled={loading || !data || data?.type === "safety_referral"}
    >
      View Personalized Explanation
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
        <polyline points="9 18 15 12 9 6" />
      </svg>
    </button>
  )

  return (
    <div className="page-enter">
      <NavBar onBack={onBack} backLabel="Back to inputs" rightSlot={nextBtn} />
      <ContextChips selectedDisease={selectedDisease} prakriti={prakriti} userContext={userContext} />

      {loading && <CardLoader />}
      {!loading && error && <CardError message={error} />}

      {/* Safety referral — no page 3 for dangerous diseases */}
      {!loading && !error && data?.type === "safety_referral" && (
        <div className="app-card" style={{ overflow: "hidden" }}>
          <SafetyReferral safety={data.safety} diseaseId={data.disease_id} />
          <div style={{ padding: "0 16px 16px" }}><Disclaimer /></div>
        </div>
      )}

      {/* Normal dual explanation */}
      {!loading && !error && data && data?.type !== "safety_referral" && (
        <div className="app-card" style={{ overflow: "hidden" }}>

          {/* Section accent bar */}
          <div style={{
            height: 3,
            background: "linear-gradient(to right, var(--primary), var(--amber))",
          }} />

          <DiseaseHeader
            diseaseName={data?.disease_name}
            confidence={data?.confidence}
            explanationLevel={data?.explanation_level}
            category={data?.category}
            diseaseId={data?.disease_id}
          />

          <PrakritiPills prakriti={prakriti} />

          {/* Western | Ayurvedic two-column */}
          <div className="grid grid-cols-1 md:grid-cols-2">
            <WesternPanel western={data?.western} />
            <AyurvedicPanel ayurvedic={data?.ayurvedic} />
          </div>

        </div>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// RPersonalizedExplanationPage (Page 3)
// Shows PersonalizedBox, ReasoningPanel, Disclaimer
// ─────────────────────────────────────────────────────────────────────────────

function PersonalizedExplanationPage({
  data, loading, error,
  selectedDisease, prakriti, userContext,
  onBack,
}) {
  return (
    <div className="page-enter">
      <NavBar
        onBack={onBack}
        backLabel="Back to explanations"
        rightSlot={
          <span style={{ fontSize: 12, color: "var(--text-3)" }}>
            Personalized Explanation
          </span>
        }
      />
      <ContextChips selectedDisease={selectedDisease} prakriti={prakriti} userContext={userContext} />

      {loading && <CardLoader message="Loading recommendations…" />}
      {!loading && error && <CardError message={error} />}

      {!loading && !error && data && (
        <div className="app-card" style={{ overflow: "hidden" }}>

          {/* Section accent bar */}
          <div style={{
            height: 3,
            background: "linear-gradient(to right, var(--amber), var(--green))",
          }} />

          {/* Fuzzy engine personalized output */}
          <PersonalizedBox
            personalized={data?.personalized}
            prevention={data?.prevention}
            dominantDosha={data?.reasoning?.dominant_dosha}
          />

          {/* Reasoning panel — always visible, no collapse */}
          <ReasoningPanel reasoning={data?.reasoning} />

          <div style={{ padding: "0 16px 20px" }}>
            <Disclaimer />
          </div>

        </div>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// App — root component
// ─────────────────────────────────────────────────────────────────────────────

export default function App() {

  const [page, setPage] = useState(1)

  const [selectedDisease, setSelectedDisease] = useState(DISEASES[0])
  const [prakriti, setPrakriti]   = useState({ vata: 0.30, pitta: 0.60, kapha: 0.10 })
  const [userContext, setUserContext] = useState({
    age_group: "adult",
    pregnancy_status: false,
    known_allergies: [],
  })

  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  // Generate button — calls API then moves to page 2
  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    setData(null)
    setPage(2)

    try {
      const result = await getFullExplanation(
        selectedDisease.id,
        selectedDisease.confidence,
        prakriti,
        userContext,
      )
      setData(result)
    } catch (err) {
      setError(
        "Could not load explanation. " +
        "Make sure backend is running on http://localhost:8000"
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>

      <AppHeader />
      <ProgressBar page={page} />

      <div style={{ maxWidth: 860, margin: "0 auto", padding: "24px 20px 60px" }}>

        {page === 1 && (
          <InputPage
            selectedDisease={selectedDisease}
            setSelectedDisease={setSelectedDisease}
            prakriti={prakriti}
            setPrakriti={setPrakriti}
            userContext={userContext}
            setUserContext={setUserContext}
            onGenerate={handleGenerate}
            loading={loading}
          />
        )}

        {page === 2 && (
          <ExplanationPage
            data={data}
            prakriti={prakriti}
            loading={loading}
            error={error}
            selectedDisease={selectedDisease}
            userContext={userContext}
            onBack={() => setPage(1)}
            onNext={() => setPage(3)}
          />
        )}

        {page === 3 && (
          <PersonalizedExplanationPage
            data={data}
            loading={loading}
            error={error}
            selectedDisease={selectedDisease}
            prakriti={prakriti}
            userContext={userContext}
            onBack={() => setPage(2)}
          />
        )}

      </div>
    </div>
  )
}