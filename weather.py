"""Open-Meteo geocoding and forecast client with a small in-memory cache."""
import time
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL_SECONDS = 600
_cache = {}
_session = requests.Session()


class WeatherError(Exception):
    """Friendly error raised when weather data cannot be retrieved."""


def _cached_get(key, url, params):
    now = time.time()
    item = _cache.get(key)
    if item and now - item["time"] < CACHE_TTL_SECONDS:
        return item["value"]
    try:
        response = _session.get(url, params=params, timeout=8)
        response.raise_for_status()
        result = response.json()
    except requests.Timeout as exc:
        raise WeatherError("The weather service timed out. Please try again.") from exc
    except requests.RequestException as exc:
        raise WeatherError("Could not connect to the weather service. Check your internet.") from exc
    except ValueError as exc:
        raise WeatherError("The weather service returned invalid data.") from exc
    _cache[key] = {"time": now, "value": result}
    return result


def get_weather(city):
    city = city.strip()
    if not city:
        raise WeatherError("Please enter a city name.")

    locations = _cached_get(
        "geo:" + city.casefold(), GEOCODING_URL,
        {"name": city, "count": 1, "language": "en", "format": "json"}
    )
    results = locations.get("results") or []
    if not results:
        raise WeatherError(f"No location found for “{city}”. Check the spelling.")

    place = results[0]
    lat, lon = place.get("latitude"), place.get("longitude")
    if lat is None or lon is None:
        raise WeatherError("The location service returned incomplete coordinates.")

    forecast = _cached_get(
        f"forecast:{lat}:{lon}", FORECAST_URL,
        {
            "latitude": lat, "longitude": lon,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
            "timezone": "auto", "forecast_days": 5
        }
    )
    current = forecast.get("current")
    daily = forecast.get("daily")
    if not current or not daily or not daily.get("time"):
        raise WeatherError("Forecast data is temporarily incomplete.")

    return {
        "name": place.get("name", city),
        "region": ", ".join(x for x in [place.get("admin1"), place.get("country")] if x),
        "current": current,
        "daily": daily,
        "timezone": forecast.get("timezone", "Local time")
    }


def describe_code(code):
    """Readable labels for common WMO weather interpretation codes."""
    if code == 0: return "Clear sky"
    if code in (1, 2, 3): return "Mainly clear / partly cloudy"
    if code in (45, 48): return "Fog"
    if code in (51, 53, 55, 56, 57): return "Drizzle"
    if code in (61, 63, 65, 66, 67): return "Rain"
    if code in (71, 73, 75, 77): return "Snow"
    if code in (80, 81, 82): return "Rain showers"
    if code in (85, 86): return "Snow showers"
    if code in (95, 96, 99): return "Thunderstorm"
    return "Weather conditions"


def activity_tip(code, max_temp, rain_chance):
    if code in (95, 96, 99) or rain_chance >= 70:
        return "Prefer indoor plans; carry rain protection if you must go out."
    if max_temp >= 35:
        return "Plan outdoor activities early or late, drink water, and seek shade."
    if code in (61, 63, 65, 80, 81, 82):
        return "Keep a raincoat or umbrella ready; consider flexible outdoor plans."
    if max_temp <= 10:
        return "Dress warmly and consider a shorter outdoor activity."
    return "Good day to schedule a walk, errands, or other outdoor activities if conditions suit."
