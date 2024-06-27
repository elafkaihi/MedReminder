# MedReminder Bot

Welcome everyone to a side project I've been developing in my free time. Managing medications can be a hassle, but with the MedReminder bot, it doesn't have to be. This smart chatbot helps users effortlessly keep track of their medications and get timely notifications. In this tutorial, we'll walk you through the steps to create a MedReminder bot using AWS, Telegram, and the OpenAI API.

## Prerequisites

Before you start, ensure you have the following:

- An AWS account.
- A Telegram bot token (you can get one by creating a bot with BotFather on Telegram).
- OpenAI API key for accessing ChatGPT.
- Basic knowledge of Python and AWS Lambda.

## Architecture

Curious to learn more? Let's dive in! Here's the architecture I've built:

![MedReminder Architecture](https://github.com/elafkaihi/MedReminder/blob/main/Architecture.png)

## Step 1: Setting Up the Telegram Bot

### Create a Telegram Bot

1. Open Telegram and search for `@BotFather`.
2. Start a conversation and use the `/newbot` command to create a new bot.
3. Follow the prompts to name your bot and get the token. Save this token for later use.

## Step 2: Setting Up AWS Services

All the mentioned codes are available in the GitHub repository: [MedReminder GitHub Repository](https://github.com/elafkaihi/MedReminder)

### Creating an RDS MySQL Database

1. **Create an RDS MySQL Instance**:
   - Go to the AWS RDS console and create a new MySQL database instance.
   - Configure the instance settings (e.g., instance class, storage, and security settings).
   - Note the endpoint, username, and password for your database.

2. **Create the Database Schema**:
   - Connect to the MySQL instance using a tool like MySQL Workbench.
   - Create the necessary tables:
     ```sql
     CREATE TABLE users (
         id INT AUTO_INCREMENT PRIMARY KEY,
         chat_id VARCHAR(15) UNIQUE,
         user_score INT DEFAULT 0
     );

     CREATE TABLE medications (
         id INT AUTO_INCREMENT PRIMARY KEY,
         chat_id VARCHAR(15),
         medication_name VARCHAR(255),
         time TIME,
         notification_status ENUM('pending', 'confirmed', 'missed') DEFAULT 'pending',
         notification_timestamp DATETIME
     );
     ```

### Configure OpenAI API

Configure an OpenAI API that will answer your patient questions based on their medications and the model you choose. Save your OpenAI Key.

### Create S3 Bucket

Create an S3 bucket that stores the quotes images to send to your users and store your S3 Bucket Name.

### Creating Lambda Functions

1. **Dispatcher Lambda Function**: This function acts as the central router for incoming Telegram messages. It parses the message, identifies the command, and invokes the appropriate Lambda function (e.g., Add, Summary, ChatGPT).

2. **ChatGPT Lambda Function**: This function handles user queries that start with `/question`. It fetches the user's medication data, constructs a prompt, and sends it to the ChatGPT API. The response from ChatGPT is then sent back to the user.

3. **Add Lambda Function**: This function processes requests to add new medications. It extracts the medication details from the message, validates them, and stores them in the RDS MySQL database.

4. **Summary Lambda Function**: This function retrieves and sends a summary of the user's medications. When a user sends a `/summary` command, this function queries the database for all medications associated with the user and sends a formatted list back to the user.

5. **Notification Lambda Function**: This function is triggered by a scheduled EventBridge cron job to send medication reminders to users. It queries the database for medications that need to be taken in the next hour and sends reminder messages via Telegram.

6. **User Response Lambda Function**: This function handles responses from users confirming whether they have taken their medication. It updates the medication status in the database and adjusts the user's score based on their response.

7. **Missed Dose Lambda Function**: This function is triggered by a scheduled EventBridge cron job to check for missed doses. It identifies medications that were not confirmed as taken and updates their status to missed in the database. It also adjusts the user's score accordingly.

8. **Motivational Lambda Function**: This function sends motivational messages or images to users at scheduled times or when they miss taking their medication. It selects a random motivational image from an S3 bucket and sends it to the user via Telegram.

Make sure to fill the environment variables in each Lambda function and to link the `requirements.txt` dependencies as a Layer.

### Configure the EventBridge Schedules

Configure two cron jobs with EventBridge. The first job, set to run at `00 * * * ? *`, will trigger the Notification Lambda Function. The second job, scheduled at `15 * * * ? *`, will invoke the Missed Dose Lambda Function. Additionally, create a third cron job to send random motivational pictures at times of your preference or when pills are not taken as scheduled.

## Step 3: Setting Up API Gateway

1. **Create an API Gateway**:
   - Go to the API Gateway console and create a new REST API.
   - Create a new resource and set up a POST method.
   - Configure the POST method to trigger the Dispatcher Lambda function.

2. **Set Up Telegram Webhook**:
   - Set the webhook URL to point to the API Gateway endpoint:
     ```sh
     https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook?url=https://<YOUR_API_GATEWAY_URL>/webhook
     ```

## Conclusion

Congratulations! You've built a MedReminder bot that helps users manage their medications and get answers to their questions using ChatGPT. This project demonstrates the power of integrating AWS services, Telegram, and advanced AI models to create useful and interactive applications.

For a detailed version of this tutorial, please visit my [Medium post](https://medium.com/@lafkaihi.mehdi/how-to-build-a-medreminder-bot-with-aws-telegram-and-chatgpt-1c0e8a518a0f).

---

Feel free to contribute to this project by submitting issues or pull requests to improve the MedReminder bot.

