import cv2
import dlib
import numpy as np
import pyttsx3
import time
from PIL import Image, ImageDraw
import math
import socket
import autofill
import autoword
import sos


# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# Load the pre-trained face detector and shape predictor
PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)

# Initialize webcam video capture
cap = cv2.VideoCapture(0)


# Define colors
BACKGROUND_COLOR = (15, 15, 15)     # Almost black
KEY_NORMAL = (0, 140, 255)          # Orange (BGR format)
KEY_SELECTED = (0, 255, 255)        # Yellow (BGR format)
TEXT_COLOR = (255, 255, 255)        # White
SHADOW_COLOR = (0, 0, 0, 60)        # Semi-transparent black

# Animation parameters
ANIMATION_SPEED = 0.15  # Lower is faster
key_animations = {}     # Store animation states

# Update keyboard dimensions to be smaller
keyboard = np.zeros((600, 900, 3), np.uint8)  # Reduced from 800x1200

# Define the keys
keys_set = {
    0: "E", 1: "T", 2: "A", 3: "O", 4: "I", 5: "N", 6: "S", 7: "H", 8: "D", 9: "R",
    10: "L", 11: "C", 12: "U", 13: "M", 14: "W", 15: "F", 16: "G", 17: "Y", 18: "P", 19: "B",
    20: "V", 21: "K", 22: "J", 23: "X", 24: "Q", 25: "Z", 26: " ", 27: "Back", 28: "Speak",
    29: "food", 30: "water", 31: "washroom",
    32: "SOS"
}

# Variables for text input
text = ""
last_key = -1

# Variables for cursor movement control
selected_key_index = 0
last_cursor_move_time = time.time()
cursor_move_delay = 0.5  # Minimum time (in seconds) between cursor movements

# Add color for special buttons (add with other color definitions)
SPECIAL_BTN_COLOR = (0, 165, 255)  # Orange-yellow for Back and Speak buttons

def send_text_to_tts_server(text):
    server_address = ('localhost', 65432)  # Same as the TTS server's address
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server_address)
            sock.sendall(text.encode('utf-8'))
            print(f"Sent text to TTS server: {text}")
    except ConnectionRefusedError:
        print("Failed to connect to TTS server. Ensure the server is running.")
    except Exception as e:
        print(f"Error sending text to TTS server: {e}")


#
#
#
#
#
#------------------------------------------------GUI------------------------------------------------------


def create_rounded_rectangle(width, height, radius, color):
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius, fill=color)
    return np.array(image)

def get_animation_offset(key_idx, current_time):
    if key_idx not in key_animations:
        key_animations[key_idx] = {'start_time': current_time, 'is_selected': False}
    
    anim_state = key_animations[key_idx]
    if anim_state['is_selected'] != (key_idx == selected_key_index):
        anim_state['start_time'] = current_time
        anim_state['is_selected'] = (key_idx == selected_key_index)
    
    time_diff = current_time - anim_state['start_time']
    progress = min(1, time_diff / ANIMATION_SPEED)
    
    if anim_state['is_selected']:
        return int(12 * math.sin(progress * math.pi / 2))  # Increased animation height
    return int(12 * (1 - math.sin(progress * math.pi / 2)))

