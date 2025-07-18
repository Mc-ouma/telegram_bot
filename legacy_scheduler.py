#!/usr/bin/env python3
"""
Legacy compatibility script for continuous execution.

This script provides backward compatibility for platforms that expect
a continuously running process (like Railway, Heroku, etc.) while
maintaining the new n8n-friendly single-execution approach.

Use this script only if you need the old continuous execution behavior.
For new deployments, prefer the n8n workflow approach.
"""

import time
import schedule
import logging
import os
import sys

# Import the main job function from the updated script
from telegram_match_poster import main_job

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def run_legacy_scheduler():
    """
    Runs the bot with the old scheduling approach for backward compatibility.
    """
    logging.info("Starting legacy scheduler for backward compatibility")
    logging.warning("Consider migrating to n8n workflow for better reliability")
    
    # Schedule the job to run at 8:00 AM EAT every day
    schedule.every().day.at("08:00").do(main_job)
    logging.info("Bot scheduled to run daily at 08:00 AM EAT")
    
    # Run immediately if in debug mode
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    if DEBUG_MODE:
        logging.info("Debug mode active, running job immediately")
        main_job()
    
    # Keep the script running and check for scheduled jobs
    logging.info("Starting continuous execution loop")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    logging.info("Legacy scheduler started")
    try:
        run_legacy_scheduler()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Scheduler failed: {e}")
        sys.exit(1)