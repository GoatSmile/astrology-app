import streamlit as st
from openai import OpenAI  # Updated import
from datetime import datetime
from astral import LocationInfo
from astral.sun import sun
from astral.moon import phase
import pytz
import os

# Configure API keys ➡️
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def get_moon_phase():
    return phase(datetime.now())

def generate_forecast(zodiac_sign):  # Updated API call ➡️
    prompt = f"Create a fun, positive weekly horoscope for {zodiac_sign} under 100 words. Use emojis!"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_image(prompt):  # Updated API call ➡️
    response = client.images.generate(
        prompt=f"Colorful mystical collage: {prompt}. Artistic style, astrology theme.",
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

# Rest of your Streamlit UI code remains the same...
# [Keep all your existing Streamlit interface code below]

#------
# App Interface
st.set_page_config(page_title="My Astrology Weekly Outlook", layout="wide")

# Custom CSS
st.markdown("""
<style>
.fun-header {
    color: #FF6B6B;
    font-family: 'Comic Sans MS';
    text-align: center;
}
.result-card {
    padding: 20px;
    border-radius: 15px;
    background: #FFF5F5;
    margin: 10px;
}
</style>
""", unsafe_allow_html=True)

# Main Form
st.markdown("<h1 class='fun-header'>🌟 My Astrology Weekly Outlook 🌟</h1>", unsafe_allow_html=True)

with st.form("user_inputs"):
    name = st.text_input("Your Name")
    dob = st.date_input("Birth Date")
    love_options = ["cats", "dogs", "flowers", "sky", "love", "my spouse", "my kids", "my life"]
    love_choice = st.selectbox("What do you love most?", love_options)
    submitted = st.form_submit_button("Generate My Astrology Report")

if submitted:
    zodiac = get_zodiac_sign(dob)
    moon_phase = get_moon_phase()
    forecast = generate_forecast(zodiac)
    image_prompt = f"{zodiac} symbol, {love_choice}, {forecast[:50]}"
    
    with st.spinner("✨ Consulting the stars..."):
        image_url = generate_image(image_prompt)
    
    # Display Results
    st.markdown(f"""
    <div class='result-card'>
        <h3>Hello {name}!</h3>
        <p>🔮 Zodiac Sign: <strong>{zodiac}</strong></p>
        <p>❤️ You Love: <strong>{love_choice}</strong></p>
        <p>🌙 Current Moon Phase: {round(moon_phase, 1)}/28 days</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(image_url, use_column_width=True)
        st.download_button("Download Your Astrology Art", image_url, file_name="my_astrology_art.png")
    
    with col2:
        st.markdown(f"""
        <div class='result-card'>
            <h3>📅 Weekly Forecast</h3>
            <p>{forecast}</p>
        </div>
        """, unsafe_allow_html=True)