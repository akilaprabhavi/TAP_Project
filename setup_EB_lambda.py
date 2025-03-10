import boto3
import json
import time
from config import ACCOUNT_ID, REGION, TIMEZONE

# AWS Clients
iam = boto3.client('iam', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)
events = boto3.client('events', region_name=REGION)

# Constants
LAMBDA_ROLE_NAME = "LambdaExecutionRole"
LAMBDA_FUNCTION_NAME = "ChatGPTThreatAnalysis"
EVENT_RULE_NAME = "DailyChatGPTThreatCheck"
SCHEDULE_EXPRESSION = "cron(13 1 * * ? *)"  

# Step 1: Create IAM Role for Lambda
def create_iam_role():
    try:
        iam.get_role(RoleName=LAMBDA_ROLE_NAME)
        print(f"IAM role '{LAMBDA_ROLE_NAME}' already exists.Skipping creation.")
        return
    except iam.exceptions.NoSuchEntityException:
        pass

        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        role = iam.create_role(
            RoleName=LAMBDA_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        print(f"IAM role '{LAMBDA_ROLE_NAME}' created successfully.")
        time.sleep(10)  # Wait for IAM role propagation

        # Attach policy for CloudWatch Logs
        iam.attach_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        print("Attached AWSLambdaBasicExecutionRole policy to IAM role.")

# Step 2: Create Lambda Function
def create_lambda_function():
    try:
        lambda_client.get_function(FunctionName=LAMBDA_FUNCTION_NAME)
        print(f"Lambda function '{LAMBDA_FUNCTION_NAME}' already exists. Skipping creation.")
        return
    except lambda_client.exceptions.ResourceNotFoundException:
        pass  # Proceed to create function

    with open("lambda_function.zip", "rb") as f:
        zipped_code = f.read()

    response = lambda_client.create_function(
        FunctionName=LAMBDA_FUNCTION_NAME,
        Runtime="python3.12",
        Role=f"arn:aws:iam::{ACCOUNT_ID}:role/{LAMBDA_ROLE_NAME}",
        Handler="lambda_function.lambda_handler",
        Code={"ZipFile": zipped_code},
        Timeout=30
    )
    print(f"Lambda function '{LAMBDA_FUNCTION_NAME}' created successfully.")

# Step 3: Create EventBridge Rule
def create_event_rule():
    try:
        # Check if the rule exists
        events.describe_rule(Name=EVENT_RULE_NAME)
        print(f"EventBridge rule '{EVENT_RULE_NAME}' already exists. Deleting...")

        # Remove existing targets before deleting the rule
        events.remove_targets(Rule=EVENT_RULE_NAME, Ids=["LambdaTarget"])
        print("Removed existing targets from EventBridge rule.")

        # Delete the existing rule
        events.delete_rule(Name=EVENT_RULE_NAME)
        print(f"Deleted EventBridge rule '{EVENT_RULE_NAME}'.")
    except events.exceptions.ResourceNotFoundException:
        print(f"EventBridge rule '{EVENT_RULE_NAME}' not found. Proceeding with creation.")

    # Create new rule with updated schedule
    events.put_rule(
        Name=EVENT_RULE_NAME,
        ScheduleExpression=SCHEDULE_EXPRESSION,
        State="ENABLED"
    )
    print(f"Created new EventBridge rule '{EVENT_RULE_NAME}' with schedule '{SCHEDULE_EXPRESSION}'.")

# Step 4: Add Lambda as Target to Event Rule
def add_lambda_as_target():
    target_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{LAMBDA_FUNCTION_NAME}"

    # Add EventBridge Target
    events.put_targets(
        Rule=EVENT_RULE_NAME,
        Targets=[{"Id": "LambdaTarget", "Arn": target_arn}]
    )
    print("Lambda function added as target to EventBridge rule.")

    # Check if permission already exists before adding
    try:
        policy = lambda_client.get_policy(FunctionName=LAMBDA_FUNCTION_NAME)
        policy_doc = json.loads(policy["Policy"])

        for statement in policy_doc["Statement"]:
            if statement["Sid"] == "AllowEventBridge":
                print("Permission 'AllowEventBridge' already exists. Skipping permission update.")
                return
    except lambda_client.exceptions.ResourceNotFoundException:
        pass  # No existing permissions, so add it

    lambda_client.add_permission(
        FunctionName=LAMBDA_FUNCTION_NAME,
        StatementId="AllowEventBridge",
        Action="lambda:InvokeFunction",
        Principal="events.amazonaws.com",
        SourceArn=f"arn:aws:events:{REGION}:{ACCOUNT_ID}:rule/{EVENT_RULE_NAME}"
    )
    print("Lambda function permissions updated.")


# Main function to execute setup
def main():
    create_iam_role()
    create_lambda_function()
    create_event_rule()
    add_lambda_as_target()
    print("Setup complete! Lambda will run daily at scheduled time.")

if __name__ == "__main__":
    main()
