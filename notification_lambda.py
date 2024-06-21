import pymysql
import json
import os
import datetime
import requests

def lambda_handler(event, context):
    # Database connection details
    rds_host = os.environ['RDS_HOST']
    username = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    
    # Telegram Bot API details
    telegram_token = os.environ['TELEGRAM_TOKEN']

    # Connect to the database
    connection = pymysql.connect(
        host=rds_host,
        user=username,
        password=password,
        db=db_name
    )
    
    current_hour = datetime.datetime.now().strftime('%H:00:00')
    next_hour = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%H:00:00')
    
    try:
        with connection.cursor() as cursor:
            # Query to fetch medications to be taken in the current hour
            sql = """
            SELECT id, user_id, phone_number, medication_name 
            FROM medications 
            WHERE time >= %s AND time < %s
            """
            cursor.execute(sql, (current_hour, next_hour))
            results = cursor.fetchall()
            
            # Sending messages via Telegram
            for result in results:
                med_id = result['id']
                user_id = result['user_id']
                chat_id = result['phone_number']
                medication_name = result['medication_name']
                message_body = f"Hey, it's time to take your {medication_name}. Please confirm with 'yes' or 'no'."
                
                send_telegram_message(telegram_token, chat_id, message_body)
                print(f"Sent message to {chat_id}: {message_body}")
                
                # Update the notification status and timestamp
                update_sql = """
                UPDATE medications 
                SET notification_status = 'pending', notification_timestamp = NOW() 
                WHERE id = %s
                """
                cursor.execute(update_sql, (med_id,))
                connection.commit()
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        connection.close()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Messages sent successfully!')
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
