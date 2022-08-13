#!/usr/bin/env python3
import os

import aws_cdk as cdk

from twecs.twecs_stack import TwecsStack


app = cdk.App()

app.synth()
