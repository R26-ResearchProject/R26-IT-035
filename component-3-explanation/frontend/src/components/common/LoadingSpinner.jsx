// LoadingSpinner.jsx
// Shows a spinning animation while the API is loading
// Displayed inside DualExplanation while waiting for response

export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      {/* Spinning circle animation */}
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      {/* Loading message */}
      <p className="ml-4 text-gray-500 text-sm">
        Generating explanation...
      </p>
    </div>
  )
}