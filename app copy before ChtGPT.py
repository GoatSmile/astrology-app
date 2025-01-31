import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from openai import OpenAI
from datetime import datetime
from astral import LocationInfo, sun, moon
from astral.moon import phase
import pytz

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Test: v1")  # Debug line


# Enhanced Zodiac Calculations
def get_zodiac_sign(birth_date):
    zodiac_dates = [
        (120, 'Capricorn'), (219, 'Aquarius'), (320, 'Pisces'),
        (420, 'Aries'), (521, 'Taurus'), (621, 'Gemini'),
        (722, 'Cancer'), (823, 'Leo'), (923, 'Virgo'),
        (1023, 'Libra'), (1122, 'Scorpio'), (1222, 'Sagittarius'),
        (1231, 'Capricorn')
    ]
    date_num = int(birth_date.strftime("%m%d"))
    for cutoff, sign in zodiac_dates:
        if date_num <= cutoff:
            return sign

# Astronomical Calculations
def get_celestial_data():
    now = datetime.now(pytz.utc)
    return {
        'moon_phase': phase(now),
        'sun_position': sun(LocationInfo().observer, date=now),
        'mercury_retrograde': (now.month % 3 == 0)  # Simplified logic
    }

# Planetary Transits (Simplified)
def get_planetary_transits():
    day_of_month = datetime.now().day
    return {
        'current_aspects': [
            "Sun trine Saturn" if day_of_month < 15 else "Sun square Neptune",
            "Venus conjunct Mars" if day_of_month % 2 == 0 else "Venus sextile Jupiter"
        ],
        'significant_transits': [
            "Jupiter in Taurus" if datetime.now().month < 6 else "Jupiter in Gemini"
        ]
    }

# Enhanced Forecast Generation
def generate_forecast(zodiac_sign, celestial_data, love_choice):
    transits = get_planetary_transits()
    
    prompt = f"""Create a detailed weekly horoscope for {zodiac_sign} considering:
    - Current moon phase: {celestial_data['moon_phase']}/28 days
    - Mercury Retrograde: {'Yes 🔙' if celestial_data['mercury_retrograde'] else 'No 🔜'}
    - Key aspects: {', '.join(transits['current_aspects'])}
    - User's passion: {love_choice}
    
    Structure the forecast with:
    1. Love & Relationships 💞 (2-3 sentences)
    2. Career & Finance 💰 (2 sentences)
    3. Health & Wellness 🧘 (1-2 sentences)
    4. Cosmic Advice 🌠 (1 impactful sentence)
    
    Use astrological terminology mixed with playful emojis. Max 150 words."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# Enhanced Image Generation
def generate_image(zodiac_sign, forecast_text, moon_phase):
    phase_symbols = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
    moon_symbol = phase_symbols[int(moon_phase % 8)]
    
    prompt = f"""Mystical digital painting of {zodiac_sign} constellation with:
    - {moon_symbol} moon prominently displayed
    - Symbols representing key forecast elements: {forecast_text[:75]}
    - Celestial color palette: deep purples, starry night sky, golden accents
    - Style: Fantasy art meets astronomical diagram"""
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd"
    )
    return response.data[0].url

# UI Configuration
st.set_page_config(page_title="Cosmic Insight", layout="wide", page_icon="🌌")

st.markdown("""
<style>
.cosmic-header {
    color: #9D70F9 !important;
    font-family: 'Papyrus', fantasy;
    text-align: center;
    text-shadow: 2px 2px #4B0082;
}
.result-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 25px;
    margin: 15px 0;
    backdrop-filter: blur(10px);
    border: 1px solid #4B0082;
}
</style>
""", unsafe_allow_html=True)

# Main App Interface
st.markdown("<h1 class='cosmic-header'>🌠 Your Cosmic Insight 🌠</h1>", unsafe_allow_html=True)

with st.form("astro_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name", placeholder="Cosmic Traveler...")
        dob = st.date_input("Birth Date", value=datetime(2000, 1, 1))
    with col2:
        love_options = ["Adventure", "Creativity", "Relationships", "Knowledge", "Nature"]
        love_choice = st.selectbox("Cosmic Passion", love_options)
        location = st.text_input("Birth Location", placeholder="City, Country")
    
    submitted = st.form_submit_button("Reveal My Cosmic Blueprint 🌟")

if submitted:
    celestial = get_celestial_data()
    transits = get_planetary_transits()
    zodiac = get_zodiac_sign(dob)
    
    with st.spinner("Consulting the celestial spheres..."):
        forecast = generate_forecast(zodiac, celestial, love_choice)
        image_url = generate_image(zodiac, forecast, celestial['moon_phase'])
    
    # Results Display
    st.markdown(f"""
    <div class='result-card'>
        <h3>Welcome, {name} of {zodiac}!</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0;">
            <div>🌙 Moon Phase: {round(celestial['moon_phase'], 1)}/28</div>
            <div>🔭 Mercury: {'Retrograde 🔙' if celestial['mercury_retrograde'] else 'Direct ➡️'}</div>
            <div>💫 Current Aspects: {', '.join(transits['current_aspects'])}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_img, col_text = st.columns([1, 2])
    with col_img:
        st.image(image_url, use_container_width=True)
        st.download_button("Download Cosmic Art", image_url, file_name="cosmic_blueprint.png")
    
    with col_text:
        st.markdown(f"""
        <div class='result-card'>
            <h3>📜 Cosmic Forecast</h3>
            <div style="line-height: 1.6; font-size: 16px;">
                {forecast.replace('\n', '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---\n*Celestial data calculated for current moment in UTC time*")