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
        if 'message' not in event:
            if 'body' in event:
                body = json.loads(event['body'])
                if 'message' not in body:
                    raise KeyError("The 'message' key is missing in the event body")
                message = body['message']
            else:
                raise KeyError("The 'message' key is missing in the event")
        else:
            message = event['message']

        chat_id = message['chat']['id']

        connection = pymysql.connect(
            host=rds_host,
            user=username,
            password=password,
            db=db_name
        )

        try:
            with connection.cursor() as cursor:
                sql = "SELECT medication_name, time FROM medications WHERE phone_number = %s"
                cursor.execute(sql, (chat_id,))
                results = cursor.fetchall()

            if results:
                summary_message = "Here is a summary of your medications:\n"
                for row in results:
                    summary_message += f"{row['medication_name']} at {row['time']}\n"
            else:
                summary_message = "You have no medications saved."

            send_telegram_message(telegram_token, chat_id, summary_message)

        except Exception as e:
            print(f"Error: {str(e)}")

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
