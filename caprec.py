import cv2
import numpy as np
from mss import mss
import pytesseract
from tkinter import Tk, Label, Button, Canvas, PhotoImage, Scrollbar, Text, Toplevel, Frame
from tkinter import messagebox
from threading import Thread, Lock
from PIL import Image, ImageTk
import google.generativeai as genai
from openai import OpenAI

# Configure OpenAI with your API key
client = OpenAI(api_key="your API key paste here")
# Configure Gemini API with your API key
genai.configure(api_key="your API key paste here")  # Replace with your Google API key
gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Initialize MSS for screen capture
sct = mss()

# Set Tesseract executable path (update for Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Lock for thread-safe API response updates
response_lock = Lock()

# Function to process and extract text using OCR
def extract_text(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    config = "--psm 6"  # Assume block of text for better performance
    text = pytesseract.image_to_string(thresholded, config=config)
    return text.strip()

# Function to send text to ChatGPT API in a thread
def send_to_chatgpt_async(text, response_container):
    try:
        modified_text = text + "\nAnswer only with correct answers. No explanation, please."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": modified_text}
            ]
        )
        with response_lock:
            response_container["chatgpt"] = response.choices[0].message.content.strip()
    except Exception as e:
        with response_lock:
            response_container["chatgpt"] = f"API Error: {str(e)}"

# Function to send text to Gemini API in a thread
def send_to_gemini_api_async(text, response_container):
    try:
        modified_text = text + " give me only correct answers no description or explanation please"
        response = gemini_model.generate_content(modified_text)
        with response_lock:
            response_container["gemini"] = response.text
    except Exception as e:
        with response_lock:
            response_container["gemini"] = f"API Error: {str(e)}"

class AIComparisonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moye Moye")

        # Initialize variables
        self.region = None
        self.captured_text = ""
        self.api_response = {"chatgpt": "", "gemini": ""}
        self.chatgpt_thread = None
        self.gemini_thread = None
        self.live_preview = None

        # Dark mode color scheme
        self.bg_color = "#2E2E2E"
        self.text_color = "#FFFFFF"
        self.button_bg = "#4CAF50"
        self.button_hover_bg = "#45a049"

        # Create layout
        self.root.config(bg=self.bg_color)

        # Canvas for live preview
        self.preview_canvas = Canvas(root, width=400, height=400, bg="black")
        self.preview_canvas.pack(side="left", fill="both", expand=False)

        self.result_frame = Frame(root, bg=self.bg_color)
        self.result_frame.pack(side="right", fill="both", expand=True)

        self.result_text = Text(self.result_frame, wrap="word", height=10, width=50, font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
        self.result_text.pack(fill="both", expand=True)

        self.chatgpt_text = Text(self.result_frame, wrap="word", height=10, width=50, font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
        self.chatgpt_text.pack(fill="both", expand=True)

        self.gemini_text = Text(self.result_frame, wrap="word", height=10, width=50, font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
        self.gemini_text.pack(fill="both", expand=True)

        # Add buttons
        self.capture_button = Button(root, text="Capture Region", command=self.select_region, bg=self.button_bg, activebackground=self.button_hover_bg)
        self.capture_button.pack(fill="x")

        self.process_button = Button(root, text="Process Text", command=self.process_text, bg=self.button_bg, activebackground=self.button_hover_bg)
        self.process_button.pack(fill="x")

        self.quit_button = Button(root, text="Quit", command=root.quit, bg=self.button_bg, activebackground=self.button_hover_bg)
        self.quit_button.pack(fill="x")

        # Add Status Indicator
        self.status_label = Label(root, text="Ready", fg="green", bg=self.bg_color, font=("Arial", 10))
        self.status_label.pack(side="bottom", fill="x")

        self.root.bind("<space>", self.capture_and_process_shortcut)

        self.update_live_preview()

    def select_region(self):
        temp_frame = np.array(sct.grab(sct.monitors[0]))
        temp_frame = cv2.cvtColor(temp_frame, cv2.COLOR_BGRA2BGR)
        region = cv2.selectROI("Select Region", temp_frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select Region")

        self.region = {
            "top": int(region[1]),
            "left": int(region[0]),
            "width": int(region[2]),
            "height": int(region[3]),
        }

    def update_live_preview(self):
        if self.region:
            screenshot = sct.grab(self.region)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            frame = cv2.resize(frame, (400, 400))
            self.live_preview = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.preview_canvas.create_image(0, 0, anchor="nw", image=self.live_preview)
        self.root.after(100, self.update_live_preview)

    def process_text(self):
        if not self.region:
            messagebox.showwarning("No Region", "Please select a region before processing.")
            return

        # Capture region and extract text
        screenshot = sct.grab(self.region)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        self.captured_text = extract_text(frame)
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", f"Captured Text:\n{self.captured_text}\n\n")

        # Start API calls
        self.api_response["chatgpt"] = "Processing ChatGPT..."
        self.api_response["gemini"] = "Processing Gemini..."

        # Update status
        self.status_label.config(text="Processing...", fg="orange")

        if self.chatgpt_thread is None or not self.chatgpt_thread.is_alive():
            self.chatgpt_thread = Thread(target=send_to_chatgpt_async, args=(self.captured_text, self.api_response))
            self.chatgpt_thread.start()

        if self.gemini_thread is None or not self.gemini_thread.is_alive():
            self.gemini_thread = Thread(target=send_to_gemini_api_async, args=(self.captured_text, self.api_response))
            self.gemini_thread.start()

        self.update_results()

    def capture_and_process_shortcut(self, event):
        self.process_text()

    def update_results(self):
        with response_lock:
            chatgpt_response = self.api_response["chatgpt"]
            gemini_response = self.api_response["gemini"]

        self.chatgpt_text.delete("1.0", "end")
        self.chatgpt_text.insert("end", f"ChatGPT Response:\n{chatgpt_response}\n\n")

        self.gemini_text.delete("1.0", "end")
        self.gemini_text.insert("end", f"Gemini Response:\n{gemini_response}\n\n")

        if self.chatgpt_thread.is_alive() or self.gemini_thread.is_alive():
            self.root.after(500, self.update_results)
        else:
            self.status_label.config(text="Ready", fg="green")

if __name__ == "__main__":
    root = Tk()
    app = AIComparisonApp(root)
    root.mainloop()
