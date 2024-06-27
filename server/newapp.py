from flask import Flask, request, jsonify
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import dotenv
import os
from flask_cors import CORS

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

# load openai api key from environment variables
openai_api_key = os.getenv('OPEN_AI_API_KEY')

# endpoint for the openai api
openai_endpoint = 'https://api.openai.com/v1/chat/completions'

# Function to interact with OpenAI API


def openai_request(text):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'gpt-3.5-turbo-16k',
        'messages': [{'role': 'system', 'content':  "You are a helpful assistant that summarizes long pieces of text."}, {"role": "user", "content": f"Please summarize the following transcript: {text}"}
                     ],
        'max_tokens': 300,
        'temperature': 0.7
    }
    response = requests.post(openai_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return f'Error: {response.text}'


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


@app.route('/transcription', methods=['GET'])
def get_transcription():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL query parameter is required.'}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube link.'}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text_transcript = ' '.join([t['text'] for t in transcript])

        return jsonify({'transcription': text_transcript})

    except Exception as e:
        return jsonify({'error': f'Error processing transcript: {str(e)}'}), 500


@app.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()
    text_to_summarize = data.get('text')

    if not text_to_summarize:
        return jsonify({'error': 'Missing text field in request.'}), 400

    try:
        summary = openai_request(text_to_summarize)
        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': f'Error processing summary: {str(e)}'}), 500


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

        return jsonify({
            'transcription': text_transcript,
            'summary': summary
        })

    except Exception as e:
        # Log the detailed error message
        print(f"Error processing transcript and summary: {str(e)}")
        return jsonify({'error': f'Error processing transcript and summary: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=4000)
