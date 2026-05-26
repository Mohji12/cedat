#!/bin/bash

# Configuration
AWS_ACCOUNT_ID=474833638797
ECR_REPO_NAME=cedat
AWS_REGION=ap-south-1
IMAGE_TAG=latest

# ECR Repository URL
ECR_REPO_URI=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}

echo "Step 1: Authenticating Docker with ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URI}

echo "Step 2: Building Docker image..."
docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

echo "Step 3: Tagging image for ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_REPO_URI}:${IMAGE_TAG}

echo "Step 4: Pushing image to ECR..."
docker push ${ECR_REPO_URI}:${IMAGE_TAG}

echo "Done! Image pushed to: ${ECR_REPO_URI}:${IMAGE_TAG}"




