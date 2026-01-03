// src/components/Header.js
import React from 'react';

function Header() {
    return (
        <header className="header">
            <div className="header-content">
                <h1>🔍 DevDocBot</h1>
                <p className="subtitle">Intelligent Documentation Search</p>
                <p className="description">
                    Semantic search powered by AI. Try searching for "kubernetes deployment" or "docker best practices"
                </p>
            </div>
        </header>
    );
}

export default Header;