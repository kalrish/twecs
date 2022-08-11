import aws_cdk as core
import aws_cdk.assertions as assertions

from twecs.twecs_stack import TwecsStack


# example tests. To run these tests, uncomment this file along with the example
# resource in twecs/twecs_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TwecsStack(app, "twecs")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
