import aws_cdk as core
import aws_cdk.assertions as assertions

from twecs.twecs_stack import TwecsStack


def test_sqs_queue_created(
):
    app = core.App(
    )
    stack = TwecsStack(
        app,
        "twecs",
    )
    template = assertions.Template.from_stack(
        stack,
    )
