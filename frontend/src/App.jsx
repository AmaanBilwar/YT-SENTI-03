import React, { useState } from 'react';
import {Line} from 'react-chartjs-2';
import { Box, CircularProgress, Slider, Typography } from '@mui/material';
import {Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip);

function App() {
    const [url, setUrl] = useState('');
    const [transcription, setTranscription] = useState('');
    const [summary, setSummary] = useState('');
    const [sentiment, setSentiment] = useState('');
    const [loading, setLoading] = useState(false);
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
                setSentiment(data.sentiment);
            } else {
                setError(data.error || 'An error occurred while processing your request.');
            }
        } catch (error) {
            setError('An error occurred while processing your request.');
        }
        setLoading(false)
    };

    return (
        <div className='flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4'>
            <Typography variant="h4" className='pb-12'>
            YouTube Transcription and Summarization
            </Typography>
            <div>
                <p className='pb-12'>
                    This app takes your Youtube video URL, transcribes the audio, and provides a summary and sentiment analysis of the transcription.
                </p>
                    
            </div>
            <form onSubmit={handleSubmit}>
                <label>
                    <Typography className='flex justify-center'>YouTube URL:</Typography>
                    <div className='flex justify-center p-4 w-screen'>
                    <input className='p-4 w-1/2'
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        required
                        placeholder='Enter a YouTube URL'
                    />
            </div>
                </label>
                <div className='flex justify-center'>
                    <button type="submit" className='rounded-md p-6 bg-blue-200 text-black hover:text-white hover:bg-blue-400'>
                    <Typography>Analyze</Typography></button>
                </div>
            </form>
            {error && <Typography color="error">{error}</Typography>}
            {sentiment && (
    <div className='w-full max-w-2xl mt-8 flex flex-col items-center'>
        <Typography  variant="h6">
            Sentiment Analysis
        </Typography>
            <Typography>
                Polarity: <span style={{color:getColor(sentiment.polarity)}}>{sentiment.polarity}</span>
            </Typography>
            <Box sx={{width: 300}}>
                <Slider 
                    value={sentiment.subjectivity}
                    min={-1}
                    max={1}
                    step={0.01}
                    marks={[
                        {value: -1, label: 'Negative'},
                        {value: 0, label: 'Neutral'},
                        {value: 1, label: 'Positive'}
                    ]}
                    disabled
                    track={false}
                    />
                    </Box>
                    <Typography>Subjectivity: <span style={{ color: getColor(sentiment.subjectivity) }}>{sentiment.subjectivity}</span></Typography>
                        <Box sx={{ width: 300 }}>
                            <Slider
                                value={sentiment.subjectivity}
                                min={0}
                                max={1}
                                step={0.01}
                                marks={[
                                    { value: 0, label: 'Objective' },
                                    { value: 1, label: 'Subject'},
                                ]}
                                disabled
                                track={false}
                            />
                            </Box>
        
                    </div>
            )}
            {summary && (
                <div className='w-full max-w-2xl mt-6'>
                    <Typography variant="h6">
                        <div className='flex justify-center align-middle text-2xl font-bold pb-6'>
                            Summary
                        </div>
                    </Typography>
                    <Typography className='text-center bg-blue-400 text-white rounded-full p-12'>{summary}</Typography>
                </div>
            )}
            {transcription && (
                <div 
                    className='w-full max-w-2x; mt-6'>
                    <Typography>
                        <div className='flex justify-center align-middle text-2xl font-bold pb-6'>
                            Transcript

                        </div>
                    </Typography>
                    <div className='flex justify-center align-middle'>
                        <Typography className='text-center w-9/12 text-black box-border-4 rounded-md p-12 '>{transcription}</Typography>
                    </div>
                </div>
            )}
            
            </div>
        
    );


   
}

const getColor = (value) => {
    if (value > 0) {
        return 'green';
    } else if (value < 0) {
        return 'red';
    } else {
        return 'gray';
    }
}


export default App;
