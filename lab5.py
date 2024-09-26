import streamlit as st
import requests
from groq import Groq

def run():
    # Initialize the Groq client with the API key from st.secrets
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # Function to get current weather data from OpenWeatherMap API
    def get_current_weather(location):
        api_key = st.secrets["OPENWEATHERMAP_API_KEY"]
        
        # Handle location format if it's comma separated
        if "," in location:
            location = location.split(",")[0].strip()
        
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric"  # Fetch temperature in Celsius
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            # Extract relevant weather data
            return {
                "location": data["name"],
                "temperature": round(data["main"]["temp"], 2),
                "feels_like": round(data["main"]["feels_like"], 2),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"]
            }
        else:
            st.error(f"Error fetching weather data: {data.get('message', 'Unknown error')}")
            return None

    # Function to get clothing suggestion from Groq API based on weather data
    def get_clothing_suggestion(weather_data):
        system_prompt = {
            "role": "system",
            "content": "You are a helpful assistant that provides clothing suggestions based on weather information."
        }
        
        user_prompt = f"""
        Given the following weather information:
        Location: {weather_data['location']}
        Temperature: {weather_data['temperature']}°C
        Feels like: {weather_data['feels_like']}°C
        Humidity: {weather_data['humidity']}%
        Description: {weather_data['description']}

        Please provide a brief suggestion on what clothes to wear today.
        """
        
        messages = [
            system_prompt,
            {"role": "user", "content": user_prompt}
        ]
        
        # Use Groq client to get a completion from the LLM
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        # Return the suggestion
        return response.choices[0].message.content

    # Streamlit app logic
    def main():
        st.title("Travel Weather and Clothing Suggestion Bot")
        
        # Input field for the location
        location = st.text_input("Enter a location:", "Syracuse, NY")
        
        # Button to get weather and clothing suggestions
        if st.button("Get Weather and Clothing Suggestion"):
            weather_data = get_current_weather(location)
            
            if weather_data:
                # Display weather data
                st.write("## Weather Information")
                st.write(f"Location: {weather_data['location']}")
                st.write(f"Temperature: {weather_data['temperature']}°C")
                st.write(f"Feels like: {weather_data['feels_like']}°C")
                st.write(f"Humidity: {weather_data['humidity']}%")
                st.write(f"Description: {weather_data['description']}")
                
                # Get and display clothing suggestion
                suggestion = get_clothing_suggestion(weather_data)
                st.write("## Clothing Suggestion")
                st.write(suggestion)

# Run the app
if __name__ == "__main__":
    run()