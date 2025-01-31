import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from datetime import datetime
from astral import LocationInfo, sun, moon
from astral.moon import phase
from astral.sun import sun  # Correct import
import pytz
from skyfield.api import load
# Add to imports
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # For accurate month calculations

# Add this after imports; ADDED FOR ONLINE VERSION
from skyfield.api import Loader
load = Loader('/tmp')
planets = load('de421.bsp')  # Now uses proper deployment path

# print("DEBUG:  app.py is RUNNING... ")  # Debug line
print(f"DEBUG: app.py is RUNNING... [Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")  # Debug line

# Load environment variables
# load_dotenv()
# For Local
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Accurate Mercury Retrograde Check
def is_mercury_retrograde():
    ts = load.timescale()
    planets = load('de421.bsp')  # NASA JPL planetary data

    mercury, sun = planets['mercury'], planets['sun']
    
    now = datetime.now(pytz.utc)
    t = ts.utc(now.year, now.month, now.day)

    mercury_position = mercury.at(t)
    sun_position = sun.at(t)
    mercury_velocity = mercury_position - sun_position

    # Get Mercury's ecliptic longitude for today and tomorrow
    _, lon1, _ = mercury_velocity.ecliptic_latlon()
    _, lon2, _ = mercury.at(ts.utc(now.year, now.month, now.day + 1)).ecliptic_latlon()

    return lon2.degrees < lon1.degrees  # Mercury is retrograde if tomorrow's longitude is less than today's

# Zodiac Calculations
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

# Celestial Data Retrieval
def get_celestial_data():
    now = datetime.now(pytz.utc)
    return {
        'moon_phase': phase(now),
        'sun_position': sun(LocationInfo().observer, date=now),
        'mercury_retrograde': is_mercury_retrograde()  # Uses new accurate function
    }

# Planetary Transits
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

# Forecast Generation
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

# Image Generation
def generate_image(zodiac_sign, forecast_text, moon_phase):
    phase_symbols = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
    moon_symbol = phase_symbols[int(moon_phase % 8)]
    
    prompt = f"""Mystical digital painting of {zodiac_sign} constellation with:
    - {moon_symbol} moon displayed
    - Incorporate {love_choice} as a cosmic element
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

# Function to generate news-related content using OpenAI
def generate_news_with_openai(news_options):
    prompt = f"""
    Generate one headline of the biggest latest news for the topic: {news_options}.
    Use concise and engaging language.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()


def generate_realtime_news(topic):
    # For Local
    #  api_key = os.getenv("GNEWS_API_KEY")
    
    api_key = OpenAI(api_key=secrets["GNEWS_API_KEY"])

    # Calculate date 13 months ago
    end_date = datetime.now()
    start_date = end_date - relativedelta(months=13)
    
    # Format dates for API (ISO 8601 format)
    from_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    to_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    url = f"https://gnews.io/api/v4/search?q={topic}&max=3&lang=en" \
          f"&from={from_date}&to={to_date}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        
        return [{
            'title': a.get('title', 'No title'),
            'url': a.get('url', '#'),
            'source': a.get('source', {}).get('name', 'Unknown'),
            'published': a.get('publishedAt', '')[:10]  # Get YYYY-MM-DD
        } for a in articles[:3]]  # Ensure max 3 articles
        
    except Exception as e:
        error(f"News Error: {str(e)}")
        return []

# Streamlit UI Setup
set_page_config(page_title="Cosmic Insight", layout="wide", page_icon="🌌")

markdown("""
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

markdown("<h1 class='cosmic-header'>🌠 Your Cosmic Insight 🌠</h1>", unsafe_allow_html=True)

# Form for User Input
with form("astro_form"):
    col1, col2 = columns(2)
    with col1:
        name = text_input("Your Name", placeholder="Cosmic Traveler...")
        dob = date_input("Birth Date", value=datetime(2000, 1, 1))
    with col2:
        # love_options = ["Adventure", "Creativity", "Relationships", "Knowledge", "Nature"]
        # love_choice = selectbox("Cosmic Passion", love_options)
        love_options = ["cats", "dogs", "flowers", "blue sky", "mother", "spouse", "kids", "bicycle", "Bitcoin"]
        love_choice = st.selectbox("What do you love most?", love_options)
    #    news_options = ["Politics", "Entertainment", "Trump","Local Copenhagen"]
    #    news_choice = st.selectbox("What news do you want to know?", news_options)

    #    location = st.text_input("Birth Location", placeholder="City, Country")
    
    submitted = st.form_submit_button("Reveal My Cosmic Blueprint 🌟")


if submitted:
    celestial = get_celestial_data()
    transits = get_planetary_transits()
    zodiac = get_zodiac_sign(dob)
    
    with st.spinner("Consulting the celestial spheres..."):
        forecast = generate_forecast(zodiac, celestial, love_choice)
        image_url = generate_image(zodiac, forecast, celestial['moon_phase'])
         # Generate news content with OpenAI
        news_content = generate_news_with_openai(love_choice)
   
    # Display Results
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

    # Apply replacement outside of the f-string
    forecast_html = forecast.replace("\n", "<br>")

    col_img, col_text = st.columns([1, 2])
    with col_img:
        st.markdown(f"""
        <div class='result-card'>
            <h3>AI generated image based on your inputs</h3>
            <img src="{image_url}" alt="Cosmic Art" style="width:100%; border-radius: 10px;"/>
            <br><br>
            <a href="{image_url}" download="cosmic_blueprint.png" style="text-decoration:none; padding: 10px; background-color:#4B0082; color: white; border-radius:5px;">Download Cosmic Art</a>
        </div>
        """, unsafe_allow_html=True)

    with col_text:
        st.markdown(f"""
        <div class='result-card'>
            <h3>📜 Cosmic Forecast</h3>
            <div style="line-height: 1.6; font-size: 16px;">
            {forecast_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Display News Section
    # In your submitted block, replace news generation with:
    news_items = generate_realtime_news(love_choice)

    # Display News Section
    st.markdown(f"""
    <div>
        <h3>📰 Recent Headlines Around the World About {love_choice}</h3>
        <ul style='list-style-type: none; padding-left: 0;'>
    """, unsafe_allow_html=True)

    if news_items:
        for idx, article in enumerate(news_items, 1):
            st.markdown(f"""
            <li style='margin-bottom: 15px;'>
                {article['title']}
                <a href="{article['url']}" target="_blank">
                 ({article['source']})
                </a>
            </li>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<li>No recent news found for this topic</li>", unsafe_allow_html=True)

    st.markdown("</ul></div>", unsafe_allow_html=True)

st.markdown("---\n*Celestial data calculated for current moment in UTC time*")
