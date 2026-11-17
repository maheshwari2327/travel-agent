import requests
from langchain_core.tools import tool

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@tool
def get_destination_info(city: str) -> str:
    """
    Get current weather and 3-day travel forecast for any destination city.
    Returns temperature, conditions, humidity, wind speed, and travel tips.
    Uses free Open-Meteo API — no API key required.
    """
    try:
        # Step 1 — Geocode
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1, "language": "en"}
        geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        results = geo_data.get("results")
        if not results:
            return f"Destination '{city}' not found. Please verify the city name."

        location = results[0]
        name = location.get("name", city)
        country = location.get("country", "")
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        # Step 2 — Fetch weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weathercode",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "forecast_days": 3,
            "timezone": "auto",
        }
        weather_resp = requests.get(weather_url, params=weather_params, timeout=10)
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()

        # Step 3 — Format response
        current = weather_data.get("current", {})
        daily = weather_data.get("daily", {})

        temp = current.get("temperature_2m", 0)
        feels = current.get("apparent_temperature", 0)
        humidity = current.get("relative_humidity_2m", 0)
        wind = current.get("wind_speed_10m", 0)
        weather_code = current.get("weathercode", 0)
        condition = WMO_WEATHER_CODES.get(weather_code, "Unknown")

        # Apply travel tip based on current temperature
        if temp < 5:
            travel_tip = "Very cold — pack heavy winter clothing."
        elif temp < 15:
            travel_tip = "Cool weather — bring a jacket."
        elif temp <= 28:
            travel_tip = "Pleasant weather — great for sightseeing!"
        elif temp <= 35:
            travel_tip = "Warm — stay hydrated and use sunscreen."
        else:
            travel_tip = "Extremely hot — limit outdoor activities midday."

        forecast_lines = []
        times = daily.get("time", [])
        min_temps = daily.get("temperature_2m_min", [])
        max_temps = daily.get("temperature_2m_max", [])
        precip_probs = daily.get("precipitation_probability_max", [])
        codes = daily.get("weathercode", [])

        for i in range(len(times)):
            d_date = times[i]
            d_lo = min_temps[i] if i < len(min_temps) else "N/A"
            d_hi = max_temps[i] if i < len(max_temps) else "N/A"
            d_code = codes[i] if i < len(codes) else 0
            d_cond = WMO_WEATHER_CODES.get(d_code, "Unknown")
            d_rain = precip_probs[i] if i < len(precip_probs) else 0
            forecast_lines.append(f"  {d_date}: {d_lo}°C – {d_hi}°C | {d_cond} | Rain: {d_rain}%")

        forecast_str = "\n".join(forecast_lines)
        country_suffix = f", {country}" if country else ""

        return (
            f"=== Travel Info: {name}{country_suffix} ===\n"
            f"Current Conditions: {condition}\n"
            f"Temperature: {temp}°C (feels like {feels}°C)\n"
            f"Humidity: {humidity}%  |  Wind: {wind} km/h\n\n"
            f"3-Day Forecast:\n"
            f"{forecast_str}\n\n"
            f"Travel Tip: {travel_tip}"
        )

    except Exception as e:
        return f"Error retrieving travel info for '{city}': {e}"
