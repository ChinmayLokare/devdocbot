// src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';
import './App.css';
import AddDocument from './components/AddDocument';

function App() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchMetadata, setSearchMetadata] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (query) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/search`,
        {
          query: query,
          top_k: 5
        }
      );

      setResults(response.data.results || []);
      setSearchMetadata({
        query: response.data.query,
        count: response.data.count,
        executionTime: response.data.execution_time_ms,
        cacheHit: response.data.cache_hit
      });

    } catch (err) {
      setError(
        err.response?.data?.error ||
        'Failed to search. Please try again.'
      );
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <Header />

      <main className="main-content">
        <AddDocument />
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {searchMetadata && (
          <div className="search-metadata">
            <span>Found {searchMetadata.count} results</span>
            <span>•</span>
            <span>{searchMetadata.executionTime}ms</span>
            {searchMetadata.cacheHit && (
              <>
                <span>•</span>
                <span className="cache-indicator">⚡ Cached</span>
              </>
            )}
          </div>
        )}

        <div className="results-container">
          {results.length > 0 ? (
            results.map((result, index) => (
              <ResultCard
                key={result.id || index}
                result={result}
                index={index}
              />
            ))
          ) : (
            hasSearched && !isLoading && (
              <div className="no-results">
                <p>No results found. Try a different search term.</p>
              </div>
            )
          )}
        </div>

        {!hasSearched && !isLoading && (
          <div className="welcome-message">
            <h2>Welcome to DevDocBot! 👋</h2>
            <p>Search across technical documentation using natural language.</p>
            <ul className="features-list">
              <li>🎯 Semantic search - finds relevant docs even with different wording</li>
              <li>⚡ Lightning fast - sub-100ms response times</li>
              <li>🤖 AI-powered - uses sentence transformers for embeddings</li>
              <li>📚 70+ documents indexed from GitHub repositories</li>
            </ul>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>
          Built with React, AWS Lambda, Pinecone, and Hugging Face •
          <a
            href="https://github.com/ChinmayLokare/devdocbot"
            target="_blank"
            rel="noopener noreferrer"
          >
            {' '}View on GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;