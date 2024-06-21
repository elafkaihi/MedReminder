import pymysql
import json
import os
import datetime

def lambda_handler(event, context):
    # Database connection details
    rds_host = os.environ['RDS_HOST']
    username = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    
    # Connect to the database
    connection = pymysql.connect(
        host=rds_host,
        user=username,
        password=password,
        db=db_name
    )
    
    two_minutes_ago = (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        with connection.cursor() as cursor:
            # Query to fetch medications with pending notifications older than 2 minutes
            sql = """
            SELECT id, user_id, phone_number, medication_name 
            FROM medications 
            WHERE notification_status = 'pending' AND notification_timestamp <= %s
            """
            cursor.execute(sql, (two_minutes_ago,))
            results = cursor.fetchall()
            
            for result in results:
                med_id = result['id']
                user_id = result['user_id']
                chat_id = result['phone_number']
                medication_name = result['medication_name']
                
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
                
                # Send a message to the user
                send_telegram_message(os.environ['TELEGRAM_TOKEN'], chat_id, f"You missed taking your {medication_name}. Your score has been decreased by 1. Please remember to take it as soon as possible.")
                print(f"Marked medication {medication_name} as missed for chat ID {chat_id}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        connection.close()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Missed notifications processed successfully!')
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
