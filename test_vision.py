#!/usr/bin/env python
import base64
import cv2
import numpy as np
import ollama

def describe_image(frame, model, prompt):
    _, buf = cv2.imencode('.jpg', frame)
    b64 = base64.b64encode(buf).decode('utf-8')
    response = ollama.generate(
        model=model,
        prompt=prompt,
        images=[b64]
    )
    return response['response']

if __name__ == '__main__':
    # Create a dummy 100x100 RGB image (gray)
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:] = 128  # gray
    model = 'moondream'
    prompt = 'Describe this image.'
    print('Calling Ollama...')
    try:
        desc = describe_image(frame, model, prompt)
        print('Result:', desc)
    except Exception as e:
        print('Error:', e)