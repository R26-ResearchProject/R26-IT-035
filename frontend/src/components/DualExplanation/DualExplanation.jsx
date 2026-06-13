// DualExplanation.jsx
// Main container component for the explanation UI.
// Handles:
// - Fetching data from the backend API
// - Loading state while waiting for response
// - Error state if backend is not running
// - Safety referral display for dangerous diseases
// - Full dual explanation display for normal diseases
//
// This component ties together all other components.
// It is the only component that calls the API directly.

import { useState, useEffect } from "react"
import { getFullExplanation } from "../../services/explanationService"
import DiseaseHeader from "./DiseaseHeader"
import PrakritiPills from "./PrakritiPills"
import WesternPanel from "./WesternPanel"
import AyurvedicPanel from "./AyurvedicPanel"
import PersonalizedBox from "./PersonalizedBox"
import ReasoningPanel from "./ReasoningPanel"
import SafetyReferral from "../SafetyReferral/SafetyReferral"
import LoadingSpinner from "../common/LoadingSpinner"
import Disclaimer from "../common/Disclaimer"

export default function DualExplanation({
  diseaseId,
  confidence,
  prakriti,
  userContext
}) {

  // State for API response data
  const [data, setData] = useState(null)

  // State for loading indicator
  const [loading, setLoading] = useState(true)

  // State for error message
  const [error, setError] = useState(null)

  // Fetch explanation whenever inputs change
  // Runs when disease, prakriti, or context changes
  useEffect(() => {
    async function fetchExplanation() {
      try {
        setLoading(true)
        setError(null)

        // Call backend API via explanationService
        const result = await getFullExplanation(
          diseaseId,
          confidence,
          prakriti,
          userContext
        )

        // Store successful response
        setData(result)

      } catch (err) {
        // Show error if API call fails
        setError(
          "Could not load explanation. " +
          "Make sure backend is running on http://localhost:8000"
        )
      } finally {
        // Always stop loading when done
        setLoading(false)
      }
    }

    fetchExplanation()
  }, [diseaseId, prakriti, userContext])

  // CASE 1: Show loading spinner while waiting
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200">
        <LoadingSpinner />
      </div>
    )
  }

  // CASE 2: Show error if backend not reachable
  if (error) {
    return (
      <div className="bg-white rounded-xl border border-red-200 p-4">
        <p className="text-sm text-red-600">{error}</p>
        <p className="text-xs text-gray-400 mt-1">
          Run: uvicorn app.main:app --reload --port 8000
        </p>
      </div>
    )
  }

  // CASE 3: Show safety referral for dangerous diseases
  // No explanation shown — only referral message
  if (data?.type === "safety_referral") {
    return (
      <div>
        <SafetyReferral
          safety={data.safety}
          diseaseId={data.disease_id}
        />
        <Disclaimer />
      </div>
    )
  }

  // CASE 4: Show full dual explanation
  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">

      {/* Disease name and confidence */}
        <DiseaseHeader
        diseaseName={data?.disease_name}
        confidence={data?.confidence}
        explanationLevel={data?.explanation_level}
        category={data?.category}
        diseaseId={data?.disease_id}
        />

      {/* Prakriti percentage pills from Novelty 1 */}
      <PrakritiPills prakriti={prakriti} />

      {/* Two column layout: Western left, Ayurvedic right */}
      <div className="grid grid-cols-1 md:grid-cols-2">
        <WesternPanel western={data?.western} />
        <AyurvedicPanel ayurvedic={data?.ayurvedic} />
      </div>

      {/* Personalized box — core fuzzy engine output */}
      {/* Color changes based on dominant dosha */}
      <PersonalizedBox
        personalized={data?.personalized}
        prevention={data?.prevention}
        dominantDosha={data?.reasoning?.dominant_dosha}
      />

      {/* Reasoning panel — expandable explainability */}
      <ReasoningPanel reasoning={data?.reasoning} />

      {/* Medical disclaimer at bottom */}
      <div className="px-4 pb-4">
        <Disclaimer />
      </div>

    </div>
  )
}