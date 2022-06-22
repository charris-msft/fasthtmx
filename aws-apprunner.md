# Instructions for deploying custom docker image to AWS App Runner

## 2-Install the pre-requisites

- [Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- or use `winget`

    ```bash
    winget install Amazon.AWSCLI
    ```

## 3-Create and Deploy

### Create the IAM role as specified in the json file

`Role Creation DOESN'T WORK YET - RELYING ON EXISTING ROLE CREATED PREVIOUSLY SOMEHOW!`

- "AccessRoleArn": "arn:aws:iam::500805876079:role/AppRunnerECRAccess"
- `aws iam create-role --role-name AppRunnerECRAccess --assume-role-policy-document file://apprunner-role.json --assume-role-policy-document ./aws-apprunner-ecr-policy.json`
- Follow [these instructions](https://aws.amazon.com/premiumsupport/knowledge-center/ecs-tasks-pull-images-ecr-repository/#:~:text=For%20AWS%20Fargate%20launch%20types%2C%20you%20must%20grant,role%20type%2C%20and%20then%20choose%20Elastic%20Container%20Service.)

### Publish the Docker image to ECR

- Login to ECR (if necessary)

    ```bash
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 500805876079.dkr.ecr.us-east-1.amazonaws.com
    ```

- Tag the image

    ```bash
    docker tag fasthtmx 500805876079.dkr.ecr.us-east-1.amazonaws.com/charris/fasthtmx:latest
    ```

- Create the ECR repository
    ```bash
    aws ecr create-repository --repository-name charris/fasthtmx
    ```

- Grant permission to the ECR repository
    ```bash
    aws ecr create-repository --repository-name 500805876079.dkr.ecr.us-east-1.amazonaws.com/charris/fasthtmx
    ```

- Push the image to ECR

    ```bash
    docker push 500805876079.dkr.ecr.us-east-1.amazonaws.com/charris/fasthtmx:latest
    ```

### Create the App Runner service

- Create a file named `aws-apprunner.json` with the configuration of the service you are creating
  - Specify your `ServiceName`
  - Specify the `AccessRoleArn` (you can get this from IAM in the AWS console)
  - Specify the `ImageIdentifier` for the image you published to ECR in the previous step
  - Specify the `Port` your application is listening on

    ```yaml
    {
        "ServiceName": "charris-fasthtmx",
        "SourceConfiguration": {
            "AuthenticationConfiguration": {
                "AccessRoleArn": "arn:aws:iam::500805876079:role/service-role/AppRunnerECRAccessRole"
            },
            "AutoDeploymentsEnabled": true,
            "ImageRepository": {
                "ImageIdentifier": "500805876079.dkr.ecr.us-east-1.amazonaws.com/charris/fasthtmx:latest",
                "ImageConfiguration": {
                    "Port": "8000"
                },
                "ImageRepositoryType": "ECR"
            }
        },
        "InstanceConfiguration": {
            "Cpu": "1 vCPU",
            "Memory": "3 GB"
        }
    }
    ```

- `aws apprunner create-service --cli-input-json file://aws-apprunner.json`

### View the creation progress

- Use the `ServiceArn` output by the creation step to view the status as the service is created

```bash
aws apprunner list-operations --service-arn arn:aws:apprunner:us-east-1:500805876079:service/charris-fasthtmx/62b8810a1414433e874ab15483dade21
```

### Get the URL for your application

- use the `ServiceArn` output by the creation step to view the description of the service, which includes the `ServiceURL`

```bash
aws apprunner describe-service --service-arn arn:aws:apprunner:us-east-1:500805876079:service/charris-fasthtmx/62b8810a1414433e874ab15483dade21
```

## 4-Update and re-deploy

- Modify the application (suggestion: increment # in H1 of templates/home/index.html)
- Update the Docker image
    `docker build --tag fasthtmx .`
- Run the local Docker image
    `docker run --name fasthtmx --publish 8000:8000 fasthtmx`
- Verify the modification on the local site
    `http://localhost:8000`
- Publish the new docker image to ECR
  - Login to ECR (if necessary)

    ```bash
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 500805876079.dkr.ecr.us-east-1.amazonaws.com
    ```

  - Tag the image

    ```bash
    docker tag fasthtmx 500805876079.dkr.ecr.us-east-1.amazonaws.com/charris/fasthtmx:latest
    ```

  - Push the image to ECR

    ```bash
    docker push 500805876079.dkr.ecr.us-east-1.amazonaws.com/charris/fasthtmx:latest
    ```

- View deployment progress

    ```bash
    aws apprunner list-operations --service-arn arn:aws:apprunner:us-east-1:500805876079:service/charris-fasthtmx/62b8810a1414433e874ab15483dade21
    ```

- Verify the modification on the cloud site
    [https://8m7sdrbget.us-east-1.awsapprunner.com/](https://8m7sdrbget.us-east-1.awsapprunner.com/)
