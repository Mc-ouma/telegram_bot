import requests
import json
from datetime import datetime, timedelta
from pytz import timezone
import time
import random
import logging
import os

# Configure logging
logging.basicConfig(
    filename='bot.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logging.getLogger().addHandler(logging.StreamHandler())  # Log to console for Railway

# Configuration
API_URL = os.getenv("API_URL")  # e.g., https://surebetsapp.com/app_json_scrits/json_toppicks.php
BOT_TOKEN = os.getenv("BOT_TOKEN")  # e.g., 589590135:AAG535MoncA24m_4EdDLHlPGg...
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g., -1001247200123
INTERVAL = 86400  # 24 hours for daily posts
MORE_MATCHES_LINK = "https://groups.google.com/u/0/g/ai-scorecast"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
EAT = timezone('Africa/Nairobi')  # East Africa Time

def validate_env_vars():
    """
    Validates environment variables.
    Returns True if all are set, False otherwise.
    """
    missing = []
    if not API_URL:
        missing.append("API_URL")
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not CHANNEL_ID:
        missing.append("CHANNEL_ID")
    if missing:
        logging.error(f"Missing environment variables: {', '.join(missing)}")
        return False
    logging.info("All environment variables are set")
    return True

def fetch_data():
    """
    Fetches JSON data from the API or uses fallback data.
    Returns parsed JSON data or None.
    """
    if not API_URL:
        logging.error("API_URL not set, using fallback data")
        return get_fallback_data()
    try:
        headers = {
            "User-Agent": "TelegramBot/1.0",
            # Uncomment and add API key if required
            # "Authorization": "Bearer your_api_key"
        }
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        logging.info(f"Successfully fetched data from {API_URL}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {API_URL}: {e}")
        return get_fallback_data()

def get_fallback_data():
    """
    Returns fallback JSON data for testing.
    """
    logging.warning("Using fallback JSON data")
    return {
        "server_response": [
            {
                "m_time": "17:30",
                "pick": "1",
                "country": "Iran",
                "league": "Iran - Persian Gulf Pro League",
                "m_date": "2025-05-16",
                "home_team": "Persepolis FC",
                "away_team": "Havadar",
                "bet_odds": "",
                "outcome": "win",
                "result": "2 - 0",
                "h_logo_path": "https://media.api-sports.io/football/teams/2742.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/15541.png",
                "league_logo": "https://media.api-sports.io/football/leagues/290.png",
                "fixture_id": "1371668",
                "m_status": "FT"
            },
            {
                "m_time": "21:00",
                "pick": "Over 1.5",
                "country": "Poland",
                "league": "Poland - II Liga - East",
                "m_date": "2025-05-17",
                "home_team": "Zaglebie Sosnowiec",
                "away_team": "Wisla Pulawy",
                "bet_odds": "",
                "outcome": "",
                "result": "-",
                "h_logo_path": "https://media.api-sports.io/football/teams/342.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/16272.png",
                "league_logo": "https://media.api-sports.io/football/leagues/109.png",
                "fixture_id": "1211823",
                "m_status": "NS"
            },
            {
                "m_time": "21:30",
                "pick": "1",
                "country": "England",
                "league": "England - Premier League",
                "m_date": "2025-05-17",
                "home_team": "Aston Villa",
                "away_team": "Tottenham",
                "bet_odds": "",
                "outcome": "",
                "result": "-",
                "h_logo_path": "https://media.api-sports.io/football/teams/66.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/47.png",
                "league_logo": "https://media.api-sports.io/football/leagues/39.png",
                "fixture_id": "1208384",
                "m_status": "NS"
            },
            {
                "m_time": "22:15",
                "pick": "1",
                "country": "England",
                "league": "England - Premier League",
                "m_date": "2025-05-17",
                "home_team": "Chelsea",
                "away_team": "Manchester United",
                "bet_odds": "",
                "outcome": "",
                "result": "-",
                "h_logo_path": "https://media.api-sports.io/football/teams/49.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/33.png",
                "league_logo": "https://media.api-sports.io/football/leagues/39.png",
                "fixture_id": "1208387",
                "m_status": "NS"
            }
        ]
    }

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
    
    # Log all match outcomes for debugging
    for match in matches:
        logging.info(f"Match: {match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}, Outcome: {match.get('outcome', 'Unknown')}")
    
    # Only count matches that have outcomes (completed matches)
    completed_matches = [match for match in matches if match.get("outcome")]
    if not completed_matches:
        logging.info("No completed matches found for yesterday")
        return None
    
    total_matches = len(completed_matches)
    won_matches = sum(1 for match in completed_matches if match.get("outcome", "").lower() == "win")
    
    win_percentage = (won_matches / total_matches) * 100 if total_matches > 0 else 0
    
    logging.info(f"Yesterday: {won_matches}/{total_matches} completed matches won ({win_percentage:.2f}%)")
    
    if won_matches == total_matches and total_matches > 0:
        return "🎉 **Perfect Day!** All of yesterday's picks were winners! Keep riding the wave! 🚀"
    elif win_percentage >= 75 and total_matches > 0:
        return f"🥳 **Amazing Day!** {won_matches}/{total_matches} of yesterday's picks won ({win_percentage:.2f}%)! Let's keep it going! 💪"
    return None

def format_match(match):
    """
    Formats a match into a beautiful Markdown string without logos.
    """
    home_team = match["home_team"]
    away_team = match["away_team"]
    league = match["league"]
    country = match["country"]
    m_time = match["m_time"]
    pick = match["pick"]
    result = match["result"] if match["result"] != "-" else "Not Played"
    outcome = match["outcome"].capitalize() if match["outcome"] else "Pending"
    return (
        f"🏆 **{league} ({country})** 🏆\n"
        f"⏰ **Time**: {m_time} EAT\n"
        f"⚽ **{home_team}** 🆚 **{away_team}**\n"
        f"🎯 **Pick**: {pick}\n"
        f"📊 **Result**: {result}\n"
        f"✅ **Outcome**: {outcome}\n"
        f"━━━━━━━━━━━━━━━"
    )

def send_message(text):
    """
    Sends a message to the Telegram channel.
    Returns True if successful, False otherwise.
    """
    if not BOT_TOKEN or not CHANNEL_ID:
        logging.error("BOT_TOKEN or CHANNEL_ID not set")
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
            logging.error(f"Telegram API error: {response.json()}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message to Telegram: {e}")
        return False

def test_bot_permissions():
    """
    Tests bot permissions with a test message.
    Returns True if successful, False otherwise.
    """
    test_message = f"🔔 **Test Message** from your Telegram bot at {datetime.now(EAT).strftime('%Y-%m-%d %H:%M:%S')} EAT to verify posting! 🔔"
    logging.info("Testing bot permissions")
    return send_message(test_message)

def main():
    """
    Main function to check yesterday's results, fetch, filter, and post matches.
    """
    logging.info("Starting main function")
    if not validate_env_vars():
        send_message("⚠️ Bot error: Missing environment variables. Contact admin.")
        return

    # Test permissions only in DEBUG_MODE
    if DEBUG_MODE:
        if not test_bot_permissions():
            logging.error("Test message failed. Check bot permissions or CHANNEL_ID.")
            send_message("⚠️ Bot error: Cannot post to channel. Check permissions.")
            return
    # In non-DEBUG mode, just log the start without testing permissions
    else:
        logging.info("Running in production mode, skipping test message")

    # Get dates in EAT
    now_eat = datetime.now(EAT)
    yesterday = (now_eat - timedelta(days=1)).strftime("%Y-%m-%d")
    today = now_eat.strftime("%Y-%m-%d")

    json_data = fetch_data()
    if json_data is None:
        message = "⚽ Error fetching match data. Using fallback data. ⚽"
        send_message(message)
        json_data = get_fallback_data()

    yesterday_matches = filter_matches_by_date(json_data, yesterday)
    congrats_message = check_yesterday_results(yesterday_matches)

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
        logging.error("Failed to post daily message")

if __name__ == "__main__":
    logging.info("Bot started")
    try:
        main()  # Run immediately
        while True:
            time.sleep(INTERVAL)
            main()
    except Exception as e:
        logging.error(f"Main loop error: {e}")
        time.sleep(60)
