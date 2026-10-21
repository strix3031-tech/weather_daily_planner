# Weather-Based Daily Planner

A Flask web application that combines public weather forecasts with personal activity planning.

## Features

- City search using the Open-Meteo geocoding API
- Current conditions and five-day forecast
- Weather-aware activity suggestions
- Save and remove favourite locations
- Add and delete activity notes
- Persistent JSON file storage
- Ten-minute in-memory API cache
- Input validation, timeouts, and friendly API errors
- Responsive interface for desktop and mobile

## Requirements

- Python 3.10 or newer
- Internet connection
- VS Code (recommended)

## Run in VS Code

1. Open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment.

   Windows:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

5. Start the app:
   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser.

## API

This project uses Open-Meteo's public APIs:
- Geocoding: https://geocoding-api.open-meteo.com/v1/search
- Forecast: https://api.open-meteo.com/v1/forecast

No API key is needed for typical non-commercial use. Review the provider's terms for your intended use.

## Storage

Saved cities and notes are stored in `data/planner.json`, created automatically. The in-memory cache expires after ten minutes.

## Testing

Run:
```bash
python -m unittest discover -s tests -v
```

## Troubleshooting

- If the app cannot retrieve weather, check your internet connection.
- If Flask is missing, activate the virtual environment and install `requirements.txt`.
- If port 5000 is busy, stop the other process or change the port in `app.py`.
