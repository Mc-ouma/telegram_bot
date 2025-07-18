# Telegram Bot Match Poster

An automated Telegram bot that posts daily football match predictions to a channel. The bot supports both modern n8n workflow automation and legacy continuous execution modes.

## Features

- **Daily Match Posting**: Automatically posts top football match predictions
- **Yesterday's Results**: Congratulates on successful predictions
- **Flexible Scheduling**: Supports both n8n workflow and legacy scheduling
- **Error Handling**: Robust error handling with fallback data
- **Environment Configuration**: Easy setup with environment variables

## Quick Start

### Option 1: n8n Workflow (Recommended)

For modern, reliable automation:

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Import n8n Workflow**:
   - Import `workflows/telegram-bot-scheduler.json` into your n8n instance
   - Configure environment variables in n8n
   - Activate the workflow

4. **Documentation**: See `docs/n8n-setup.md` for detailed setup instructions

### Option 2: Legacy Continuous Execution

For backward compatibility with Railway, Heroku, etc.:

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Legacy Scheduler**:
   ```bash
   python legacy_scheduler.py
   ```

### Option 3: Single Execution

For custom scheduling solutions:

```bash
python telegram_match_poster.py
```

## Configuration

Required environment variables:

- `API_URL`: Match data API endpoint
- `BOT_TOKEN`: Telegram bot token (from @BotFather)
- `CHANNEL_ID`: Telegram channel ID
- `DEBUG_MODE`: Set to "true" for testing (optional)

See `.env.example` for details.

## Project Structure

```
├── telegram_match_poster.py    # Main bot script (single execution)
├── legacy_scheduler.py         # Legacy continuous execution
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── workflows/
│   └── telegram-bot-scheduler.json  # n8n workflow
└── docs/
    └── n8n-setup.md          # Detailed n8n setup guide
```

## Migration Guide

Migrating from the old schedule-based approach:

1. **Update your code**: The main script no longer has built-in scheduling
2. **Choose deployment method**: n8n workflow (recommended) or legacy scheduler
3. **Update your deployment**: Use appropriate script for your platform

## Development

Test the bot functionality:

```bash
DEBUG_MODE=true python telegram_match_poster.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request