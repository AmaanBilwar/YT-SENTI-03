import React, { useState } from 'react';

function App() {
    const [url, setUrl] = useState('');
    const [transcription, setTranscription] = useState('');
    const [summary, setSummary] = useState('');
    const [error, setError] = useState('');
    const [sentiment, setSentiment] = useState('');
    const [sentimentScore, setSentimentScore] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await fetch('http://localhost:4000/transcribe-and-summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (response.ok) {
                setTranscription(data.transcription);
                setSummary(data.summary);
                setSentiment(data.sentiment);
                setSentimentScore(data.sentiment_score);
            } else {
                setError(data.error || 'An error occurred while processing your request.');
            }
        } catch (error) {
            setError('An error occurred while processing your request.');
        }
    };

    return (
        <div className="container">
            <h1>YouTube Transcription and Summarization</h1>
            <form onSubmit={handleSubmit}>
                <label>
                    YouTube URL:
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        required
                    />
                </label>
                <button type="submit">Submit</button>
            </form>
            {error && <div className="error">{error}</div>}
            {transcription && (
                <div className="result">
                    <h2>Transcription</h2>
                    <p>{transcription}</p>
                </div>
            )}
            {summary && (
                <div className="result">
                    <h2>Summary</h2>
                    <p>{summary}</p>
                </div>
            )}
            {sentiment && (
    <div className="result">
        <h2>Sentiment Analysis</h2>
        <p>Sentiment: {sentiment}</p>
        <p>Sentiment Score: {sentimentScore}</p>
    </div>
)}

        </div>
    );
}

export default App;
