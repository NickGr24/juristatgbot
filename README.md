# Academy Bot - Telegram Bot for Legal Terms

A Telegram bot that sends daily legal terms and definitions to users.

## Features

- 📖 Daily legal terms delivery
- 📚 Personal word list management
- 🕒 Customizable delivery time
- ➕ Add/remove terms from personal list

## Local Testing Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Bot

```bash
python bot.py
```

The bot will start and begin listening for messages.

### 3. Test the Bot

1. Open Telegram
2. Find your bot (using the token in `bot.py`)
3. Send `/start` to begin
4. Use the keyboard buttons to interact with the bot

## Files

- `bot.py` - Main bot logic
- `database.py` - Database functions
- `bot_database.db` - SQLite database with 680 Romanian legal terms
- `requirements.txt` - Python dependencies
- `parse.py` - Utility functions

## Database

The bot uses SQLite with the following tables:
- `users` - User information and preferences
- `words` - Legal terms and definitions (680 Romanian terms)
- `user_words` - User's personal word lists

## Bot Commands

- `/start` - Initialize the bot and show welcome message
- "📖 Primește un cuvânt" - Get a new legal term
- "🕒 Setează ora de primire a termenilor" - Set delivery time
- "📚 Lista mea de noțiuni" - View personal word list

## Deployment

For deployment to Pella hosting or other platforms, ensure:
- All dependencies are installed
- The bot token is properly configured
- Database file is accessible
- Environment supports Python 3.8+ 

## Deploying to Pella Hosting

1. **Set up your environment variables:**
   - Create a `.env` file in the project root with:
     ```
     TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
     ```
2. **Ensure your `Procfile` exists:**
   - Content should be:
     ```
     worker: python bot.py
     ```
3. **Push your code to Pella:**
   - Follow Pella’s documentation for deploying Python bots.
   - Make sure your `requirements.txt`, `Procfile`, and `.env` are included.
4. **Database:**
   - The file `bot_database.db` must be present in the deployment directory. If you want persistent storage, check Pella’s docs for volume or storage options.

**Note:** Never commit your real bot token to version control. Use environment variables for secrets. 