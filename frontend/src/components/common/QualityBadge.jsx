// QualityBadge.jsx
// Shows the quality level of the explanation source
// high   = from your validated dataset (green badge)
// medium = from MedlinePlus or Wikipedia (blue badge)
// low    = fallback message (gray badge)

export default function QualityBadge({ quality }) {

  // Badge background and text colors per quality level
  const styles = {
    high: "bg-green-100 text-green-800 border border-green-200",
    medium: "bg-blue-100 text-blue-800 border border-blue-200",
    low: "bg-gray-100 text-gray-600 border border-gray-200"
  }

  // Human readable labels per quality level
  const labels = {
    high: "Validated source",
    medium: "Medical reference",
    low: "Limited info"
  }

  return (
    <span className={`
      text-xs font-medium px-2 py-1 rounded-full
      ${styles[quality] || styles.low}
    `}>
      {labels[quality] || "Source"}
    </span>
  )
}