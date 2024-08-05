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

To create the pre-requisites:
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

## Tidy up
At the end, you may want to remove all the resources created.

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