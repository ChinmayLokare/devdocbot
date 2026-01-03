import React, { useState } from 'react';
import axios from 'axios';

function AddDocument({ onUploadSuccess }) {
    const [title, setTitle] = useState('');
    const [text, setText] = useState('');
    const [source, setSource] = useState('manual');
    const [status, setStatus] = useState('idle'); // idle, uploading, success, error

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!title || !text) return;

        setStatus('uploading');

        try {
            // Structure matches your Upload Lambda expectations
            const payload = {
                documents: [
                    {
                        title: title,
                        text: text,
                        source: source,
                        url: window.location.href // Or add a URL input field
                    }
                ]
            };

            await axios.post(
                `${process.env.REACT_APP_API_URL}/documents`,
                payload
            );

            setStatus('success');
            setTitle('');
            setText('');

            // Notify parent to maybe refresh or show notification
            if (onUploadSuccess) onUploadSuccess();

            // Reset success message after 3 seconds
            setTimeout(() => setStatus('idle'), 3000);

        } catch (error) {
            console.error("Upload failed", error);
            setStatus('error');
        }
    };

    return (
        <div className="add-doc-container">
            <h3>📝 Add New Documentation</h3>

            <form onSubmit={handleSubmit} className="add-doc-form">
                <div className="form-group">
                    <label>Title</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="e.g. How to Restart Server"
                        disabled={status === 'uploading'}
                    />
                </div>

                <div className="form-group">
                    <label>Content</label>
                    <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Paste documentation content here..."
                        rows={5}
                        disabled={status === 'uploading'}
                    />
                </div>

                <div className="form-row">
                    <select
                        value={source}
                        onChange={(e) => setSource(e.target.value)}
                        className="source-select"
                    >
                        <option value="manual">Manual Entry</option>
                        <option value="email">Email</option>
                        <option value="slack">Slack</option>
                    </select>

                    <button
                        type="submit"
                        className={`upload-btn ${status}`}
                        disabled={status === 'uploading' || !title || !text}
                    >
                        {status === 'uploading' ? 'Uploading...' :
                            status === 'success' ? '✅ Indexed!' :
                                status === 'error' ? '❌ Failed' :
                                    'Upload Document'}
                    </button>
                </div>
            </form>
        </div>
    );
}

export default AddDocument;