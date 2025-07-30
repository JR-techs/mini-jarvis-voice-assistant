import customtkinter as ctk
import threading
import queue
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import json
import time
import re
import random
import math
from PIL import Image, ImageTk

# --- Configuration ---
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your actual key

# --- State Management ---
Youtube_results = []
current_video_index = 0

# ==================================================================================
# --- BACKEND JARVIS LOGIC ---
# ==================================================================================

class JarvisBackend:
    def __init__(self, gui_queue):
        self.gui_queue = gui_queue
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
        self.running = True
        self.last_command_time = time.time()

    def speak(self, text):
        self.gui_queue.put(('jarvis_speak', text))
        self.engine.say(text)
        self.engine.runAndWait()
        self.engine.stop()  # Add this to prevent speech queue buildup

    def take_command(self):
        with sr.Microphone() as source:
            self.gui_queue.put(('update_status', "Listening..."))
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)
        try:
            self.gui_queue.put(('update_status', "Processing..."))
            command = self.recognizer.recognize_google(audio, language='en-in').lower()
            self.gui_queue.put(('user_said', f"You: {command}"))
            self.last_command_time = time.time()
            return command
        except (sr.UnknownValueError, sr.RequestError):
            return "None"

    def ask_gemini(self, question):
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            self.speak("Gemini API key is not configured.")
            return
        self.gui_queue.put(('update_status', "Contacting Gemini AI..."))
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts": [{"text": question}]}]}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            if 'candidates' in result and result['candidates']:
                answer = result['candidates'][0]['content']['parts'][0]['text']
                self.speak(answer)
            else:
                self.speak("I couldn't get a response from Gemini.")
        except Exception as e:
            self.speak("An error occurred while contacting Gemini.")
            print(f"Gemini API error: {e}")

    def run(self):
        global Youtube_results, current_video_index
        self.speak("JARVIS system is online and ready.")

        while self.running:
            command = self.take_command()
            self.gui_queue.put(('update_status', "Idle"))

            if command == "None":
                continue

            # --- Core Commands ---
            if 'open google' in command:
                self.speak("Opening Google, sir.")
                webbrowser.open("https://www.google.com")

            elif 'open youtube' in command:
                self.speak("Opening YouTube.")
                webbrowser.open("https://www.youtube.com")

            elif 'search for' in command:
                search_term = command.replace('search for', '').strip()
                if search_term:
                    self.speak(f"Here are the web results for {search_term}.")
                    webbrowser.open(f"https://www.google.com/search?q={search_term}")
                else:
                    self.speak("What would you like me to search for?")

            elif 'play' in command:
                search_term = command.replace('play', '').strip()
                if search_term:
                    self.speak(f"Searching YouTube for {search_term}.")
                    try:
                        search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
                        response = requests.get(search_url)
                        response.raise_for_status()
                        video_ids = re.findall(r"\"videoId\":\"(.*?)\"", response.text)
                        if video_ids:
                            Youtube_results = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]
                            current_video_index = 0
                            self.speak(f"Playing the first result for {search_term}.")
                            webbrowser.open(Youtube_results[current_video_index])
                        else:
                            self.speak("I could not find any videos for that search.")
                    except Exception as e:
                        self.speak("I encountered an error trying to find the video.")
                        print(f"Error playing video: {e}")
                else:
                    self.speak("What would you like me to play?")

            elif 'next one' in command or 'play next' in command:
                if Youtube_results:
                    current_video_index += 1
                    if current_video_index < len(Youtube_results):
                        self.speak("Playing the next video.")
                        webbrowser.open(Youtube_results[current_video_index])
                    else:
                        self.speak("That was the last video in the search results, sir.")
                else:
                    self.speak("You need to play something first before you can ask for the next one.")

            elif 'ask a question' in command:
                self.speak("Of course. What is your question?")
                question = self.take_command()
                if question and question != "None":
                    self.ask_gemini(question)

            elif 'what time is it' in command:
                str_time = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f"The time is {str_time}")

            elif 'goodbye' in command or 'shut down' in command:
                self.speak("Shutting down. Goodbye, sir.")
                self.running = False
                self.gui_queue.put(('shutdown', ''))
                break

            elif 'system status' in command:
                uptime = time.time() - self.last_command_time
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                self.speak(f"System is operational. Uptime: {hours} hours and {minutes} minutes.")

# ==================================================================================
# --- ENHANCED VISUAL COMPONENTS ---
# ==================================================================================

