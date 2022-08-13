#!/usr/bin/env python3
import os

import aws_cdk

import twecs.twecs_stack


app = aws_cdk.App(
)

Wise_profile_IDs = {
	twecs.twecs_stack.WiseEnvironment.LIVE: "13914146",
	twecs.twecs_stack.WiseEnvironment.SANDBOX: "16206006",
}

Wise_environment = twecs.twecs_stack.WiseEnvironment.SANDBOX

twecs.twecs_stack.CoreStack(
	app,
	"TwecsStack",
	env=aws_cdk.Environment(
		account="659664769788",
		region="us-east-1",
	),
	Wise_API_host=twecs.twecs_stack.WiseEnvironment.SANDBOX,
	Wise_profile_ID=Wise_profile_IDs[Wise_environment],
)

app.synth(
)
