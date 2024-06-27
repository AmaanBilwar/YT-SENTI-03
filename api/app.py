from flask import Flask, request, jsonify
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
from transformers import pipeline

from flask_cors import CORS

app = Flask(__name__)
CORS(app)


load_dotenv()

model_id = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
sentiment_analysis = pipeline('sentiment-analysis', model=model_id)


openai_api_key = os.getenv('OPEN_AI_API_KEY')
if not openai_api_key:
    raise ValueError(
        "OpenAI API key not found. Please set the OPEN_AI_API_KEY environment variable.")

# openai endpoint
openai_endpoint = 'https://api.openai.com/v1/chat/completions'


def openai_request(text):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {"role": "system", "content": "You are a helpful assistant that summarizes long pieces of text."},
            {"role": "user", "content": f"Please summarize the following transcript: {text}"}
        ],
        'max_tokens': 300,
        'temperature': 0.7
    }
    response = requests.post(openai_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return f'Error: {response.text}'

# Function to extract video ID from YouTube URL


def extract_video_id(url):
    from urllib.parse import urlparse, parse_qs

    if 'youtube.com' in url:
        query = urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if 'v' in query.query:
            return query.query.split('v=')[1].split('&')[0]
    elif 'youtube.googleapis.com' in url:
        return url.split('/')[-1]

    return None

# Route for transcribing and summarizing


@app.route('/transcribe-and-summarize', methods=['POST'])
def transcribe_and_summarize():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'Missing URL field in request.'}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube link.'}), 400

    try:
        # Step 1: Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text_transcript = ' '.join([t['text'] for t in transcript])

        # Step 2: Summarize the transcript
        summary = openai_request(text_transcript)

        # sentiment analysis using transformer models
        sentiment_results = sentiment_analysis(text_transcript)

        return jsonify({
            'transcription': text_transcript,
            'summary': summary,
            'sentiment': sentiment_results[0]['label'],
            'sentiment_score': sentiment_results[0]['score']
        })

    except Exception as e:
        # Log the detailed error message
        app.logger.error(f"Error processing transcript and summary: {str(e)}")
        return jsonify({'error': f'Error processing transcript and summary: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(port=4000)
