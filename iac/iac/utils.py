from aws_cdk import Tags
from constructs import Construct


def add_tags(construct: Construct):
    Tags.of(construct).add("sedric:app", "call_searcher")
    Tags.of(construct).add("sedric:owner", "abangau@cloudgeometry.io")
    Tags.of(construct).add("sedric:environment", "dev")
