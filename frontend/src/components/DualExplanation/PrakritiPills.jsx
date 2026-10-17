// PrakritiPills.jsx
// Shows the user Prakriti percentages as colored pills
// Values come from Novelty 1 output
// Vata = purple, Pitta = amber, Kapha = teal
// These pills remind user that explanation is personalized

export default function PrakritiPills({ prakriti }) {

  // Color classes for each dosha type
  const colors = {
    vata: "bg-purple-100 text-purple-800",
    pitta: "bg-amber-100 text-amber-800",
    kapha: "bg-teal-100 text-teal-800"
  }

  return (
    <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">

      {/* Label explaining where these values come from */}
      <p className="text-xs text-gray-500 mb-2">
        Your Prakriti (body type) from Novelty 1:
      </p>

      {/* Row of colored pills one per dosha */}
      <div className="flex gap-2 flex-wrap">
        {Object.entries(prakriti).map(([dosha, score]) => (
          <span
            key={dosha}
            className={`
              text-xs font-medium px-3 py-1 rounded-full
              ${colors[dosha]}
            `}
          >
            {/* Capitalize first letter of dosha name */}
            {dosha.charAt(0).toUpperCase() + dosha.slice(1)}{" "}
            {/* Show percentage */}
            {Math.round(score * 100)}%
          </span>
        ))}
      </div>

    </div>
  )
}