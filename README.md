# 33_StiffenHacking
# OptiLink

An assistive typing application designed for ALS patients, enabling text input through eye movement tracking and AI-powered predictive text.

## Features

- Eye movement tracking using dlib and OpenCV
- Intuitive split keyboard interface
- Hierarchical letter selection system
- AI-powered predictive text using Gemini
- User-friendly GUI built with PyQt

## Technical Requirements

- Python 3.x
- OpenCV
- dlib
- PyQt
- CMake
- NumPy
- Google Gemini API

## How It Works

1. **Eye Tracking System**
   - Uses dlib for facial landmark detection
   - OpenCV for real-time video processing
   - Tracks eye movements to determine gaze direction

2. **Split Keyboard Interface**
   - Divided into left and right letter groups
   - Looking at a section activates sub-menu of available letters
   - Reduces required eye movements for letter selection

3. **Predictive Text**
   - Integrates Google Gemini for intelligent text prediction
   - Generates contextual sentence suggestions
   - Learns from user input patterns

## Requirements 
opencv-python
dlib
numpy
pillow
pyttsx3
geocoder
twillio
dotenv
google=generativeai
azure-cognitiveservices-speech
requests
sounddevice
soundfile

## How to run
1. Install all required dependencies
2. Create .env file with required details
3. run emotionalTTS_server.py
4. run gaze_tracking_with_ui_1.py
