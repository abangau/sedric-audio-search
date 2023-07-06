from aws_cdk import Tags
from constructs import Construct


def add_tags(construct: Construct):
    Tags.of(construct).add("upteam:application", "sedric-test-dev")
    Tags.of(construct).add("upteam:owner", "abangau@cloudgeometry.io")
    Tags.of(construct).add("upteam:environment", "dev")
    Tags.of(construct).add("upteam:service", "app")
    Tags.of(construct).add("upteam:sshAccess", "abangau:abangau")
