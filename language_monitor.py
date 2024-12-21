import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from termcolor import colored
import openai
import pygame
import threading
import tempfile
from pathlib import Path

# Constants
FILE_PATH = "write_here.txt"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TARGET_LANGUAGE = None
START_TAG = "<WRITE IN BETWEEN THESE TAGS>"
END_TAG = "<WRITE IN BETWEEN THESE TAGS>"
LAST_CONTENT = ""
LAST_LANGUAGE = None
TEMP_DIR = Path(tempfile.gettempdir()) / "language_monitor"
CURRENT_AUDIO_PATH = None
AUDIO_LOCK = threading.Lock()
SAVED_AUDIO_PATH = "latest_translation.mp3"
MODEL = "gpt-4o-mini"
# Initialize pygame mixer
pygame.mixer.init()

def cleanup_old_audio():
    """Clean up old audio files."""
    try:
        for file in TEMP_DIR.glob("*.mp3"):
            try:
                file.unlink()
            except Exception:
                pass
    except Exception as e:
        print(colored(f"Error cleaning up audio files: {str(e)}", "red"))

def play_audio(audio_path):
    """Play audio file and handle interruption."""
    global CURRENT_AUDIO_PATH
    try:
        with AUDIO_LOCK:
            CURRENT_AUDIO_PATH = audio_path
            pygame.mixer.music.stop()
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            print(colored("Playing audio translation...", "green"))
    except Exception as e:
        print(colored(f"Error playing audio: {str(e)}", "red"))

def generate_and_play_audio(text):
    """Generate audio from text and play it."""
    try:
        temp_file = TEMP_DIR / f"audio_{int(time.time())}.mp3"
        print(colored("Generating audio...", "yellow"))
        
        # Generate and save temporary file for playback
        with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text
        ) as response:
            response.stream_to_file(str(temp_file))
            
        # Generate and save permanent file
        with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text
        ) as response:
            response.stream_to_file(SAVED_AUDIO_PATH)
            
        threading.Thread(target=play_audio, args=(temp_file,), daemon=True).start()
        cleanup_old_audio()
    except Exception as e:
        print(colored(f"Error generating audio: {str(e)}", "red"))

def detect_target_language_from_file():
    """Detect target language from the first line of the file."""
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            first_line = file.readline().strip()
            if first_line.startswith("LANGUAGE:"):
                return first_line.split("LANGUAGE:")[1].strip().lower()
    except Exception as e:
        print(colored(f"Error reading language from file: {str(e)}", "red"))
    return None

def get_translation(text, target_language):
    """Get translation using OpenAI API."""
    try:
        system_prompt = f"You are a translator. Translate the following text to {target_language}. Only respond with the translation, no explanations."
        print(colored(f"Translating to {target_language}...", "yellow"))
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(colored(f"Error getting translation: {str(e)}", "red"))
        return None

def extract_text_between_tags(content):
    """Extract text between the tags."""
    try:
        start_idx = content.find(START_TAG)
        end_idx = content.find(END_TAG, start_idx + len(START_TAG))
        if start_idx != -1 and end_idx != -1:
            text = content[start_idx + len(START_TAG):end_idx].strip()
            return text
        return ""
    except Exception as e:
        print(colored(f"Error extracting text between tags: {str(e)}", "red"))
        return ""

def update_file_with_translation(original_content, translation):
    """Update the file with the translation while preserving structure."""
    try:
        lines = original_content.split('\n')
        last_tag_index = -1
        for i, line in enumerate(lines):
            if END_TAG in line:
                last_tag_index = i

        if last_tag_index == -1:
            print(colored("Error: Could not find end tag", "red"))
            return

        # Remove any existing translation lines
        lines = [line for line in lines if not line.strip().startswith("TRANSLATION:")]
        
        # Add the new translation after the last tag
        lines.insert(last_tag_index + 1, "")  # Add empty line for spacing
        lines.insert(last_tag_index + 2, f"TRANSLATION: {translation}")

        with open(FILE_PATH, "w", encoding="utf-8") as file:
            file.write('\n'.join(lines))
        
        print(colored("Translation updated successfully!", "green"))
        generate_and_play_audio(translation)
        
    except Exception as e:
        print(colored(f"Error updating file with translation: {str(e)}", "red"))

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == os.path.abspath(FILE_PATH):
            try:
                global LAST_CONTENT, TARGET_LANGUAGE, LAST_LANGUAGE
                time.sleep(0.1)
                
                # Check for language change first
                current_language = detect_target_language_from_file()
                if current_language != LAST_LANGUAGE:
                    LAST_LANGUAGE = current_language
                    TARGET_LANGUAGE = current_language
                    print(colored(f"Target language changed to: {TARGET_LANGUAGE}", "cyan"))
                    # Retranslate existing content with new language
                    with open(FILE_PATH, "r", encoding="utf-8") as file:
                        content = file.read()
                    text_between_tags = extract_text_between_tags(content)
                    if text_between_tags and text_between_tags != "":
                        translation = get_translation(text_between_tags, TARGET_LANGUAGE)
                        if translation:
                            update_file_with_translation(content, translation)
                    return

                # Handle regular content changes
                with open(FILE_PATH, "r", encoding="utf-8") as file:
                    content = file.read()
                
                text_between_tags = extract_text_between_tags(content)
                if not text_between_tags or text_between_tags == LAST_CONTENT:
                    return
                
                LAST_CONTENT = text_between_tags
                print(colored("Detecting changes and translating...", "yellow"))
                translation = get_translation(text_between_tags, TARGET_LANGUAGE)
                
                if translation:
                    update_file_with_translation(content, translation)
                
            except Exception as e:
                print(colored(f"Error handling file change: {str(e)}", "red"))

def reset_file():
    """Reset the file to its original state."""
    try:
        content = f"""LANGUAGE: german

{START_TAG}
{END_TAG}"""
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            file.write(content)
        print(colored("File reset to original state", "green"))
        return True
    except Exception as e:
        print(colored(f"Error resetting file: {str(e)}", "red"))
        return False

def main():
    global TARGET_LANGUAGE, LAST_LANGUAGE
    
    print(colored("Starting Language Monitor...", "cyan"))
    
    if not OPENAI_API_KEY:
        print(colored("Error: OpenAI API key not found in environment variables", "red"))
        return

    try:
        openai.api_key = OPENAI_API_KEY
    except Exception as e:
        print(colored(f"Error initializing OpenAI: {str(e)}", "red"))
        return
    
    # Reset file to original state
    if not reset_file():
        return

    # Detect target language
    TARGET_LANGUAGE = detect_target_language_from_file()
    LAST_LANGUAGE = TARGET_LANGUAGE
    if not TARGET_LANGUAGE:
        print(colored("Error: Could not detect target language from file", "red"))
        return
    
    print(colored(f"Target language for translation: {TARGET_LANGUAGE}", "green"))
    cleanup_old_audio()
    
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(FILE_PATH)), recursive=False)
    
    try:
        observer.start()
        print(colored("Monitoring for changes... (Press Ctrl+C to stop)", "cyan"))
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(colored("\nStopping Language Monitor...", "yellow"))
        cleanup_old_audio()
    observer.join()

if __name__ == "__main__":
    main() 