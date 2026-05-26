# PowerShell script for Docker and ECR commands

# Configuration
$AWS_ACCOUNT_ID = "474833638797"
$ECR_REPO_NAME = "cedat"
$AWS_REGION = "ap-south-1"
$IMAGE_TAG = "latest"

# ECR Repository URL
$ECR_REPO_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

Write-Host "Step 1: Authenticating Docker with ECR..." -ForegroundColor Green
$loginCommand = aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URI
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to authenticate with ECR" -ForegroundColor Red
    exit 1
}

Write-Host "Step 2: Building Docker image..." -ForegroundColor Green
docker build -t "${ECR_REPO_NAME}:${IMAGE_TAG}" .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Step 3: Tagging image for ECR..." -ForegroundColor Green
docker tag "${ECR_REPO_NAME}:${IMAGE_TAG}" "${ECR_REPO_URI}:${IMAGE_TAG}"

Write-Host "Step 4: Pushing image to ECR..." -ForegroundColor Green
docker push "${ECR_REPO_URI}:${IMAGE_TAG}"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to push image to ECR" -ForegroundColor Red
    exit 1
}

Write-Host "Done! Image pushed to: ${ECR_REPO_URI}:${IMAGE_TAG}" -ForegroundColor Green




