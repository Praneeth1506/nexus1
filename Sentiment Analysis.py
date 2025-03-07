import google.generativeai as genai
import json

# Set Up Gemini API
GENAI_API_KEY = "your_gemini_api_key"
genai.configure(api_key=GENAI_API_KEY)

# Load News Data
def load_news_data(file_path="news_data.json"):
    with open(file_path, "r") as file:
        return json.load(file)

# Function to Get Sentiment Using Gemini
def analyze_sentiment_gemini(text):
    prompt = f"Analyze the sentiment of this news headline and return only Positive, Negative, or Neutral:\n\n{text}"
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()

# Adding Sentiment to News Data
def add_sentiment_to_news(news_list):
    for news in news_list:
        news["sentiment"] = analyze_sentiment_gemini(news["title"])
    return news_list

# Run the Sentiment Analysis
news_list = load_news_data()
news_with_sentiment = add_sentiment_to_news(news_list)

# Save Updated News Data
with open("news_with_sentiment.json", "w") as file:
    json.dump(news_with_sentiment, file, indent=4)

print("Sentiment Analysis Done! Check 'news_with_sentiment.json'")


