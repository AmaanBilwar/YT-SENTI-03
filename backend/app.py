from flask import Flask, request, jsonify, send_from_directory
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
from textblob import TextBlob
from flask_cors import CORS
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')


CORS(app)
load_dotenv()

openai_api_key = os.getenv('OPEN_AI_API_KEY')
if not openai_api_key:
    raise ValueError(
        "OpenAI API key not found. Please set the OPEN_AI_API_KEY environment variable.")

openai_endpoint = 'https://api.openai.com/v1/chat/completions'

# Function to extract video ID from YouTube URL


def extract_video_id(url):
    from urllib.parse import urlparse, parse_qs

    if 'youtube.com' in url or 'youtu.be' in url or 'youtube.googleapis.com' in url:
        query = urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if 'v' in query.query:
            return query.query.split('v=')[1].split('&')[0]
        return query.path.split('/')[-1]
    return None

# Function to request OpenAI for summarization


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

# Route for transcribing and summarizing


@app.route('/')
def server():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/debug', methods=['GET'])
def debug():
    api_key = os.getenv('OPEN_AI_API_KEY')
    return jsonify({'openai_api_key': api_key})


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
        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text_transcript = ' '.join([t['text'] for t in transcript])

        # Summarize the transcript
        summary = openai_request(text_transcript)

        # sentiment analysis using TextBlob
        blob = TextBlob(text_transcript)
        sentiment = {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }

        return jsonify({
            'transcription': text_transcript,
            'summary': summary,
            'sentiment': sentiment,
        })

    except Exception as e:
        # Log the detailed error message
        app.logger.error(f"Error processing transcript and summary: {str(e)}")
        return jsonify({'error': f'Error processing transcript and summary: {str(e)}'}), 500


if __name__ == '__main__':
    app.run()
