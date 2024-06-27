import random
import pymysql
import json
import os
import requests
import boto3

def lambda_handler(event, context):
    # Database connection details
    rds_host = os.environ['RDS_HOST']
    username = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    
    # Telegram Bot API details
    telegram_token = os.environ['TELEGRAM_TOKEN']
    
    # S3 bucket details
    s3_bucket = os.environ['S3_BUCKET']
    
    # Create S3 client
    s3 = boto3.client('s3')
    
    # List all images in the S3 bucket
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix='quotes/')
        images = [content['Key'] for content in response.get('Contents', [])]
        print(images)
    except Exception as e:
        print(f"Error listing objects in S3: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to list images in S3')
        }
    
    if not images:
        print("No images found in S3 bucket")
        return {
            'statusCode': 404,
            'body': json.dumps('No images found in S3 bucket')
        }
    
    # Select a random image
    image_key = random.choice(images)
    
    # Generate a presigned URL for the image
    try:
        image_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket, 'Key': image_key},
            ExpiresIn=3600
        )
    except Exception as e:
        print(f"Error generating presigned URL: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to generate presigned URL')
        }
    
    # Connect to the database
    connection = pymysql.connect(
        host=rds_host,
        user=username,
        password=password,
        db=db_name
    )

    try:
        with connection.cursor() as cursor:
            # Query to fetch all patient chat IDs
            sql = "SELECT DISTINCT chatid FROM medreminder"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            for result in results:
                chat_id = result[0]
                send_telegram_image(telegram_token, chat_id, image_url)
                print(f"Sent quote to {chat_id}: {image_url}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        connection.close()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Motivational quotes sent successfully!')
    }

def send_telegram_image(token, chat_id, image_url):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        'chat_id': chat_id,
        'photo': image_url
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send image: {response.text}")
    else:
        print(f"Sent image: {image_url}")
