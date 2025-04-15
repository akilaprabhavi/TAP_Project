import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_deployment as s3_deployment,
    aws_events as events,
    aws_events_targets as targets,
    aws_dynamodb as dynamodb,
    Duration,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct
from aws_cdk.aws_lambda import FunctionUrlAuthType
from aws_cdk import aws_ecr as ecr
from pathlib import Path
import json
from config.config import *

class MyCdkStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ------------------ BE deployment -----------------------

        # IAM role for Lambda_function
        self.lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            role_name="MyLambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Add Secrets Manager permission as an inline policy
        self.lambda_role.add_to_policy(iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            resources=["*"]
        ))

        # Allow Lambda to put, get, and list objects in the S3 bucket
        self.lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            resources=[
                "arn:aws:s3:::promptbucketakila",
                "arn:aws:s3:::promptbucketakila/*"
            ]
        ))

        # Allow Lambda to get items from DynamoDB
        self.lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:Scan"
            ],
            resources=["arn:aws:dynamodb:us-east-1:713881796790:table/AttackVectorsData"]
        ))
    

        # Allow Lambda to get items from DynamoDB
        self.lambda_role3.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:CreateTable",
                "dynamodb:DeleteItem",
                "dynamodb:DeleteTable",
                "dynamodb:DescribeTable",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:UpdateItem",
                "dynamodb:UpdateTable",
                "dynamodb:DescribeTable",
                "dynamodb:ListTables"
            ],
            resources=[
                "arn:aws:dynamodb:us-east-1:713881796790:table/ThreatPulses",
                "arn:aws:dynamodb:us-east-1:713881796790:table/ThreatPulses/*"
            ]
        ))


        # Reference the existing ECR repository
        repository = ecr.Repository.from_repository_name(self, "Repository", "cyber-sec-be-lambda")

        # Define the Lambda function using the container image
        flask_lambda = _lambda.DockerImageFunction(
            self,
            "FlaskLambda",
            function_name=BE_lAMBDA_FUNCTION_NAME,
            code=_lambda.DockerImageCode.from_image_asset("lambda/"),
            role=self.lambda_role,
            timeout=Duration.seconds(30),
        )

        # Create a Lambda Function URL (publicly accessible)
        function_url = flask_lambda.add_function_url(auth_type=FunctionUrlAuthType.NONE)

        # ------------------- FE deployment -------------------------

        website_bucket = s3.Bucket(self, "WebsiteBucket",
            bucket_name=WEBSITE_BUCKET_NAME,
            website_index_document="index.html",
            website_error_document="index.html",
            block_public_access=s3.BlockPublicAccess(block_public_policy=False, restrict_public_buckets=False),
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # ---------------- DynamoDB Table ----------------
        self.threat_pulses_table = dynamodb.Table(
            self, "ThreatPulsesTable",
            table_name="ThreatPulses",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # ----------------- Other resources ----------------------

        prompt_bucket_name = "promptbucketakila"
        self.prompt_bucket = s3.Bucket(
            self, "promptbucket",
            bucket_name=prompt_bucket_name,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Grant permissions to access DynamoDB
        self.threat_pulses_table.grant_read_write_data(self.lambda_role3)

        # ---------------- Scheduled Threat Sync Lambda ----------------
        self.my_threat_updater = _lambda.Function(
            self,
            "MyThreatUpdaterLambda",
            function_name="MyThreatUpdater",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="auto_threat_sync.lambda_handler",
            code=_lambda.Code.from_asset("threat_updater_lambda/"),
            role=self.lambda_role3,  # <--- updated
            timeout=cdk.Duration.seconds(30),
            environment={
                "DYNAMODB_TABLE_NAME": self.threat_pulses_table.table_name,
            }
        )

        self.my_midnight_rule = events.Rule(
            self,
            "MidnightThreatSyncRule",
            rule_name="MidnightThreatSyncRule",
            schedule=events.Schedule.expression("cron(0 0 * * ? *)")  # Midnight UTC
        )

        self.my_midnight_rule.add_target(targets.LambdaFunction(self.my_threat_updater))



        self.event_rule_threat_update = events.Rule(
            self, "ThreatAutoSyncSchedule",
            schedule=events.Schedule.expression("cron(0 * * * ? *)")
        )

        self.event_rule_threat_update.add_target(targets.LambdaFunction(self.my_threat_updater))

        # ----------------------- CloudFormation Outputs ------------------
        CfnOutput(self, "LambdaPublicUrl", value=function_url.url, export_name="LambdaPublicUrl")
        CfnOutput(self, "S3WebsiteUrl", value=website_bucket.bucket_website_url, export_name="S3WebsiteUrl")

        # ---------------- Lambda function for scheduled execution ----------------
        self.lambda_function = _lambda.Function(
            self,
            "ChatGPTThreatAnalysis",
            function_name=LAMBDA_FUNCTION_NAME,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="scheduledExecute.lambda_handler",
            code=_lambda.Code.from_asset("EBlambda/"),
            role=self.lambda_role,
            timeout=cdk.Duration.seconds(60)
        )

        self.event_rule = events.Rule(
            self, "LambdaScheduleRule",
            rule_name="ThreatAnalysisTriggerRule",
            schedule=events.Schedule.expression("cron(0 9 * * ? *)")
        )

        self.event_rule.add_target(targets.LambdaFunction(self.lambda_function))

        # ---------------- Pinecone Knowledge base Context lambda ----------------

        self.context_lambda_function = _lambda.Function(
            self,
            "ContextLambda",
            function_name=CONTEXT_LAMBDA_FUNCTION_NAME,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="AV_data.lambda_handler",
            code=_lambda.Code.from_asset("Contextlambda/"),
            role=self.lambda_role,
            timeout=cdk.Duration.seconds(60)
        )

        self.event_rule2 = events.Rule(
            self, "ContextLambdaScheduleRule",
            rule_name="ContextTriggerRule",
            schedule=events.Schedule.expression("cron(0 * * * ? *)")
        )

        self.event_rule2.add_target(targets.LambdaFunction(self.context_lambda_function))


app = cdk.App()
MyCdkStack(app, "MyCdkStack")
app.synth()
