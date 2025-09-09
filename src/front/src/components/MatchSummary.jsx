import React from 'react'

const MatchSummary = ({ matchResult }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981' // green
    if (score >= 60) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match'
    if (score >= 60) return 'Good Match'
    if (score >= 40) return 'Fair Match'
    return 'Poor Match'
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Match Results</h3>
      </div>
      
      <div className="mb-3">
        <div className="flex items-center gap-2 mb-2">
          <div 
            className="w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl"
            style={{ backgroundColor: getScoreColor(matchResult.score) }}
          >
            {matchResult.score}
          </div>
          <div>
            <h4 className="text-lg font-semibold">
              {getScoreLabel(matchResult.score)}
            </h4>
            <p className="text-sm text-gray-600">
              Overall Match Score: {matchResult.score}/100
            </p>
          </div>
        </div>
      </div>
      
      {matchResult.missing_keywords && matchResult.missing_keywords.length > 0 && (
        <div className="mb-3">
          <h4 className="font-semibold mb-2">Missing Keywords:</h4>
          <div className="flex flex-wrap gap-1">
            {matchResult.missing_keywords.map((keyword, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-red-100 text-red-800 text-sm rounded"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {matchResult.suggestions && matchResult.suggestions.length > 0 && (
        <div className="mb-3">
          <h4 className="font-semibold mb-2">Suggestions:</h4>
          <ul className="list-disc list-inside space-y-1">
            {matchResult.suggestions.map((suggestion, index) => (
              <li key={index} className="text-sm text-gray-700">
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      <div className="text-sm text-gray-500">
        Generated: {new Date(matchResult.created_at).toLocaleString()}
      </div>
    </div>
  )
}

export default MatchSummary
