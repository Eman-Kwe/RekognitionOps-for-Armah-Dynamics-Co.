# RekognitionOps for Arm Dynamics Co.

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

## Project Phases

This project is built in three progressive phases. Each phase builds on the previous one.

| Phase | Status | Description |
|---|---|---|
| **Phase 1 — Foundational** | ✅ Complete | Python scripts run directly in GitHub Actions |
| **Phase 2 — Advanced** | 🔄 In Progress | Lambda functions triggered by S3 events |
| **Phase 3 — Complex** | 🔜 Coming Soon | Full Infrastructure-as-Code with CloudFormation and Terraform |

---

## Architecture

### Phase 1 — Foundational
```
Developer adds image to images/ folder
              ↓
GitHub Actions workflow triggers
              ↓
Python script uploads image to S3
              ↓
Amazon Rekognition analyzes the image
              ↓
Labels saved directly to DynamoDB
```

### Phase 2 — Advanced (Event-Driven)
```
Developer adds image to images/ folder
              ↓
GitHub Actions uploads image to S3 only
              ↓
S3 Event Notification triggers Lambda
              ↓
Lambda calls Amazon Rekognition
              ↓
Lambda saves labels to DynamoDB
```

### Phase 3 — Complex (Infrastructure-as-Code)
```
Infrastructure defined in CloudFormation / Terraform
              ↓
GitHub Actions deploys all AWS resources automatically
              ↓
Same event-driven pipeline as Phase 2
              ↓
Full reproducibility across any AWS account
```

---

### Branch-Based Environments

| Git Event | Environment | DynamoDB Table |
|---|---|---|
| Pull Request → main | Beta (testing) | `beta_results` |
| Merge → main | Production | `prod_results` |

---

## Project Structure

```
RekognitionOps-for-Armah-Dynamics-Co/
│
├── .github/workflows/
│   ├── on_pull_request.yml              # Phase 1: PR → beta analysis
│   ├── on_merge.yml                     # Phase 1: merge → prod analysis
│   ├── on_pull_request_advanced.yml     # Phase 2: PR → S3 upload only
│   ├── on_merge_advanced.yml            # Phase 2: merge → S3 upload only
│   └── deploy_infrastructure.yml        # Phase 3: IaC deployment
│
├── docs/
│   ├── AWS_SETUP.md
│   ├── GITHUB_SETUP.md
│   ├── VALIDATION_GUIDE.md
│   ├── LAMBDA_DEPLOYMENT.md             # Phase 2
│   ├── S3_EVENT_CONFIGURATION.md        # Phase 2
│   ├── IAC_DEPLOYMENT.md                # Phase 3
│   └── screenshots/
│
├── images/                              # Drop .jpg or .png files here
│
├── lambda/                              # Phase 2
│   ├── beta/
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── prod/
│       ├── handler.py
│       └── requirements.txt
│
├── infrastructure/                      # Phase 3
│   ├── cloudformation/
│   │   └── template.yml
│   └── terraform/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── scripts/
│   └── analyze_image.py                 # Phase 1 core script
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Quick Start

### 1 — Add an Image

```bash
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

| Guide | Phase | Description |
|---|---|---|
| [AWS Setup](docs/AWS_SETUP.md) | 1 | Create S3, DynamoDB, and IAM resources |
| [GitHub Setup](docs/GITHUB_SETUP.md) | 1 | Configure repository secrets |
| [Validation Guide](docs/VALIDATION_GUIDE.md) | 1 | Test and verify the pipeline |
| [Lambda Deployment](docs/LAMBDA_DEPLOYMENT.md) | 2 | Deploy Lambda functions to AWS |
| [S3 Event Configuration](docs/S3_EVENT_CONFIGURATION.md) | 2 | Connect S3 uploads to Lambda |
| [IaC Deployment](docs/IAC_DEPLOYMENT.md) | 3 | Deploy all infrastructure as code |

---

## Phase 1 — Foundational Detail

**How it works:**
- GitHub Actions runs the full pipeline directly
- `on_pull_request.yml` → uploads image → calls Rekognition → writes to `beta_results`
- `on_merge.yml` → uploads image → calls Rekognition → writes to `prod_results`

**Files:**
- `scripts/analyze_image.py` — core Python script
- `.github/workflows/on_pull_request.yml`
- `.github/workflows/on_merge.yml`

---

## Phase 2 — Advanced Detail

**How it works:**
- GitHub Actions only uploads the image to S3
- S3 automatically triggers a Lambda function
- Lambda calls Rekognition and saves results to DynamoDB
- Analysis is fully decoupled from the CI/CD pipeline

**Files:**
- `lambda/beta/handler.py` — Lambda for beta environment
- `lambda/prod/handler.py` — Lambda for prod environment
- `.github/workflows/on_pull_request_advanced.yml`
- `.github/workflows/on_merge_advanced.yml`

**Docs:**
- [Lambda Deployment Guide](docs/LAMBDA_DEPLOYMENT.md)
- [S3 Event Configuration Guide](docs/S3_EVENT_CONFIGURATION.md)

---

## Phase 3 — Complex Detail

**How it works:**
- All AWS infrastructure is defined as code
- CloudFormation or Terraform creates every resource automatically
- GitHub Actions deploys infrastructure on merge
- No manual clicking in AWS Console required

**Files:**
- `infrastructure/cloudformation/template.yml`
- `infrastructure/terraform/main.tf`
- `infrastructure/terraform/variables.tf`
- `infrastructure/terraform/outputs.tf`
- `.github/workflows/deploy_infrastructure.yml`

**Docs:**
- [IaC Deployment Guide](docs/IAC_DEPLOYMENT.md)

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

| Field | Type | Description |
|---|---|---|
| `filename` | String | S3 path of the image — used as unique ID |
| `labels` | List | Detected objects and scenes with confidence scores |
| `timestamp` | String | UTC timestamp of when analysis ran |
| `branch` | String | `beta` (PR) or `prod` (merge) |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Amazon S3 | Image storage |
| Amazon Rekognition | AI image classification |
| Amazon DynamoDB | Results storage |
| AWS Lambda | Event-driven compute (Phase 2) |
| CloudFormation / Terraform | Infrastructure-as-Code (Phase 3) |
| GitHub Actions | CI/CD automation |
| Python + boto3 | AWS SDK for scripting |
| IAM | Secure credential management |
