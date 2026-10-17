// SafetyReferral.jsx
// Shown INSTEAD of dual explanation for dangerous diseases.
// Completely replaces Western and Ayurvedic panels.
// Three danger levels with different colors:
// critical    = red (cancer, melanoma)
// urgent      = orange (severe conditions)
// supervision = yellow (complex conditions)
//
// No explanation is ever shown for dangerous diseases.
// Only the referral message and action steps.

export default function SafetyReferral({ safety, diseaseId }) {

  // Color styles based on danger level
  const styles = {
    critical: {
      bg: "bg-red-50 border-red-300",
      header: "bg-red-100",
      title: "text-red-800",
      text: "text-red-700"
    },
    urgent: {
      bg: "bg-orange-50 border-orange-300",
      header: "bg-orange-100",
      title: "text-orange-800",
      text: "text-orange-700"
    },
    supervision: {
      bg: "bg-yellow-50 border-yellow-300",
      header: "bg-yellow-100",
      title: "text-yellow-800",
      text: "text-yellow-700"
    }
  }

  // Use critical as default if level not recognized
  const s = styles[safety?.level] || styles.critical

  return (
    <div className={`rounded-xl border ${s.bg} overflow-hidden`}>

      {/* Header with danger level title */}
      <div className={`p-4 ${s.header}`}>
        {/* Danger title e.g. "Immediate Medical Attention Required" */}
        <p className={`text-sm font-medium ${s.title}`}>
          {safety?.title}
        </p>
        {/* Disease name that triggered the safety block */}
        <p className={`text-xs ${s.text} mt-1`}>
          {diseaseId?.replace(/_/g, " ")} identified
        </p>
      </div>

      {/* Content section with message and action */}
      <div className="p-4 space-y-3">

        {/* Main safety message */}
        <p className={`text-sm ${s.text}`}>
          {safety?.message}
        </p>

        {/* Action box with what user must do */}
        <div className={`p-3 rounded-lg border ${s.bg}`}>
          <p className={`text-xs font-medium ${s.title} mb-1`}>
            What you must do:
          </p>
          <p className={`text-xs ${s.text}`}>
            {safety?.action}
          </p>
        </div>

        {/* Notice that no explanation is provided */}
        <p className={`text-xs ${s.text} opacity-70`}>
          This system does not provide explanations
          for serious medical conditions.
          Early medical intervention is critical.
        </p>

      </div>
    </div>
  )
}