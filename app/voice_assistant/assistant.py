import os
from dotenv import load_dotenv
import requests  # Use requests for the Groq API
import speech_recognition as sr
import pyttsx3

# Load environment variables from .env file
load_dotenv()

# Retrieve the Groq API Key from environment variables
api_key = os.getenv("GROQ_API_KEY")
base_url = "https://api.groq.com/openai/v1"

# Initialize the Text-to-Speech engine
engine = pyttsx3.init()

def speak(text):
    """Converts text to speech."""
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listens for a voice command and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)
            return command
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("Speech recognition service is unavailable.")
            return ""

def chat_with_groq(prompt):
    """Sends prompt to Groq API and gets a response."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",  # Adjust model name based on Groq's available models
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP errors
        data = response.json()
        return data['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def main():
    """Main loop for continuous interaction."""
    speak("Hi! I'm your voice assistant. How can I help you?")
    while True:
        query = listen()
        if query:
            if "exit" in query.lower() or "quit" in query.lower():
                speak("Goodbye!")
                break
            reply = chat_with_groq(query)
            speak(reply)

# Only run if not imported
if __name__ == "__main__":
    main()
