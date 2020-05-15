# pulumi-infra-az

### What Is This?

This is Pulumi code for deploying own AWS VPC with 6 subnets (3 public and 3 private) in 3 AZs. Each public subnet needs NAT gateway/EIP for Internet access.

### How To Use It?

It's not hard. We are going to use AWS S3 backend for saving states/checkpoints.

1. Install Pulumi https://www.pulumi.com/docs/get-started/install/.

2. Create a bucket in web console or with command:
```
$ aws s3api create-bucket \
      --bucket pulumi-states-zeezpha \
      --region us-east-1

$ aws s3api put-bucket-versioning \
      --bucket pulumi-states-zeezpha \
```
Don't forget to change bucket name because it must be unique.

3. Export values of your Programmatic Access and region:
```
$ export AWS_ACCESS_KEY_ID=AKIA1234563J76A
$ export AWS_SECRET_ACCESS_KEY=/xLmpmdp1V3abcdefghklmnopabcdefg2nKRDKO
$ export AWS_REGION=us-east-1
```
There are a lot of ways to do the same https://www.pulumi.com/docs/intro/cloud-providers/aws/setup/.

4. Login with Pulumi to s3:
```
$ pulumi login s3://pulumi-states-zeezpha
```

5. Go inside this dir and create stack:
```
$ pulumi stack init pulumi-infra-az_dev
```

6. Create Python venv and install dependencies:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

7. Copy `Pulumi.template.yaml` data to automatically created `Pulumi.pulumi-infra-az_dev.yaml`:
```
$ cat Pulumi.template.yaml >> Pulumi.pulumi-infra-az_dev.yaml
```

8. Edit `Pulumi.pulumi-infra-az_dev.yaml` according to your needs and launch:
```
$ pulumi up
```

9. Destroy when you finished your experiments:
```
$ pulumi destroy
$ pulumi stack rm pulumi-infra-az_dev
``` 