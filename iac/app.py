#!/usr/bin/env python3
import os
import yaml

import aws_cdk as cdk

from iac.call_analysis_stack import CallAnalysisStack


app = cdk.App()
CallAnalysisStack(
    app,
    yaml.safe_load(open('app-config.yml', 'r'))
)

app.synth()
