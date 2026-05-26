#!/bin/bash

# Configuration
AWS_ACCOUNT_ID="941377152660"
AWS_REGION="ap-south-1"
ECR_REPOSITORY_NAME="cedat-email"
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting deployment process...${NC}"

# Step 1: Create ECR Repository (if it doesn't exist)
echo -e "${YELLOW}📦 Creating ECR repository...${NC}"
aws ecr create-repository \
    --repository-name $ECR_REPOSITORY_NAME \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 2>/dev/null || echo "Repository already exists or error occurred"

# Step 2: Get ECR Login Token
echo -e "${YELLOW}🔐 Logging into ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully logged into ECR${NC}"
else
    echo -e "${RED}❌ Failed to login to ECR${NC}"
    exit 1
fi

# Step 3: Build Docker Image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t $ECR_REPOSITORY_NAME:$IMAGE_TAG .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Step 4: Tag the Image for ECR
echo -e "${YELLOW}🏷️  Tagging image for ECR...${NC}"
docker tag $ECR_REPOSITORY_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG

# Step 5: Push Image to ECR
echo -e "${YELLOW}⬆️  Pushing image to ECR...${NC}"
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Image pushed successfully to ECR!${NC}"
    echo -e "${GREEN}🎯 Image URI: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG${NC}"
else
    echo -e "${RED}❌ Failed to push image to ECR${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
