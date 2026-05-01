import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    # Entry point — triggered automatically when image lands in S3 prod prefix
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        print(f"[PROD] Processing: s3://{bucket}/{key}")

        labels = analyze_with_rekognition(bucket, key)

        table_name = os.environ.get('DYNAMODB_TABLE_PROD', 'prod_results')
        write_to_dynamodb(table_name, key, labels, 'prod')

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Production image analysis complete',
                'filename': key,
                'label_count': len(labels)
            })
        }

    except Exception as e:
        print(f"[PROD] Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def analyze_with_rekognition(bucket, key):
    # Call Rekognition to detect labels in the S3 image
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=10,
        MinConfidence=70
    )
    labels = [
        {
            "Name": label['Name'],
            "Confidence": Decimal(str(round(label['Confidence'], 2)))
        }
        for label in response['Labels']
    ]
    print(f"[PROD] Rekognition detected {len(labels)} labels")
    return labels


def write_to_dynamodb(table_name, filename, labels, branch):
    # Save analysis results to DynamoDB prod_results table
    table = dynamodb.Table(table_name)
    item = {
        'filename':  filename,
        'labels':    labels,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'branch':    branch
    }
    table.put_item(Item=item)
    print(f"[PROD] Saved to DynamoDB [{table_name}]")