# Use the official AWS Lambda Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

# Set the working directory inside the container
WORKDIR /var/task

# Copy the application code and requirements file into the container
COPY requirements.txt .
# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Command to run the Lambda function
CMD ["application.handler"]