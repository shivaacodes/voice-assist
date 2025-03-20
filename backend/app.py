# Import necessary libraries
from dotenv import load_dotenv
import os
from hume import AsyncHumeClient
import asyncio
import time
import base64
import tempfile
from pathlib import Path
import aiofiles
from hume.tts import PostedUtterance, PostedContextWithGenerationId, PostedUtteranceVoiceWithName

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv("HUME_API_KEY")
if not api_key:
    raise EnvironmentError("HUME_API_KEY not found in environment variables")

# Initialize the Hume client with the API key
hume = AsyncHumeClient(api_key=api_key)

# Helper function to write audio to a file
timestamp = int(time.time() * 1000)
output_dir = Path(tempfile.gettempdir()) / f"hume-audio-{timestamp}"


async def write_result_to_file(base64_encoded_audio: str, filename: str) -> None:
    file_path = output_dir / f"{filename}.wav"
    audio_data = base64.b64decode(base64_encoded_audio)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(audio_data)
    print("Wrote", file_path)

# Main function to run the TTS examples


async def main() -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    print("Results will be written to", output_dir)

    # Define a consistent voice name
    voice_name = f"assistant-female-{int(time.time())}"

    # Example 1: Generate speech with a professional, warm, and friendly female assistant voice
    speech1 = await hume.tts.synthesize_json(
        utterances=[
            PostedUtterance(
                # Updated voice description
                description="A professional, warm, and friendly female assistant with a clear American accent",
                # Updated text to fit the assistant role
                text="Hello! How can I assist you today?",
            )
        ]
    )
    await write_result_to_file(speech1.generations[0].audio, "speech1_0")

    # Save the voice for reuse with the consistent name
    generation_id = speech1.generations[0].generation_id
    await hume.tts.voices.create(
        name=voice_name,  # Updated voice_name to reflect the new voice
        generation_id=generation_id
    )
    print(f"Saved voice as: {voice_name}")

    # Example 2: Continue with the saved voice
    speech2 = await hume.tts.synthesize_json(
        utterances=[
            PostedUtterance(
                voice=PostedUtteranceVoiceWithName(
                    name=voice_name),  # Use the updated voice_name
                text="I’m here to assist you with any questions or concerns you might have, so feel free to ask me anything, and I’ll do my best to provide the answers you need!",  # Updated text
            )
        ],
        context=PostedContextWithGenerationId(generation_id=generation_id),
        num_generations=2,
    )
    await write_result_to_file(speech2.generations[0].audio, "speech2_0")
    await write_result_to_file(speech2.generations[1].audio, "speech2_1")

    # Example 3: Add acting instructions to the voice
    speech3 = await hume.tts.synthesize_json(
        utterances=[
            PostedUtterance(
                voice=PostedUtteranceVoiceWithName(
                    name=voice_name),  # Use the updated voice_name
                description="Spoken with a calm and reassuring tone, as if guiding a student",
                text="Let me guide you—where would you like to start?",
            )
        ],
        context=PostedContextWithGenerationId(
            generation_id=speech2.generations[0].generation_id
        ),
        num_generations=1,
    )
    await write_result_to_file(speech3.generations[0].audio, "speech3_0")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
    print("Done")
