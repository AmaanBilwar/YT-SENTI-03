from flask import Flask, request, jsonify
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import dotenv
import os

dotenv.load_dotenv()


app = Flask(__name__)

# Replace with your OpenAI API key and endpoint
openai_api_key = dotenv.load_dotenv('OPEN_AI_API_KEY')

# Endpoint for the OpenAI API
openai_endpoint = 'https://api.openai.com/v1/chat/completions'

# Function to interact with OpenAI API


def openai_request(text):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'gpt-3.5-turbo-16k',  # Updated model name
        'prompt': text,
        'max_tokens': 150
    }
    response = requests.post(openai_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['text'].strip()
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

# Route for summarization (GET and POST)


@app.route('/summary', methods=['GET', 'POST'])
def summarize_text():
    if request.method == 'GET':
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'URL query parameter is required.'}), 400

        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube link.'}), 400

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text_transcript = ' '.join([t['text'] for t in transcript])

            # Perform summarization using OpenAI
            summary = openai_request(text_transcript)

            return jsonify({
                'transcription': text_transcript,
                'summary': summary
            })

        except Exception as e:
            return jsonify({'error': f'Error processing transcript and summary: {str(e)}'}), 500

    elif request.method == 'POST':
        data = request.get_json()
        text_to_summarize = data.get('text')

        if not text_to_summarize:
            return jsonify({'error': 'Missing text field in request.'}), 400

        try:
            summary = openai_request(text_to_summarize)
            return jsonify({'summary': summary})

        except Exception as e:
            return jsonify({'error': f'Error processing summary: {str(e)}'}), 500

    else:
        return jsonify({'error': 'Method Not Allowed'}), 405


if __name__ == '__main__':
    app.run(debug=True, port=4000)
