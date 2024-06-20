import pymysql
import json
import os
import datetime
from twilio.rest import Client

def lambda_handler(event, context):
    # Database connection details
    rds_host = os.environ['RDS_HOST']
    username = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    
    # Twilio credentials
    twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
    twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']

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
            sql = "SELECT phone_number, medication_name FROM medications WHERE time >= %s AND time < %s"
            cursor.execute(sql, (current_hour, next_hour))
            results = cursor.fetchall()
            
            # Sending messages via Twilio
            client = Client(twilio_account_sid, twilio_auth_token)
            for result in results:
                phone_number = result['phone_number']
                medication_name = result['medication_name']
                message_body = f"Hey, your {medication_name} has to be taken now."
                
                message = client.messages.create(
                    body=message_body,
                    from_=twilio_phone_number,
                    to=phone_number
                )
                
                print(f"Sent message to {phone_number}: {message_body}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        connection.close()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Messages sent successfully!')
    }
