import streamlit as st
import requests
import pandas as pd
import joblib
import os
from datetime import datetime

# ========================
# 🌿 CONFIGURATION
# ========================
st.set_page_config(
    page_title="Breathify — Air Quality Advisory for Pakistan",
    page_icon="🌿",
    layout="centered",
)

# ========================
# 🎨 STYLING
# ========================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 720px;
        }

        /* ── HERO ── */
        .hero {
            text-align: center;
            padding: 36px 24px 28px;
            border-radius: 20px;
            background: linear-gradient(140deg, #d4f5e2 0%, #eafaf1 60%, #c8f0da 100%);
            border: 1px solid #b2e8c8;
            margin-bottom: 28px;
        }
        .hero-eyebrow {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #27ae60;
            margin-bottom: 10px;
        }
        .hero h1 {
            font-size: 44px;
            font-weight: 800;
            color: #1a5c38;
            margin: 0 0 6px 0;
            line-height: 1.1;
        }
        .hero-sub {
            font-size: 15px;
            color: #4a7c5e;
            margin: 0;
            font-weight: 500;
        }

        /* ── INPUT CARD ── */
        .input-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 16px;
            padding: 20px 24px 16px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .input-label {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #888;
            margin-bottom: 8px;
        }

        /* ── Streamlit input override ── */
        div[data-testid="stTextInput"] input {
            border-radius: 10px !important;
            border: 1.5px solid #d0d0d0 !important;
            padding: 10px 14px !important;
            font-size: 15px !important;
            font-family: 'Inter', sans-serif !important;
            max-width: 320px !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #27ae60 !important;
            box-shadow: 0 0 0 3px rgba(39,174,96,0.12) !important;
        }

        /* ── BUTTON ── */
        div[data-testid="stButton"] button {
            background-color: #1a5c38 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 24px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            cursor: pointer !important;
            transition: background 0.2s ease !important;
            width: auto !important;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #27ae60 !important;
        }

        /* ── RESULT CARD ── */
        .result-card {
            border-radius: 16px;
            padding: 22px 26px;
            border-left: 6px solid;
            box-shadow: 0 4px 16px rgba(0,0,0,0.07);
            margin-top: 4px;
        }
        .result-category {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 4px;
            opacity: 0.7;
        }
        .result-title {
            font-size: 26px;
            font-weight: 800;
            margin: 0 0 14px 0;
            line-height: 1.2;
        }
        .result-advisory {
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .result-urdu {
            font-size: 15px;
            line-height: 1.8;
            text-align: right;
            direction: rtl;
            background: rgba(255,255,255,0.35);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 14px;
        }
        .result-meta {
            font-size: 11px;
            opacity: 0.6;
            font-weight: 500;
            letter-spacing: 0.3px;
        }

        /* ── POLLUTANT PILLS ── */
        .pills-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }
        .pill {
            background: rgba(255,255,255,0.5);
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 600;
        }

        /* ── FOOTER ── */
        .footer {
            text-align: center;
            padding-top: 20px;
            font-size: 12px;
            color: #aaa;
        }

        /* hide streamlit default footer */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ========================
# 🌿 HERO HEADER
# ========================
st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">🌍 Real-Time Monitoring</div>
        <h1>🌿 Breathify</h1>
        <p class="hero-sub">AI-powered air quality & health advisory for Pakistan</p>
    </div>
""", unsafe_allow_html=True)

# ========================
# ⚙️ Load Model & Scaler
# ========================
try:
    model = joblib.load(r"C:\Users\User\Desktop\AQI project\aqi_lightgbm_model.pkl")
    scaler = joblib.load(r"C:\Users\User\Desktop\AQI project\aqi_scaler.pkl")
except Exception as e:
    st.error(f"❌ Error loading model/scaler: {e}")
    st.stop()

# ========================
# 🌦️ API Functions
# ========================
OPENWEATHER_KEY = "enter your openweather key here"  # replace with your API key

def get_live_data(city_name):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},PK&limit=1&appid={OPENWEATHER_KEY}"
    geo_data = requests.get(geo_url).json()
    if not geo_data:
        raise ValueError("City not found.")

    lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
    air_data = requests.get(
        f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
    ).json()
    weather_data = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,surface_pressure,wind_speed_10m,wind_direction_10m,shortwave_radiation"
    ).json()

    if 'current' not in weather_data or 'list' not in air_data:
        raise ValueError("Incomplete API response.")

    air = air_data['list'][0]['components']
    weather = weather_data['current']

    return pd.DataFrame([{
        "components_co": air.get("co", 0),
        "components_no": air.get("no", 0),
        "components_no2": air.get("no2", 0),
        "components_o3": air.get("o3", 0),
        "components_so2": air.get("so2", 0),
        "components_pm2_5": air.get("pm2_5", 0),
        "components_pm10": air.get("pm10", 0),
        "components_nh3": air.get("nh3", 0),
        "temperature_2m": weather.get("temperature_2m", 0),
        "relative_humidity_2m": weather.get("relative_humidity_2m", 0),
        "dew_point_2m": weather.get("dew_point_2m", 0),
        "precipitation": weather.get("precipitation", 0),
        "surface_pressure": weather.get("surface_pressure", 0),
        "wind_speed_10m": weather.get("wind_speed_10m", 0),
        "wind_direction_10m": weather.get("wind_direction_10m", 0),
        "shortwave_radiation": weather.get("shortwave_radiation", 0)
    }])

# ========================
# 💬 Advisory Function
# ========================
def get_advisory(aqi_class, temperature=None, humidity=None):
    configs = {
        1: ("Good",      "#d4f5e2", "#1a5c38", "#27ae60",
            "Air quality is clean and safe. Great day to go outside.",
            "ہوا صاف اور محفوظ ہے۔ باہر نکلنے کا بہترین وقت ہے۔"),
        2: ("Fair",      "#eafaf1", "#1a5c38", "#52be80",
            "Acceptable air quality. Sensitive groups should limit extended outdoor activity.",
            "ہوا معتدل ہے۔ حساس افراد زیادہ دیر باہر نہ رہیں۔"),
        3: ("Moderate",  "#fff8e7", "#7d5a00", "#f0a500",
            "Moderate pollution detected. Wear a mask outdoors if you feel discomfort.",
            "ہوا میں آلودگی ہے۔ باہر جائیں تو ماسک پہنیں۔"),
        4: ("Poor",      "#fff0ed", "#7d2000", "#e05c2a",
            "Unhealthy air. Avoid prolonged outdoor exposure. Keep children indoors.",
            "ہوا آلودہ ہے۔ بچوں کو گھر پر رکھیں اور ماسک لازمی پہنیں۔"),
        5: ("Very Poor", "#fde8e8", "#6b0000", "#c0392b",
            "Extremely unhealthy air. Avoid all outdoor exposure.",
            "انتہائی آلودہ ہوا۔ باہر جانے سے مکمل گریز کریں۔"),
    }
    cat, bg, text, border, en, ur = configs.get(aqi_class, configs[5])

    if humidity and humidity > 70:
        en += " High humidity may worsen breathing — ventilate indoors."
        ur += " زیادہ نمی سانس میں دشواری بڑھا سکتی ہے۔"
    if temperature and temperature > 35:
        en += " Stay hydrated in the heat."
        ur += " گرمی میں پانی زیادہ پیئیں۔"

    return cat, bg, text, border, en, ur

# ========================
# 🚀 MAIN LAYOUT
# ========================
col_input, col_result = st.columns([1, 1.4], gap="large")

with col_input:
    st.markdown('<div class="input-label">Select City</div>', unsafe_allow_html=True)
    city_name = st.selectbox(
        label="city",
        options=["Karachi", "Lahore", "Islamabad", "Peshawar", "Quetta"],
        label_visibility="collapsed"
    )
    check = st.button("🔍 Check Air Quality")

    if check:
        with st.spinner("Fetching live data..."):
            try:
                df = get_live_data(city_name)
                df_scaled = pd.DataFrame(scaler.transform(df), columns=df.columns)
                prediction = model.predict(df_scaled)[0]
                temperature = df["temperature_2m"].values[0]
                humidity = df["relative_humidity_2m"].values[0]
                pm25 = df["components_pm2_5"].values[0]
                pm10 = df["components_pm10"].values[0]
                no2 = df["components_no2"].values[0]
                o3 = df["components_o3"].values[0]

                cat, bg, text, border, en, ur = get_advisory(prediction, temperature, humidity)
                st.session_state.update({
                    'prediction': prediction, 'category': cat,
                    'bg': bg, 'text': text, 'border': border,
                    'en': en, 'ur': ur, 'city': city_name,
                    'temp': temperature, 'hum': humidity,
                    'pm25': pm25, 'pm10': pm10, 'no2': no2, 'o3': o3
                })
            except Exception as e:
                st.error(f"❌ {e}")

with col_result:
    if 'prediction' in st.session_state:
        s = st.session_state
        st.markdown(f"""
        <div class="result-card" style="background:{s['bg']};border-color:{s['border']};color:{s['text']};">
            <div class="result-category">AQI Category</div>
            <div class="result-title">{s['category']}</div>
            <div class="result-advisory">{s['en']}</div>
            <div class="result-urdu">{s['ur']}</div>
            <div class="pills-row">
                <span class="pill">🌡️ {s['temp']}°C</span>
                <span class="pill">💧 {s['hum']}% RH</span>
                <span class="pill">PM2.5 {s['pm25']:.1f}</span>
                <span class="pill">PM10 {s['pm10']:.1f}</span>
                <span class="pill">NO₂ {s['no2']:.1f}</span>
                <span class="pill">O₃ {s['o3']:.1f}</span>
            </div>
            <div class="result-meta" style="margin-top:12px;">
                📍 {s['city']} &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y, %H:%M")}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            border: 1.5px dashed #ccc;
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            color: #bbb;
            font-size: 13px;
            font-weight: 500;
        ">
            🌿 Select a city and<br>check air quality
        </div>
        """, unsafe_allow_html=True)

# ========================
# FOOTER
# ========================
st.markdown("""
    <div class="footer">
        ⚠️ Predictions based on historical AQI patterns (2021–2024) and may vary from real-time conditions.<br>
        🍃 Breathify · Developed by Muhammad Sami
    </div>
""", unsafe_allow_html=True)
