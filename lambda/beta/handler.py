import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Connect to AWS — Lambda automatically uses its IAM role for auth
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    # Entry point — triggered automatically when image lands in S3 beta prefix
    try:
        # Extract bucket name and file path from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        print(f"Processing: s3://{bucket}/{key}")

        # Step 1 — Analyze image with Rekognition
        labels = analyze_with_rekognition(bucket, key)

        # Step 2 — Save results to beta DynamoDB table
        table_name = os.environ.get('DYNAMODB_TABLE_BETA', 'beta_results')
        write_to_dynamodb(table_name, key, labels, 'beta')

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Beta image analysis complete',
                'filename': key,
                'label_count': len(labels)
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def analyze_with_rekognition(bucket, key):
    # Call Rekognition to detect labels in the S3 image
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=10,                                               # Top 10 labels only
        MinConfidence=70                                            # 70% confidence minimum
    )
    labels = [
        {
            "Name": label['Name'],
            "Confidence": Decimal(str(round(label['Confidence'], 2)))
            # Decimal used here — DynamoDB does not accept float numbers
        }
        for label in response['Labels']
    ]
    print(f"Rekognition detected {len(labels)} labels")
    return labels


def write_to_dynamodb(table_name, filename, labels, branch):
    # Save analysis results to DynamoDB beta_results table
    table = dynamodb.Table(table_name)
    item = {
        'filename':  filename,
        'labels':    labels,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'branch':    branch
    }
    table.put_item(Item=item)
    print(f"Saved to DynamoDB [{table_name}]")