def draw_keyboard():
    global keyboard
    current_time = time.time()
    screen_width = keyboard.shape[1]
    screen_height = keyboard.shape[0]
    
    # Base key sizes
    base_key_width = min(120, screen_width // 12)
    base_key_height = min(120, screen_height // 8)
    spacing = min(12, base_key_width // 4)
    corner_radius = min(15, base_key_width // 5)
    
    # Text area calculations
    text_area_height = min(90, screen_height // 6)
    text_area_y = 20  # Adjust as needed
    
    # Fill background
    keyboard.fill(BACKGROUND_COLOR[0])
    
    # Draw text area
    cv2.rectangle(keyboard, (0, text_area_y), (screen_width, text_area_y + text_area_height), (25, 25, 25), -1)
    cv2.line(keyboard, (0, text_area_y + text_area_height), (screen_width, text_area_y + text_area_height), (45, 45, 45), 2, cv2.LINE_AA)
    
    # Text display logic with overflow handling
    if text:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = min(1.0, screen_width / 1000)
        thickness = 2
        
        display_text = text
        text_size = cv2.getTextSize(display_text, font, font_scale, thickness)[0]
        while text_size[0] > screen_width - 40:
            display_text = display_text[1:] + "..."
            text_size = cv2.getTextSize(display_text, font, font_scale, thickness)[0]
        
        text_x = 20
        text_y = text_area_y + text_area_height // 2 + text_size[1] // 2
        
        cv2.putText(keyboard, display_text, (text_x + 1, text_y + 1), font, font_scale, (0, 0, 0), thickness + 1, cv2.LINE_AA)
        cv2.putText(keyboard, display_text, (text_x, text_y), font, font_scale, TEXT_COLOR, thickness, cv2.LINE_AA)
    
    # Keys start position
    keys_start_y = text_area_y + text_area_height + 20  # Ensure there's space after the text area
    
    # Base start x position for regular keys
    total_width = 10 * (base_key_width + spacing) - spacing
    start_x = (screen_width - total_width) // 2
    
    for i in range(len(keys_set)):
        key_label = keys_set[i]
        
        # Determine if key is one of the special keys to be centered
        if i in [29, 30, 31]:
            # Increase size
            key_width = int(base_key_width * 1.5)
            key_height = int(base_key_height * 1.5)
            key_color = KEY_SELECTED if i == selected_key_index else SPECIAL_BTN_COLOR
            corner_radius_large = min(20, key_width // 5)
            
            # Total width of the three large keys including spacing
            total_large_keys_width = 3 * key_width + 2 * spacing
            start_x_large_keys = (screen_width - total_large_keys_width) // 2
            
            # Calculate x position for each key
            index_in_large_keys = i - 29  # 0, 1, or 2
            x = start_x_large_keys + index_in_large_keys * (key_width + spacing)
            
            # Set y position for the large keys
            y = keys_start_y + 3 * (base_key_height + spacing)  # Place them below existing rows
            
            y_offset = get_animation_offset(i, current_time)
            y += y_offset
            
            # Create the key background
            key_bg = create_rounded_rectangle(key_width, key_height, corner_radius_large, key_color)
        else:
            # Regular key sizes and positions
            key_width = base_key_width
            key_height = base_key_height
            row = i // 10
            col = i % 10
            x = start_x + col * (key_width + spacing)
            y = keys_start_y + row * (key_height + spacing)
            
            y_offset = get_animation_offset(i, current_time)
            y += y_offset
            
            # Key color
            if key_label in ["Back", "Speak"]:
                key_color = KEY_SELECTED if i == selected_key_index else SPECIAL_BTN_COLOR
            else:
                key_color = KEY_SELECTED if i == selected_key_index else KEY_NORMAL
            
            # Create the key background
            key_bg = create_rounded_rectangle(key_width, key_height, corner_radius, key_color)
        
        # Add shadow with bounds check
        shadow = create_rounded_rectangle(key_width, key_height, corner_radius, SHADOW_COLOR)
        shadow_offset = 4
        
        if y + shadow_offset + key_height <= screen_height and x + shadow_offset + key_width <= screen_width:
            alpha_shadow = shadow[:, :, 3:] / 255.0
            for c in range(3):
                shadow_area = keyboard[int(y) + shadow_offset:int(y) + shadow_offset + key_height, 
                                       int(x) + shadow_offset:int(x) + shadow_offset + key_width, c]
                shadow_area[:] = (shadow_area * (1 - alpha_shadow[:, :, 0]) + 
                                  shadow[:, :, c] * alpha_shadow[:, :, 0])
        
        # Blend key
        alpha_key = key_bg[:, :, 3:] / 255.0
        for c in range(3):
            key_area = keyboard[int(y):int(y) + key_height, int(x):int(x) + key_width, c]
            key_area[:] = (key_area * (1 - alpha_key[:, :, 0]) + 
                           key_bg[:, :, c] * alpha_key[:, :, 0])
        
        # Key label with size adjustment
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        
        # Adjust font scale for long text
        adjusted_font_scale = font_scale
        while True:
            text_size = cv2.getTextSize(key_label, font, adjusted_font_scale, 2)[0]
            if text_size[0] < key_width - 10:
                break
            adjusted_font_scale *= 0.9
        
        text_x = int(x + (key_width - text_size[0]) // 2)
        text_y = int(y + (key_height + text_size[1]) // 2)
        
        cv2.putText(keyboard, key_label, (text_x + 1, text_y + 1), font, adjusted_font_scale, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(keyboard, key_label, (text_x, text_y), font, adjusted_font_scale, TEXT_COLOR, 2, cv2.LINE_AA)
    
    # Ensure no elements are covering the text area
    # Adjust vertical positions if necessary to prevent overlap
    
    # SOS button adjusted for screen size
    sos_diameter = min(100, screen_width // 10)
    sos_x = screen_width // 2 - sos_diameter // 2
    last_row_y = keys_start_y + (2 * (key_height + spacing))
    sos_y = last_row_y + key_height + spacing
        
    # Add SOS text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    thickness = 3
    text_size = cv2.getTextSize("SOS", font, font_scale, thickness)[0]
    text_x = sos_x + (sos_diameter - text_size[0]) // 2
    text_y = sos_y + (sos_diameter + text_size[1]) // 2
    
    # Add text shadow and text for SOS
    # cv2.putText(keyboard, "SOS", (text_x+1, text_y+1), font, font_scale, (0,0,0), thickness+1, cv2.LINE_AA)
    # cv2.putText(keyboard, "SOS", (text_x, text_y), font, font_scale, TEXT_COLOR, thickness, cv2.LINE_AA)


#------------------------------------------------GUI------------------------------------------------------
#
#
#
#
#
#


# Function to calculate the Eye Aspect Ratio (EAR) for blink detection
def calculate_EAR(eye_points, facial_landmarks):
    # Vertical eye landmarks
    A = np.linalg.norm(np.array([facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y]) -
                       np.array([facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y]))
    B = np.linalg.norm(np.array([facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y]) -
                       np.array([facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y]))
    # Horizontal eye landmark
    C = np.linalg.norm(np.array([facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y]) -
                       np.array([facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y]))
    EAR = (A + B) / (2.0 * C)
    return EAR

# Thresholds and constants for blink detection
EAR_THRESHOLD = 0.35
EAR_CONSEC_FRAMES = 2
blink_counter = 0
blink_detected = False

# Variables for gaze smoothing
gaze_history = []
history_length = 5  # Number of frames to include in the moving average

def get_gaze_ratio(eye_points, facial_landmarks, gray_frame):
    # Get the eye region
    left_eye_region = np.array([
        (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
        (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
        (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
        (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
        (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
        (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)
    ], np.int32)

    # Create a mask to extract the eye
    height, width = gray_frame.shape
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.polylines(mask, [left_eye_region], isClosed=True, color=255, thickness=2)
    cv2.fillPoly(mask, [left_eye_region], color=255)

    eye = cv2.bitwise_and(gray_frame, gray_frame, mask=mask)

    # Get the bounding rectangle of the eye region
    min_x = np.min(left_eye_region[:, 0])
    max_x = np.max(left_eye_region[:, 0])
    min_y = np.min(left_eye_region[:, 1])
    max_y = np.max(left_eye_region[:, 1])

    # Crop the eye image
    eye = eye[min_y:max_y, min_x:max_x]

    # Apply thresholding to get the pupil
    _, threshold_eye = cv2.threshold(eye, 70, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the eye region
    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # If no contours are detected, return None
    if len(contours) == 0:
        return None

    # Find the largest contour which should be the pupil
    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
    pupil_contour = contours[0]

    # Calculate the centroid of the pupil
    M = cv2.moments(pupil_contour)
    if M['m00'] == 0:
        cx = int(M['m10'] / (M['m00'] + 1))
        cy = int(M['m01'] / (M['m00'] + 1))
    else:
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])

    # Calculate gaze ratio
    eye_width = max_x - min_x
    gaze_ratio = cx / eye_width

    return gaze_ratio


# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip the frame horizontally
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame)

    # Draw the keyboard
    draw_keyboard()

    if len(faces) == 0:
        cv2.putText(frame, "No face detected", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 2)
    else:
        for face in faces:
            landmarks = predictor(gray_frame, face)

            # Get gaze ratio for both eyes
            left_gaze_ratio = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks, gray_frame)
            right_gaze_ratio = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks, gray_frame)

            if left_gaze_ratio is not None and right_gaze_ratio is not None:
                # Average gaze ratio and add to history
                gaze_ratio = (left_gaze_ratio + right_gaze_ratio) / 2
                gaze_history.append(gaze_ratio)
                if len(gaze_history) > history_length:
                    gaze_history.pop(0)

                # Calculate moving average of gaze ratios
                avg_gaze_ratio = sum(gaze_history) / len(gaze_history)

                # Implement dead zone around center gaze ratio (e.g., 0.45 to 0.55)
                if avg_gaze_ratio < 0.35:
                    direction = "RIGHT"
                elif avg_gaze_ratio > 0.65:
                    direction = "LEFT"
                else:
                    direction = "CENTER"

                # Move cursor if enough time has passed since last movement
                current_time = time.time()
                if current_time - last_cursor_move_time > cursor_move_delay and direction != "CENTER":
                    if direction == "LEFT":
                        selected_key_index = (selected_key_index - 1) % len(keys_set)
                    elif direction == "RIGHT":
                        selected_key_index = (selected_key_index + 1) % len(keys_set)
                    last_cursor_move_time = current_time

            else:
                cv2.putText(frame, "Pupil not detected", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

            # Blink detection for key selection
            left_EAR = calculate_EAR([36, 37, 38, 39, 40, 41], landmarks)
            right_EAR = calculate_EAR([42, 43, 44, 45, 46, 47], landmarks)
            avg_EAR = (left_EAR + right_EAR) / 2.0

            if avg_EAR < EAR_THRESHOLD:
                blink_counter += 1
            else:
                if blink_counter >= EAR_CONSEC_FRAMES:
                    blink_detected = True
                    blink_counter = 0
                else:
                    blink_counter = 0

            # If blink detected, select the key
            if blink_detected:
                blink_detected = False
                if selected_key_index != -1:
                    key = keys_set[selected_key_index]
                    if key == "Back":
                        text = text[:-1]
                    elif key == "Speak":
                        if text.strip():
                            text = autofill.autocomplete_sentence(text, autofill.chat)
                            send_text_to_tts_server(text)    
                            print("Text to speak:", text)
                            text = ""
                    elif key == "SOS":
                        sos.trigger_sos()
                        print("SOS")
                    elif selected_key_index in [29,30,31]:
                        text=key
                    else:
                        text += key
                        if len(text)>2:
                            autowords = autoword.autoCompleteWord(text, autoword.chat)
                            print(autowords[0], '\n',autowords[1],'\n',autowords[2])
                            keys_set[29] = autowords[0] if autowords and autowords[0] else ""
                            keys_set[30] = autowords[1] if autowords and autowords[1] else ""
                            keys_set[31] = autowords[2] if autowords and autowords[2] else ""
                    # Provide a delay after selection
                    time.sleep(0.5)

    # Display the frames
    cv2.imshow("Webcam", frame)
    cv2.imshow("Virtual Keyboard", keyboard)

    # Exit on 'Esc' key
    key = cv2.waitKey(1)
    if key == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()