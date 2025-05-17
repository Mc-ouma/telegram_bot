import requests
import json
from datetime import datetime, timedelta
from pytz import timezone
import time
import random
import logging


# Configure logging
logging.basicConfig(
    filename='bot.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Configuration
API_URL = os.getenv("API_URL")  # e.g., https://surebetsapp.com/app_json_scrits/json_toppicks.php
BOT_TOKEN = os.getenv("BOT_TOKEN")  # e.g., 589590135:AAG535MoncA24m_4EdDLHlPGgxxxxx
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g., -1001247200xxx
INTERVAL = 86400  # Post once per day (86400 seconds)
MORE_MATCHES_LINK = "https://surebetsapp.com"  # Updated to match your domain
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

def fetch_data():
    """
    Fetches JSON data from the specified API.
    Returns the parsed JSON data if successful, otherwise None.
    """
    if not API_URL:
        logging.error("API_URL environment variable is not set")
        return None
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        logging.info(f"Successfully fetched data from {API_URL}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {API_URL}: {e}")
        return None

def filter_matches_by_date(data, target_date):
    """
    Filters matches for the specified date.
    Returns a list of matches for the target date.
    """
    if not data or "server_response" not in data:
        logging.warning("No server_response in data")
        return []
    matches = [match for match in data["server_response"] if match["m_date"] == target_date]
    logging.info(f"Found {len(matches)} matches for {target_date}")
    return matches

def check_yesterday_results(matches):
    """
    Checks the results of yesterday's matches.
    Returns a congratulatory message if all or >80% of matches were won, else None.
    """
    if not matches:
        logging.info("No matches found for yesterday")
        return None

    total_matches = len(matches)
    won_matches = sum(1 for match in matches if match["outcome"].lower() == "win")
    win_percentage = (won_matches / total_matches) * 100 if total_matches > 0 else 0

    logging.info(f"Yesterday: {won_matches}/{total_matches} matches won ({win_percentage:.2f}%)")

    if won_matches == total_matches:
        return "🎉 **Perfect Day!** All of yesterday's picks were winners! Keep riding the wave! 🚀"
    elif win_percentage > 80:
        return f"🥳 **Amazing Day!** {won_matches}/{total_matches} of yesterday's picks won ({win_percentage:.2f}%)! Let's keep it going! 💪"
    return None

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
    Returns True if successful, False otherwise.
    """
    if not BOT_TOKEN or not CHANNEL_ID:
        logging.error("BOT_TOKEN or CHANNEL_ID environment variable is not set")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        if response.json().get("ok"):
            logging.info("Message posted successfully")
            return True
        else:
            logging.error(f"Telegram API response not ok: {response.json()}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message to Telegram: {e}")
        return False

def test_bot_permissions():
    """
    Tests if the bot can post a test message to the channel.
    Returns True if successful, False otherwise.
    """
    test_message = f"🔔 **Test Message** from your Telegram bot at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} to verify posting permissions! 🔔"
    logging.info("Testing bot permissions with a test message")
    return send_message(test_message)

def main():
    """
    Main function to check yesterday's results, then fetch, filter, select 3 random matches, format, and post today's matches.
    """
    logging.info("Starting main function")

    # Test bot permissions if in debug mode
    if DEBUG_MODE:
        if not test_bot_permissions():
            logging.error("Failed to post test message. Check bot permissions and channel ID.")
            return

    # Get yesterday's and today's dates
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    # Fetch data from API
    json_data = fetch_data()
    if json_data is None:
        message = "⚽ Error fetching match data. Please try again later. ⚽"
        send_message(message)
        return

    # Check yesterday's results
    yesterday_matches = filter_matches_by_date(json_data, yesterday)
    congrats_message = check_yesterday_results(yesterday_matches)

    # Get today's matches
    todays_matches = filter_matches_by_date(json_data, today)
    
    message_parts = []
    if congrats_message:
        message_parts.append(congrats_message + "\n\n")

    if not todays_matches:
        message_parts.append(f"⚽ No matches scheduled for today ({today}). Check back tomorrow! ⚽")
    else:
        selected_matches = random.sample(todays_matches, min(3, len(todays_matches)))
        formatted_matches = [format_match(match) for match in selected_matches]
        message_parts.append(
            f"⚽ **Today's Top Matches ({today})** ⚽\n\n"
            + "\n\n".join(formatted_matches)
            + f"\n\n🔗 [Check More Matches]({MORE_MATCHES_LINK})"
        )

    message = "".join(message_parts)
    if not send_message(message):
        logging.error("Failed to post daily message to Telegram channel")

# Run the script once for testing, then periodically
if __name__ == "__main__":
    logging.info("Bot started")
    try:
        main()  # Run immediately for testing
        while True:
            time.sleep(INTERVAL)
            main()
    except Exception as e:
        logging.error(f"An error occurred in main loop: {e}")
        time.sleep(60)
