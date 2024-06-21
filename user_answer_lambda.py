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

    # Parse the incoming message from Telegram
    body = json.loads(event['body'])
    message = body['message']
    chat_id = message['chat']['id']
    text = message['text'].strip().lower()

    # Connect to the database
    connection = pymysql.connect(
        host=rds_host,
        user=username,
        password=password,
        db=db_name
    )

    try:
        with connection.cursor() as cursor:
            # Check if there is a pending notification
            sql = """
            SELECT id, user_id, medication_name 
            FROM medications 
            WHERE phone_number = %s AND notification_status = 'pending'
            """
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            
            if result:
                med_id = result['id']
                user_id = result['user_id']
                medication_name = result['medication_name']
                
                if text == 'yes':
                    # Update the notification status to confirmed and increment the user's score
                    update_med_sql = """
                    UPDATE medications 
                    SET notification_status = 'confirmed' 
                    WHERE id = %s
                    """
                    update_user_sql = """
                    UPDATE users 
                    SET user_score = user_score + 1 
                    WHERE id = %s
                    """
                    cursor.execute(update_med_sql, (med_id,))
                    cursor.execute(update_user_sql, (user_id,))
                    connection.commit()
                    send_telegram_message(telegram_token, chat_id, f"Great! You've confirmed taking your {medication_name}. Your score has been increased by 1.")
                elif text == 'no':
                    # Update the notification status to missed and decrement the user's score
                    update_med_sql = """
                    UPDATE medications 
                    SET notification_status = 'missed' 
                    WHERE id = %s
                    """
                    update_user_sql = """
                    UPDATE users 
                    SET user_score = user_score - 1 
                    WHERE id = %s
                    """
                    cursor.execute(update_med_sql, (med_id,))
                    cursor.execute(update_user_sql, (user_id,))
                    connection.commit()
                    send_telegram_message(telegram_token, chat_id, f"Please remember to take your {medication_name} as soon as possible. Your score has been decreased by 1.")
                else:
                    send_telegram_message(telegram_token, chat_id, "Please respond with 'yes' or 'no'.")
            else:
                send_telegram_message(telegram_token, chat_id, "No pending medication notifications.")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        connection.close()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Response processed successfully!')
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
