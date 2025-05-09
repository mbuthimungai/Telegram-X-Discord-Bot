# Telegram-X-Discord-Bot

**Telegram-X-Discord-Bot** is a powerful multi-platform monitoring bot that listens for messages on **Discord**, **Twitter (X)**, and **Telegram**, processes those messages, and sends curated or relevant content back into specified Discord channels.

---

## Features

- Listens to new messages from:

  - Discord servers
  - Telegram groups or channels
  - Twitter accounts or hashtags

- Processes and filters messages based on keywords, patterns, or custom logic
- Sends results to configurable Discord channels
- Supports real-time or interval-based processing

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/mbuthimungai/Telegram-X-Discord-Bot.git
cd Telegram-X-Discord-Bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the root directory with the following:

```env
DISCORD_TOKEN=your_discord_bot_token
TELEGRAM_API_KEY=your_telegram_api_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TARGET_DISCORD_CHANNEL_ID=your_channel_id
KEYWORDS=bitcoin,ethereum,elonmusk
```

### 4. Run the bot

```bash
python main.py
```

---

## Architecture Overview

```text
+------------------+       +------------------+
| Telegram Listener|----->|                  |
+------------------+      |                  |
                          |                  |
+------------------+      |                  |       +----------------------+
| Twitter Listener |----->| Message Processor|----->| Discord Message Pusher|
+------------------+      |                  |       +----------------------+
                          |                  |
+------------------+      |                  |
| Discord Listener |----->|                  |
+------------------+       +------------------+
```

---

## Configuration Options

You can extend or configure:

- Keywords to filter
- Message formatting
- Rate limiting
- Platform-specific behavior (e.g., only fetch tweets with images)

---

## Example Use Cases

- Track mentions of specific stocks or crypto coins
- Centralize alerts across platforms into one Discord channel
- Create a custom social media dashboard for real-time trends

---

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

---
