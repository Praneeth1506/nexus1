from flask import Flask, request, jsonify
import json
import os
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Configure Gemini API (Securely using Environment Variable)
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("API key is missing! Set GENAI_API_KEY in your environment variables.")
print(f"API Key Loaded: {GENAI_API_KEY[:4]}****")  
genai.configure(api_key=GENAI_API_KEY)

# Load News Data
def load_news(file_path="news_data.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Search for matching news articles
def search_news(query, news_list):
    return [news for news in news_list if query.lower() in news["title"].lower()]

# Analyze Sentiment Using Gemini
def analyze_sentiment_gemini(text):
    prompt = f"Analyze the sentiment of this news headline and return only Positive, Negative, or Neutral:\n\n{text}"
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()

# Save User Preferences
def save_user_preference(user_id, news_title, sentiment):
    preferences_file = "user_preferences.json"

    try:
        with open(preferences_file, "r") as file:
            user_preferences = json.load(file)
    except FileNotFoundError:
        user_preferences = {}

    if user_id not in user_preferences:
        user_preferences[user_id] = {"positive": [], "negative": [], "neutral": []}

    user_preferences[user_id][sentiment.lower()].append(news_title)

    with open(preferences_file, "w") as file:
        json.dump(user_preferences, file, indent=4)

# Recommend News Based on Preferences
def recommend_news_using_gemini(user_id):
    try:
        with open("user_preferences.json", "r") as file:
            user_preferences = json.load(file)
    except FileNotFoundError:
        return "No preferences found."

    if user_id not in user_preferences:
        return "No preferences found."

    preference_text = json.dumps(user_preferences[user_id], indent=2)
    prompt = f"Based on this user's preferences:\n{preference_text}\nRecommend 3 news categories."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()

# API Endpoints

# Voice search for news articles
@app.route("/voice-search", methods=["GET"])
def voice_search():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for a voice query...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        print(f"User said: {query}")

        news_list = load_news()
        results = search_news(query, news_list)

        return jsonify({"query": query, "results": results})
    
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand your voice"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service unavailable"}), 500

# Get news articles with sentiment analysis
@app.route("/news-with-sentiment", methods=["GET"])
def news_with_sentiment():
    news_list = load_news()
    for news in news_list:
        news["sentiment"] = analyze_sentiment_gemini(news["title"])
    return jsonify(news_list)

# Save user news preference
@app.route("/save-preference", methods=["POST"])
def save_preference():
    data = request.json
    save_user_preference(data["user_id"], data["news_title"], data["sentiment"])
    return jsonify({"message": "Preference saved!"})

# Recommend news based on user preferences
@app.route("/recommend-news", methods=["GET"])
def recommend_news():
    user_id = request.args.get("user_id")
    recommendations = recommend_news_using_gemini(user_id)
    return jsonify({"recommendations": recommendations})

# Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
