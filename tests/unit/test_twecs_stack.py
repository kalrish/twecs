import aws_cdk
import aws_cdk.assertions

import twecs.twecs_stack


def test_sqs_queue_created(
):
	app = aws_cdk.App(
	)
	stack = twecs.twecs_stack.TwecsStack(
		app,
		"twecs",
	)
	template = aws_cdk.assertions.Template.from_stack(
		stack,
	)
