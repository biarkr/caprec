# caprec
it's screen capture tool that captures the character from selected area of screen then sends  it to chatgpt and gemini and shows the respose in the side bar


# AI-Based Text Extraction and Comparison Tool

## Overview
This application allows users to capture a specific region of their screen, extract text using Optical Character Recognition (OCR), and compare the responses generated by OpenAI's ChatGPT and Google's Gemini AI models. The extracted text is processed and displayed alongside the AI-generated responses for easy comparison.

## Features
- **Screen Capture**: Select a region of your screen for text extraction.
- **OCR Processing**: Extract text from the captured image using Tesseract OCR.
- **AI Comparison**: Send extracted text to both ChatGPT and Gemini AI for processing.
- **Live Preview**: Continuously updates the selected region preview.
- **Dark Mode UI**: Provides a visually comfortable interface.
- **Multi-threading**: Ensures smooth API calls without freezing the UI.

## Requirements
### Dependencies
Ensure you have the following installed:
- Python 3.8+
- OpenAI API Key
- Google Gemini API Key
- Required Python Libraries:
  ```sh
  pip install opencv-python numpy mss pytesseract Pillow google-generativeai openai tkinter
  ```
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
  - Windows users need to set the correct path:
    ```python
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    ```

## Installation & Usage
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/caprec.git
   cd ai-text-comparison
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Add API keys in the script:
   ```python
   client = OpenAI(api_key="your_openai_api_key")
   genai.configure(api_key="your_google_gemini_api_key")
   ```
4. Run the application:
   ```sh
   python main.py
   ```

## How to Use
1. Click **"Capture Region"** to select a portion of the screen.
2. Click **"Process Text"** to extract and send the text to ChatGPT and Gemini AI.
3. View responses side-by-side in the UI.

## Troubleshooting
- **No text is extracted?**
  - Ensure Tesseract is installed and configured correctly.
  - Increase the contrast of the captured text.
- **API errors?**
  - Check if API keys are correct and active.
  - Ensure you have an active internet connection.

## License
This project is licensed under the MIT License.

## Author
Developed by [Your Name].

