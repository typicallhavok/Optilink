# OptiLink

An assistive typing application designed for ALS patients, enabling text input through eye movement tracking and AI-powered predictive text.
[Demo](https://drive.google.com/file/d/1QxqZ243CU5L0t8J9qjV_5jJiGR6JZNq1/view?usp=sharing)

## Features

- Eye movement tracking using dlib and OpenCV
- Better keyboard using gaze
- Autofill words
- AI-powered predictive text using Gemini
- User-friendly GUI
- Text-to-Speech with emotion detection
- SOS signal with geolocation

## Technical Requirements

- Python 3.x
- OpenCV
- dlib
- CMake
- NumPy
- Google Gemini API

## How It Works

1. **Eye Tracking System**
   - Uses dlib for facial landmark detection
   - OpenCV for real-time video processing
   - Tracks eye movements to determine gaze direction

2. **Better Keyboard Interface**
   - Most commonly used letter at quick access
   - Easy scroll through keyboard
   - Contains autofill
   - Contains SOS

3. **Predictive Text**
   - Integrates Google Gemini for intelligent text prediction
   - Generates contextual sentence suggestions
   - Learns from user input patterns
   
## Requirements 
- opencv-python
- dlib
- numpy
- pillow
- pyttsx3
- geocoder
- twillio
- dotenv
- google=generativeai
- azure-cognitiveservices-speech
- requests
- sounddevice
- soundfile

## How to run
1. Install all required dependencies
2. Download shape_predictor_68_face_landmarks.dat
4. Create .env file with required details
5. run emotionalTTS_server.py
6. run gaze_tracking_with_ui_1.py
