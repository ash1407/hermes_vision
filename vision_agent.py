#!/usr/bin/env python
"""
local-vision-agent: Capture webcam/screen and query a local vision LLM via Ollama.
"""

import argparse
import base64
import sys
import cv2
import mss
import numpy as np
import ollama
import win32com.client as wincl

def capture_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Unable to access webcam. Please check if a camera is connected and not in use by another application.")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("Failed to capture frame from webcam")
    return frame

def capture_screen():
    with mss.MSS() as sct:
        monitor = sct.monitors[1]  # primary monitor
        img = np.array(sct.grab(monitor))
        # Drop alpha channel, convert RGB to BGR for OpenCV
        frame = cv2.cvtColor(img[:,:,:3], cv2.COLOR_RGB2BGR)
        return frame

def describe_image(frame, model, prompt):
    _, buf = cv2.imencode('.jpg', frame)
    b64 = base64.b64encode(buf).decode('utf-8')
    response = ollama.generate(
        model=model,
        prompt=prompt,
        images=[b64]
    )
    return response['response']

def speak_text(text):
    speaker = wincl.Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

def main():
    parser = argparse.ArgumentParser(description="Local vision agent: capture webcam/screen and describe with Ollama LLM.")
    parser.add_argument('--source', choices=['webcam', 'screen'], default='screen',
                        help="Source of image: webcam or screen (default: screen)")
    parser.add_argument('--model', default='moondream',
                        help="Ollama model name (default: moondream2)")
    parser.add_argument('--prompt', default='Describe what you see in this image in one sentence.',
                        help="Prompt for the vision model")
    parser.add_argument('--speak', action='store_true',
                        help="Speak the result using Windows TTS")
    parser.add_argument('--output', choices=['text', 'json'], default='text',
                        help="Output format: plain text or JSON (default: text)")
    args = parser.parse_args()

    if args.source == 'webcam':
        frame = capture_webcam()
    else:
        frame = capture_screen()

    description = describe_image(frame, args.model, args.prompt)

    if args.output == 'json':
        import json
        result = {
            'source': args.source,
            'model': args.model,
            'prompt': args.prompt,
            'description': description
        }
        print(json.dumps(result, indent=2))
    else:
        print(description)

    if args.speak:
        speak_text(description)

if __name__ == '__main__':
    main()
