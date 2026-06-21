# AI Multi-Language Translator

A Flask-based real-time AI language translator web application with a modern Google Translate-inspired UI, speech input, voice output, translation history, dark mode, and responsive UI.


## Features

- Text translation with source and target language dropdowns
- Auto language detection
- Real-time translation while typing
- Microphone speech-to-text
- Text-to-speech output using gTTS with pyttsx3 fallback
- Swap languages button
- Copy, clear, and speak controls
- Translation history saved in SQLite
- Light and dark mode with localStorage preference
- Responsive glassmorphism UI using Bootstrap 5 and FontAwesome

## Supported Languages

- English
- Telugu
- Hindi
- Tamil
- Kannada
- Malayalam
- Marathi
- Bengali
- Urdu
- French

## Folder Structure

```text
ai-multi-language-translator/
├── app.py
├── database.py
├── database.db
├── models.py
├── translator.py
├── speech.py
├── utils.py
├── requirements.txt
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   ├── audio/
│   └── images/
└── templates/
    ├── base.html
    ├── index.html
    ├── history.html

```

## How To Run

Open PowerShell and run these commands:

```powershell
cd D:\10kcoders\projects\ai-multi-language-translator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open this URL in your browser:

```text
http://127.0.0.1:5000
```

## Stop The App

In the PowerShell window where the app is running, press:

```text
Ctrl + C
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Main translator page |
| POST | `/translate` | Translate text |
| POST | `/speech-to-text` | Convert microphone speech to text |
| POST | `/text-to-speech` | Convert translated text to audio |
| GET | `/history` | History page |
| GET | `/api/history` | History JSON data |

## Troubleshooting

If `PyAudio` installation fails on Windows, try:

```powershell
pip install pipwin
pipwin install pyaudio
pip install -r requirements.txt
```

If translation does not work, check your internet connection. The app uses online translation providers through `deep-translator`.

If microphone input does not work, allow microphone permission in your browser and make sure your system microphone is enabled.

## Notes

- `database.db` is created automatically when the Flask app starts.
- Live translation requires internet access.
- Offline voice fallback requires `pyttsx3`.
- For production deployment, update the Flask `SECRET_KEY` in `app.py`.
