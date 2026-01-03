// src/components/ResultCard.js
import React from 'react';

function ResultCard({ result, index }) {
    const getScoreColor = (score) => {
        if (score >= 0.8) return '#10b981'; // green
        if (score >= 0.6) return '#f59e0b'; // yellow
        return '#ef4444'; // red
    };

    const getScoreLabel = (score) => {
        if (score >= 0.8) return 'Excellent Match';
        if (score >= 0.6) return 'Good Match';
        return 'Weak Match';
    };

    return (
        <div className="result-card">
            <div className="result-header">
                <span className="result-rank">#{index + 1}</span>
                <div className="result-score">
                    <span
                        className="score-badge"
                        style={{ backgroundColor: getScoreColor(result.score) }}
                    >
                        {(result.score * 100).toFixed(0)}% {getScoreLabel(result.score)}
                    </span>
                </div>
            </div>

            <h3 className="result-title">
                {result.metadata?.title || result.id}
            </h3>

            <p className="result-text">
                {result.text.length > 300
                    ? result.text.substring(0, 300) + '...'
                    : result.text
                }
            </p>

            <div className="result-metadata">
                {result.metadata?.source && (
                    <span className="metadata-tag">
                        📂 {result.metadata.source}
                    </span>
                )}
                {result.metadata?.url && (
                    <a
                        href={result.metadata.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="result-link"
                    >
                        🔗 View Source
                    </a>
                )}
            </div>
        </div>
    );
}

export default ResultCard;