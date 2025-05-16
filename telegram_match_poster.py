import requests
import json
from datetime import datetime
import time

# Configuration
API_URL = "${{API_URL}}"  # Use Railway environment variable
BOT_TOKEN = "${{BOT_TOKEN}}"  # Use Railway environment variable
CHANNEL_ID = "${{CHANNEL_ID}}"  # Use Railway environment variable
INTERVAL = 86400  # Post once per day (86400 seconds)

def fetch_data():
    """
    Fetches JSON data from the specified API.
    Returns the parsed JSON data if successful, otherwise None.
    """
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def filter_todays_matches(data):
    """
    Filters matches for today's date.
    Returns a list of matches for today.
    """
    today = datetime.now().strftime("%Y-%m-%d")  # Dynamic date
    if not data or "server_response" not in data:
        return []
    return [match for match in data["server_response"] if match["m_date"] == today]

def format_match(match):
    """
    Formats a match into a beautiful Markdown string.
    """
    home_team = match["home_team"]
    away_team = match["away_team"]
    league = match["league"]
    country = match["country"]
    m_time = match["m_time"]
    pick = match["pick"]
    result = match["result"] if match["result"] != "-" else "Not Played"
    outcome = match["outcome"].capitalize() if match["outcome"] else "Pending"
    h_logo = match["h_logo_path"]
    a_logo = match["a_logo_path"]
    league_logo = match["league_logo"]

    return (
        f"🏆 **{league} ({country})** 🏆\n"
        f"⏰ **Time**: {m_time}\n"
        f"⚽ **{home_team}** 🆚 **{away_team}**\n"
        f"🎯 **Pick**: {pick}\n"
        f"📊 **Result**: {result}\n"
        f"✅ **Outcome**: {outcome}\n"
        f"\n[Home Team Logo]({h_logo}) | [Away Team Logo]({a_logo}) | [League Logo]({league_logo})\n"
        f"━━━━━━━━━━━━━━━"
    )

def send_message(text):
    """
    Sends a message to the Telegram channel using the bot.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Message posted successfully!")
    else:
        print(f"Failed to post message: {response.text}")

def main():
    """
    Main function to fetch, filter, format, and post today's matches.
    """
    data = fetch_data()
    if data is None:
        message = "⚽ Error fetching match data. Please try again later. ⚽"
        send_message(message)
        return

    todays_matches = filter_todays_matches(data)
    
    if not todays_matches:
        message = f"⚽ No matches scheduled for today ({datetime.now().strftime('%Y-%m-%d')}). Check back tomorrow! ⚽"
        send_message(message)
    else:
        formatted_matches = [format_match(match) for match in todays_matches]
        message = f"⚽ **Today's Matches ({datetime.now().strftime('%Y-%m-%d')})** ⚽\n\n" + "\n\n".join(formatted_matches)
        send_message(message)

# Run the script periodically
if __name__ == "__main__":
    while True:
        try:
            main()
            time.sleep(INTERVAL)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Wait before retrying
