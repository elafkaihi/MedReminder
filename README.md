# MedReminder

Your health assistant on Telegram. Receive personalized reminders for your medications, daily health tips, and rewards for staying on track. Because every dose counts!

## Table of Contents
- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## About

MedReminder is a health assistant bot on Telegram designed to help you manage your medication schedule. It provides personalized reminders for your medications, daily health tips, and rewards for adhering to your medication schedule.

## Features

- **Personalized Medication Reminders**: Never miss a dose with timely reminders.
- **Daily Health Tips**: Receive tips to improve your health and well-being.
- **Rewards System**: Get rewarded for staying on track with your medication.

## Installation

To set up the MedReminder bot, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/elafkaihi/MedReminder.git
    cd MedReminder
    ```

2. Set up a virtual environment:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up your environment variables for the Telegram Bot API:
    ```sh
    export TELEGRAM_TOKEN='your_telegram_bot_token'
    ```

5. Run the bot:
    ```sh
    python main.py
    ```

## Usage

1. Start a chat with your bot on Telegram.
2. Use the `/start` command to initialize the bot.
3. Follow the prompts to set up your medication schedule and preferences.
4. Receive reminders and health tips directly in your Telegram chat.

## Contributing

We welcome contributions to improve MedReminder! To contribute, follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```sh
    git checkout -b feature/your-feature-name
    ```
3. Make your changes and commit them:
    ```sh
    git commit -m 'Add new feature'
    ```
4. Push to the branch:
    ```sh
    git push origin feature/your-feature-name
    ```
5. Create a pull request and describe your changes.
