

import os
import socket
import threading
import azure.cognitiveservices.speech as speechsdk
import requests
import sounddevice as sd
import soundfile as sf
import io
from dotenv import load_dotenv
import signal
import sys

load_dotenv()

def signal_handler(sig, frame):
    print('\nExiting gracefully...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Azure Speech Service configuration
speech_key = os.getenv("SPEECH_KEY")
service_region = os.getenv("SPEECH_REGION")

hf_api_token = os.getenv("HUGGING_FACE_KEY")
if hf_api_token is None:
    raise Exception("Hugging Face API token not found. Please set the 'HUGGINGFACE_API_TOKEN'.")

headers = {"Authorization": f"Bearer {hf_api_token}"}

if speech_key is None:
    raise Exception("Azure Speech Service key not found. Please set the 'AZURE_SPEECH_KEY'.")

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Voice and emotion configuration
voice_name = "en-US-JennyNeural"
speech_config.speech_synthesis_voice_name = voice_name

def analyze_emotion(text):
    API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
    payload = {"inputs": text}
    print(f"Analyzing emotion for text: {text}")
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        # Parse the result to get the highest scoring emotion
        sorted_results = sorted(result[0], key=lambda x: x['score'], reverse=True)
        detected_emotion = sorted_results[0]['label']
        print(f"Detected emotion: {detected_emotion}")
        return detected_emotion.lower()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return 'neutral'
    except KeyError:
        print("Unexpected response format from the Hugging Face API.")
        return 'neutral'

emotion_to_style = {
    'admiration': 'cheerful',
    'amusement': 'cheerful',
    'anger': 'angry',
    'annoyance': 'angry',
    'approval': 'cheerful',
    'caring': 'cheerful',
    'confusion': 'chat',
    'curiosity': 'chat',
    'desire': 'cheerful',
    'disappointment': 'sad',
    'disapproval': 'sad',
    'disgust': 'disgruntled',
    'embarrassment': 'sad',
    'excitement': 'cheerful',
    'fear': 'fearful',
    'gratitude': 'cheerful',
    'grief': 'sad',
    'joy': 'cheerful',
    'love': 'cheerful',
    'nervousness': 'chat',
    'optimism': 'cheerful',
    'pride': 'cheerful',
    'realization': 'chat',
    'relief': 'cheerful',
    'remorse': 'sad',
    'sadness': 'sad',
    'surprise': 'chat',
    'neutral': 'neutral',
    # Map additional emotions as needed
}

def synthesize_with_emotion(text, style):
    ssml_template = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
           xmlns:mstts='http://www.w3.org/2001/mstts'
           xml:lang='en-US'>
        <voice name='en-US-JennyNeural'>
            <mstts:express-as style='{style}'>
                {text}
            </mstts:express-as>
        </voice>
    </speak>
    """
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = synthesizer.speak_ssml_async(ssml_template).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}] with emotion [{style}]")
        audio_data = result.audio_data
        return audio_data
    else:
        print(f"Speech synthesis canceled: {result.cancellation_details.reason}")
        if result.cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {result.cancellation_details.error_details}")
        return None

def play_audio_in_memory(audio_data):
    # Create an in-memory bytes buffer
    audio_stream = io.BytesIO(audio_data)
    # Read the audio data using soundfile
    data, samplerate = sf.read(audio_stream, dtype='float32')
    # Play the audio using sounddevice
    sd.play(data, samplerate=samplerate)
    sd.wait()

def process_text(text):
    # Analyze emotion
    detected_emotion = analyze_emotion(text)
    # Map emotion to style
    tts_style = emotion_to_style.get(detected_emotion, 'neutral')
    # Synthesize speech
    audio_data = synthesize_with_emotion(text, tts_style)
    if audio_data:
        # Play audio
        play_audio_in_memory(audio_data)
    else:
        print("Failed to synthesize speech.")

def handle_client_connection(client_socket):
    try:
        # Receive data from the client
        data = client_socket.recv(4096)
        text = data.decode('utf-8')
        print(f"Received text: {text}")
        if text.strip():
            process_text(text)
        else:
            print("No text to process.")
    except Exception as e:
        print(f"Error handling client connection: {e}")
    finally:
        client_socket.close()

def start_server():
    server_address = ('localhost', 65432)  # You can choose any open port above 1024
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(server_address)
    server.listen(5)
    print(f"TTS server listening on {server_address[0]}:{server_address[1]}")

    try:
        while True:
            client_sock, address = server.accept()
            print(f"Accepted connection from {address[0]}:{address[1]}")
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_sock,)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()