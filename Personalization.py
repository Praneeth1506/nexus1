import json

# Function to Save User Preferences
def save_user_preference(user_id, news_title, sentiment):
    preferences_file = "user_preferences.json"

    # Load existing preferences
    try:
        with open(preferences_file, "r") as file:
            user_preferences = json.load(file)
    except FileNotFoundError:
        user_preferences = {}

    # Add new preference data
    if user_id not in user_preferences:
        user_preferences[user_id] = {"positive": [], "negative": [], "neutral": []}

    user_preferences[user_id][sentiment.lower()].append(news_title)

    # Save back to file
    with open(preferences_file, "w") as file:
        json.dump(user_preferences, file, indent=4)



