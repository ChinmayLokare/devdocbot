// src/components/SearchBar.js
import React, { useState } from 'react';

function SearchBar({ onSearch, isLoading }) {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query.trim());
        }
    };

    const exampleQueries = [
        "troubleshoot crashloopbackoff",
        "python logging standards",
        "python best practices",
        "Who works on the checkout API?",
        "How do I fetch a product by id?",
        "AWS lambda functions"


    ];

    return (
        <div className="search-container">
            <form onSubmit={handleSubmit} className="search-form">
                <input
                    type="text"
                    className="search-input"
                    placeholder="Search documentation... (e.g., 'how to deploy to kubernetes')"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    className="search-button"
                    disabled={isLoading || !query.trim()}
                >
                    {isLoading ? 'Searching...' : 'Search'}
                </button>
            </form>

            <div className="example-queries">
                <span className="example-label">Try: </span>
                {exampleQueries.map((example, idx) => (
                    <button
                        key={idx}
                        className="example-chip"
                        onClick={() => {
                            setQuery(example);
                            onSearch(example);
                        }}
                        disabled={isLoading}
                    >
                        {example}
                    </button>
                ))}
            </div>
        </div>
    );
}

export default SearchBar;