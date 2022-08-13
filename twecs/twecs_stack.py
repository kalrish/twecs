import enum

import aws_cdk
import aws_cdk.aws_lambda_python_alpha
import constructs


class WiseEnvironment(
	enum.Enum,
):
	LIVE = "api.transferwise.com"
	SANDBOX = "api.sandbox.transferwise.tech"


class CoreStack(
	aws_cdk.Stack,
):
	def __init__(
		self,
		scope: constructs.Construct,
		construct_id: str,
		Wise_API_host: str,
		Wise_profile_ID: str,
		**kwargs,
	) -> None:
		super(
		).__init__(
			scope,
			construct_id,
			**kwargs,
		)

		Wise_API_token_secret = aws_cdk.aws_secretsmanager.Secret(
			self,
			"WiseApiToken",
			description="token for Wise API",
		)

		Wise_profile_ID_parameter = aws_cdk.aws_ssm.StringParameter(
			self,
			"WiseProfileId",
			description="Wise profile ID",
			string_value=Wise_profile_ID,
		)

		currency_conversion_scheduling_function = aws_cdk.aws_lambda_python_alpha.PythonFunction(
			self,
			"CurrencyConversionScheduler",
			architecture=aws_cdk.aws_lambda.Architecture.ARM_64,
			description="scheduled currency conversions with Wise",
			entry="lambda/functions/wise/",
			environment={
				"logging_level": "DEBUG",  # FIXME
				"Wise API host": Wise_API_host,
				"Wise API token secret ARN": Wise_API_token_secret.secret_arn,
				"Wise profile ID parameter name": Wise_profile_ID_parameter.parameter_name,
			},
			handler="aws_lambda_handler",
			index="index.py",
			memory_size=128,
			runtime=aws_cdk.aws_lambda.Runtime.PYTHON_3_9,
			timeout=aws_cdk.Duration.seconds(
				15,
			),
		)

		Wise_API_token_secret.grant_read(
			currency_conversion_scheduling_function,
		)
		Wise_profile_ID_parameter.grant_read(
			currency_conversion_scheduling_function,
		)


class CurrencyConversionFixSide(
	enum.Enum,
):
	SOURCE = "source"
	TARGET = "target"


class CurrencyConversionScheduleStack(
	aws_cdk.Stack,
):
	def __init__(
		self,
		scope: constructs.Construct,
		construct_id: str,
		amount: int,
		amount_fix_side: CurrencyConversionFixSide,
		handler: aws_cdk.aws_lambda.IFunction,
		reference: str,
		schedule: aws_cdk.aws_events.Schedule,
		source_currency: str,
		target_currency: str,
		**kwargs,
	) -> None:
		super(
		).__init__(
			scope,
			construct_id,
			**kwargs,
		)

		rule = aws_cdk.aws_events.Rule(
			self,
			"Rule",
			schedule=schedule,
		)

		event_data = {
			"amount": amount,
			"amount_fix_side": amount_fix_side,
			"reference": reference,
			"source_currency": source_currency,
			"target_currency": target_currency,
		}

		target = aws_cdk.aws_events_targets.LambdaFunction(
			handler,
			event=aws_cdk.aws_events.RuleTargetInput.from_object(
				event_data,
			),
		)

		rule.add_target(
			target,
		)
