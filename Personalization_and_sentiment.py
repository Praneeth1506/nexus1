from flask import Flask, request, jsonify
import google.generativeai as genai
import json

app = Flask(__name__)

# Configure Gemini API
GENAI_API_KEY = "your_gemini_api_key"
genai.configure(api_key=GENAI_API_KEY)

# Load News Data
def load_news_data(file_path="news_data.json"):
    with open(file_path, "r") as file:
        return json.load(file)

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
    with open("user_preferences.json", "r") as file:
        user_preferences = json.load(file)

    if user_id not in user_preferences:
        return "No preferences found."

    preference_text = json.dumps(user_preferences[user_id], indent=2)
    prompt = f"Based on this user's preferences:\n{preference_text}\nRecommend 3 news categories."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()

# API Endpoints
@app.route("/news-with-sentiment", methods=["GET"])
def news_with_sentiment():
    news_list = load_news_data()
    for news in news_list:
        news["sentiment"] = analyze_sentiment_gemini(news["title"])
    return jsonify(news_list)

@app.route("/save-preference", methods=["POST"])
def save_preference():
    data = request.json
    save_user_preference(data["user_id"], data["news_title"], data["sentiment"])
    return jsonify({"message": "Preference saved!"})

@app.route("/recommend-news", methods=["GET"])
def recommend_news():
    user_id = request.args.get("user_id")
    recommendations = recommend_news_using_gemini(user_id)
    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True)
