import streamlit as st
import requests
from groq import Groq
import openai

def run():
    # Initialize the Groq and OpenAI clients with API keys from st.secrets
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    openai_client = openai.OpenAI(api_key=st.secrets["openai_api_key"])

    def get_current_weather(location):
        api_key = st.secrets["OPEN_WEATHER_API_KEY"]
        if "," in location:
            location = location.split(",")[0].strip()
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": api_key, "units": "metric"}
        response = requests.get(base_url, params=params)
        data = response.json()
        if response.status_code == 200:
            return {
                "location": data["name"],
                "temperature": round(data["main"]["temp"], 2),
                "feels_like": round(data["main"]["feels_like"], 2),
                "temp_min": round(data["main"]["temp_min"], 2),
                "temp_max": round(data["main"]["temp_max"], 2),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"]
            }
        else:
            st.error(f"Error fetching weather data: {data.get('message', 'Unknown error')}")
            return None

    def get_clothing_suggestion(weather_data, llm_choice):
        system_prompt = "You are a helpful assistant that provides clothing suggestions based on weather information."
        user_prompt = f"""
        Given the following weather information:
        Location: {weather_data['location']}
        Temperature: {weather_data['temperature']}°C (Min: {weather_data['temp_min']}°C, Max: {weather_data['temp_max']}°C)
        Feels like: {weather_data['feels_like']}°C
        Humidity: {weather_data['humidity']}%
        Description: {weather_data['description']}

        Please provide a brief suggestion on what clothes to wear today.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        if llm_choice == "Groq":
            response = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
        elif llm_choice == "OpenAI":
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
        return response.choices[0].message.content

    st.title("Travel Weather and Clothing Suggestion Bot")
    
    location = st.text_input("Enter a location:", "Syracuse, NY")
    llm_choice = st.selectbox("Choose LLM:", ["Groq", "OpenAI"])
    
    if st.button("Get Weather and Clothing Suggestion"):
        weather_data = get_current_weather(location)
        
        if weather_data:
            st.write("## Weather Information")
            st.write(f"Location: {weather_data['location']}")
            st.write(f"Temperature: {weather_data['temperature']}°C (Min: {weather_data['temp_min']}°C, Max: {weather_data['temp_max']}°C)")
            st.write(f"Feels like: {weather_data['feels_like']}°C")
            st.write(f"Humidity: {weather_data['humidity']}%")
            st.write(f"Description: {weather_data['description']}")
            
            suggestion = get_clothing_suggestion(weather_data, llm_choice)
            st.write("## Clothing Suggestion")
            st.write(suggestion)

# This ensures the run() function is called when the script is executed
if __name__ == "__main__":
    run()