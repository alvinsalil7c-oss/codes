from pynput import keyboard, mouse
import time
import threading
import numpy as np

# -----------------------------
# Data storage
# -----------------------------

key_times = []
backspace_count = 0
click_count = 0
mouse_distances = []

last_key_time = None
last_mouse_position = None


# -----------------------------
# Keyboard monitoring
# -----------------------------

def on_press(key):
    global last_key_time, backspace_count

    current_time = time.time()

    if last_key_time is not None:
        key_times.append(current_time - last_key_time)

    last_key_time = current_time

    try:
        if key == keyboard.Key.backspace:
            backspace_count += 1
    except:
        pass


# -----------------------------
# Mouse monitoring
# -----------------------------

def on_move(x, y):
    global last_mouse_position

    if last_mouse_position is not None:
        old_x, old_y = last_mouse_position

        distance = np.sqrt(
            (x - old_x) ** 2 +
            (y - old_y) ** 2
        )

        mouse_distances.append(distance)

    last_mouse_position = (x, y)


def on_click(x, y, button, pressed):
    global click_count

    if pressed:
        click_count += 1


# -----------------------------
# Start listeners
# -----------------------------

keyboard_listener = keyboard.Listener(
    on_press=on_press
)

mouse_listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click
)

keyboard_listener.start()
mouse_listener.start()


# -----------------------------
# Analyze behavior
# -----------------------------

def analyze_behavior():

    if len(key_times) > 0:
        avg_key_interval = np.mean(key_times)
        typing_speed = 1 / avg_key_interval
    else:
        avg_key_interval = 0
        typing_speed = 0

    if len(mouse_distances) > 0:
        avg_mouse_movement = np.mean(mouse_distances)
    else:
        avg_mouse_movement = 0

    # Simple prototype scoring
    stress_score = 0

    # Faster typing
    if typing_speed > 5:
        stress_score += 30

    # Frequent corrections
    if backspace_count > 10:
        stress_score += 20

    # Frequent clicking
    if click_count > 30:
        stress_score += 20

    # High mouse movement
    if avg_mouse_movement > 20:
        stress_score += 20

    stress_score = min(stress_score, 100)

    if stress_score < 30:
        emotion = "Calm"
    elif stress_score < 60:
        emotion = "Moderate Stress"
    else:
        emotion = "High Stress"

    return {
        "stress_score": stress_score,
        "emotion": emotion,
        "typing_speed": round(typing_speed, 2),
        "backspaces": backspace_count,
        "clicks": click_count,
        "mouse_movement": round(avg_mouse_movement, 2)
    }


# -----------------------------
# Print results every 10 sec
# -----------------------------

while True:

    time.sleep(10)

    result = analyze_behavior()

    print("\n-----------------------------")
    print("       TILT AI BEHAVIOR")
    print("-----------------------------")
    print("Emotion:", result["emotion"])
    print("Stress:", result["stress_score"], "%")
    print("Typing speed:", result["typing_speed"])
    print("Backspaces:", result["backspaces"])
    print("Clicks:", result["clicks"])
    print("Mouse movement:", result["mouse_movement"])