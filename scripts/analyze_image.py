import boto3
import json
import os
from datetime import datetime
from decimal import Decimal   # Added to fix DynamoDB float error
from pathlib import Path

# Connect to AWS services using credentials from GitHub Secrets
s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))
rekognition_client = boto3.client('rekognition', region_name=os.getenv('AWS_REGION'))
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION'))


def upload_image_to_s3(image_path, bucket_name, branch):
    # Upload image to S3 under rekognition-input/{branch}/ prefix
    filename = os.path.basename(image_path)
    s3_key = f"rekognition-input/{branch}/{filename}"
    s3_client.upload_file(image_path, bucket_name, s3_key)
    print(f"✓ Uploaded {filename} to s3://{bucket_name}/{s3_key}")
    return s3_key


def analyze_image_with_rekognition(bucket_name, s3_key):
    # Send image to Rekognition and get back detected labels with confidence scores
    response = rekognition_client.detect_labels(
        Image={'S3Object': {'Bucket': bucket_name, 'Name': s3_key}},
        MaxLabels=10,      # Return top 10 most confident labels only
        MinConfidence=70   # Only include labels with 70%+ confidence
    )
    labels = [
        {
            "Name": label['Name'],
            "Confidence": Decimal(str(round(label['Confidence'], 2)))
            # Decimal() fixes DynamoDB error — it does not accept float numbers
        }
        for label in response['Labels']
    ]
    print(f"✓ Rekognition detected {len(labels)} labels")
    return labels


def write_results_to_dynamodb(table_name, filename, labels, branch):
    # Save analysis results to DynamoDB with timestamp and branch tag
    table = dynamodb.Table(table_name)
    item = {
        'filename':  filename,                              # S3 path — used as the unique record ID
        'labels':    labels,                               # AI-detected labels from Rekognition
        'timestamp': datetime.utcnow().isoformat() + 'Z', # When analysis ran
        'branch':    branch                                # beta (PR) or prod (merge)
    }
    table.put_item(Item=item)
    print(f"✓ Results written to DynamoDB table: {table_name}")
    print(json.dumps(item, indent=2, default=str))
    # default=str handles Decimal printing in the log output


def main():
    # Read all config from environment variables — set by GitHub Secrets in workflows
    bucket_name = os.getenv('S3_BUCKET')
    branch = os.getenv('BRANCH', 'unknown')

    # Pick the correct DynamoDB table based on which workflow is running
    table_name = os.getenv('DYNAMODB_TABLE_PROD') if branch == 'prod' else os.getenv('DYNAMODB_TABLE_BETA')

    if not all([bucket_name, table_name]):
        raise ValueError("Missing environment variables: S3_BUCKET or DYNAMODB_TABLE")

    # Find all jpg and png files inside the images/ folder
    image_files = list(Path('images').glob('*.jpg')) + list(Path('images').glob('*.png'))

    if not image_files:
        print("No images found in images/ folder")
        return

    print(f"Found {len(image_files)} image(s) — environment: {branch}")

    # Run the full pipeline for each image: upload → analyze → store
    for image_path in image_files:
        print(f"\nProcessing: {image_path}")
        s3_key = upload_image_to_s3(str(image_path), bucket_name, branch)
        labels = analyze_image_with_rekognition(bucket_name, s3_key)
        write_results_to_dynamodb(table_name, s3_key, labels, branch)

    print(f"\n✓ All {len(image_files)} image(s) processed successfully.")


if __name__ == '__main__':
    main()
    # Only runs when script is called directly (not when imported by another file)
