import json
import os
import boto3
import pymysql
import requests

def lambda_handler(event, context):
    # Log the incoming event for debugging purposes
    print("Received event: ", json.dumps(event, indent=4))

    try:
        # Parse the incoming message from Telegram
        message = get_message(event)
        chat_id = message['chat']['id']
        text = message['text']

        # Handle /start command
        if text == "/start":
            initialize_user(chat_id)
            send_telegram_message(os.environ['TELEGRAM_TOKEN'], chat_id, 
                "Hello! Welcome to the MedReminder bot. Use /add to add a medication or /summary to get a summary of your medications.")
            return response(200, 'Start message sent successfully!')

        elif text.startswith("/add"):
            target_function = get_env_variable('ADD_DRUG_FUNCTION')

        elif text.startswith("/summary"):
            target_function = get_env_variable('SUMMARY_FUNCTION')

        else:
            send_telegram_message(os.environ['TELEGRAM_TOKEN'], chat_id, 
                "Invalid command. Use /add or /summary.")
            return response(200, 'Invalid command message sent successfully!')

        # Invoke the target Lambda function
        invoke_lambda(target_function, event)

        return response(200, 'Request routed successfully!')

    except KeyError as e:
        print(f"KeyError: {str(e)}")
        return response(400, f"Missing key: {str(e)}")
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return response(500, f"Internal server error: {str(e)}")

def get_message(event):
    """ Extract the message from the incoming event """
    if 'message' in event:
        return event['message']
    elif 'body' in event:
        body = json.loads(event['body'])
        if 'message' in body:
            return body['message']
    raise KeyError("The 'message' key is missing in the event")

def get_env_variable(name):
    """ Retrieve environment variable or raise an error """
    value = os.environ.get(name)
    if not value:
        raise KeyError(f"Environment variable {name} is missing")
    return value

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

def invoke_lambda(function_name, event):
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',  # Asynchronous invocation
        Payload=json.dumps(event)
    )
    print(f"Invoked function {function_name}, response: {response}")

def response(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps(message)
    }

def initialize_user(chat_id):
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

    try:
        with connection.cursor() as cursor:
            # Check if the chatid already exists
            cursor.execute("SELECT chatid FROM users_scores WHERE chatid = %s", (chat_id,))
            result = cursor.fetchone()
            if not result:
                # Insert a new record with chatid and score 0
                cursor.execute("INSERT INTO users_scores (chatid, score) VALUES (%s, %s)", (chat_id, 0))
                connection.commit()
                print(f"Initialized user with chatid {chat_id}")

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {str(e)}")
    finally:
        connection.close()