class Particle:
    def __init__(self, canvas, **kwargs):
        self.canvas = canvas
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)
        self.vx = kwargs.get('vx', 0)
        self.vy = kwargs.get('vy', 0)
        self.radius = kwargs.get('radius', 3)
        self.color = kwargs.get('color', "#00aeef")
        self.behavior = kwargs.get('behavior', "drift")
        self.lifespan = random.randint(100, 255)
        self.alpha = 255
        self.id = None
        self.create_particle()

    def create_particle(self):
        x0, y0 = self.x - self.radius, self.y - self.radius
        x1, y1 = self.x + self.radius, self.y + self.radius
        self.id = self.canvas.create_oval(x0, y0, x1, y1, fill=self.color, outline="")

    def update(self, center_x=0, center_y=0):
        if self.behavior == "drift":
            self.vy -= 0.05
            self.vx *= 0.99
        elif self.behavior == "vortex":
            angle = math.atan2(self.y - center_y, self.x - center_x)
            force = 0.5 + (0.5 * math.sin(time.time() * 2))
            self.vx = -math.sin(angle) * force * 3
            self.vy = math.cos(angle) * force * 3
        elif self.behavior == "burst":
            self.vx *= 0.95
            self.vy *= 0.95

        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 2
        self.alpha = max(0, self.lifespan)

        if self.alpha > 0:
            r, g, b = self.hex_to_rgb(self.color)
            faded_color = f'#{int(r*self.alpha/255):02x}{int(g*self.alpha/255):02x}{int(b*self.alpha/255):02x}'
            self.canvas.coords(self.id, 
                             self.x - self.radius, 
                             self.y - self.radius, 
                             self.x + self.radius, 
                             self.y + self.radius)
            self.canvas.itemconfig(self.id, fill=faded_color)
            return True
        else:
            self.canvas.delete(self.id)
            return False

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class AnimatedGauge(ctk.CTkCanvas):
    def __init__(self, master, width=200, height=20, **kwargs):
        # Use a solid color instead of trying to get it from master
        bg_color = "#092135"  # Same as your panel_color
        super().__init__(master, width=width, height=height, bg=bg_color, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.value = 0
        self.target_value = 0
        self.animation_id = None
        self.draw_gauge()

    def draw_gauge(self):
        self.delete("all")
        # Background - using slightly darker color
        self.create_rectangle(0, 0, self.width, self.height, 
                            fill="#071a2a", outline="#071a2a")
        # Active fill
        current_width = int(self.width * self.value / 100)
        self.create_rectangle(0, 0, current_width, self.height, 
                            fill="#00aeef", outline="#00aeef")
        # Pulsing effect when active
        if self.value > 0 and self.value < 100:
            pulse_width = current_width + 5 * math.sin(time.time() * 5)
            self.create_rectangle(0, 0, pulse_width, self.height, 
                                fill="#00aeef", outline="#00aeef", stipple="gray50")

    def set_value(self, value, animate=True):
        self.target_value = max(0, min(100, value))
        if not animate:
            self.value = self.target_value
            self.draw_gauge()
        elif not self.animation_id:
            self.animate()

    def animate(self):
        step = (self.target_value - self.value) * 0.1
        if abs(step) < 0.5:
            self.value = self.target_value
            self.animation_id = None
        else:
            self.value += step
            self.animation_id = self.after(16, self.animate)
        self.draw_gauge()

# ==================================================================================
# --- PROFESSIONAL GUI WITH OPTIMIZED ANIMATIONS ---
# ==================================================================================

class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("J.A.R.V.I.S. AI System")
        self.geometry("900x700")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Custom dark theme colors
        self.bg_color = "#031526"
        self.panel_color = "#092135"
        self.accent_color = "#00aeef"
        self.text_color = "#ffffff"
        
        self.configure(fg_color=self.bg_color)
        
        # Animation variables
        self.particles = []
        self.active_mode = "idle"  # idle, listening, processing
        self.last_animation_time = time.time()
        
        # System queue
        self.gui_queue = queue.Queue()
        self.backend = JarvisBackend(self.gui_queue)
        self.backend_thread = threading.Thread(target=self.backend.run, daemon=True)
        self.backend_thread.start()
        
        self.create_widgets()
        self.after(100, self.update_animations)
        self.after(100, self.process_queue)

    def create_widgets(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color=self.panel_color, corner_radius=20)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Header with logo and status
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="#092135")  
        self.header_frame.pack(pady=(10, 0), padx=10, fill="x")
        
        # Logo label with animation
        self.logo_label = ctk.CTkLabel(self.header_frame, 
                                     text="J.A.R.V.I.S.", 
                                     font=ctk.CTkFont(size=24, weight="bold", family="Arial"),
                                     text_color=self.accent_color)
        self.logo_label.pack(side="left")
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(self.header_frame, 
                                           text="●", 
                                           font=ctk.CTkFont(size=16),
                                           text_color="#555555")
        self.status_indicator.pack(side="right", padx=10)
        
        # Voice activity gauge
        self.gauge = AnimatedGauge(self.header_frame, width=150, height=8)
        self.gauge.pack(side="right", padx=10)
        
        # Particle canvas for visual effects
        self.canvas = ctk.CTkCanvas(self.main_frame, bg=self.panel_color, highlightthickness=0)
        self.canvas.pack(pady=(10, 0), fill="x", expand=False, ipady=80)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.main_frame, 
                                        text="Initializing...", 
                                        font=ctk.CTkFont(size=16, weight="bold"), 
                                        text_color=self.text_color)
        self.status_label.pack(pady=(10, 0))
        
        # Conversation log
        self.log_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.log_frame.pack(pady=(10, 0), padx=10, fill="both", expand=True)
        
        self.log_textbox = ctk.CTkTextbox(self.log_frame, 
                                         font=ctk.CTkFont(size=14, family="Consolas"), 
                                         corner_radius=10, 
                                         border_width=2, 
                                         border_color=self.accent_color, 
                                         fg_color="#031526",
                                         wrap="word")
        self.log_textbox.pack(fill="both", expand=True)
        self.log_textbox.configure(state="disabled")
        
        # Configure text tags
        self.log_textbox.tag_config("jarvis", foreground=self.accent_color)
        self.log_textbox.tag_config("user", foreground=self.text_color)
        self.log_textbox.tag_config("system", foreground="#aaaaaa")
        
        # Control buttons
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(pady=(0, 10), fill="x")
        
        self.voice_button = ctk.CTkButton(self.button_frame, 
                                         text="VOICE COMMAND", 
                                         command=self.trigger_voice_command,
                                         fg_color=self.accent_color,
                                         hover_color="#0088cc",
                                         font=ctk.CTkFont(weight="bold"))
        self.voice_button.pack(side="left", padx=5, expand=True, fill="x")
        
        self.quit_button = ctk.CTkButton(self.button_frame, 
                                        text="SHUT DOWN", 
                                        command=self.on_closing,
                                        fg_color="#d32f2f",
                                        hover_color="#b71c1c",
                                        font=ctk.CTkFont(weight="bold"))
        self.quit_button.pack(side="left", padx=5, expand=True, fill="x")

    def trigger_voice_command(self):
            # Simulate voice command trigger
            self.gui_queue.put(('update_status', "Listening..."))
        
    def create_particles(self, count, behavior="drift"):
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        colors = ["#00aeef", "#0088cc", "#00c8ff", "#0066aa"]
        
        for _ in range(count):
            if behavior == "burst":
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 5)
                x, y = canvas_w/2, canvas_h/2
                vx, vy = math.cos(angle)*speed, math.sin(angle)*speed
                radius = random.uniform(1, 4)
            elif behavior == "vortex":
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0, canvas_w/3)
                x = canvas_w/2 + math.cos(angle) * dist
                y = canvas_h/2 + math.sin(angle) * dist
                vx, vy = random.uniform(-1, 1), random.uniform(-1, 1)
                radius = random.uniform(1, 3)
            else:  # drift
                x = random.uniform(0, canvas_w)
                y = random.uniform(canvas_h-20, canvas_h)
                vx = random.uniform(-0.5, 0.5)
                vy = random.uniform(-2, -1)
                radius = random.uniform(1, 3)
            
            color = random.choice(colors)
            self.particles.append(Particle(
                canvas=self.canvas,
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                color=color,
                radius=radius,
                behavior=behavior
            ))

    def update_animations(self):
        current_time = time.time()
        
        # Get canvas dimensions
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        # Update status indicator
        if self.active_mode == "listening":
            pulse = 0.5 * (1 + math.sin(current_time * 10))
            self.status_indicator.configure(text_color=f"#ff{int(255*(1-pulse)):02x}{int(255*(1-pulse)):02x}")
            self.gauge.set_value(50 + 50 * pulse)
        elif self.active_mode == "processing":
            pulse = 0.5 * (1 + math.sin(current_time * 3))
            self.status_indicator.configure(text_color=f"#00{int(174 + 81*pulse):02x}{int(239 - 81*pulse):02x}")
            self.gauge.set_value(30 + 20 * pulse)
        else:  # idle
            self.status_indicator.configure(text_color="#555555")
            self.gauge.set_value(0)
        
        # Update particles based on mode
        if self.active_mode == "listening" and current_time - self.last_animation_time > 0.1:
            self.create_particles(2, "burst")
            self.last_animation_time = current_time
        elif self.active_mode == "processing" and current_time - self.last_animation_time > 0.2:
            self.create_particles(1, "vortex")
            self.last_animation_time = current_time
        elif self.active_mode == "idle" and current_time - self.last_animation_time > 0.3:
            self.create_particles(1, "drift")
            self.last_animation_time = current_time
        
        # Update all particles with proper canvas dimensions
        self.particles = [p for p in self.particles if p.update(canvas_w/2, canvas_h/2)]
        
        self.after(16, self.update_animations)

    def process_queue(self):
        try:
            while True:
                message_type, data = self.gui_queue.get_nowait()
                
                if message_type == 'update_status':
                    self.status_label.configure(text=data)
                    if "Listening" in data:
                        self.active_mode = "listening"
                    elif "Processing" in data or "Contacting" in data:
                        self.active_mode = "processing"
                    else:
                        self.active_mode = "idle"
                
                elif message_type == 'jarvis_speak':
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.insert("end", f"JARVIS: {data}\n", "jarvis")
                    self.log_textbox.configure(state="disabled")
                    self.log_textbox.see("end")
                
                elif message_type == 'user_said':
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.insert("end", f"{data}\n", "user")
                    self.log_textbox.configure(state="disabled")
                    self.log_textbox.see("end")
                
                elif message_type == 'shutdown':
                    self.destroy()
                    return
                    
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)
    
    def on_closing(self):
        self.backend.running = False
        self.after(200, self.destroy)

if __name__ == "__main__":
    app = JarvisGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()