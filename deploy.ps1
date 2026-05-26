# Configuration
$AWS_ACCOUNT_ID = "941377152660"
$AWS_REGION = "ap-south-1"
$ECR_REPOSITORY_NAME = "cedat-email"
$IMAGE_TAG = "latest"

Write-Host "🚀 Starting deployment process..." -ForegroundColor Yellow

# Step 1: Create ECR Repository (if it doesn't exist)
Write-Host "📦 Creating ECR repository..." -ForegroundColor Yellow
try {
    aws ecr create-repository `
        --repository-name $ECR_REPOSITORY_NAME `
        --region $AWS_REGION `
        --image-scanning-configuration scanOnPush=true `
        --encryption-configuration encryptionType=AES256 2>$null
    Write-Host "✅ ECR repository created or already exists" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ Repository already exists or error occurred" -ForegroundColor Cyan
}

# Step 2: Get ECR Login Token
Write-Host "🔐 Logging into ECR..." -ForegroundColor Yellow
try {
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    Write-Host "✅ Successfully logged into ECR" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to login to ECR" -ForegroundColor Red
    exit 1
}

# Step 3: Build Docker Image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
try {
    docker build -t "$ECR_REPOSITORY_NAME`:$IMAGE_TAG" .
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Step 4: Tag the Image for ECR
Write-Host "🏷️ Tagging image for ECR..." -ForegroundColor Yellow
docker tag "$ECR_REPOSITORY_NAME`:$IMAGE_TAG" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME`:$IMAGE_TAG"

# Step 5: Push Image to ECR
Write-Host "⬆️ Pushing image to ECR..." -ForegroundColor Yellow
try {
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME`:$IMAGE_TAG"
    Write-Host "✅ Image pushed successfully to ECR!" -ForegroundColor Green
    Write-Host "🎯 Image URI: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME`:$IMAGE_TAG" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to push image to ECR" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
