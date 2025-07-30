# JARVIS: AI HUD Voice Assistant by Girisudhan



A highly advanced, Python-based desktop voice assistant with a futuristic, data-rich "Heads-Up Display" (HUD) interface. Inspired by the iconic AI from the movies, this project leverages modern AI and multi-threading to create an interactive and responsive experience.

This isn't just a simple voice assistant; it's a sophisticated application featuring a hybrid command system, live system monitoring, and a true AI core for understanding natural language commands.

---

## 🌟 Features

* **Voice-Activated Control:** Hands-free operation using speech recognition.
* **Futuristic HUD Interface:** A custom-built `tkinter` interface with complex, multi-layered "Arc Reactor" animations that respond to the assistant's state (Idle, Listening, Thinking, Speaking).
* **Live System Monitoring:** Real-time data visualization of your computer's performance, including:
    * Dynamic CPU utilization graph.
    * Live RAM usage bar.
    * Real-time network activity (Upload/Download speed).
* **True AI Core (Gemini Function Calling):** Instead of rigid commands, JARVIS uses Google's Gemini AI to understand the *intent* of your natural language requests and execute the appropriate function ("tool").
* **Hybrid "Reflex" Command System for Speed:**
    * **Reflex Commands:** Simple, common commands (like getting the time, date, or opening Google) are handled instantly *without* AI for lightning-fast responses.
    * **AI Delegation:** Complex queries (like weather or web searches) are delegated to the AI core for intelligent processing.
* **Personalized Experience:** The assistant is configured to greet the owner, **Girisudhan V**, by name upon startup.
* **Useful Built-in Skills:** Includes tools for getting the time, date, live weather reports, and performing Google searches.
* **Immersive Fullscreen UI:** The application runs in a borderless, fullscreen window for a complete HUD experience (press `Esc` to exit).



## 🛠️ Architectural Overview

This application is built on a robust, multi-threaded architecture to ensure the UI remains smooth and responsive at all times.

* **UI Thread (Main):** Manages the `tkinter` window, draws all HUD elements, and runs the complex animations.
* **Backend Assistant Thread:** The "brain" of the operation. It handles the main loop of listening for voice commands, processing them through the Reflex System or the AI Core, and generating responses.
* **System Data Thread:** Runs in parallel to continuously fetch live system statistics (CPU, RAM, Network) using the `psutil` library.
* **Thread-Safe Communication:** A `queue.Queue` is used to pass messages safely from the backend threads to the main UI thread for updating the display (e.g., changing status text, updating graphs), preventing any freezing or race conditions.

---

## 🚀 Installation & Setup

Follow these steps to get JARVIS up and running on your system.

### 1. Prerequisites

* Python 3.8 or newer.
* Git for cloning the repository.
* A microphone connected to your computer.

### 2. Clone the Repository

Open your terminal or command prompt and clone the project:

```bash
git clone [https://github.com/your-username/jarvis-hud-assistant.git](https://github.com/your-username/jarvis-hud-assistant.git)
cd jarvis-hud-assistant
```

### 3. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

This project requires several Python libraries. Install them all using the provided `requirements.txt` file.

First, create a file named `requirements.txt` in your project folder and paste the following content into it:

```
speechrecognition
pyttsx3
pyaudio
pyautogui
requests
Pillow
psutil
```

Now, run the installation command:

```bash
pip install -r requirements.txt
```

*(Note: Installing `pyaudio` can sometimes be tricky. If you encounter issues, you may need to install system-level dependencies like `portaudio` or find a pre-compiled wheel for your system.)*

---

## ⚙️ Configuration

Before running the application, you need to configure two important settings at the top of the script.

### 1. Set Your Gemini API Key

This project uses the Google Gemini API for its AI capabilities.

1.  Get your free API key from **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
2.  Open the script and paste your key into the `GEMINI_API_KEY` variable:

    ```python
    GEMINI_API_KEY = "YOUR_SECRET_API_KEY_HERE"
    ```

### 2. Confirm Your Name

The owner's name is already set, but you can change it here if needed:

```python
OWNER_NAME = "xxx"
```

---

## ▶️ Usage

Once the installation and configuration are complete, run the application from your terminal:

```bash
python your_script_name.py
```

The application will launch in fullscreen. Start by saying "hello" or giving a command.

### Sample Commands

* **Reflex Commands (Instant):**
    * `"what time is it?"`
    * `"what's the date today?"`
    * `"open google"`
    * `"open youtube"`

* **AI-Powered Commands:**
    * `"search for the latest news on electric cars"`
    * `"what is the weather like in Chennai?"`
    * `"what is the capital of Japan?"` (General knowledge)

* **System Commands:**
    * `"goodbye"` or `"shut down"` to exit the application.

---

## 🔧 Key Technologies Used

* **GUI:** `tkinter`
* **Voice Recognition:** `SpeechRecognition` library (using Google Web Speech API)
* **Text-to-Speech:** `pyttsx3`
* **AI & NLP:** Google Gemini API
* **System Monitoring:** `psutil`
* **Web Interaction:** `requests`, `webbrowser`

---

## 🔮 Future Enhancements (Roadmap)

* **Add More Tools:** Integrate new skills like controlling Spotify, sending emails, or managing a to-do list.
* **Audio-Reactive Visualizer:** Re-integrate the `pyaudio` live visualizer to make the central core pulse in real-time with your voice.
* **Settings Panel:** Create a settings screen within the UI to change API keys, voices, and colors without editing the code.
* **Conversation Memory:** Implement a system to remember the context of the last few interactions for follow-up questions.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## 🙏 Acknowledgments

* Inspired by the incredible work in the Marvel Cinematic Universe.
* Thanks to the developers of all the open-source libraries that made this project possible.
