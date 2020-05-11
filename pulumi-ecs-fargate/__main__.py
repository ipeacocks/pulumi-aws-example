from pulumi import export, ResourceOptions, Config, StackReference, get_stack

import pulumi_aws as aws
import json

# Read local config settings
config = Config()

# ---------------

# Reading state for app.pulumi.com backend
# env = pulumi.get_stack()
# infra = pulumi.StackReference(f"hello-world/pulumi-infra-az/{env}")

# ---------------

# Reading S3 state
infra = StackReference(f"pulumi-infra-az_dev")

# --------------

# Read back the default VPC and public subnets, which we will use.
pulumi_vpc = infra.get_output("pulumi-vpc-id")
pulumi_private_subnets = infra.get_output("pulumi-private-subnet-ids")
pulumi_public_subnets = infra.get_output("pulumi-public-subnet-ids")
pulumi_az_amount = infra.get_output("pulumi-az-amount")


# Create an ECS cluster to run a container-based service.
cluster = aws.ecs.Cluster("pulumi-app-cluster")

# Create a SecurityGroup that permits HTTP ingress and unrestricted egress.
sgroup = aws.ec2.SecurityGroup(
    "pulumi-app-sg",
    vpc_id=pulumi_vpc,
    description="Enable HTTP access",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],}
    ],
)

# Create a load balancer to listen for HTTP traffic on port 80.
alb = aws.lb.LoadBalancer(
    "pulumi-app-alb", security_groups=[sgroup.id], subnets=pulumi_public_subnets
)

tg = aws.lb.TargetGroup(
    "pulumi-app-tg", port=80, protocol="HTTP", target_type="ip", vpc_id=pulumi_vpc
)

lb_listener = aws.lb.Listener(
    "pulumi-app-listener",
    load_balancer_arn=alb.arn,
    port=80,
    default_actions=[{"type": "forward", "target_group_arn": tg.arn}],
)

# Create an IAM role that can be used by our service's task.
te_role = aws.iam.Role(
    "pulumi-app-te-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2008-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
)

te_role_policy_attach = aws.iam.RolePolicyAttachment(
    "pulumi-app-te-policy-attach",
    role=te_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
)

# Spin up a load balanced service running our container image.
task_definition = aws.ecs.TaskDefinition(
    "pulumi-app-task-def",
    family="fargate-task-definition",
    cpu="256",
    memory="512",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    execution_role_arn=te_role.arn,
    container_definitions=json.dumps(
        [
            {
                "name": "my-app",
                "image": "nginx",
                "portMappings": [
                    {"containerPort": 80, "hostPort": 80, "protocol": "tcp"}
                ],
            }
        ]
    ),
)

service = aws.ecs.Service(
    "pulumi-app-svc",
    cluster=cluster.arn,
    # one task per az
    desired_count=pulumi_az_amount,
    launch_type="FARGATE",
    task_definition=task_definition.arn,
    network_configuration={
        "assign_public_ip": "true",
        "subnets": pulumi_private_subnets,
        "security_groups": [sgroup.id],
    },
    load_balancers=[
        {"target_group_arn": tg.arn, "container_name": "my-app", "container_port": 80}
    ],
    opts=ResourceOptions(depends_on=[lb_listener]),
)

export("url", alb.dns_name)
