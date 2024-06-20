import pymysql
import json
import os
import requests

def lambda_handler(event, context):
    # Database connection details
    rds_host = os.environ['RDS_HOST']
    username = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    
    # Telegram Bot API details
    telegram_token = os.environ['TELEGRAM_TOKEN']

    # Log the incoming event for debugging purposes
    print("Received event: ", json.dumps(event))

    try:
        # Check if event has the necessary keys directly
        if 'message' not in event:
            raise KeyError("The 'message' key is missing in the event")

        # Parse the incoming message from Telegram
        body = event  # Directly use event as it now matches the desired structure
        print("Parsed body (JSON): ", body)

        message = body['message']
        chat_id = message['chat']['id']
        message_body = message['text']

        # Check if the message format is correct
        if ',' not in message_body:
            raise ValueError("Invalid message format. Expected 'medication_name, time'.")

        # Assuming the format is "medication_name, time"
        medication_name, time = map(str.strip, message_body.split(','))

        # Connect to the database
        connection = pymysql.connect(
            host=rds_host,
            user=username,
            password=password,
            db=db_name
        )

        try:
            with connection.cursor() as cursor:
                # Insert data into MySQL
                sql = "INSERT INTO medreminder (chatid, medication_name, time) VALUES (%s, %s, %s)"
                cursor.execute(sql, (chat_id, medication_name, time))
                connection.commit()
            print(f"Inserted medication: {medication_name} at {time} for chat ID: {chat_id}")

            # Send confirmation message back to the user
            send_telegram_message(telegram_token, chat_id, f"Medication '{medication_name}' has been saved for {time}.")

        except Exception as e:
            print(f"Error: {str(e)}")

        finally:
            connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Medication saved successfully!')
        }

    except KeyError as e:
        print(f"KeyError: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Missing key: {str(e)}")
        }
    
    except ValueError as e:
        print(f"ValueError: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Value error: {str(e)}")
        }
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    else:
        print(f"Sent message: {message}")
