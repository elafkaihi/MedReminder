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
    print("Received event: ", json.dumps(event, indent=4))

    try:
        # Check if the message key is present in the event
        message = get_message_from_event(event)

        chat_id = message['chat']['id']

        # Connect to the database
        connection = pymysql.connect(
            host=rds_host,
            user=username,
            password=password,
            db=db_name
        )

        try:
            with connection.cursor() as cursor:
                # Query to fetch medication details
                sql = "SELECT medication_name, time FROM medreminder WHERE chatid = %s"
                cursor.execute(sql, (chat_id,))
                results = cursor.fetchall()

            # Create the summary message
            if results:
                summary_message = "Here is a summary of your medications:\n"
                for row in results:
                    summary_message += f"{row['medication_name']} at {row['time']}\n"
            else:
                summary_message = "You have no medications saved."

            # Send the summary message to the user
            send_telegram_message(telegram_token, chat_id, summary_message)

        except pymysql.MySQLError as e:
            print(f"MySQL Error: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"MySQL Error: {str(e)}")
            }
        finally:
            connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Summary sent successfully!')
        }

    except KeyError as e:
        print(f"KeyError: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Missing key: {str(e)}")
        }
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }

def get_message_from_event(event):
    """Extract the message from the incoming event"""
    if 'message' in event:
        return event['message']
    if 'body' in event:
        body = json.loads(event['body'])
        if 'message' in body:
            return body['message']
    raise KeyError("The 'message' key is missing in the event")

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
