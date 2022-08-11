import aws_cdk
import constructs


class TwecsStack(
	aws_cdk.Stack,
):

	def __init__(
		self,
		scope: constructs.Construct,
		construct_id: str,
		**kwargs,
	) -> None:
		super(
		).__init__(
			scope,
			construct_id,
			**kwargs,
		)
