import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_deployment as s3_deployment,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    CfnOutput,
    RemovalPolicy    
)
from constructs import Construct
from aws_cdk.aws_lambda import FunctionUrlAuthType
from aws_cdk.aws_lambda import Code, DockerImageCode
from aws_cdk import aws_ecr as ecr

class MyCdkStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #-------------------FE deployment -------------------------
           
        # S3 Website for CRA Build       
        website_bucket = s3.Bucket(self, "WebsiteBucket",
            bucket_name="websitebucketakila",                  
            website_index_document="index.html",
            website_error_document="index.html",
            block_public_access=s3.BlockPublicAccess(block_public_policy=False, restrict_public_buckets=False),
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY, 
            auto_delete_objects=True
        )

        # Deploy static website content from the CRA build output
        s3_deployment.BucketDeployment(self, "DeployWebsite",
            sources=[s3_deployment.Source.asset("Dashboard/build")],
            destination_bucket=website_bucket      
        )


        #------------------ BE deployment-----------------------

          #IAM role for Lambda_function
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
            actions=["dynamodb:GetItem"],
            resources=["arn:aws:dynamodb:us-east-1:713881796790:table/AttackVectors"]
        ))


        # Reference the existing ECR repository
        repository = ecr.Repository.from_repository_name(self, "Repository", "cyber-sec-be-lambda")

        # Define the Lambda function using the container image
        flask_lambda = _lambda.DockerImageFunction(
            self,
            "FlaskLambda",
            function_name="BELambdaFunction",
            #handler="application.handler",
            #runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.DockerImageCode.from_image_asset("lambda/"),
            role=self.lambda_role,
            timeout=Duration.seconds(30),
        )

        # Create a Lambda Function URL(publicly accessible)
        function_url = flask_lambda.add_function_url(auth_type=FunctionUrlAuthType.NONE)
       

        # CloudFormation Outputs
        CfnOutput(self, "LambdaPublicUrl", value=function_url.url, export_name="LambdaPublicUrl")
        CfnOutput(self, "S3WebsiteUrl", value=website_bucket.bucket_website_url, export_name="S3WebsiteUrl")


        # -----------------Other resources----------------------

        # s3 bucket to store prompts
        prompt_bucket_name = "promptbucketakila" 

        self.prompt_bucket = s3.Bucket(
                self, "promptbucket",
                bucket_name=prompt_bucket_name,
                removal_policy=cdk.RemovalPolicy.DESTROY, 
                auto_delete_objects=True
            )
                       
        # Lambda_function to execute predefined prompts
        self.lambda_function = _lambda.Function(
            self,
            "ChatGPTThreatAnalysis",
            function_name="ThreatAnalysisLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="scheduledExecute.lambda_handler",
            code=_lambda.Code.from_asset("EBlambda/"),
            role=self.lambda_role,
            timeout=cdk.Duration.seconds(30)
        )
        
        # EventBridge rule to trigger lambda
        self.event_rule = events.Rule(
            self, "LambdaScheduleRule",
            rule_name="ThreatAnalysisTriggerRule",  
            schedule=events.Schedule.expression("cron(0 * * * ? *)")
        )
        
        # Add Lambda as the target of the EventBridge rule
        self.event_rule.add_target(targets.LambdaFunction(self.lambda_function))     

app = cdk.App()
MyCdkStack(app, "MyCdkStack")
app.synth()