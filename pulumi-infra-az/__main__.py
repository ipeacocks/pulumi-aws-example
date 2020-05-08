import pulumi
from pulumi_aws import ec2, get_availability_zones

import utils


# read local config settings
config = pulumi.Config()

private_subnet_cidrs = config.require_object("private_subnet_cidrs")
public_subnet_cidrs = config.require_object("public_subnet_cidrs")
zones_amount = config.require_int("zones_amount")

zones = utils.get_aws_az(zones_amount)

vpc = ec2.Vpc(
    "pulumi-vpc", cidr_block=config.require("vpc_cidr"), tags={"Name": "pulumi-vpc"}
)

igw = ec2.InternetGateway("pulumi-igw", vpc_id=vpc.id)

public_rt = ec2.RouteTable(
    "pulumi-public-rt",
    vpc_id=vpc.id,
    routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": igw.id}],
    tags={"Name": "pulumi-public-rt"},
)

public_subnet_ids = []
private_subnet_ids = []

for zone, public_subnet_cidr, private_subnet_cidr in zip(
    zones, private_subnet_cidrs, public_subnet_cidrs
):

    ### public stuff

    public_subnet = ec2.Subnet(
        f"pulumi-public-subnet-{zone}",
        assign_ipv6_address_on_creation=False,
        vpc_id=vpc.id,
        map_public_ip_on_launch=True,
        cidr_block=public_subnet_cidr,
        availability_zone=zone,
        tags={"Name": f"pulumi-public-subnet-{zone}"},
    )
    ec2.RouteTableAssociation(
        f"pulumi-public-rta-{zone}",
        route_table_id=public_rt.id,
        subnet_id=public_subnet.id,
    )
    public_subnet_ids.append(public_subnet.id)

    #### private stuff

    private_subnet = ec2.Subnet(
        f"pulumi-private-subnet-{zone}",
        assign_ipv6_address_on_creation=False,
        vpc_id=vpc.id,
        map_public_ip_on_launch=False,
        cidr_block=private_subnet_cidr,
        availability_zone=zone,
        tags={"Name": f"pulumi-private-subnet-{zone}"},
    )
    eip = ec2.Eip(f"pulumi-eip-{zone}", tags={"Name": f"pulumi-eip-{zone}"})
    nat_gateway = ec2.NatGateway(
        f"pulumi-natgw-{zone}",
        subnet_id=public_subnet.id,
        allocation_id=eip.id,
        tags={"Name": f"pulumi-natgw-{zone}"},
    )
    private_rt = ec2.RouteTable(
        f"pulumi-private-rt-{zone}",
        vpc_id=vpc.id,
        routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": nat_gateway.id}],
        tags={"Name": f"pulumi-private-rt-{zone}"},
    )
    ec2.RouteTableAssociation(
        f"pulumi-private-rta-{zone}",
        route_table_id=private_rt.id,
        subnet_id=private_subnet.id,
    )
    private_subnet_ids.append(private_subnet.id)


pulumi.export("pulumi-az-amount", zones_amount)
pulumi.export("pulumi-vpc-id", vpc.id)
pulumi.export("pulumi-public-subnet-ids", public_subnet_ids)
pulumi.export("pulumi-private-subnet-ids", private_subnet_ids)
pulumi.export("pulumi-private-subnet-ids", private_subnet_ids)
