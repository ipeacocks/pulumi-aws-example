# pulumi-ecs-fargate

### What Is This?

This is Pulumi code for deploying own [ECS Fargate cluster](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html) on top of [previously configured network](https://github.com/ipeacocks/pulumi-aws-example/tree/master/pulumi-infra-az).

### How To Use It?

It's not hard. We are going to use AWS S3 backend for saving states/checkpoints.

&nbsp;  1-4. points you need to do only [once](https://github.com/ipeacocks/pulumi-aws-example/tree/master/pulumi-infra-az).

5. Go inside this dir and create stack:
```
$ pulumi stack init pulumi-ecs-fargate_dev
```

6. Create Python venv and install dependencies:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

7. Copy `Pulumi.template.yaml` data to automatically created `Pulumi.pulumi-ecs-fargate_dev.yaml`:
```
$ cat Pulumi.template.yaml >> Pulumi.pulumi-ecs-fargate_dev.yaml
```

8. Edit `Pulumi.pulumi-ecs-fargate_dev.yaml` according to your needs and launch:
```
$ pulumi up
```

9. Destroy when you finished your experiments:
```
$ pulumi destroy
$ pulumi stack rm pulumi-ecs-fargate_dev
```

Example is almost identical to original one https://github.com/pulumi/examples/tree/master/aws-py-fargate