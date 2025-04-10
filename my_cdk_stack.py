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

class MyCdkStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #-------------------FE deployment -------------------------           
        website_bucket = s3.Bucket(self, "WebsiteBucket",
            bucket_name="websitebucketakila",                  
            website_index_document="index.html",
            block_public_access=s3.BlockPublicAccess(block_public_policy=False, restrict_public_buckets=False),
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY, 
            auto_delete_objects=True
        )

        s3_deployment.BucketDeployment(self, "DeployWebsite",
            sources=[s3_deployment.Source.asset("Dashboard/build")],
            destination_bucket=website_bucket      
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

        # -----------------Other resources----------------------
        prompt_bucket_name = "promptbucketakila" 
        self.prompt_bucket = s3.Bucket(
            self, "promptbucket",
            bucket_name=prompt_bucket_name,
            removal_policy=cdk.RemovalPolicy.DESTROY, 
            auto_delete_objects=True
        )

        # IAM role for Lambda_function
        self.lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            role_name="MyLambdaExecutionRole", 
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Grant permissions to access DynamoDB
        self.threat_pulses_table.grant_read_write_data(self.lambda_role)

        # ---------------- Scheduled Threat Sync Lambda ----------------
        self.my_threat_updater = _lambda.Function(
            self,
            "MyThreatUpdaterLambda",
            function_name="MyThreatUpdater",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="auto_threat_sync.lambda_handler",
            code=_lambda.Code.from_asset("threat_updater_lambda/"),
            role=self.lambda_role,
            timeout=cdk.Duration.seconds(30),
            environment={
                "DYNAMODB_TABLE_NAME": self.threat_pulses_table.table_name,
                "AWS_REGION": "us-east-1"
            }
        )

        self.event_rule_threat_update = events.Rule(
            self, "ThreatAutoSyncSchedule",
            schedule=events.Schedule.expression("cron(0 * * * ? *)")
        )

        self.event_rule_threat_update.add_target(targets.LambdaFunction(self.my_threat_updater))


app = cdk.App()
MyCdkStack(app, "MyCdkStack")
app.synth()
