import requests
import json
from datetime import datetime, timedelta
import time
import random
import logging

# Configure logging
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Configuration
API_URL = "${{API_URL}}"  # Use Railway environment variable
BOT_TOKEN = "${{BOT_TOKEN}}"  # Use Railway environment variable
CHANNEL_ID = "${{CHANNEL_ID}}"  # Use Railway environment variable
INTERVAL = 86400  # Post once per day (86400 seconds)
MORE_MATCHES_LINK = "https://yourwebsite.com/matches"  # Replace with your link

def fetch_data():
    """
    Fetches JSON data from the specified API.
    Returns the parsed JSON data if successful, otherwise None.
    """
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            logging.info("Successfully fetched data from API")
            return response.json()
        else:
            logging.error(f"Failed to fetch data: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
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
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logging.info("Message posted successfully")
        else:
            logging.error(f"Failed to post message: {response.text}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

def main():
    """
    Main function to check yesterday's results, then fetch, filter, select 3 random matches, format, and post today's matches.
    """
    logging.info("Starting main function")
    # For testing, use provided JSON data
    json_data = {
        "server_response": [
            {
                "m_time": "17:30",
                "pick": "1",
                "country": "Iran",
                "league": "Iran - Persian Gulf Pro League",
                "m_date": "2025-05-15",
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
                "pick": "2",
                "country": "Saudi-Arabia",
                "league": "Saudi-Arabia - Pro League",
                "m_date": "2025-05-15",
                "home_team": "Al-Raed",
                "away_team": "Al-Ittihad FC",
                "bet_odds": "",
                "outcome": "win",
                "result": "1 - 3",
                "h_logo_path": "https://media.api-sports.io/football/teams/2935.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/2938.png",
                "league_logo": "https://media.api-sports.io/football/leagues/307.png",
                "fixture_id": "1252700",
                "m_status": "FT"
            },
            {
                "m_time": "14:45",
                "pick": "Over 2.5",
                "country": "Singapore",
                "league": "Singapore - Premier League",
                "m_date": "2025-05-15",
                "home_team": "Young Lions",
                "away_team": "Geylang International",
                "bet_odds": "",
                "outcome": "win",
                "result": "1 - 2",
                "h_logo_path": "https://media.api-sports.io/football/teams/4208.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/4203.png",
                "league_logo": "https://media.api-sports.io/football/leagues/368.png",
                "fixture_id": "1196675",
                "m_status": "FT"
            },
            {
                "m_time": "16:00",
                "pick": "1",
                "country": "Kenya",
                "league": "Kenya - FKF Premier League",
                "m_date": "2025-05-15",
                "home_team": "GOR Mahia",
                "away_team": "Nairobi City Stars",
                "bet_odds": "",
                "outcome": "lose",
                "result": "1 - 2",
                "h_logo_path": "https://media.api-sports.io/football/teams/2467.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/2482.png",
                "league_logo": "https://media.api-sports.io/football/leagues/276.png",
                "fixture_id": "1303840",
                "m_status": "FT"
            },
            {
                "m_time": "21:00",
                "pick": "Over 1.5",
                "country": "Poland",
                "league": "Poland - II Liga - East",
                "m_date": "2025-05-16",
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
                "m_date": "2025-05-16",
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
                "m_time": "19:00",
                "pick": "1",
                "country": "Norway",
                "league": "Norway - Eliteserien",
                "m_date": "2025-05-16",
                "home_team": "Rosenborg",
                "away_team": "Haugesund",
                "bet_odds": "",
                "outcome": "",
                "result": "-",
                "h_logo_path": "https://media.api-sports.io/football/teams/331.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/328.png",
                "league_logo": "https://media.api-sports.io/football/leagues/103.png",
                "fixture_id": "1342237",
                "m_status": "NS"
            },
            {
                "m_time": "21:30",
                "pick": "2",
                "country": "Austria",
                "league": "Australia - 2. Liga",
                "m_date": "2025-05-16",
                "home_team": "Schwarz-WeiSs Bregenz",
                "away_team": "Ried",
                "bet_odds": "",
                "outcome": "",
                "result": "-",
                "h_logo_path": "https://media.api-sports.io/football/teams/8259.png",
                "a_logo_path": "https://media.api-sports.io/football/teams/1028.png",
                "league_logo": "https://media.api-sports.io/football/leagues/219.png",
                "fixture_id": "1219918",
                "m_status": "NS"
            },
            {
                "m_time": "22:15",
                "pick": "1",
                "country": "England",
                "league": "England - Premier League",
                "m_date": "2025-05-16",
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

    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_matches = filter_matches_by_date(json_data, yesterday)
    congrats_message = check_yesterday_results(yesterday_matches)

    # Get today's matches
    todays_matches = filter_matches_by_date(json_data, datetime.now().strftime("%Y-%m-%d"))
    
    message_parts = []
    if congrats_message:
        message_parts.append(congrats_message + "\n\n")

    if not todays_matches:
        message_parts.append(f"⚽ No matches scheduled for today ({datetime.now().strftime('%Y-%m-%d')}). Check back tomorrow! ⚽")
    else:
        selected_matches = random.sample(todays_matches, min(3, len(todays_matches)))
        formatted_matches = [format_match(match) for match in selected_matches]
        message_parts.append(
            f"⚽ **Today's Top Matches ({datetime.now().strftime('%Y-%m-%d')})** ⚽\n\n"
            + "\n\n".join(formatted_matches)
            + f"\n\n🔗 [Check More Matches]({MORE_MATCHES_LINK})"
        )

    message = "".join(message_parts)
    send_message(message)

# Run the script periodically
if __name__ == "__main__":
    logging.info("Bot started")
    while True:
        try:
            main()
            time.sleep(INTERVAL)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(60)  # Wait before retrying
