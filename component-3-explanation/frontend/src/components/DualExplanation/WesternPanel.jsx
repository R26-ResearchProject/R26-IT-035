// WesternPanel.jsx
// Left panel of the dual explanation.
// Shows Western medical explanation for the disease.
// Content comes from your validated dataset template
// or MedlinePlus/Wikipedia for unknown diseases.

import QualityBadge from "../common/QualityBadge"

export default function WesternPanel({ western }) {

  // Do not render if no western data
  if (!western) return null

  return (
    <div className="p-4 border-r border-gray-100">

      {/* Panel header with blue medical icon */}
      <div className="flex items-center gap-2 mb-3">
        <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
          {/* ECG/heartbeat icon representing medical */}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#1e40af" strokeWidth="2.5">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
        </div>
        <p className="text-sm font-medium text-blue-800">
          Western medical perspective
        </p>
      </div>

      {/* Main explanation text from dataset template */}
      <p className="text-sm text-gray-700 leading-relaxed mb-3">
        {western.explanation}
      </p>

      {/* Footer with quality badge and source name */}
      <div className="flex items-center justify-between flex-wrap gap-2 pt-3 border-t border-gray-100">

        {/* Quality badge shows validated/medium/low */}
        <QualityBadge quality={western.quality} />

        {/* Source name e.g. Validated Medical Knowledge Base */}
        <p className="text-xs text-blue-600">
          {western.source}
        </p>

      </div>
    </div>
  )
}