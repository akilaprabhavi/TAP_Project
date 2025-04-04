
# Configuration for AWS and timezone
ACCOUNT_ID = 713881796790 
REGION = "us-east-1"  
TIMEZONE = "Australia/Sydney" 
LAMBDA_ROLE_NAME = "LambdaExecutionRole"
LAMBDA_FUNCTION_NAME = "ChatGPTThreatAnalysis"
EVENT_RULE_NAME = "DailyChatGPTThreatCheck"
SCHEDULE_EXPRESSION = "cron(44 10 * * ? *)"
PROMPT_BUCKET_NAME = "promptbucketakila"
CSV_FILE_NAME = "user_prompts"
IAM_ROLE_NAME = "LambdaS3AccessRole"
DYNAMO_DB_TABLE="AttackVectors"


