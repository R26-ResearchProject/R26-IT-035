// AyurvedicPanel.jsx
// Right panel of the dual explanation.
// Shows Ayurvedic explanation for the disease.
// Content generated from dataset using Ayurvedic template.
// Shows Sanskrit name with Western name in brackets
// so users unfamiliar with Ayurveda can still understand.

export default function AyurvedicPanel({ ayurvedic }) {

  // Do not render if no ayurvedic data
  if (!ayurvedic) return null

  // Badge colors for each dosha type
  const doshaColors = {
    pitta: "bg-orange-100 text-orange-800",
    vata: "bg-purple-100 text-purple-800",
    kapha: "bg-teal-100 text-teal-800"
  }

  return (
    <div className="p-4">

      {/* Panel header with Ayurvedic leaf icon */}
      <div className="flex items-center gap-2 mb-3">
        <div className="w-5 h-5 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
          {/* Leaf/nature icon representing Ayurveda */}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9a3412" strokeWidth="2.5">
            <path d="M12 2a7 7 0 0 0-7 7c0 3 2 5 3.5 6.5L12 19l3.5-3.5C17 14 19 12 19 9a7 7 0 0 0-7-7z"/>
            <circle cx="12" cy="9" r="2"/>
          </svg>
        </div>
        <p className="text-sm font-medium text-orange-800">
          Ayurvedic perspective
        </p>
      </div>

      {/* Sanskrit name section */}
      {/* Shows Sanskrit name + meaning for non-Ayurveda users */}
      <div className="mb-3">
        <p className="text-xs text-gray-500 mb-1">
          Ayurvedic name
        </p>
        {/* Sanskrit name in italics */}
        <p className="text-sm font-medium text-gray-800 italic">
          {ayurvedic.sanskrit_name}
        </p>
        {/* English meaning of Sanskrit name */}
        <p className="text-xs text-gray-500 mt-0.5">
          {ayurvedic.ayurveda_meaning}
        </p>
      </div>

      {/* Primary dosha imbalance badge */}
      {/* Shows which dosha is primarily affected */}
      <div className="mb-3">
        <p className="text-xs text-gray-500 mb-1">
          Primary dosha imbalance
        </p>
        <span className={`
          text-xs font-medium px-2 py-1 rounded-full
          ${doshaColors[ayurvedic.primary_dosha] || "bg-gray-100 text-gray-700"}
        `}>
          {ayurvedic.primary_dosha?.charAt(0).toUpperCase() +
           ayurvedic.primary_dosha?.slice(1)} dominant
        </span>
      </div>

      {/* Main Ayurvedic explanation text */}
      {/* Generated from Ayurvedic template in template_composer.py */}
      <p className="text-sm text-gray-700 leading-relaxed mb-3">
        {ayurvedic.explanation}
      </p>

      {/* Classical text reference at bottom */}
      {/* Shows which Ayurvedic text this is based on */}
      <div className="pt-3 border-t border-gray-100">
        <p className="text-xs text-gray-400 italic">
          {ayurvedic.classical_text}
        </p>
      </div>

    </div>
  )
}