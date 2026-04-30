# RekognitionOps for Armah Dynamics Co.

Automated image classification system powered by **Amazon Rekognition** and **GitHub Actions**. Images added to this repository are automatically analyzed, labeled, and stored in **DynamoDB** — no manual tagging required.

---

## What This Project Does

| Without This System | With This System |
|---|---|
| Manual image tagging — hours per batch | Automatic tagging — seconds per image |
| Inconsistent labels across teams | Standardized AI-generated labels |
| No content moderation | Automatic classification and filtering |
| Hard to search image content | Queryable metadata stored in DynamoDB |

---

## Architecture

```
Developer adds image to images/ folder
              ↓
GitHub detects the change
              ↓
GitHub Actions workflow triggers
              ↓
Image uploads to S3
(rekognition-input/beta/ or rekognition-input/prod/)
              ↓
Amazon Rekognition analyzes the image
              ↓
Labels + confidence scores saved to DynamoDB
```

### Branch-Based Environments

| Git Event | Environment | DynamoDB Table |
|---|---|---|
| Pull Request → main | Beta (testing) | `beta_results` |
| Merge → main | Production | `prod_results` |

---

## Project Structure

```
RekognitionOps-for-Armah-Dynamics-Co/
├── .github/
│   └── workflows/
│       ├── on_pull_request.yml   # Triggers on PR → writes to beta_results
│       └── on_merge.yml          # Triggers on merge → writes to prod_results
├── docs/
│   ├── AWS_SETUP.md
│   ├── GITHUB_SETUP.md
│   ├── VALIDATION_GUIDE.md
│   └── screenshots/
├── images/                       # Drop .jpg or .png files here
├── scripts/
│   └── analyze_image.py          # Core script: upload → analyze → store
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Quick Start

### 1 — Add an Image

```bash
# Add any .jpg or .png file to the images/ folder
# Then push to a new branch
git checkout -b feature/new-image
git add images/your-image.jpg
git commit -m "Add image for classification"
git push origin feature/new-image
```

### 2 — Open a Pull Request

- Go to GitHub → open a Pull Request targeting `main`
- The **Analyze Images (PR - Beta)** workflow triggers automatically

### 3 — Check Results in DynamoDB

```bash
aws dynamodb scan --table-name beta_results --region us-east-1
```

### Expected DynamoDB Output

```json
{
  "filename": "rekognition-input/beta/your-image.jpg",
  "labels": [
    {"Name": "Whiteboard", "Confidence": 98.5},
    {"Name": "Text",       "Confidence": 94.2},
    {"Name": "Person",     "Confidence": 88.7}
  ],
  "timestamp": "2026-04-29T21:00:00Z",
  "branch": "beta"
}
```

---

## AWS Resources

| Resource | Name |
|---|---|
| S3 Bucket | `arm-dyanamics-rekognition-eman-kwe` |
| DynamoDB Table (Beta) | `beta_results` |
| DynamoDB Table (Prod) | `prod_results` |
| IAM User | `pixelvision-ci` |
| AWS Region | `us-east-1` |

---

## GitHub Secrets Required

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | `us-east-1` |
| `S3_BUCKET` | `arm-dyanamics-rekognition-eman-kwe` |
| `DYNAMODB_TABLE_BETA` | `beta_results` |
| `DYNAMODB_TABLE_PROD` | `prod_results` |

---

## Setup Guides

| Guide | Description |
|---|---|
| [AWS Setup](docs/AWS_SETUP.md) | Create S3, DynamoDB, and IAM resources |
| [GitHub Setup](docs/GITHUB_SETUP.md) | Configure repository secrets |
| [Validation Guide](docs/VALIDATION_GUIDE.md) | Test and verify the pipeline |

---

## How the Pipeline Works

**Pull Request Workflow** (`on_pull_request.yml`)
- Triggers when a PR is opened targeting `main`
- Only runs if files in `images/` changed
- Uploads image to S3 under `rekognition-input/beta/`
- Calls Rekognition to detect labels
- Saves results to `beta_results` DynamoDB table

**Merge Workflow** (`on_merge.yml`)
- Triggers when code is merged into `main`
- Only runs if files in `images/` changed
- Uploads image to S3 under `rekognition-input/prod/`
- Calls Rekognition to detect labels
- Saves results to `prod_results` DynamoDB table

---

## Troubleshooting

| Error | Fix |
|---|---|
| `requirements.txt not found` | Make sure `requirements.txt` is in the root folder |
| `AccessDenied: s3:PutObject` | Check IAM policy has `s3:PutObject` permission |
| `InvalidS3ObjectException` | Check IAM policy has `s3:GetObject` permission |
| `Float types not supported` | Make sure `analyze_image.py` uses `Decimal` for confidence scores |
| `ResourceNotFoundException` | Verify DynamoDB table names match GitHub Secrets exactly |
| Workflow not triggering | Confirm image is inside `images/` folder and PR targets `main` |

---

## Data Format

Every record stored in DynamoDB follows this structure:

| Field | Type | Description |
|---|---|---|
| `filename` | String | S3 path of the image — used as unique ID |
| `labels` | List | Detected objects and scenes with confidence scores |
| `timestamp` | String | UTC timestamp of when analysis ran |
| `branch` | String | `beta` (PR) or `prod` (merge) |

---

## Tech Stack

- **Amazon S3** — Image storage
- **Amazon Rekognition** — AI image classification
- **Amazon DynamoDB** — Results storage
- **GitHub Actions** — CI/CD automation
- **Python + boto3** — AWS SDK for scripting
- **IAM** — Secure credential management
