# Use Amazon Linux 2 as the base image for Lambda with Python 3.11
FROM public.ecr.aws/lambda/python:3.11

# Set the working directory in the container
WORKDIR /var/task

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip, wheel, setuptools to latest
RUN pip install --upgrade pip wheel setuptools

# Install the dependencies in the container using only pre-built wheels
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt -t .

# Copy the entire application into the container
COPY app/ ./app

# Set the Lambda handler (app.main.handler points to the `handler` in main.py)
CMD ["app.main.handler"]
