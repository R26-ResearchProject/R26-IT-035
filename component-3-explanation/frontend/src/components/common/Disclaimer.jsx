// Disclaimer.jsx
// Medical disclaimer shown at bottom of every explanation
// Required for all health AI applications
// Reminds user this is educational only

export default function Disclaimer() {
  return (
    <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
      <p className="text-xs text-gray-500 text-center">
        This system provides educational information only
        and does not replace professional medical advice.
        Always consult a qualified healthcare provider
        for diagnosis and treatment.
      </p>
    </div>
  )
}