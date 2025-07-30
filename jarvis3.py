# JARVIS: Advanced Voice Assistant (Refined)
# This script creates a voice assistant that can perform tasks, dictate text, and answer questions using AI.

# First, you need to install the required Python libraries.
# Open your terminal or command prompt and run these commands:
# pip install speechrecognition
# pip install pyttsx3
# pip install pyaudio
# pip install pyautogui
# pip install requests
# pip install beautifulsoup4

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import pyautogui
import requests
import json
import time
import re
from bs4 import BeautifulSoup

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyAeA1W02ldiJM21j_1KXO0jujllKBHRnHY"

# --- State Management for YouTube ---
youtube_search_results = []
current_video_index = 0

# --- Initialization ---
recognizer = sr.Recognizer()

# --- Core Functions ---

def speak(text):
    """
    Initializes the TTS engine, speaks the given text, and then shuts down.
    This is done within the function to prevent a common bug where the TTS engine
    gets stuck after the first use in a loop.
    """
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id) 
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 0.9)
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def take_command():
    """Listens for a command and returns it as lowercase text."""
    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='en-in').lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        return None  # Return None if speech is unintelligible
    except sr.RequestError:
        speak("I'm having trouble connecting to my systems. Please check your internet connection.")
        return None
    except Exception as e:
        print(e)
        speak("An unexpected error occurred while listening.")
        return None

# --- Command Handler Functions ---

def greet_user():
    """Greets the user based on the time of day."""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        greeting = "Good morning, sir."
    elif 12 <= hour < 18:
        greeting = "Good afternoon, sir."
    else:
        greeting = "Good evening, sir."
    speak(f"{greeting} I am JARVIS, online and ready.")

def get_time():
    """Tells the current time."""
    str_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"Sir, the time is {str_time}")

def get_date():
    """Tells the current date."""
    today = datetime.date.today()
    speak(f"Today's date is {today.strftime('%B %d, %Y')}")

def open_website(url, name):
    """Opens a specified website and confirms."""
    speak(f"Understood. Opening {name}.")
    webbrowser.open(url)
    time.sleep(1) # Reduced delay
    speak(f"Task completed, sir. {name} is open.")

def close_active_tab():
    """Closes the currently active tab using a keyboard shortcut."""
    speak("Closing the active tab, sir.")
    pyautogui.hotkey('ctrl', 'w')
    time.sleep(0.5) # Reduced delay
    speak("Task completed.")

def search_web(command):
    """Searches the web for a given query."""
    search_term = command.replace('search for', '').strip()
    if search_term:
        speak(f"Searching for {search_term} on the web.")
        webbrowser.open(f"https://www.google.com/search?q={search_term}")
        time.sleep(1) # Reduced delay
        speak(f"Search for {search_term} completed.")
    else:
        speak("What would you like me to search for?")

def play_youtube(command):
    """Searches and plays the first video result on YouTube."""
    global youtube_search_results, current_video_index
    search_term = command.replace('play', '').strip()
    if not search_term:
        speak("What would you like me to play on YouTube?")
        return

    speak(f"Searching for {search_term} on YouTube.")
    try:
        search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
        response = requests.get(search_url)
        response.raise_for_status()
        
        video_ids = re.findall(r"\"videoId\":\"(.*?)\"", response.text)
        
        if video_ids:
            youtube_search_results = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]
            current_video_index = 0
            speak(f"Playing the first result for {search_term}.")
            webbrowser.open(youtube_search_results[current_video_index])
            time.sleep(1) # Reduced delay
            speak("Playback started, sir.")
        else:
            speak(f"I could not find any videos for '{search_term}', sir.")

    except Exception as e:
        speak("I encountered an error trying to find the video.")
        print(f"Error playing video: {e}")

def play_next_video():
    """Plays the next video from the previous YouTube search."""
    global current_video_index
    if youtube_search_results:
        current_video_index += 1
        if current_video_index < len(youtube_search_results):
            speak("Playing the next video, sir.")
            webbrowser.open(youtube_search_results[current_video_index])
            time.sleep(1) # Reduced delay
            speak("Playback started.")
        else:
            speak("I have reached the end of the search results, sir.")
    else:
        speak("You must first ask me to play something before you can ask for the next one.")

def open_notepad_and_dictate():
    """Opens Notepad and immediately starts dictation mode."""
    speak("Opening Notepad and initiating dictation mode.")
    try:
        os.startfile("notepad.exe")
        time.sleep(1) # Reduced delay
        dictate_mode()
    except Exception as e:
        speak("I could not find Notepad on your system.")
        print(e)

def dictate_mode():
    """Listens continuously and types out what is said."""
    speak("Dictation mode activated. Say 'stop dictation' to exit.")
    pyautogui.sleep(1) # Reduced delay

    while True:
        with sr.Microphone() as source:
            print("\nDictating...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language='en-in')
            print(f"Dictated: {text}")

            if 'stop dictation' in text.lower():
                speak("Deactivating dictation mode.")
                break
            
            pyautogui.typewrite(text + ' ')

        except sr.UnknownValueError:
            print("Could not understand audio, listening again.")
        except sr.RequestError:
            speak("Connection error, please check your internet and try again.")
            break

def ask_question():
    """Asks for a question, sends it to Gemini AI, and speaks the answer."""
    speak("Of course. What is your question?")
    question = take_command()
    if question:
        speak("Processing your query.")
        if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyAeA1W02ldiJM21j_1KXO0jujllKBHRnHY":
            speak("The Gemini API key is not configured. Please add it to the script to use this feature.")
            return
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": question}]}]}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status() 
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                answer = result['candidates'][0]['content']['parts'][0]['text']
                speak("According to my analysis:")
                speak(answer)
            else:
                speak("I received an unusual response from my systems. I am unable to answer at this time.")

        except requests.exceptions.RequestException as e:
            speak("I'm having trouble connecting to the AI service.")
            print(f"API Request Error: {e}")
        except Exception as e:
            speak("An error occurred while processing the AI response.")
            print(f"Error: {e}")

def shutdown(command):
    """Shuts down the JARVIS program."""
    speak("Shutting down systems. Goodbye, sir.")
    return "exit" # Return a signal to exit the loop

# --- Main Program Loop ---

def main():
    """The main function to run the JARVIS assistant."""
    greet_user()
    
    # This loop will continue until the shutdown command returns "exit"
    while True:
        command = take_command()
        
        if command is None:
            continue # If no command was heard, loop again

        # Command mapping
        if 'play' in command:
            play_youtube(command)
        elif 'next one' in command or 'play next' in command:
            play_next_video()
        elif 'search for' in command:
            search_web(command)
        elif 'open notepad' in command:
            open_notepad_and_dictate()
        elif 'start dictation' in command:
            dictate_mode()
        elif 'open google' in command:
            open_website("https://www.google.com", "Google")
        elif 'open youtube' in command:
            open_website("https://www.youtube.com", "YouTube")
        elif 'close youtube' in command or 'close google' in command or 'close tab' in command:
            close_active_tab()
        elif 'what time is it' in command:
            get_time()
        elif 'what is the date' in command:
            get_date()
        elif 'ask a question' in command:
            ask_question()
        elif 'goodbye' in command or 'shut down' in command or 'jarvis exit' in command:
            if shutdown(command) == "exit":
                break # Exit the loop
        elif 'thank you' in command:
            speak("You're welcome, sir.")
        elif 'hello' in command or 'hey jarvis' in command:
            speak("At your service, sir.")

if __name__ == '__main__':
    main()
