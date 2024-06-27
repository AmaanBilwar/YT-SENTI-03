import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios'

function App() {
  
  const [url, setUrl] = useState('');
    const [transcription, setTranscription] = useState('');
    const [summary, setSummary] = useState('');
    const [error, setError] = useState('');

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
            } else {
                setError(data.error || 'An error occurred while processing your request.');
            }
        } catch (error) {
            setError('An error occurred while processing your request.');
        }
    };



  return (
    <>
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
            {error && <div style={{ color: 'red' }}>{error}</div>}
            {transcription && (
                <div>
                    <h2>Transcription</h2>
                    <p>{transcription}</p>
                </div>
            )}
            {summary && (
                <div>
                    <h2>Summary</h2>
                    <p>{summary}</p>
                </div>
            )}
    </>
  )
}

export default App
