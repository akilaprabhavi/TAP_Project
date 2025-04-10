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

class MyCdkStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #-------------------FE deployment -------------------------
           
        # S3 Website for CRA Build       
        website_bucket = s3.Bucket(self, "WebsiteBucket",
            bucket_name="websitebucketakila",                  
            website_index_document="index.html",
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

        # # Lambda Function for Flask App       
        # flask_lambda = _lambda.Function(self, "FlaskLambda",
        #     runtime=_lambda.Runtime.PYTHON_3_12,
        #     handler="application.handler",
        #     code=_lambda.Code.from_asset("lambda", bundling={
        #         "image": DockerImageCode.from_registry("public.ecr.aws/lambda/python:3.12"),
        #         "command":[
        #             "sh", "-c",
        #             "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"
        #         ]
        #     }),
        #     timeout=Duration.seconds(30)  
        # )

        # # Create a Lambda Function URL
        # function_url = flask_lambda.add_function_url(auth_type=FunctionUrlAuthType.NONE)
       
        # # CloudFormation Outputs
        # CfnOutput(self, "LambdaPublicUrl", value=function_url.url, export_name="LambdaPublicUrl")
        # CfnOutput(self, "S3WebsiteUrl", value=website_bucket.bucket_website_url, export_name="S3WebsiteUrl")


        # -----------------Other resources----------------------

        # s3 bucket to store prompts
        prompt_bucket_name = "promptbucketakila" 

        self.prompt_bucket = s3.Bucket(
                self, "promptbucket",
                bucket_name=prompt_bucket_name,
                removal_policy=cdk.RemovalPolicy.DESTROY, 
                auto_delete_objects=True
            )

        #IAM role for Lambda_function
        self.lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            role_name="MyLambdaExecutionRole", 
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Lambda_function to execute predefined prompts
        self.lambda_function = _lambda.Function(
            self,
            "ChatGPTThreatAnalysis",
            function_name="ThreatAnalysisLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="scheduledExecute.lambda_handler",
            code=_lambda.Code.from_asset("lambda/"),
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

        #------------------handle predefined prompts-------------------

        #  # Create Lambda Function to handle API requests
        # self.chat_lambda = _lambda.Function(self, "save_prompt_lambda",
        #     function_name="ChatLambda",
        #     runtime=_lambda.Runtime.PYTHON_3_12,
        #     handler="save_prompt_lambda.lambda_handler",
        #     code=_lambda.Code.from_asset("lambda/"),
        #     environment={
        #         "BUCKET_NAME": self.website_bucket.bucket_name,
        #     }
        # )

        # # Grant Lambda permissions to write to S3
        # self.website_bucket.grant_write(self.chat_lambda)

        # # Create API Gateway to expose the Lambda function
        # self.api = apigw.LambdaRestApi(self, "ChatAPI",
        #     handler=self.chat_lambda,
        #     proxy=True
        # )

        # cdk.CfnOutput(self, "APIEndpoint", value=self.api.url)

app = cdk.App()
MyCdkStack(app, "MyCdkStack")
app.synth()