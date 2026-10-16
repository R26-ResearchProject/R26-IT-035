// ReasoningPanel.jsx
// Explainability layer of Novelty 3.
// Shows HOW the system made its decisions.
// Hidden by default — user clicks to expand.
//
// Shows:
// - Fuzzy emphasis scores as visual bars
// - Dominant dosha interpretation
// - Source used for Western explanation
//
// This is the transparency feature that makes
// your system trustworthy and explainable

import { useState } from "react"

export default function ReasoningPanel({ reasoning }) {

  // Toggle state for showing/hiding reasoning
  const [show, setShow] = useState(true)

  // Do not render if no reasoning data
  if (!reasoning) return null

  // Bar colors for each dosha in the fuzzy score chart
  const barColors = {
    pitta: "bg-amber-400",
    vata: "bg-purple-400",
    kapha: "bg-teal-400"
  }

  return (
    <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">

      {/* Toggle button to show/hide reasoning */}
      <button
        onClick={() => setShow(!show)}
        className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
      >
      
      </button>

      {/* Reasoning content — only shown when expanded */}
      {show && (
        <div className="mt-3 space-y-3">

          {/* Fuzzy scores as horizontal bar chart */}
          {/* Each bar shows how much that dosha influences explanation */}
          <div>
            <p className="text-xs font-medium text-gray-600 mb-2">
              Fuzzy emphasis scores (disease × Prakriti)
            </p>
            {Object.entries(reasoning.fuzzy_scores || {}).map(
              ([dosha, score]) => (
                <div key={dosha} className="flex items-center gap-2 mb-1">
                  {/* Dosha name label */}
                  <span className="text-xs text-gray-500 w-12 capitalize">
                    {dosha}
                  </span>
                  {/* Progress bar background */}
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    {/* Colored fill based on score */}
                    <div
                      className={`h-2 rounded-full ${barColors[dosha] || "bg-gray-400"}`}
                      style={{ width: `${(score * 100).toFixed(1)}%` }}
                    />
                  </div>
                  {/* Percentage label */}
                  <span className="text-xs text-gray-600 w-12 text-right">
                    {(score * 100).toFixed(1)}%
                  </span>
                </div>
              )
            )}
          </div>

          {/* Interpretation text */}
          {/* Human readable explanation of fuzzy scores */}
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">
              Interpretation
            </p>
            <p className="text-xs text-gray-500">
              {reasoning.emphasis_interpretation}
            </p>
          </div>

          {/* Source information */}
          {/* Shows where Western explanation came from */}
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">
              Western explanation source
            </p>
            <p className="text-xs text-gray-500">
              {reasoning.western_source} —{" "}
              {reasoning.western_quality} quality
            </p>
          </div>

        </div>
      )}

    </div>
  )
}