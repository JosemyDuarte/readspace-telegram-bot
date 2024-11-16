# ReadSpace - A Omnivore Telegram Bot

[Omnivore shutdown](https://blog.omnivore.app/p/details-on-omnivore-shutting-down), this service doesn't work anymore.
---

This is a Telegram bot that sends highlights from [Omnivore](https://omnivore.app/) to users. Inspired
by [Readwise](https://readwise.io/), this bot allows users to receive their highlights from Omnivore in their Telegram
chat.

## How to use

1. Start a chat with the bot: [@OmniReadSpaceBot](https://t.me/OmniReadSpaceBot)
    - Note that this bot will only reply if I have this service running, I can't guarantee I will 😅 But instructions are similar if you are running your own version.
2. Send the command `/start` to the bot.
3. The bot will ask you for your Omnivore API key. You can get it from your Omnivore account settings.
4. The bot will ask you for the label of the highlights you want to receive.
5. The bot will ask you for the number of highlights you want to receive.
6. You will receive your highlights in your chat.

Run `/help` to see the available commands. Watch the video below to see how to use the bot.

https://github.com/JosemyDuarte/readspace-telegram-bot/assets/6247860/81e94478-99a3-4127-ada5-43acee9bee83

## Development

- You need to have a Google Cloud Platform account and a project to run this bot.
    - You need to enable the Google Sheets API for your project.
    - You need to create a service account and download the JSON key file.
    - You need to set the `GCP_CREDENTIALS` environment variable to the path of the JSON key file.
- You need to create and share a spreadsheet with the service account email created in the previous step.
    - You need to set the `SPREADSHEET_ID` environment variable to the ID of the spreadsheet you created.
- You need to have a Telegram bot token. You can get one by talking to [BotFather](https://t.me/BotFather).
    - You need to set the `TELEGRAM_BOT_TOKEN` environment variable to the token.

Check the file `docker-compose.yml` fill the environment variables and mount the GCP credentials into the containers.
Then just run `docker-compose up` and it will be running.

## Limitations

* Telegram API doesn't allow messages longer than 4096 characters, so too long highlights might need to be split into
  multiple messages.
* Telegram API doesn't allow sending more than 30 messages per second, so if you have a lot of highlights, it might take
  a while to send them all.
* Not storing highlights means that we are retrieving all the highlights from Omnivore every time we need to get them.
* Using a spreadsheet as a database comes with its own limitations and complexity.
* Google Spread Sheet API is limited to 300 reads and 300 writes per minute.

## Improvement ideas

* Add a way to store highlights so we don't need to retrieve them from Omnivore every time we need to send them.
* Automate the highlight sending process so that users automatically receive their highlights at a specific time.
    * Allow users to choose specific schedules for specific highlights. A highlight I'm more interesting in learning I
      might want to receive every day, while a highlight I'm less interested in learning I might want to receive only
      once a week.
* Build a web interface to allow users to manage their highlights and schedules.
* Allow users to choose other ways to receive their highlights, like email.
* Add more telemetry to the bot to understand how users are using it and what we can improve.
* Current implementation don't scale horizontally. We could use a message broker to allow multiple instances of the bot
  to process messages in parallel.
* Use proper database instead of Google Spread Sheet.
