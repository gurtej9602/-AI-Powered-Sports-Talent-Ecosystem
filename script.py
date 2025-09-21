import cv2
import mediapipe as mp
import csv
import time
import threading
import google.generativeai as genai
import os
import pygame
from datetime import datetime, timedelta

# ---------------- Gemini Setup ----------------
# Set your Gemini API key here
API_KEY = "AIzaSyBeIdCI3HEJoQf7QEEMc2PbXVHsD-5zR7w"
genai.configure(api_key=API_KEY)

def analyze_with_gemini(csv_file, sport, role, prompt_file="prompt.txt"):
    """Reads CSV + prompt and gets analysis from Gemini"""
    # Load prompt
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_text = f.read()
    else:
        prompt_text = f"Analyze the following body joint movement data for the sport of {sport}, where the role is {role}. Provide feedback based on this information."

    # Load CSV data
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_text = f.read()

    # Prepare input
    contents = [f"{prompt_text}\n\nHere is the recorded body joint data:\n{csv_text} Also, consider the sport: {sport} and the role: {role}. how you should ananlye is first look at the movement and check is the movement same as the sport and the role if not tell the persone he did wrong if he is right then only output a Single score to summarize the performance out of 100.noting else just the score.,also the score should be given in the respect to how good the performance is in the respect to the sport and role.And give a very low numbers score every time "]

    # Ask Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(contents)
    return response.text

# State variables
tracking = False
cap = None
csv_file = None
csv_writer = None
frame_count = 0
filename = None
sport = None  # Variable to store sport type
role = None   # Variable to store role in the sport

# Mediapipe setup
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Initialize pygame mixer for sound
pygame.mixer.init()

# Load sound for notifications (make sure you have a sound file in the working directory)
sound = pygame.mixer.Sound("alert_sound.wav")  # Replace with your sound file path

# State variables for VideoWriter
video_writer = None
video_filename = None
raw_video_writer = None  # For saving the raw video feed
raw_video_filename = None  # For the raw video filename

def start_tracking():
    global tracking, cap, csv_file, csv_writer, frame_count, filename, video_writer, video_filename, raw_video_writer, raw_video_filename

    if tracking:  # already tracking
        return

    cap = cv2.VideoCapture(0)
    filename = f"body_joints_{int(time.time())}.csv"
    csv_file = open(filename, mode="w", newline="")
    csv_writer = csv.writer(csv_file)

    # header row
    landmark_names = [l.name for l in mp_pose.PoseLandmark]
    header = ["Frame"] + landmark_names
    csv_writer.writerow(header)

    # Setup video recording
    video_filename = f"tracking_video_{int(time.time())}.avi"
    video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

    # Setup raw video recording (original feed)
    raw_video_filename = f"raw_video_feed_{int(time.time())}.avi"
    raw_video_writer = cv2.VideoWriter(raw_video_filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

    frame_count = 0
    tracking = True

    # Run in separate thread
    threading.Thread(target=track_pose, daemon=True).start()
    print("✅ Tracking started...")

def stop_tracking():
    global tracking, cap, csv_file, filename, video_writer, video_filename, raw_video_writer, raw_video_filename
    if not tracking:
        return
    tracking = False
    if cap:
        cap.release()
    if csv_file:
        csv_file.close()
    if video_writer:
        video_writer.release()
    if raw_video_writer:
        raw_video_writer.release()
    cv2.destroyAllWindows()
    print(f"🛑 Tracking stopped. Data saved to {filename}, video saved to {video_filename}, and raw video saved to {raw_video_filename}")

    # ---- Run Gemini analysis ----
    try:
        output = analyze_with_gemini(filename, sport, role, "prompt.txt")
        with open("analysis_output.txt", "w", encoding="utf-8") as f:
            f.write(output)
        print("🤖 Gemini Analysis:\n", output)
        print("✅ Analysis saved to analysis_output.txt")
    except Exception as e:
        print("❌ Gemini analysis failed:", e)

def track_pose():
    global tracking, cap, csv_writer, frame_count, video_writer, raw_video_writer

    with mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:

        while tracking:
            success, frame = cap.read()
            if not success:
                continue

            # Write the raw frame to the raw video file
            raw_video_writer.write(frame)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                frame_count += 1
                row = [frame_count]
                for lm in results.pose_landmarks.landmark:
                    row.append(f"({lm.x:.4f}, {lm.y:.4f}, {lm.z:.4f})")
                csv_writer.writerow(row)

            # Save the processed frame to video (pose tracking video)
            video_writer.write(image)

            cv2.imshow("Body Movement Tracking", image)

            if cv2.waitKey(5) & 0xFF == 27:  # ESC stops everything
                stop_tracking()
                break

# Function to set a timer for start and stop with sound alerts
def set_timer(start_delay=0, stop_delay=0):
    """Set a timer to start and stop recording after specific delays in seconds with sound alerts"""
    
    # Play sound 1 second before starting
    if start_delay > 1:
        print(f"⏳ Sound will play in 1 second before starting...")
        time.sleep(start_delay - 1)
        sound.play()  # Play sound
        time.sleep(1)

    print(f"⏳ Waiting {start_delay} seconds to start tracking...")
    time.sleep(start_delay)
    start_tracking()
    
    # Play sound 1 second before stopping
    if stop_delay > 1:
        print(f"⏳ Sound will play in 1 second before stopping...")
        time.sleep(stop_delay - 1)
        sound.play()  # Play sound
        time.sleep(1)

    print(f"⏳ Recording will stop after {stop_delay} seconds...")
    time.sleep(stop_delay)
    stop_tracking()

# Command line interface (CLI)
def main():
    global sport, role
    print("Body Movement Tracking - Console Version")
    print("You can now set a timer to start and stop recording.")
    
    # Prompt for sport and role input
    sport = input("Enter the sport you are practicing (e.g., Basketball, Soccer): ").strip()
    role = input("Enter your role in the sport (e.g., Forward, Goalkeeper): ").strip()

    print(f"Sport: {sport}, Role: {role}")

    print("Commands: 'start' to begin, 'stop' to stop, 'timer' to set a timer, 'exit' to quit.")
    
    while True:
        command = input("Command: ").strip().lower()

        if command == "start":
            start_tracking()
        elif command == "stop":
            stop_tracking()
        elif command == "timer":
            try:
                start_delay = int(input("Enter start delay (seconds): "))
                stop_delay = int(input("Enter stop delay (seconds): "))
                set_timer(start_delay, stop_delay)
            except ValueError:
                print("❌ Invalid input. Please enter numbers for the delays.")
        elif command == "exit":
            if tracking:
                stop_tracking()
            print("Exiting...")
            break
        else:
            print("Invalid command. Please type 'start', 'stop', 'timer', or 'exit'.")

if _name_ == "_main_":
    main()