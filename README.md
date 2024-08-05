# Deploying MWAA with Cloud Formation
A sample Cloud Formation project that deploys MWAA into a given AWS account.

## Set up and requirements
You will require an AWS account. Cloud formation gets deployed via AWS CLI. An AWS login session is required. An AWS profile can be configured by running:
```
aws configure
```
Fill the details as required. Once a profile is configured, a session can be created by running:
```
aws sso login --profile <PROFILE-NAME>
```
Once you are logged in, we can export the variables that will be needed for the deployment as follows:
```
export AWS_PROFILE=<PROFILE-NAME>
export CREATOR=<YOUR-NAME>
```

## Cloud formation deployment
The cloud formation template is split into pre-requisites and MWAA resources. Pre-requisites include resources that are needed before MWAA can be dployed (VPC resources, S3 bucket). Once these are deployed, some files are required to be present in the S3 bucket (we run `s3 sync` for those). Then, the MWAA resources get deployed.

### Pre-requisites deployment
MWAA requires some resources to exist in your account already - VPC resources with private and public subnets and an S3 bucket
```
aws cloudformation create-stack --stack-name mwaa-pre-requisites \
--template-body file://cf/pre-requisites.yml --profile $AWS_PROFILE \
--parameters ParameterKey=BucketName,ParameterValue=mwaa-bucket \
--tags \
 Key=Project,Value=Personal \
 Key=Environment,Value=Dev \
 Key=Creator,Value=$CREATOR \
 Key=Owner,Value=$CREATOR \
 Key=Version,Value=0.1.0
```
### Sync to S3 bucket
Next, we need to upload files required by MWAA to the S3 bucket. These include:
- folder with our dags - in this case we have a simple dag with a Dummy Operator
- startup script which will be used to set up MWAA workers
- requirements.txt file which will contain packages used by our environment
- lambda function code which will be run after MWAA gets created

#### Building a wheel for requirements

> When you create an environment with private web server access, you must package all of your dependencies in a Python wheel archive (.whl), then reference the .whl in your requirements.txt. For instructions on packaging and installing your dependencies using wheel
[From Apache Airflow access modes](https://docs.aws.amazon.com/mwaa/latest/userguide/configuring-networking.html)
You can build a wheel of all requirements and package them into a zip with:
```bash
cd mwaa
mkdir -p wheels
pip3.11 download -r requirements/requirements-wheels.txt -d wheels/
pip3.11 download -r startup/requirements-startup-wheels.txt -d wheels/
mkdir -p plugins
zip -j plugins/plugins.zip wheels/*
rm -r wheels
cd ..
```
#### Zipping lambda code
Equally our Lambda function code will need to be zipped before updating to S3
```
cd mwaa/lambda
mkdir code
cp * ./code
cd code
pip3 install -r ../requirements.txt -t .
zip -r ../airflow-lambda.zip .
cd ..
rm -r code
cd ../..
```
#### Upload files to s3
Once done, we need to sync the file to S3.
We can get the bucket name from the stack, and then run an s3 sync command to sync the contents of the `mwaa` folder into the bucket:
```
bucket_name=$(aws cloudformation describe-stacks --stack-name mwaa-pre-requisites --profile $AWS_PROFILE --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)

aws s3 sync mwaa s3://$bucket_name --profile $AWS_PROFILE
```
### MWAA deployment
Once the pre-requisites are in places, we can deploy MWAA and its resources.

We will extract some variables from the previous stack and then pass them as variables to our MWAA stack:
```
vpc_id=$(aws cloudformation describe-stacks --stack-name mwaa-pre-requisites --profile $AWS_PROFILE --query "Stacks[0].Outputs[?OutputKey=='VPC'].OutputValue" --output text)
bucket_arn=$(aws cloudformation describe-stacks --stack-name mwaa-pre-requisites --profile $AWS_PROFILE --query "Stacks[0].Outputs[?OutputKey=='BucketARN'].OutputValue" --output text)
bucket_name=$(aws cloudformation describe-stacks --stack-name mwaa-pre-requisites --profile $AWS_PROFILE --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)
private_subnet_1=$(aws cloudformation describe-stacks --stack-name mwaa-pre-requisites --profile $AWS_PROFILE --query "Stacks[0].Outputs[?OutputKey=='PrivateSubnet1'].OutputValue" --output text)
private_subnet_2=$(aws cloudformation describe-stacks --stack-name mwaa-pre-requisites --profile $AWS_PROFILE --query "Stacks[0].Outputs[?OutputKey=='PrivateSubnet2'].OutputValue" --output text)

aws cloudformation update-stack --stack-name mwaa-resources \
--template-body file://cf/mwaa-resources.yml --profile $AWS_PROFILE \
--parameters ParameterKey=VPCId,ParameterValue=$vpc_id\
 ParameterKey=BucketArn,ParameterValue=$bucket_arn\
 ParameterKey=BucketName,ParameterValue=$bucket_name\
 ParameterKey=Creator,ParameterValue=$CREATOR\
 ParameterKey=PrivateSubnet1,ParameterValue=$private_subnet_1\
 ParameterKey=PrivateSubnet2,ParameterValue=$private_subnet_2 \
--tags \
 Key=Project,Value=Personal \
 Key=Environment,Value=Dev \
 Key=Creator,Value=$CREATOR \
 Key=Owner,Value=$CREATOR \
 Key=Version,Value=0.1.0 \
--capabilities CAPABILITY_NAMED_IAM
 ```
## Tidy up
At the end, you may want to remove all the resources created.

Delete cloud formation template for NWAA:
```
aws cloudformation delete-stack --stack-name mwaa-resources --profile $AWS_PROFILE
```

Ensure that the S3 bucket is empties before attempting to delete it.

Delete cloud formation template with pre-requisites:
```
aws cloudformation delete-stack --stack-name mwaa-pre-requisites --profile $AWS_PROFILE
```

## Licence
Copyright 2024 Mechanical Rock

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.