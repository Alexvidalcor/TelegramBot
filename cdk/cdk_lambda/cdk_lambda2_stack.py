# AWS libraries
from aws_cdk import (
    Stack,
    aws_lambda as lambda2,
    aws_s3 as _s3,
    aws_iam as iam
)
from constructs import Construct

# Custom importation
from env.cdk_support import *

# MainClass
class Lambda2Stack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        with open("lambda/lambda2/ec2_stop_instance.py", "r") as fLambdaRead:
            lambdaData = fLambdaRead.read()

        lambdaDataProcessed = lambdaData.replace("REPLACEREGION", awsRegion).replace(
            "REPLACEAPPNAME", appName).replace("REPLACEENVDEPLOY", envDeploy)

        # Instance Role and managed Polices
        lambdaRole = iam.Role(self, appName + "_Lambda2_Role",
                        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        lambdaRole.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2FullAccess"))

        # Create ec2_stop lambda function
        function = lambda2.Function(self, "ec2_stop_lambda",
                                    runtime=lambda2.Runtime.PYTHON_3_10,
                                    handler="index.ec2_stop_function",
                                    code=lambda2.Code.from_inline(
                                        lambdaDataProcessed),
                                    role=lambdaRole)