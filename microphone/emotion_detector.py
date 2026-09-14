import os
import json
import asyncio
import base64
import urllib.parse
import sounddevice as sd
import websockets
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUME_API_KEY")

if not API_KEY:
    print("HUME_API_KEY not found!")
    raise SystemExit

SAMPLE_RATE = 44100
CHANNELS = 1
DEVICE = 1
BLOCK_SIZE = 4410   # about 100 ms


async def main():
    encoded_key = urllib.parse.quote(API_KEY)

    url = (
        "wss://api.hume.ai/v0/evi/chat"
        f"?api_key={encoded_key}"
        "&verbose_transcription=true"
    )

    print("Connecting to Hume...")

    try:
        async with websockets.connect(url) as websocket:

            print("Connected to Hume!")

            # Tell Hume what kind of raw audio we're sending
            session_settings = {
                "type": "session_settings",
                "audio": {
                    "encoding": "linear16",
                    "sample_rate": SAMPLE_RATE,
                    "channels": CHANNELS
                }
            }

            await websocket.send(json.dumps(session_settings))

            loop = asyncio.get_running_loop()

            print()
            print("Speak into your microphone.")
            print("Pause for a moment after speaking.")
            print("Press Ctrl+C to stop.")
            print()

            def audio_callback(indata, frames, time, status):
                if status:
                    print("Microphone status:", status)

                audio_bytes = indata.tobytes()

                message = {
                    "type": "audio_input",
                    "data": base64.b64encode(audio_bytes).decode("utf-8")
                }

                asyncio.run_coroutine_threadsafe(
                    websocket.send(json.dumps(message)),
                    loop
                )

            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                blocksize=BLOCK_SIZE,
                device=DEVICE,
                callback=audio_callback
            ):

                async for raw_message in websocket:

                    data = json.loads(raw_message)

                    message_type = data.get("type")

                    # Show Hume errors instead of silently closing
                    if message_type == "error":
                        print()
                        print("HUME ERROR:")
                        print(data)
                        continue

                    if message_type == "chat_metadata":
                        print("Chat started.")

                    if message_type == "user_message":

                        # Ignore unfinished/interim transcripts
                        if data.get("interim"):
                            continue

                        transcript = (
                            data.get("message", {})
                            .get("content", "")
                        )

                        if transcript:
                            print()
                            print("You said:", transcript)

                        # Hume's vocal-expression scores
                        scores = (
                            data.get("models", {})
                            .get("prosody", {})
                            .get("scores", {})
                        )

                        if scores:
                            top_emotions = sorted(
                                scores.items(),
                                key=lambda item: item[1],
                                reverse=True
                            )[:5]

                            print()
                            print("==============================")
                            print("VOICE EMOTION RESULT")
                            print("==============================")

                            for emotion, score in top_emotions:
                                print(f"{emotion}: {score:.2f}")

                            print("==============================")
                            print()

    except websockets.exceptions.ConnectionClosed as e:
        print()
        print("Hume connection closed.")
        print("Code:", e.code)
        print("Reason:", e.reason)

    except Exception as e:
        print()
        print("ERROR:", type(e).__name__)
        print(e)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")