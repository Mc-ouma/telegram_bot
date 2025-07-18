# n8n Setup Guide for Telegram Match Posting Bot

This guide explains how to set up and deploy the Telegram match posting bot using n8n for automated scheduling and execution.

## Overview

The n8n workflow provides a more robust automation solution compared to the previous approach that used the `schedule` library with an infinite loop. The new setup offers:

- **Better reliability**: No need for continuous process execution
- **Visual monitoring**: Track execution status through n8n interface
- **Error handling**: Built-in retry mechanisms and error notifications
- **Resource efficiency**: Runs only when needed (daily at 8:00 AM EAT)
- **Scalability**: Easy to extend with additional automation steps

## Prerequisites

1. **n8n instance** (self-hosted or cloud)
2. **Python environment** with required dependencies
3. **Telegram bot token** and channel access
4. **API access** for match data (if using external API)

## Setup Instructions

### 1. Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Fill in your configuration values:
   ```bash
   # Required values
   API_URL=https://your-api-endpoint.com/matches.json
   BOT_TOKEN=your_telegram_bot_token
   CHANNEL_ID=your_telegram_channel_id
   DEBUG_MODE=false
   ```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Import n8n Workflow

1. Open your n8n interface
2. Go to **Workflows** → **Import from File**
3. Upload `workflows/telegram-bot-scheduler.json`
4. The workflow will be imported with the name "Telegram Bot Scheduler"

### 4. Configure Workflow Environment Variables

In your n8n instance, set the following environment variables:

- `API_URL`: Your match data API endpoint
- `BOT_TOKEN`: Telegram bot token
- `CHANNEL_ID`: Telegram channel ID
- `DEBUG_MODE`: Set to "false" for production

**Methods to set environment variables in n8n:**

#### Option A: Docker Environment Variables
If running n8n with Docker:
```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -e API_URL="your_api_url" \
  -e BOT_TOKEN="your_bot_token" \
  -e CHANNEL_ID="your_channel_id" \
  -e DEBUG_MODE="false" \
  n8nio/n8n
```

#### Option B: Environment File
Create a `.env` file in your n8n directory:
```bash
API_URL=your_api_url
BOT_TOKEN=your_bot_token
CHANNEL_ID=your_channel_id
DEBUG_MODE=false
```

#### Option C: n8n Settings
1. Go to **Settings** → **Environments**
2. Add each variable manually

### 5. Workflow Configuration

The imported workflow includes:

1. **Daily Trigger**: Runs at 05:00 UTC (8:00 AM EAT)
2. **Manual Trigger**: For testing purposes
3. **Script Execution**: Runs the Python script with environment variables
4. **Error Handling**: Logs success/failure and handles errors
5. **Status Checking**: Validates execution results

### 6. Testing the Setup

1. **Test the Python script directly**:
   ```bash
   DEBUG_MODE=true python telegram_match_poster.py
   ```

2. **Test the n8n workflow**:
   - Open the workflow in n8n
   - Click the "Manual Trigger (Test)" node
   - Click "Execute Workflow"
   - Monitor the execution in the workflow interface

### 7. Production Deployment

1. **Activate the workflow**: In n8n, set the workflow to "Active"
2. **Verify timezone**: Ensure n8n is configured for `Africa/Nairobi` timezone
3. **Monitor execution**: Check the workflow execution history daily

## Workflow Details

### Schedule
- **Frequency**: Daily
- **Time**: 05:00 UTC (08:00 AM EAT)
- **Timezone**: Africa/Nairobi

### Execution Path
1. Cron trigger activates at scheduled time
2. Execute Command node runs the Python script
3. Script output is captured and analyzed
4. Success/failure is logged accordingly
5. Errors trigger the error handling path

### Error Handling
- Exit code validation
- Stdout/stderr capture
- Detailed logging
- Future extension points for notifications

## Monitoring and Maintenance

### Execution Logs
- View execution history in n8n interface
- Check logs for each workflow run
- Monitor for failed executions

### Manual Execution
- Use the manual trigger for testing
- Helpful for debugging issues
- Can be run outside of scheduled times

### Troubleshooting

#### Common Issues

1. **Environment variables not found**:
   - Check n8n environment variable configuration
   - Verify variable names match exactly

2. **Python script fails**:
   - Test script execution directly first
   - Check Python dependencies
   - Verify file paths and permissions

3. **Telegram API errors**:
   - Validate bot token and permissions
   - Check channel ID format (should include negative sign for channels)
   - Ensure bot is added to the channel with posting permissions

4. **Timezone issues**:
   - Verify n8n timezone setting
   - Check that cron expression matches intended schedule

### Extending the Workflow

The workflow can be extended with additional nodes:

- **Slack notifications** for execution status
- **Email alerts** for failures
- **Data processing** steps before posting
- **Multiple channel posting**
- **Custom analytics** and reporting

## Migration from Schedule-based Approach

If migrating from the previous schedule-based implementation:

1. **Stop the old process**: Terminate any running instances of the old script
2. **Deploy modified script**: Use the new version without built-in scheduling
3. **Activate n8n workflow**: Enable the workflow to take over scheduling
4. **Monitor transition**: Verify successful execution for several days

## Security Considerations

1. **Environment Variables**: Never commit actual credentials to version control
2. **Bot Permissions**: Use principle of least privilege for bot permissions
3. **API Access**: Secure API endpoints appropriately
4. **n8n Access**: Secure your n8n instance with proper authentication

## Support

For issues or questions:
1. Check the workflow execution logs in n8n
2. Review the Python script logs
3. Test components individually
4. Refer to n8n documentation for platform-specific issues