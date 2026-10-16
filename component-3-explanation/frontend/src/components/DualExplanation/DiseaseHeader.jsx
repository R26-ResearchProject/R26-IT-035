export default function DiseaseHeader({
  diseaseName,
  explanationLevel,
  category,
  diseaseId
}) {

  const levelLabel = {
    validated: "Validated dataset",
    category: "Category level",
    general: "General"
  }

  return (
    <div className="p-4 border-b border-gray-100">

      {/* Top row: disease name and badges */}
      <div className="flex items-center justify-between flex-wrap gap-2">

        {/* Left: disease name and subtitle */}
        <div>
          <h2 className="text-base font-medium text-gray-900">
            {diseaseName}
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Skin condition identified by AI
          </p>
        </div>

        {/* Right: explanation level badge only */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-medium px-2 py-1 rounded-full bg-purple-100 text-purple-800">
            {levelLabel[explanationLevel] || "AI identified"}
          </span>
        </div>

      </div>

      {/* Bottom row: category badge */}
      {category && (
        <div className="mt-2">
          <span className="text-xs font-medium px-2 py-1 rounded-full bg-gray-100 text-gray-600">
            Category: {category.replace(/_/g, " ")}
          </span>
        </div>
      )}

    </div>
  )
}