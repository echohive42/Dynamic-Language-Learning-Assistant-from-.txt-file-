# Real-Time Language Translator

This is a real-time language translation tool that automatically translates text as you type and provides audio pronunciation.

## ✨ Features

- ✨ Real-time Translation: Instantly translates as you type
- 🎯 Multi-Language Support: Works with any source language
- 🎙️ Audio Pronunciation: Automatic text-to-speech conversion
- 🔄 Dynamic Language Switching: Change target language on the fly
- 💾 Audio Storage: Saves latest translation audio
- 🌐 OpenAI Integration: Powered by advanced language models
- 🎨 User-Friendly: Simple text file interface
- 🔍 Auto-Detection: Automatically detects text changes
- 🎵 Audio Control: Seamless audio playback management
- ⚡ Efficient: Optimized for real-time performance

## ❤️ Support & Get 400+ AI Projects

This is one of 400+ fascinating projects in my collection! [Support me on Patreon](https://www.patreon.com/c/echohive42/membership) to get:

- 🎯 Access to 400+ AI projects (and growing daily!)
  - Including advanced projects like [2 Agent Real-time voice template with turn taking](https://www.patreon.com/posts/2-agent-real-you-118330397)
- 📥 Full source code & detailed explanations
- 📚 1000x Cursor Course
- 🎓 Live coding sessions & AMAs
- 💬 1-on-1 consultations (higher tiers)
- 🎁 Exclusive discounts on AI tools & platforms

## Setup

1. Make sure you have Python installed on your computer
2. Install the required packages:
   ```bash
   pip install openai watchdog termcolor requests pygame
   ```
3. Set your OpenAI API key as an environment variable:
   ```bash
   # Windows
   set OPENAI_API_KEY=your-api-key-here
   
   # Mac/Linux
   export OPENAI_API_KEY=your-api-key-here
   ```

## How to Use

1. Run the script:
   ```bash
   python language_monitor.py
   ```

2. The script will create a file called 'write_here.txt' with this structure:
   ```
   LANGUAGE: german

   <WRITE IN BETWEEN THESE TAGS>
   <WRITE IN BETWEEN THESE TAGS>
   ```

3. Start typing between the tags. The script will:
   - Automatically detect your text changes
   - Translate your text to the target language
   - Play the audio pronunciation
   - Save the audio as 'latest_translation.mp3'

## Changing the Target Language

To change the target language, simply edit the first line:
```
LANGUAGE: french
```
(The translation will update automatically)

## Example

If your write_here.txt looks like this:
```
LANGUAGE: german

<WRITE IN BETWEEN THESE TAGS>
Hello, how are you?
<WRITE IN BETWEEN THESE TAGS>
```

It will automatically add:
```
TRANSLATION: Hallo, wie geht es dir?
```
And play the pronunciation.

## Notes

- The script needs an active internet connection
- Audio files are automatically cleaned up
- Press Ctrl+C in the terminal to stop the script
- Previous translations are overwritten with new ones 